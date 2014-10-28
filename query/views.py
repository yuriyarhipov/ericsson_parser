import json

from django.http import HttpResponse

from query.models import GroupCells


def get_cells(request, technology):
    data = []
    if (technology == '3g') and request.wcdma:
        data = request.wcdma.get_cells()

    return HttpResponse(json.dumps(data), content_type='application/json')


def save_group_of_cells(request):
    project = request.project
    title = request.POST.get('title')
    network = request.POST.get('network')
    cells = ','.join(request.POST.getlist('cells[]'))
    GroupCells.objects.create(project=project, group_name=title, network=network, cells=cells)
    return HttpResponse(json.dumps({'success': 'ok'}), content_type='application/json')


def get_groups(request):
    project = request.project
    data = []
    for group in GroupCells.objects.filter(project=project):
        data.append({'name': group.group_name, 'network': group.network})
    return HttpResponse(json.dumps(data), content_type='application/json')
