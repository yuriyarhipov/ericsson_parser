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
    url(r'^data/login/$', project_views.login),
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
    url(r'^data/measurements/wncs/$', files_views.measurements_wncs),
    url(r'^data/measurements/wncs_top/$', files_views.measurements_wncs_top),
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
    url(r'^data/universal_table/(\S+)/$', files_views.universal_table),

    url(r'^data/dash_num_sectors/$', dash_view.dash_num_sectors),
    url(r'^data/dash_model_eq/$', dash_view.dash_model_eq),
    url(r'^data/dash_cells_lac/$', dash_view.dash_cells_lac),

    url(r'^data/audit/set_audit_template/$', table_views.set_audit_template),
    url(r'^data/audit/get_audit_template/$', table_views.get_audit_template),
    url(r'^data/audit/run_audit/(\S+)/(\S+)/$', table_views.run_audit),
    url(r'^data/audit/audit_param/(\S+)/(\S+)/(\S+)/$', table_views.audit_param),
    url(r'^data/audit/excel_audit/(\S+)/(\S+)/$', table_views.excel_audit),
    url(r'^data/audit/power_audit/(\S+)/$', table_views.power_audit),
    url(r'^data/audit/excel_power_audit/(\S+)/$', table_views.excel_power_audit),

    url(r'^data/distance/get_sectors/$', table_views.get_sectors),
    url(r'^data/distance/get_logical_sectors/$', table_views.get_logical_sectors),

    url(r'^data/distance/get_rbs/$', table_views.get_rbs),
    url(r'^data/distance/get_dates/$', table_views.get_dates),
    url(r'^data/distance/get_charts/(\S+)/(\S+)/(\S+)/$', table_views.get_charts),
    url(r'^data/distance/get_low_coverage/(\S+)/(\S+)/(\S+)/$', table_views.get_low_coverage),
    url(r'^data/distance/get_over_coverage/(\S+)/(\S+)/(\S+)/$', table_views.get_over_coverage),
    url(r'^data/distance/get_load_distr/(\S+)/(\S+)/(\S+)/$', table_views.get_load_distr),
    url(r'^data/distance/get_excel/(\S+)/(\S+)/$', table_views.get_distance_excel),
    url(r'^data/distance/logical_sectors/(\S+)/(\S+)/$', table_views.logical_sectors),
    url(r'^data/distance/logical_sectors/$', table_views.logical_sectors),
    url(r'^data/distance/psc_distance/$', table_views.psc_distance),

    url(r'^data/rnd/get_param_values/(\S+)/(\S+)/$', files_views.get_param_values),
    url(r'^data/rnd/get_rnd_pd/(\S+)/(\S+)/(\S+)/(\S+)/$', files_views.get_rnd_pd),
    url(r'^data/rnd/get_rnd_neighbors(\S+)/(\S+)/$', files_views.get_rnd_neighbors),
    url(r'^data/rnd/get_new3g(\S+)/(\S+)/$', files_views.get_new3g),
    url(r'^data/rnd/new3g3g/$', files_views.new3g3g),
    url(r'^data/rnd/del3g3g/$', files_views.del3g3g),
    url(r'^data/rnd/flush3g3g/$', files_views.flush3g3g),
    url(r'^data/rnd/get3g3gscript/$', files_views.get3g3gscript),
    url(r'^data/rnd/same_neighbor/$', files_views.get_same_neighbor),
    url(r'^data/rnd/table/(\S+)/$', files_views.rnd_table),
    url(r'^data/rnd/init_map/$', files_views.init_map),
    url(r'^data/rnd/map_frame/(\S+)/$', files_views.map_frame),
    url(r'^data/rnd/(\S+)/$', files_views.rnd),
    url(r'^data/rnd/$', files_views.rnd),

    url(r'^data/drive_test/$', files_views.drive_test),
    url(r'^data/drive_test_init/$', files_views.drive_test_init),
    url(r'^data/files/set_drive_test_legend/$', files_views.set_drive_test_legend),
    url(r'^data/files/get_drive_test_legend/$', files_views.get_drive_test_legend),
    url(r'^data/files/get_drive_test_param/(\S+)/$', files_views.get_drive_test_param),
    url(r'^data/drive_test_point/(\S+)/$', files_views.drive_test_point),

    url(r'^data/save_logical_relation/$', table_views.save_logical_relation),
    url(r'^data/logical_relations/$', table_views.logical_relations),
    url(r'^data/delete_logical_relation/$', table_views.delete_logical_relation),





    url(r'^data/admin/', include(admin.site.urls)),
    url(r'^data/api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
