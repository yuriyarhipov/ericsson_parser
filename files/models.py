from django.db import models
from project.models import Project

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
