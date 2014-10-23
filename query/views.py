import json

from django.http import HttpResponse

def get_cells(request, technology):
    data = []
    if (technology == '3g') and request.wcdma:
        data = request.wcdma.get_cells()

    return HttpResponse(json.dumps(data), mimetype='application/json')
