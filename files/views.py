import json


from django.http import HttpResponse
from django.conf import settings

from celery.result import AsyncResult

from .models import Files, UploadedFiles
from tables.table import Table
from files.compare import CompareFiles, CompareTable
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
    tasks.worker.delay(filename, project, description, vendor, file_type, network)
    data = dict()
    return HttpResponse(json.dumps(data), content_type='application/json')


def files(request):
    project = request.project
    files = []
    for f in Files.objects.filter(project=project):
        files.append({
            'filename': f.filename,
            'date': f.date.strftime('%m.%d.%Y'),
            'file_type': f.file_type,
            'network': f.network,
            'vendor': f.vendor,
            'description': f.description
        })

    uploaded_files = []
    for f in UploadedFiles.objects.filter(project=project):
        job = AsyncResult(f.description)
        data = job.result or job.state
        status = 0
        if 'current' in data:
            status = data.get('current')
        uploaded_files.append({
            'filename': f.filename,
            'date': f.date.strftime('%m.%d.%Y'),
            'file_type': f.file_type,
            'status': int(status),
        })
    return HttpResponse(json.dumps({'files': files, 'uploaded_files': uploaded_files}), content_type='application/json')


def measurements(request, file_type):
    project = request.project
    data = []
    for f in Files.objects.filter(project=project, file_type=file_type):
        data.append({'filename': f.filename, 'file_type': f.file_type, 'network': f.network})
    return HttpResponse(json.dumps(data), content_type='application/json')

def licenses(request):
    project = request.project
    data = []
    for f in Files.objects.filter(project=project, file_type='license'):
        data.append({'filename': f.filename, 'file_type': f.file_type, 'network': f.network})
    return HttpResponse(json.dumps(data), content_type='application/json')

def license(request, filename, table):
    current_table = Table(table, filename)
    columns = current_table.columns
    data = current_table.get_data()
    data = data[:20]
    return HttpResponse(json.dumps({'columns': columns, 'data': data}), content_type='application/json')

def hardwares(request):
    project = request.project
    data = []
    for f in Files.objects.filter(project=project, file_type='hardware'):
        data.append({'filename': f.filename, 'file_type': f.file_type, 'network': f.network})
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_files_for_compare(request, network):
    main_file = ''
    tables = []

    if network == 'WCDMA':
        main_file = request.wcdma.filename
        for table in request.wcdma.tables.split(','):
            tables.append({'table': table, 'type': 'Table'})

    data = [file.filename for file in Files.objects.filter(project=request.project, network=network, file_type='xml')]
    data.sort()
    return HttpResponse(json.dumps({'files': data, 'main_file': main_file, 'tables': tables}), content_type='application/json')

def compare_files(request):
    data = dict()
    filename = request.POST.get('main_file')
    files = request.POST.getlist('files')
    table = request.POST.get('table')
    cells = request.POST.getlist('cells')
    if not table:
        data['compare_files'] = CompareFiles(filename, files).get_tables_info()
    if (not cells) and table:
        ct = CompareTable(table, filename, files)
        mo = ct.get_mo_list()
        data['compare_table'] = {'columns': ct.columns, 'data': ct.get_data(mo)}

    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_file(request, filename):
    Files.objects.filter(filename=filename).delete()
    return HttpResponse(json.dumps([]), content_type='application/json')

def get_files(request, network):
    project = request.project
    data = [f.filename for f in Files.objects.filter(project = project, network=network)]
    return HttpResponse(json.dumps(data), content_type='application/json')

def save_superfile(request):

    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')