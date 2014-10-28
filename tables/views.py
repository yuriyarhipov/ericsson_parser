import json

from django.http import HttpResponse

from table import Table

def table(request, table_name):
    active_file = None
    if table_name == 'rnd':
        active_file = request.wcdma
        if active_file.network == '3g':
            table_name = 'rnd_wcdma'
        else:
            table_name = 'rnd_wcdma'

    current_table = Table(table_name, active_file.filename)
    columns = current_table.get_columns()
    data = current_table.get_data()[:20]

    return HttpResponse(json.dumps({'columns': columns, 'data': data}), content_type='application/json')