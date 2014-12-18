import json

from django.http import HttpResponse

from project.models import Project
from tables.table import Topology


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
        {'id': 'network', 'label': '  Radio Network Design Info (RND)', 'children': []},
        {'id': 'GSM', 'label': 'GSM', 'children': project.get_network_tree('GSM')},
        {'id': 'WCDMA', 'label': 'WCDMA', 'children': project.get_network_tree('WCDMA')},
        {'id': 'LTE', 'label': 'LTE', 'children': project.get_network_tree('LTE')}
     ]
    return HttpResponse(json.dumps(data), content_type='application/json')

def topology_treeview(request):
    data = []
    wcdma = request.wcdma.filename
    tree = Topology(wcdma).get_tree()
    for rnc in tree:
        rnc_children = []
        for site in tree[rnc]:
            site_children = []
            for sector in tree[rnc][site]:
                sector_children = []
                for utrancell in tree[rnc][site][sector]:
                    sector_children.append({'id': utrancell, 'label': utrancell, 'children': []})
                site_children.append({'id': sector, 'label': sector, 'children': sector_children})
            rnc_children.append({'id': site, 'label': site, 'children': site_children})
        data.append({'id': rnc, 'label': rnc, 'children': rnc_children})
    return HttpResponse(json.dumps(data), content_type='application/json')