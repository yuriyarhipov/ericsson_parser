from django.conf.urls import patterns, include, url

from django.contrib import admin
from project import views as project_views
from files import views as files_views
from query import views as query_views
from tables import views as table_views

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^data/projects/$', project_views.projects),
    url(r'^data/save_project/$', project_views.save_project),
    url(r'^data/treeview/(\S+)/$', project_views.treeview),

    url(r'^data/get_cells/(\S+)/$', query_views.get_cells),
    url(r'^data/save_group_of_cells/$', query_views.save_group_of_cells),
    url(r'^data/get_groups/$', query_views.get_groups),

    url(r'^data/table/(\S+)/$', table_views.table),


    url(r'^data/save_file/$', files_views.save_files),
    url(r'^data/files/$', files_views.files),
    url(r'^admin/', include(admin.site.urls)),
)
