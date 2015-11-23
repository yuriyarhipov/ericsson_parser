var XmlApp = angular.module(
    'xmlApp',
    [
        'ngRoute',
        'ngCookies',
        'ui.bootstrap',
        'highcharts-ng',
        'xmlControllers',
        'filesControllers',
        'ngUpload',
        'treeControl',
        'treeViewControllers',
        'activeProjectModule',
        'activeFileModule',
        'uploadFileModule',
        'queryControllers',
        'tableControllers',
        'dashControllers',
        'parameterControllers',
        'measurementsControllers',
        'rndControllers',
        'ui.select',
        'ng-context-menu',
        'smart-table',
        'auditControllers',
        'distanceControllers',
        'flash',
        'leaflet-directive',
        'pageslide-directive',
        'ui.grid',
        'angularSpinner',
        'ui.grid.exporter',
        'ui.grid.selection',
        'ui.grid.resizeColumns',
        'ui.grid.moveColumns',
        'ui.grid.edit',
        'ui.grid.rowEdit',
        'ui.grid.cellNav'
    ]);

XmlApp.config(['$routeProvider',
    function($routeProvider){
        $routeProvider.
            when('/projects',{
                templateUrl: 'templates/projects.html',
                controller: 'ProjectsCtrl'
            }).
            when('/add_project',{
                templateUrl: 'templates/add_project.html',
                controller: 'AddProjectCtrl'
            }).
            when('/files_hub',{
                templateUrl: 'templates/files/files_hub.html',
                controller: 'FilesHubCtrl'
            }).
            when('/add_file',{
                templateUrl: 'templates/files/add_file.html',
                controller: 'AddFileCtrl'
            }).
            when('/create_group_of_cells',{
                templateUrl: 'templates/query/create_group_of_cells.html',
                controller: 'CreateGroupOfCellsCtrl'
            }).
            when('/groups',{
                templateUrl: 'templates/query/groups.html',
                controller: 'GroupsCtrl'
            }).
            when('/table/:filename/:table_name',{
                templateUrl: 'templates/tables/table.html',
                controller: 'TableCtrl'
            }).
            when('/register_version_release',{
                templateUrl: 'templates/tables/table.html',
                controller: 'registerVRCtrl'
            }).
            when('/create_predefined_template',{
                templateUrl: 'templates/template/create_template.html',
                controller: 'createTemplateCtrl'
            }).
             when('/edit_template/:template',{
                templateUrl: 'templates/template/create_template.html',
                controller: 'editTemplateCtrl'
            }).
            when('/predefined_templates',{
                templateUrl: 'templates/template/predefined_templates.html',
                controller: 'predefinedTemplatesCtrl'
            }).
            when('/run_template',{
                templateUrl: 'templates/template/run_template.html',
                controller: 'runTemplateCtrl'
            }).
            when('/explore/:filename',{
                templateUrl: 'templates/tables/explore.html',
                controller: 'exploreCtrl'
            }).
            when('/measurements/:file_type',{
                templateUrl: 'templates/measurements/measurements_table.html',
                controller: 'measurementsCtrl'
            }).
            when('/licenses',{
                templateUrl: 'templates/files/licenses.html',
                controller: 'licensesCtrl'
            }).
            when('/license/:filename/:table',{
                templateUrl: 'templates/tables/table.html',
                controller: 'licenseCtrl'
            }).
            when('/hardwares',{
                templateUrl: 'templates/files/hardwares.html',
                controller: 'hardwaresCtrl'
            }).
            when('/hardware/:filename/:table',{
                templateUrl: 'templates/tables/table.html',
                controller: 'hardwareCtrl'
            }).
            when('/compare_files/',{
                templateUrl: 'templates/files/compare_files.html',
                controller: 'compareFilesCtrl'
            }).
            when('/compare_templates/',{
                templateUrl: 'templates/files/compare_templates.html',
                controller: 'compareTemplatesCtrl'
            }).
            when('/by_technology/',{
                templateUrl: 'templates/tables/by_technology.html',
                controller: 'byTechnologyCtrl'
            }).
            when('/dashboard_wcdma/',{
                templateUrl: 'templates/dashboard/wcdma.html',
                controller: 'dashWcdmaCtrl'
            }).
            when('/superfile/',{
                templateUrl: 'templates/files/superfile.html',
                controller: 'superfileCtrl'
            }).
            when('/set_automatic_site_query/',{
                templateUrl: 'templates/query/set_automatic_site_query.html',
                controller: 'automaticSiteQueryCtrl'
            }).
            when('/parameters_overview/',{
                templateUrl: 'templates/query/parameters_overview.html',
                controller: 'parameters_overviewCtrl'
            }).
            when('/set_cna_template/',{
                templateUrl: 'templates/files/set_cna_template.html',
                controller: 'setCnaTemplateCtrl'
            }).
            when('/set_audit_template/',{
                templateUrl: 'templates/audit/set_audit_template.html',
                controller: 'setAuditTemplateCtrl'
            }).
            when('/run_network_audit/',{
                templateUrl: 'templates/audit/run_network_audit.html',
                controller: 'runNetworkAuditCtrl'
            }).
            when('/status/:id/',{
                templateUrl: 'templates/files/upload.html',
                controller: 'uploadFileCtrl'
            }).
            when('/run_audit/',{
                templateUrl: 'templates/audit/run_network_audit.html',
                controller: 'runAuditCtrl'
            }).
            when('/power_audit/',{
                templateUrl: 'templates/audit/power_audit.html',
                controller: 'powerAuditCtrl'
            }).
            when('/access_distance/',{
                templateUrl: 'templates/distance/distance.html',
                controller: 'accessDistanceCtrl'
            }).
            when('/psc_distance/',{
                templateUrl: 'templates/distance/psc_distance.html',
                controller: 'pscDistanceCtrl'
            }).
            when('/audit_param/:network/:filename/:param_name/',{
                templateUrl: 'templates/audit/audit_param.html',
                controller: 'auditParamCtrl'
            }).
            when('/cell_definition',{
                templateUrl: 'templates/tables/cell_definition.html',
                controller: 'cellDefCtrl'
            }).
            when('/set_logical_sector',{
                templateUrl: 'templates/distance/set_logical_sector.html',
                controller: 'logicalSectorCtrl'
            }).
            when('/rnd/:network',{
                templateUrl: 'templates/rnd/rnd.html',
                controller: 'rndCtrl'
            }).
            when('/map/',{
                templateUrl: 'templates/rnd/map.html',
                controller: 'mapCtrl'
            }).
            when('/about/',{
                templateUrl: 'templates/about.html',
            }).
            when('/map_settings/',{
                templateUrl: 'templates/rnd/settings.html',
                controller: 'mapSettingsCtrl'
            }).
            when('/same_neighbor/',{
                templateUrl: 'templates/rnd/same_neighbor.html',
                controller: 'sameNeighborCtrl'
            }).
            when('/login/',{
                templateUrl: 'templates/login.html',
                controller: 'authCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });

    }]);

XmlApp.run(function($rootScope, $http, $cookies){
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.get('csrftoken');
    $http.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';

});