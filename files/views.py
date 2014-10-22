import json


from django.http import HttpResponse
from django.shortcuts import HttpResponseRedirect
from django.conf import settings

from .models import Files
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
    print 'OK1'
    job = tasks.worker.delay(filename, project, description, vendor, file_type, network)

    #Files.objects.filter(filename=filename, project=project).delete()
    #Files.objects.create(filename=filename, project=project, description=description, vendor=vendor, network=network, file_type=file_type)
    data = dict()
    return HttpResponse(json.dumps(data), mimetype='application/json')


def files(request):
    data = []
    for f in Files.objects.all():
        data.append({
            'filename': f.filename,
            'date': f.date.strftime('%m.%d.%Y'),
            'file_type': f.file_type,
            'network': f.network,
            'vendor': f.vendor,
            'description': f.description
        })
    return HttpResponse(json.dumps(data), mimetype='application/json')