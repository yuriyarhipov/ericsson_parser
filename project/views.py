import json

from django.http import HttpResponse
from django.db import connection
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from project.models import Project, UserSettings


def projects(request):
    data = []
    user_name = request.COOKIES.get('username')
    user = User.objects.get(username=user_name)
    for project in Project.objects.filter(user=user).order_by('project_name'):
        data.append({'id': project.id, 'project_name': project.project_name, 'created': project.created.strftime('%m.%d.%Y')})
    return HttpResponse(json.dumps(data), content_type='application/json')


def save_project(request):
    user_name = request.COOKIES.get('username')
    user = User.objects.get(username=user_name)        
    data = {'status': 'error', 'message': 'Sorry, Internal Error'}
    if request.POST:
        project_name = request.POST.get('project_name').replace(' ', '_')
        if Project.objects.filter(project_name=project_name, user=user).exists():
            data = {'status': 'error', 'message': 'Sorry, A project with name "%s" exists' % project_name}
        else:
            Project.objects.create(project_name=project_name, user=user)
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
            {'id': 'network', 'label': '  Radio Network Design Info (RND)', 'children': project.get_rnd_tree()},
            {'id': 'Architecture', 'label': 'Network Architecture', 'children': [
                {'id': 'GSM', 'label': 'GSM', 'children': project.get_network_tree('GSM')},
                {'id': 'WCDMA', 'label': 'WCDMA', 'children': project.get_network_tree('WCDMA')},
                {'id': 'LTE', 'label': 'LTE', 'children': project.get_network_tree('LTE')}
            ]},
            {'id': 'drive_test', 'label': 'Drive Test', 'children': project.get_drive_test()},
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


def change_pass(request):
    new_pass = request.POST.get('new_pass')
    old_pass = request.POST.get('old_pass')
    user_name = request.POST.get('user_name')
    user = authenticate(username=user_name, password=old_pass)
    if user is not None:
        user.set_password(new_pass)
        user.save()
        return HttpResponse(json.dumps({'status': 'ok'}), content_type='application/json')
    else:
        return HttpResponse(json.dumps({'status': 'no'}), content_type='application/json')



def user_settings(request, username):
    project = request.project
    if not UserSettings.objects.filter(current_project=project, user=username).exists():
        UserSettings.objects.create(
                current_project=project,
                user=username,
                gsm_file = '',
                wcdma_file = '',
                lte_file = '',
                rnd_gsm_file = '',
                rnd_wcdma_file = '',
                rnd_lte_file = '',
                gsm_color = '#ffa500',
                wcdma_color = '#0000FF',
                lte_color = '#008000',
                element_color = '#FF00FF',
                gsm_radius = '1000',
                wcdma_radius = '1200',
                lte_radius = '1500',
                map_center = '0,0',
                map_zoom = '10',
            )

    if request.method == 'GET':
        data = {
            'gsm_color': '#ffa500',
            'wcdma_color': '#0000FF',
            'lte_color': '#008000',
            'element_color': '#FF00FF',
        }
        if UserSettings.objects.filter(current_project=project, user=username).exists():
            us = UserSettings.objects.get(current_project=project, user=username)
            data['gsm_color'] = us.gsm_color
            data['wcdma_color'] = us.wcdma_color
            data['lte_color'] = us.lte_color
            data['element_color'] = us.element_color
            return HttpResponse(json.dumps(data), content_type='application/json')
    elif request.method == 'POST':

        if UserSettings.objects.filter(current_project=project, user=username).exists():
            us = UserSettings.objects.get(current_project=project, user=username)
            us.gsm_color = request.POST.get('gsm_color', us.gsm_color)
            us.wcdma_color = request.POST.get('wcdma_color', us.wcdma_color)
            us.lte_color = request.POST.get('lte_color', us.lte_color)
            us.element_color = request.POST.get('element_color', us.element_color)
            us.save()
        else:
            UserSettings.objects.create(
                current_project=project,
                user=username,
                gsm_file = '',
                wcdma_file = '',
                lte_file = '',
                rnd_gsm_file = '',
                rnd_wcdma_file = '',
                rnd_lte_file = '',
                gsm_color = '#ffa500',
                wcdma_color = '#0000FF',
                lte_color = '#008000',
                element_color = '#FF00FF',
                gsm_radius = '1000',
                wcdma_radius = '1200',
                lte_radius = '1500',
                map_center = '0,0',
                map_zoom = '10',
            )
    data = {}
    us = UserSettings.objects.get(current_project=project, user=username)
    data['gsm_color'] = us.gsm_color
    data['wcdma_color'] = us.wcdma_color
    data['lte_color'] = us.lte_color
    data['element_color'] = us.element_color
    return HttpResponse(json.dumps(data), content_type='application/json')

def changelog(request):
    project = request.project
    cursor = connection.cursor()
    cursor.execute('''
        SELECT
            mo, rnc, site, Utrancell, param_name, new_value, old_value, change_time
        FROM changelog
        WHERE (project_id=%s)''', (project.id, ))
    data = []
    for row in cursor.fetchall():
        data.append({
            'mo': row[0],
            'rnc': row[1],
            'site': row[2],
            'utrancell': row[3],
            'parameter': row[4],
            'new_value': row[5],
            'old_value': row[6],
            'date': row[7].strftime("%B %d, %Y"),
        })
    return HttpResponse(json.dumps(data), content_type='application/json')
