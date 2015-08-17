from django.conf.urls import patterns, include, url

from django.contrib import admin
from project import views as project_views
from files import views as files_views
from query import views as query_views
from tables import views as table_views
from parameters import views as parameters_views
from dashboard import views as dash_view

admin.autodiscover()

urlpatterns = patterns('',

    url(r'^data/projects/$', project_views.projects),
    url(r'^data/save_project/$', project_views.save_project),
    url(r'^data/delete_projects/(\S+)/$', project_views.delete_projects),
    url(r'^data/treeview/(\S+)/$', project_views.treeview),
    url(r'^data/topology_treeview/(\S+)/(\S+)/$', project_views.topology_treeview),
    url(r'^data/get_topology_roots/(\S+)/$', project_views.get_topology_roots),

    url(r'^data/get_cells/(\S+)/$', query_views.get_cells),
    url(r'^data/save_group_of_cells/$', query_views.save_group_of_cells),
    url(r'^data/get_groups/$', query_views.get_groups),
    url(r'^data/upload_cells_template/$', query_views.upload_cells_template),

    url(r'^data/table/(\S+)/(\S+)/$', table_views.table),
    url(r'^data/explore/(\S+)/$', table_views.explore),
    url(r'^data/by_technology/(\S+)/$', table_views.by_technology),

    url(r'^data/maps/$', table_views.maps),
    url(r'^data/map/(\S+)/$', table_views.map),

    url(r'^data/version_release/$', parameters_views.version_release),
    url(r'^data/get_param/(\S+)/$', parameters_views.get_param),
    url(r'^data/add_template/$', parameters_views.add_template),
    url(r'^data/predefined_templates/$', parameters_views.predefined_templates),
    url(r'^data/delete_template/(\S+)/$', parameters_views.delete_template),
    url(r'^data/get_templates/(\S+)/$', parameters_views.get_templates),

    url(r'^data/get_template_cells/(\S+)/(\S+)/$', parameters_views.get_template_cells),
    url(r'^data/run_template/$', parameters_views.run_template),
    url(r'^data/upload_template/$', parameters_views.upload_template),
    url(r'^data/edit_template/(\S+)/$', parameters_views.edit_template),
    url(r'^data/save_automatic_site_query/$', parameters_views.save_automatic_site_query),
    url(r'^data/automatic_site_query/(\S+)/$', parameters_views.automatic_site_query),
    url(r'^data/get_site_query/(\S+)/(\S+)/$', parameters_views.get_site_query),
    url(r'^data/get_sites/(\S+)/$', parameters_views.get_sites),
    url(r'^data/get_network_files/(\S+)/$', parameters_views.get_network_files),

    url(r'^data/save_file/$', files_views.save_files),
    url(r'^data/files/$', files_views.files),
    url(r'^data/measurements/(\S+)/$', files_views.measurements),
    url(r'^data/licenses/$', files_views.licenses),
    url(r'^data/license/(\S+)/(\S+)/$', files_views.license),
    url(r'^data/hardwares/$', files_views.hardwares),
    url(r'^data/get_files_for_compare/(\S+)/$', files_views.get_files_for_compare),
    url(r'^data/compare_files/$', files_views.compare_files),
    url(r'^data/delete_file/(\S+)/$', files_views.delete_file),
    url(r'^data/files/get_files/(\S+)/$', files_views.get_files),
    url(r'^data/files/save_superfile/$', files_views.save_superfile),
    url(r'^data/files/set_cna_template/$', files_views.set_cna_template),
    url(r'^data/files/get_cna_template/$', files_views.get_cna_template),
    url(r'^data/files/status/(\S+)/$', files_views.status),
    url(r'^data/files/get_excel/(\S+)/$', files_views.get_excel),

    url(r'^data/dash_num_sectors/$', dash_view.dash_num_sectors),
    url(r'^data/dash_model_eq/$', dash_view.dash_model_eq),
    url(r'^data/dash_cells_lac/$', dash_view.dash_cells_lac),

    url(r'^data/audit/set_audit_template/$', table_views.set_audit_template),
    url(r'^data/audit/get_audit_template/$', table_views.get_audit_template),


    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
