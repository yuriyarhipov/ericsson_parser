from django.db import models


class Project(models.Model):
    project_name = models.TextField()
    created = models.DateField(auto_now=True)

    def get_list_files(self, network, file_type):
        from files.models import Files
        return [f.filename for f in Files.objects.filter(project=self, network=network, file_type=file_type)]


    def get_tree(self, network, file_type):
        data = []
        for f in self.get_list_files(network, file_type):
            data.append({'id': f.lower(), 'label': f, 'children': ''})
        return data
