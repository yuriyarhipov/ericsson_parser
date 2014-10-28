from django.db import models
from project.models import Project
from files.wcdma import WCDMA

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

    def get_cells(self):
        cells = []
        if (self.file_type == 'xml') and (self.network == '3g'):
            wcdma = WCDMA()
            for cell in wcdma.get_rnc(self.filename):
                cells.append({'cell': cell, 'type': 'RNC'})
            for cell in wcdma.get_cells(self.filename):
                cells.append({'cell': cell, 'type': 'Individuals'})
        return cells

    def get_mo(self):
        data = []
        for f in Files.objects.filter(file_type=self.file_type):
            data.extend(f.tables.split(','))
        data = set(data)
        data = list(data)
        data.sort()
        return data