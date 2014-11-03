import json

from django.http import HttpResponse

from table import Table
from files.models import Files


def table(request, filename, table_name):
    if table_name == 'rnd':
        if request.wcdma.network == '3g':
            table_name = 'rnd_wcdma'
        else:
            table_name = 'rnd_wcdma'

    if Files.objects.filter(filename=table_name, project=request.project).exists():
        f = Files.objects.get(filename=table_name, project=request.project)
        columns, data = f.get_data()
    else:
        current_table = Table(table_name, filename)
        columns = current_table.columns
        data = current_table.get_data()
    data = data
    return HttpResponse(json.dumps({'columns': columns, 'data': data}), content_type='application/json')


def explore(request, filename):
    tables = [{'table': table, 'filename': filename} for table in request.wcdma.tables.split(',')]
    tables.sort()
    return HttpResponse(json.dumps(tables), content_type='application/json')