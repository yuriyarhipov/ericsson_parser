import json

from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from table import Table, get_excel
from files.models import Files


def table(request, filename, table_name):

    if table_name == 'rnd':
        active_file = request.COOKIES.get('active_file')
        if Files.objects.filter(filename__iexact=active_file, project=request.project).exists():
            active_file = Files.objects.filter(filename__iexact=active_file, project=request.project).first()
        else:
            active_file = Files.objects.filter(project=request.project, file_type='xml', network__in=['3g', '4g']).first()

        if active_file:
            if active_file.network == '3g':
                table_name = 'rnd_wcdma'
            else:
                table_name = 'rnd_lte'
            filename = active_file.filename

    if Files.objects.filter(filename=table_name, project=request.project).exists():
        f = Files.objects.get(filename=table_name, project=request.project)
        columns, data = f.get_data()
    else:
        current_table = Table(table_name, filename)
        columns = current_table.columns
        data = current_table.get_data()

    if request.GET.get('excel'):
        return HttpResponseRedirect('/static/%s' % get_excel(table_name, columns, data))

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
        active_file = Files.objects.filter(project=request.project, file_type='xml', network_in=['3g', '4g']).first()

    if active_file:
        if active_file.network == '3g':
            table_name = 'rnd_wcdma'
        else:
            table_name = 'rnd_lte'
        current_table = Table(table_name, active_file.filename)
        columns = current_table.columns
        data = current_table.get_data()
    return HttpResponse(json.dumps({'columns': columns, 'data': data}), content_type='application/json')


def explore(request, filename):
    tables = [{'table': table, 'filename': filename} for table in request.wcdma.tables.split(',')]
    tables.sort()
    return HttpResponse(json.dumps(tables), content_type='application/json')