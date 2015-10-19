from project.models import Project


class ActiveProject(object):

    def process_request(self, request):
        active_project = request.COOKIES.get('active_project')
        print active_project
        if Project.objects.filter(project_name=active_project).exists():
            project = Project.objects.get(project_name=active_project)
        else:
            project = Project.objects.all().first()
        request.project = project