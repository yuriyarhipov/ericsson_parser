from django.conf.urls import patterns, include, url

from django.contrib import admin
from project import views as project_views
from files import views as files_views
from query import views as query_views
from tables import views as table_views
from parameters import views as parameters_views

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^data/projects/$', project_views.projects),
    url(r'^data/save_project/$', project_views.save_project),
    url(r'^data/treeview/(\S+)/$', project_views.treeview),

    url(r'^data/get_cells/(\S+)/$', query_views.get_cells),
    url(r'^data/save_group_of_cells/$', query_views.save_group_of_cells),
    url(r'^data/get_groups/$', query_views.get_groups),
    url(r'^data/upload_cells_template/$', query_views.upload_cells_template),

    url(r'^data/table/(\S+)/(\S+)/$', table_views.table),
    url(r'^data/explore/(\S+)/$', table_views.explore),
    url(r'^data/by_technology/(\S+)/$', table_views.by_technology),

    url(r'^data/version_release/$', parameters_views.version_release),
    url(r'^data/get_mo/(\S+)/$', parameters_views.get_mo),
    url(r'^data/get_param/(\S+)/$', parameters_views.get_param),
    url(r'^data/add_template/$', parameters_views.add_template),
    url(r'^data/predefined_templates/$', parameters_views.predefined_templates),
    url(r'^data/delete_template/(\S+)/$', parameters_views.delete_template),
    url(r'^data/get_template_cells/(\S+)/$', parameters_views.get_template_cells),
    url(r'^data/run_template/$', parameters_views.run_template),
    url(r'^data/upload_template/$', parameters_views.upload_template),

    url(r'^data/save_file/$', files_views.save_files),
    url(r'^data/files/$', files_views.files),
    url(r'^data/measurements/(\S+)/$', files_views.measurements),
    url(r'^data/licenses/$', files_views.licenses),
    url(r'^data/license/(\S+)/(\S+)/$', files_views.license),
    url(r'^data/hardwares/$', files_views.hardwares),
    url(r'^data/hardware/(\S+)/(\S+)/$', files_views.hardware),
    url(r'^data/get_files_for_compare/(\S+)/$', files_views.get_files_for_compare),
    url(r'^data/compare_files/$', files_views.compare_files),


    url(r'^admin/', include(admin.site.urls)),
)
