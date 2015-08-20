import json

from django.shortcuts import HttpResponseRedirect
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from table import Table, get_excel
from files.models import Files, SuperFile, CNATemplate, AuditTemplate
from files.excel import Excel
from django.conf import settings
from openpyxl import load_workbook


def handle_uploaded_file(files):
    path = settings.STATICFILES_DIRS[0]
    result = []
    for f in files:
        filename = '/xml/'.join([path, f.name])
        destination = open(filename, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        result.append(filename)
    return result


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
    columns = []
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
    file_filter = request.GET.get('filter')
    project = request.project
    if network == 'GSM':
        filename = request.gsm.filename
        for cna_table in CNATemplate.objects.all().order_by('table_name'):
            data.append({'label': cna_table.table_name, 'table': cna_table.table_name, 'type': 'CNA Table', 'filename': filename})

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

    data_result = []

    for f in data:
        if file_filter and f.get('label'):
            if file_filter.lower() in f.get('label').lower():
                data_result.append(f)
        else:
            data_result.append(f)

    return HttpResponse(
        json.dumps(data_result),
        content_type='application/json')


def maps(request):
    project = request.project
    filenames = [f.filename for f in Files.objects.filter(project=project)]
    return HttpResponse(
        json.dumps(filenames),
        content_type='application/json')


def map(request, filename):
    project = request.project
    f = Files.objects.filter(project=project, filename=filename).first()
    data = f.get_map()
    return HttpResponse(
        json.dumps(data),
        content_type='application/json')


def set_audit_template(request):
    project = request.project
    network = request.POST.get('network')
    AuditTemplate.objects.filter(project=project, network=network).delete()
    filename = handle_uploaded_file(request.FILES.getlist('uploaded_file'))[0]
    wb = load_workbook(filename=filename, use_iterators=True)
    result = []
    for sheet_name in wb.get_sheet_names():
        ws = wb.get_sheet_by_name(sheet_name)
        for row in ws.iter_rows():
            if (row[0].value != 'Parameter') and (row[1].value):
                result.append({'param': row[0].value, 'value': row[1].value})
                AuditTemplate.objects.create(project=project, network=network, param=row[0].value, value=row[1].value)

    return HttpResponse(json.dumps(result), content_type='application/json')


def get_audit_template(request):
    project = request.project
    network = request.GET.get('network')
    result = []
    for at in AuditTemplate.objects.filter(
            project=project,
            network__iexact=network):
        result.append({'param': at.param, 'value': at.value})
    return HttpResponse(json.dumps(result), content_type='application/json')


def run_audit(request, network, filename):
    project = request.project
    result = []
    for at in AuditTemplate.objects.filter(project=project, network=network):
        value = at.check_param(filename)
        complaint = value.get('complaint', 0)
        not_complaint = value.get('not_complaint', 0)
        total = complaint + not_complaint
        if total != 0:
            percent = int(float(complaint) / float(total) * 100)
        else:
            percent = 0

        result.append({
            'param': at.param,
            'recommended': at.value,
            'complaint': complaint,
            'not_complaint': not_complaint,
            'total': total,
            'percent': percent})
    chart = []
    for param in result:
        chart.append([param.get('param'), param.get('complaint')])
    return HttpResponse(json.dumps({'table': result, 'chart': chart}), content_type='application/json')


def power_audit(request, filename):
    project = request.project
    audit = Files.objects.get(project=project, filename=filename).power_audit()
    chart = [audit.get(sector_count), len(audit.get('miss_sector'))]
    table = audit.get('miss_sector')
    return HttpResponse(json.dumps({'chart':chart, 'table': table}), content_type='application/json')