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

def dash_model_eq(request):
    cursor = connection.cursor()
    cursor.execute("SELECT rnc, COUNT(productname)  FROM RND_WCDMA WHERE filename=%s GROUP BY rnc", (request.wcdma.filename, ))
    data = []
    for row in cursor:
        data.append([row[0], row[1]])
    data.sort()
    return HttpResponse(json.dumps(data), mimetype='application/json')


def dash_cells_lac(request):
    cursor = connection.cursor()
    cursor.execute("SELECT lac, rac, COUNT(utrancell)  FROM RND_WCDMA WHERE filename=%s GROUP BY lac, rac", (request.wcdma.filename, ))
    data = []
    for row in cursor:
        data.append(['%s %s' % (row[0], row[1]), row[2]])
    data.sort()
    return HttpResponse(json.dumps(data), mimetype='application/json')
