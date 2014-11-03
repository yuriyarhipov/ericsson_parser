import json

from openpyxl import load_workbook

from django.http import HttpResponse
from django.db import connection

from query.models import QueryTemplate
from files.wcdma import WCDMA
from files.views import handle_uploaded_file
from template import Template


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
    if network == '3g':
        data = request.wcdma.get_mo()
    return HttpResponse(json.dumps(data), content_type='application/json')


def get_param(request, mo):
    cursor = connection.cursor()
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
    for qt in QueryTemplate.objects.filter(project=request.project).distinct('template_name').order_by('template_name'):
        data.append({'template_name': qt.template_name, 'network': qt.network})
    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_template(request, template_name):
    QueryTemplate.objects.filter(project=request.project, template_name=template_name).delete()
    return HttpResponse(json.dumps([]), content_type='application/json')


def get_template_cells(request, network):
    data = []
    if network == '3g':
        wcdma = WCDMA()
        data = wcdma.get_cells(request.wcdma.filename)

    return HttpResponse(json.dumps(data), content_type='application/json')


def run_template(request):
    template = request.POST.get('template')
    cells = request.POST.getlist('cell')
    columns, data = WCDMA().run_query(template, cells, request.wcdma.filename)
    return HttpResponse(json.dumps({'columns': columns, 'data': data[:20]}), content_type='application/json')

def upload_template(request):
    data =[]
    filename = handle_uploaded_file(request.FILES.getlist('excel'))[0]
    wb = load_workbook(filename=filename, use_iterators=True)
    ws = wb.active
    for row in ws.iter_rows():
        if row[0].value != 'MO':
            excel_mo = row[0].value #check_mo(mo_list, row[0].internal_value)
            excel_param = row[1].value #check_param(excel_mo, row[1].internal_value, type)
            if excel_mo and excel_param:
                data.append(dict(mo=excel_mo, param=excel_param, min_value=row[2].value, max_value=row[3].value))

    return HttpResponse(json.dumps(data), content_type='application/json')