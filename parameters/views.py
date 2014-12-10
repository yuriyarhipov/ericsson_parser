import json

from openpyxl import load_workbook

from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.db import connection
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


from query.models import QueryTemplate
from files.wcdma import WCDMA
from files.cna import CNA
from files.lte import LTE
from files.views import handle_uploaded_file
from files.models import Files
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


def get_mo(request, network):
    data = []
    project = request.project
    if network == 'WCDMA':
        data = request.wcdma.get_mo()
    elif network == 'GSM':
        data = [f.filename for f in Files.objects.filter(project=project, network='GSM')]
    elif network == 'LTE':
        data = request.lte.get_mo()
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_param(request, mo):
    cursor = connection.cursor()
    if Files.objects.filter(filename=mo).exists():
        cursor.execute('SELECT * FROM "%s" LIMIT 0;' % mo)
    else:
        cursor.execute('SELECT * FROM %s LIMIT 0;' % mo)
    data = [desc[0] for desc in cursor.description]

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
        if row[0].value != 'MO':
            excel_mo = row[0].value
            excel_param = row[1].value
            if excel_mo and excel_param:
                data.append(dict(mo=excel_mo, param=excel_param, min_value=row[2].value, max_value=row[3].value))

    return HttpResponse(json.dumps(data), content_type='application/json')


def edit_template(request, template):
    data = {}
    data['template'] = template
    data['param_table'] = []
    for qt in QueryTemplate.objects.filter(template_name=template).all():
        data['network'] = qt.network
        data['param_table'].append({'mo': qt.mo, 'param': qt.param_name, 'min_value': qt.min_value, 'max_value': qt.max_value})
    return HttpResponse(json.dumps(data), content_type='application/json')