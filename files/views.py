import json

from openpyxl import load_workbook

from django.http import HttpResponse
from django.conf import settings
from django.shortcuts import HttpResponseRedirect

from celery.result import AsyncResult

from .models import Files, UploadedFiles, SuperFile, CNATemplate
from tables.table import Table
from files.compare import CompareFiles, CompareTable
from files.excel import ExcelFile
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


def status(request, id):
    job = AsyncResult(id)
    data = job.result or job.state

    try:
        json_data = json.dumps(data)
    except:
        data = {'current': 100, }
        json_data = json.dumps(data)

    return HttpResponse(json_data, mimetype='application/json')


def save_files(request):
    project = request.project
    description = request.POST.get('description')
    vendor = request.POST.get('vendor')
    file_type = request.POST.get('file_type')
    network = request.POST.get('network')
    filename = handle_uploaded_file(request.FILES.getlist('uploaded_file'))[0]
    job = tasks.worker.delay(filename, project, description, vendor, file_type, network)
    data = dict(id=job.id)
    return HttpResponse(json.dumps(data), content_type='application/json')


def files(request):
    project = request.project
    files = []

    active_files = []

    if request.lte:
        active_files.append(request.lte.filename)
    if request.cna:
        active_files.append(request.cna.filename)
    if request.wcdma:
        active_files.append(request.wcdma.filename)

    for f in Files.objects.filter(project=project):
        status = 'uploaded'
        files.append({
            'filename': f.filename,
            'date': f.date.strftime('%m.%d.%Y'),
            'file_type': f.file_type,
            'network': f.network,
            'vendor': f.vendor,
            'description': f.description,
            'status': status
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
            'status': 'processing',
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
    for f in Files.objects.filter(project=project, file_type__in=['WCDMA LICENSE FILE OSS XML', 'LTE LICENSE FILE OSS XML']):
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
    for f in Files.objects.filter(project=project, file_type__in=['WCDMA HARDWARE FILE OSS XML', 'LTE HARDWARE FILE OSS XML']):
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
    SuperFile.objects.filter(filename=filename).delete()
    return HttpResponse(json.dumps([]), content_type='application/json')


def get_files(request, network):
    project = request.project
    data = [f.filename for f in Files.objects.filter(project=project, network=network)]
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_superfile(request):
    project = request.project
    filename = request.POST.get('filename')
    selected_files = request.POST.getlist('files')
    source_file = Files.objects.filter(filename=selected_files[0], project=project).first()
    network = source_file.network
    file_type = source_file.file_type
    vendor = source_file.vendor
    tasks.superfile.delay(filename, selected_files)
    #SuperFile.objects.filter(filename=filename, network=network, project=project).delete()
    #SuperFile.objects.create(
    #    filename=filename,
    #    files=','.join(selected_files),
    #    network=network,
    #    project=project,
    #    file_type=file_type,
    #    vendor=vendor)
    return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')


def set_cna_template(request):
    project = request.project
    CNATemplate.objects.filter(project=project).delete()

    filename = handle_uploaded_file(request.FILES.getlist('uploaded_file'))[0]
    wb = load_workbook(filename=filename)

    for sheet_name in wb.get_sheet_names():
        ws = wb.get_sheet_by_name(sheet_name)
        columns = []
        for col in ws.columns:
            if col[0].value:
                columns.append(col[0].value)
        sql_columns = ','.join(columns)

        table_name = sheet_name.split('-')
        table_name = table_name[len(table_name)-1]
        table_name = table_name.strip().replace(' ', '_')
        CNATemplate.objects.create(project=project, table_name=table_name, columns=sql_columns)

    return HttpResponse(json.dumps([]), content_type='application/json')


def get_cna_template(request):
    tables = []
    project = request.project
    for cna_template in CNATemplate.objects.filter(project=project).order_by('table_name'):
        tables.append({'table_name': cna_template.table_name, 'columns': cna_template.columns})

    return HttpResponse(json.dumps(tables), content_type='application/json')


def get_excel(request, network):
    filename = ''
    if network == 'GSM':
        filename = request.gsm.filename
    elif network == 'WCDMA':
        filename = request.wcdma.filename
    elif network == 'LTE':
        filename = request.lte.filename


    return HttpResponseRedirect(ExcelFile(request.project, filename).excel_filename)





