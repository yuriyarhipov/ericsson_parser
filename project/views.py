import json

from django.http import HttpResponse
from django.db import connection
from project.models import Project


def projects(request):
    data = []
    for project in Project.objects.all().order_by('project_name'):
        data.append({'project_name': project.project_name, 'created': project.created.strftime('%m.%d.%Y')})

    return HttpResponse(json.dumps(data), content_type='application/json')


def save_project(request):
    data = {'status': 'error', 'message': 'Sorry, Internal Error'}
    if request.POST:
        project_name = request.POST.get('project_name')
        if Project.objects.filter(project_name=project_name).exists():
            data = {'status': 'error', 'message': 'Sorry, A project with name "%s" exists' % project_name}
        else:
            Project.objects.create(project_name=project_name)
            data = {'status': 'ok', 'message': 'Done'}

    return HttpResponse(json.dumps(data), content_type='application/json')


def treeview(request, project):
    project = Project.objects.get(project_name=project)
    data = [
        {'id': 'network', 'label': '  Radio Network Design Info (RND)', 'children': {}},
        {'id': 'GSM', 'label': 'GSM', 'children': project.get_network_tree('GSM')},
        {'id': 'WCDMA', 'label': 'WCDMA', 'children': project.get_network_tree('WCDMA')},
        {'id': 'LTE', 'label': 'LTE', 'children': project.get_network_tree('LTE')}
     ]
    return HttpResponse(json.dumps(data), content_type='application/json')

def topology_treeview(request, network):
    data = []
    filename = ''
    if network == 'GSM':
        filename = request.cna.filename
    elif network == 'WCDMA':
        filename = request.wcdma.filename
    elif network == 'LTE':
        filename = request.lte.filename
    cursor = connection.cursor()
    cursor.execute("SELECT TREEVIEW FROM TOPOLOGY_TREEVIEW WHERE filename='%s'" % (filename, ))
    for row in cursor:
        data = row[0]

    return HttpResponse(json.dumps(data), content_type='application/json')
