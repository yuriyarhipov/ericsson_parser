import json

from django.http import HttpResponse

from .models import Files

def save_files(request):
    project = request.project
    description = request.POST.get('description')
    vendor = request.POST.get('vendor')
    file_type = request.POST.get('file_type')
    network = request.POST.get('network')

    filename = request.FILES.get('uploaded_file')

    Files.objects.filter(filename=filename, project=project).delete()
    Files.objects.create(filename=filename, project=project, description=description, vendor=vendor, network=network, file_type=file_type)
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