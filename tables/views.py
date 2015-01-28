import json

from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from table import Table, get_excel
from files.models import Files, SuperFile, CNATemplate
from files.excel import Excel


def table(request, filename, table_name):
    if SuperFile.objects.filter(filename=filename, project=request.project).exists():
        filename = SuperFile.objects.filter(filename=filename, project=request.project).first().files
    if table_name == 'rnd':
        active_file = request.COOKIES.get('active_file')
        if Files.objects.filter(filename__iexact=active_file, project=request.project).exists():
            active_file = Files.objects.filter(filename__iexact=active_file, project=request.project).first()
        else:
            active_file = Files.objects.filter(project=request.project, network__in=['WCDMA', 'LTE']).first()

        if active_file:
            if active_file.network == 'WCDMA':
                table_name = 'rnd_wcdma'
            else:
                table_name = 'rnd_lte'
            filename = active_file.filename

    if Files.objects.filter(filename=table_name, project=request.project).exists():
        f = Files.objects.get(filename=table_name, project=request.project)
        columns, data = f.get_data()
    else:
        current_table = Table(table_name, filename)
        data = current_table.get_data()
        columns = current_table.columns

    if request.GET.get('excel'):
        return HttpResponseRedirect(Excel(request.project.project_name, table_name, columns, data).filename)

    page = request.GET.get('page', 1)
    data_length = len(data)
    t = Paginator(data, 20)
    try:
        data = t.page(page)
    except PageNotAnInteger:
        data = t.page(1)
    except EmptyPage:
        data = t.page(t.num_pages)

    return HttpResponse(json.dumps({'columns': columns, 'data': data.object_list, 'count': data_length}), content_type='application/json')


def rnd(request):
    columns =[]
    data = []
    active_file = request.COOKIES.get('active_file')
    if Files.objects.filter(filename=active_file, project=request.project).exists():
        active_file = Files.objects.filter(filename=active_file, project=request.project).first()
    else:
        active_file = Files.objects.filter(project=request.project, file_type='xml', network_in=['WCDMA', 'LTE']).first()

    if active_file:
        if active_file.network == 'WCDMA':
            table_name = 'rnd_wcdma'
        else:
            table_name = 'rnd_lte'
        current_table = Table(table_name, active_file.filename)
        columns = current_table.columns
        data = current_table.get_data()
    return HttpResponse(json.dumps({'columns': columns, 'data': data}), content_type='application/json')


def explore(request, filename):
    project = request.project
    tree_file = None
    tables = []

    if Files.objects.filter(project=project, filename=filename).exists():
        tree_file = Files.objects.filter(project=project, filename=filename).first()
        if tree_file.network == 'GSM':
            if tree_file.file_type == 'GSM BSS CNA  OSS FILE':
                tables = [{'table': cna_tables.table_name, 'filename': filename} for cna_tables in CNATemplate.objects.all()]

    else:
        tables = [{'table': table, 'filename': filename} for table in request.wcdma.tables.split(',')]

    tables.sort()
    return HttpResponse(json.dumps(tables), content_type='application/json')


def by_technology(request, network):
    data = []
    project = request.project
    if network == 'GSM':
        data = [{'label': f.filename, 'table': f.filename, 'type': 'CNA Table', 'filename': f.filename} for f in Files.objects.filter(network='GSM', project=project)]

    elif network == 'WCDMA':
        filename = request.wcdma.filename
        tables = request.wcdma.tables.split(',')
        tables.sort()
        data = [
            {'label': 'Topology', 'table': 'topology', 'type': 'Additional table', 'filename': filename},
            {'label': 'RND', 'table': 'rnd_wcdma', 'type': 'Additional table', 'filename': filename},
            {'label': 'BrightcommsRNDDate', 'table': 'BrightcommsRNDDate', 'type': 'Additional table', 'filename': filename},
            {'label': '3GNeighbors', 'table': 'threegneighbors', 'type': 'Additional table', 'filename': filename},
            {'label': '3GIRAT', 'table': '3girat', 'type': 'Additional table', 'filename': filename},
            {'label': '3GMAP_INTRAFREQ', 'table': 'map_intrafreq', 'type': 'Additional table', 'filename': filename},
            {'label': '3GMAP_INTERFREQ', 'table': 'map_interfreq', 'type': 'Additional table', 'filename': filename},
            {'label': '3GMAP_GSMIRAT', 'table': 'map_gsmirat', 'type': 'Additional table', 'filename': filename},
            {'label': '3GNeighbors_CO-SC', 'table': 'neighbors_co-sc', 'type': 'Additional table', 'filename': filename},
            {'label': '3GNeighbors_TWO_WAYS', 'table': 'neighbors_two_ways', 'type': 'Additional table', 'filename': filename},
        ]
        data.extend([{'label': table, 'table': table, 'type': 'XML table', 'filename': filename} for table in tables])

    elif network == 'LTE':
        filename = request.lte.filename
        tables = request.lte.tables.split(',')
        tables.sort()
        data = [
            {'label': 'Topology', 'table': 'topology_lte', 'type': 'Additional table', 'filename': filename},
            {'label': 'RND', 'table': 'rnd_lte', 'type': 'Additional table', 'filename': filename},
        ]
        data.extend([{'label': table, 'table': table, 'type': 'XML table', 'filename': filename} for table in tables])

    return HttpResponse(json.dumps(data), content_type='application/json')