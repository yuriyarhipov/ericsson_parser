import json

from django.http import HttpResponse

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
    data = [{'id': 'network', 'label': 'Radio Network Configuration', 'children': [
        {'id': '2g', 'label': 'GSM', 'children': [{'id': '2g_ERICSSON', 'label': 'ERICSSON', 'children': project.get_tree('2g', 'txt')}]},
        {'id': '3g', 'label': 'WCDMA', 'children': [{'id': '3g_ERICSSON', 'label': 'ERICSSON', 'children': project.get_tree('3g', 'xml')}]},
        {'id': '4g', 'label': 'LTE', 'children': [{'id': '4g_ERICSSON', 'label': 'ERICSSON', 'children': project.get_tree('4g', 'xml')}]}
    ]}, ]

    return HttpResponse(json.dumps(data), content_type='application/json')