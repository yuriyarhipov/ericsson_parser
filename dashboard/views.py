import json

from django.http import HttpResponse
from django.db import connection

def dash_num_sectors(request):

    cursor = connection.cursor()
    cursor.execute("SELECT rnc, count(site) from Topology where filename='%s' group by rnc" % (request.wcdma.filename, ))
    rnc = []
    for r in cursor:
        rnc.append([r[0], r[1]])
    data = rnc
    data.sort()
    return HttpResponse(json.dumps(data), mimetype='application/json')
