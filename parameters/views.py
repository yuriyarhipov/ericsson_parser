import json
from collections import OrderedDict

from openpyxl import load_workbook

from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from query.models import QueryTemplate, SiteQuery
from files.wcdma import WCDMA
from files.cna import CNA
from files.lte import LTE
from files.views import handle_uploaded_file
from template import Template
from tables.table import get_excel


def version_release(request):
    cursor = connection.cursor()
    columns = ['version', 'name']
    data = []

    cursor.execute("select DISTINCT version, vendorName from UtranCell")
    for row in cursor:
        data.append([row[0], '%s WCDMA' % row[1], ])

    return HttpResponse(json.dumps({'columns': columns, 'data': data}), content_type='application/json')


def get_param(request, network):
    data = []
    if network == 'WCDMA':
        data = request.wcdma.get_param()
    elif network == 'GSM':
        data = request.cna.get_param()
    elif network == 'LTE':
        data = request.lte.get_param()

    return HttpResponse(json.dumps(data), content_type='application/json')


def add_template(request):
    data = []
    select_mo_val = request.POST.getlist('mo')
    select_mo_param_val = request.POST.getlist('param')
    min_values = request.POST.getlist('min_value')
    max_values = request.POST.getlist('min_value')
    template_name = request.POST.get('template_name')
    project = request.project
    network = request.POST.get('network')
    if network == 'WCDMA':
        i = 0
        select_mo_param_val = []
        select_mo_val = []
        min_values = []
        max_values = []
        for param in request.POST.getlist('param'):
            print param
            mo = request.wcdma.get_mo(param)
            if mo:
                select_mo_val.append(mo)
                select_mo_param_val.append(param)
                min_values.append(request.POST.getlist('min_value')[i])
                max_values.append(request.POST.getlist('max_value')[i])
            i += 1

    elif network == 'GSM':
        select_mo_val = [request.cna.filename, ]
    elif network == 'LTE':
        select_mo_val, select_mo_param_val = request.lte.get_mo(select_mo_param_val)
    Template().save_template(project, network, template_name, select_mo_val, select_mo_param_val, min_values, max_values)
    Template().check_tables()
    return HttpResponse(json.dumps(data), content_type='application/json')


def predefined_templates(request):
    data = []
    for qt in QueryTemplate.objects.filter().distinct('template_name').order_by('template_name'):
        data.append({'template_name': qt.template_name, 'network': qt.network})
    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_template(request, template_name):
    QueryTemplate.objects.filter(project=request.project, template_name=template_name).delete()
    return HttpResponse(json.dumps({'sucess': 'ok', }), content_type='application/json')


def get_template_cells(request, network):
    data = []
    if network == 'GSM':
        data = CNA().get_cells(request.cna.filename)
    elif network == 'WCDMA':
        wcdma = WCDMA()
        data = wcdma.get_cells(request.wcdma.filename)
    elif network == 'LTE':
        data = LTE().get_cells(request.lte.filename)

    return HttpResponse(json.dumps(data), content_type='application/json')


def run_template(request):
    template = request.GET.get('template')
    cells = request.GET.getlist('cell')
    network = request.GET.get('network')

    if network == 'GSM':
        columns, data = CNA().run_query(template, cells, request.cna.filename)
    elif network == 'WCDMA':
        columns, data = WCDMA().run_query(template, cells, request.wcdma.filename)
    elif network == 'LTE':
        columns, data = LTE().run_query(template, cells, request.lte.filename)

    if request.GET.get('excel'):
        excel_data = []
        for row in data:
            new_row = [cell[0] for cell in row]
            excel_data.append(new_row)
        return HttpResponseRedirect('/static/%s' % get_excel(template, columns, excel_data))

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


def upload_template(request):
    data =[]
    filename = handle_uploaded_file(request.FILES.getlist('excel'))[0]
    wb = load_workbook(filename=filename, use_iterators=True)
    ws = wb.active
    for row in ws.iter_rows():
        if row[0].value != 'PARAMETER':
            excel_param = row[0].value
            if excel_param:
                data.append(dict(param=excel_param, min_value=row[1].value, max_value=row[2].value))

    return HttpResponse(json.dumps(data), content_type='application/json')


def edit_template(request, template):
    data = {}
    data['template'] = template
    data['param_table'] = []
    for qt in QueryTemplate.objects.filter(template_name=template).all():
        data['network'] = qt.network
        data['param_table'].append({'mo': qt.mo, 'param': qt.param_name, 'min_value': qt.min_value, 'max_value': qt.max_value})
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_automatic_site_query(request):
    filename = handle_uploaded_file(request.FILES.getlist('uploaded_file'))[0]
    data = Template().site_query(project=request.project, filename=filename)
    return HttpResponse(json.dumps({'data': data}), content_type='application/json')


def automatic_site_query(request):
    data = OrderedDict()
    for query in SiteQuery.objects.filter(project=request.project):
        if query.site not in data:
            data[query.site] = []
        data[query.site].append([query.param_name, query.param_min, query.param_max])
    return HttpResponse(json.dumps({'data': data}), content_type='application/json')


def get_site_query(request, site):
    data = dict()
    data['tabs'] = []
    params = Template().get_site_query(site, request.wcdma.filename)
    for tab_name, tab_params in params.iteritems():
        data['tabs'].append({'title': tab_name, 'content': tab_params})

    return HttpResponse(json.dumps(data), content_type='application/json')

