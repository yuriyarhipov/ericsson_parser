import json


from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.conf import settings

from .models import Files
from tables.table import Table
import tasks


def handle_uploaded_file(files):
    path = settings.STATICFILES_DIRS[0]
    result = []
    for f in files:
        filename = '/xml/'.join([path, f.name])
        destination = open(filename, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
        result.append(filename)
    return result


def save_files(request):
    project = request.project
    description = request.POST.get('description')
    vendor = request.POST.get('vendor')
    file_type = request.POST.get('file_type')
    network = request.POST.get('network')
    filename = handle_uploaded_file(request.FILES.getlist('uploaded_file'))[0]
    job = tasks.worker.delay(filename, project, description, vendor, file_type, network)
    data = dict()
    return HttpResponse(json.dumps(data), mimetype='application/json')


def files(request):
    project = request.project
    data = []
    for f in Files.objects.filter(project=project):
        data.append({
            'filename': f.filename,
            'date': f.date.strftime('%m.%d.%Y'),
            'file_type': f.file_type,
            'network': f.network,
            'vendor': f.vendor,
            'description': f.description
        })
    return HttpResponse(json.dumps(data), mimetype='application/json')


def measurements(request, file_type):
    project = request.project
    data = []
    for f in Files.objects.filter(project=project, file_type=file_type):
        data.append({'filename': f.filename, 'file_type': f.file_type, 'network': f.network})
    return HttpResponse(json.dumps(data), mimetype='application/json')

def licenses(request):
    project = request.project
    data = []
    for f in Files.objects.filter(project=project, file_type='license'):
        data.append({'filename': f.filename, 'file_type': f.file_type, 'network': f.network})
    return HttpResponse(json.dumps(data), mimetype='application/json')

def license(request, filename, table):
    current_table = Table(table, filename)
    columns = current_table.columns
    data = current_table.get_data()
    data = data[:20]
    return HttpResponse(json.dumps({'columns': columns, 'data': data}), mimetype='application/json')

def hardwares(request):
    project = request.project
    data = []
    for f in Files.objects.filter(project=project, file_type='hardware'):
        data.append({'filename': f.filename, 'file_type': f.file_type, 'network': f.network})
    return HttpResponse(json.dumps(data), mimetype='application/json')

def hardware(request, filename, table):
    current_table = Table(table, filename)
    columns = current_table.columns
    data = current_table.get_data()
    data = data[:20]
    return HttpResponse(json.dumps({'columns': columns, 'data': data}), mimetype='application/json')