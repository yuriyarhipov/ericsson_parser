from django.db import models
from django.db import connection

from project.models import Project
from files.wcdma import WCDMA


class UploadedFiles(models.Model):
    filename = models.TextField()
    date = models.DateTimeField(auto_now=True)
    file_type = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    vendor = models.TextField()
    network = models.TextField()
    project = models.ForeignKey(Project)


class Files(models.Model):
    filename = models.TextField()
    date = models.DateTimeField(auto_now=True)
    tables = models.TextField(blank=True)
    excel_filename = models.TextField(blank=True)
    archive = models.TextField(blank=True)
    file_type = models.CharField(max_length=50, blank=True)
    description = models.TextField()
    vendor = models.TextField()
    network = models.TextField()
    project = models.ForeignKey(Project)

    def get_active_file(self, project, network, filename):
        file_type = ''
        if Files.objects.filter(filename=filename, project=project).exists():
            return Files.objects.get(filename=filename, project=project)

        if SuperFile.objects.filter(filename=filename, project=project).exists():
            return SuperFile.objects.get(filename=filename, project=project)

        if SuperFile.objects.filter(project=project, network=network).exists():
            return SuperFile.objects.filter(project=project, network=network).first()

        if network == 'WCDMA':
            file_type = ['WCDMA RADIO OSS BULK CM XML FILE', ]
        elif network == 'LTE':
            file_type = ['LTE RADIO eNodeB BULK CM XML FILE', ]
        elif network == 'GSM':
            file_type = ['GSM BSS CNA  OSS FILE', ]

        return Files.objects.filter(project=project, file_type__in=file_type, network=network).first()

    def get_cells(self):
        cells = []
        if ('XML FILE' in self.file_type) and (self.network == 'WCDMA'):
            wcdma = WCDMA()
            cells = wcdma.get_cells(self.filename)
        return cells

    def get_mo(self, param):
        cursor = connection.cursor()
        if self.network in ['WCDMA', 'LTE']:
            tables = set()
            for f in Files.objects.filter(project=self.project, network=self.network):
                tables = tables.union(set(f.tables.split(',')))
            for table in tables:
                cursor.execute('SELECT * FROM %s LIMIT 0;' % table)
                columns = [desc[0] for desc in cursor.description]
                if (param.lower() in columns) and (('utrancell' in columns) or ('element1' in columns) or ('element2' in columns)):
                    return table

    def get_data(self):
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM "%s"' % (self.filename.split('.')[0], ))
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return columns, data

    def get_param(self):
        cursor = connection.cursor()
        tables = set()
        params = set()
        if self.network in ['WCDMA', 'LTE']:
            for f in Files.objects.filter(project=self.project, network=self.network):
                tables = tables.union(set(f.tables.split(',')))
            for table in tables:
                cursor.execute('SELECT * FROM %s LIMIT 0;' % table)
                table_params = set(desc[0] for desc in cursor.description)
                if ('utrancell' in table_params) or ('element1' in table_params) or ('element2' in table_params):
                    params = params.union(set(desc[0] for desc in cursor.description))
            params.discard('mo')
            params.discard('version')
            params.discard('vendor')
            params.discard('element')
            params.discard('element1')
            params.discard('element2')
            params.discard('vendorname')
            params.discard('utrancell')
        else:
            cursor.execute('SELECT * FROM "%s" LIMIT 0' % self.filename)
            params = set(desc[0] for desc in cursor.description)

        data = list(params)
        data.sort()
        return data



class SuperFile(models.Model):
    filename = models.TextField()
    date = models.DateTimeField(auto_now=True)
    files = models.TextField()
    network = models.TextField()
    project = models.ForeignKey(Project)
    file_type = models.CharField(max_length=50, blank=True)
    vendor = models.TextField()

class ExcelFile(models.Model):
    filename = models.TextField()
    table = models.TextField()
    project = models.ForeignKey(Project)
    excel_file = models.TextField()