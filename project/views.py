import json

from django.http import HttpResponse
from django.db import connection
from django.contrib.auth import authenticate
from project.models import Project


def projects(request):
    data = []
    for project in Project.objects.all().order_by('project_name'):
        data.append({'id': project.id, 'project_name': project.project_name, 'created': project.created.strftime('%m.%d.%Y')})

    return HttpResponse(json.dumps(data), content_type='application/json')


def save_project(request):
    data = {'status': 'error', 'message': 'Sorry, Internal Error'}
    if request.POST:
        project_name = request.POST.get('project_name').replace(' ', '_')
        if Project.objects.filter(project_name=project_name).exists():
            data = {'status': 'error', 'message': 'Sorry, A project with name "%s" exists' % project_name}
        else:
            Project.objects.create(project_name=project_name)
            data = {'status': 'ok', 'message': 'Done'}

    return HttpResponse(json.dumps(data), content_type='application/json')


def delete_projects(request, project_name):
    data = []
    Project.objects.filter(project_name=project_name).delete()
    for project in Project.objects.all().order_by('project_name'):
        data.append({'project_name': project.project_name, 'created': project.created.strftime('%m.%d.%Y')})

    return HttpResponse(json.dumps(data), content_type='application/json')


def treeview(request, project):
    #project.project_name
    project = Project.objects.get(project_name=project)
    data = [
            {'id': 'network', 'label': '  Radio Network Design Info (RND)',
                'children': [
                    {'id': 'GSM', 'label': 'GSM', 'link': '/rnd/gsm/'},
                    {'id': 'WCDMA', 'label': 'WCDMA', 'link': '/rnd/wcdma/'},
                    {'id': 'LTE', 'label': 'LTE', 'link': '/rnd/lte/'},
                ]},
            {'id': 'Architecture', 'label': 'Network Architecture', 'children': [
                {'id': 'GSM', 'label': 'GSM', 'children': project.get_network_tree('GSM')},
                {'id': 'WCDMA', 'label': 'WCDMA', 'children': project.get_network_tree('WCDMA')},
                {'id': 'LTE', 'label': 'LTE', 'children': project.get_network_tree('LTE')}
            ]},
            {'id': 'drive_test', 'label': 'Drive Test', 'show_check': True, 'children': project.get_drive_test()},
    ]
    return HttpResponse(json.dumps(data), content_type='application/json')


def topology_treeview(request, network, root):
    data = []
    filename = ''
    if network == 'GSM':
        filename = request.cna.filename
    elif network == 'WCDMA':
        filename = request.wcdma.filename
    elif network == 'LTE':
        filename = request.lte.filename
    cursor = connection.cursor()
    cursor.execute("SELECT TREEVIEW FROM TOPOLOGY_TREEVIEW WHERE (filename='%s') AND (root='%s')" % (filename, root, ))
    for row in cursor:
        data.extend(row[0])
    return HttpResponse(json.dumps(data), content_type='application/json')

def get_topology_roots(request, network):
    data = []
    filename = ''
    if network == 'GSM':
        filename = request.cna.filename
    elif network == 'WCDMA':
        filename = request.wcdma.filename
    elif network == 'LTE':
        filename = request.lte.filename
    cursor = connection.cursor()
    cursor.execute("SELECT DISTINCT root FROM TOPOLOGY_TREEVIEW WHERE filename='%s'" % (filename, ))
    for row in cursor:
        data.append(row[0])
    return HttpResponse(json.dumps(data), content_type='application/json')


def login(request):
    login = request.POST.get('login')
    password = request.POST.get('pass')
    user = authenticate(username=login, password=password)
    if user is not None:
        return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'no'}), content_type='application/json')




