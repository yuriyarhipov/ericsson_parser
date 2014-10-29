import json

from django.http import HttpResponse
from django.db import connection
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
