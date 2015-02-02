from django.db import models
from project.models import Project


class GroupCells(models.Model):
    project = models.ForeignKey(Project)
    group_name = models.CharField(max_length=255)
    network = models.CharField(max_length=255)
    cells = models.TextField()


class QueryTemplate(models.Model):
    project = models.ForeignKey(Project)
    network = models.CharField(max_length=255)
    template_name = models.CharField(max_length=255)
    param_name = models.CharField(max_length=255)
    min_value = models.CharField(max_length=255)
    max_value = models.CharField(max_length=255)


class SiteQuery(models.Model):
    project = models.ForeignKey(Project)
    site = models.TextField()
    param_name = models.TextField()
    param_min = models.TextField(blank=True)
    param_max = models.TextField(blank=True)
