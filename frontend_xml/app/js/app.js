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
        'angularTreeview',
        'treeViewControllers',
        'activeProjectModule',
        'queryControllers',
        'tableControllers',
        'dashControllers',
        'parameterControllers',
        'measurementsControllers',
        'ui.select'
    ]);

XmlApp.config(['$routeProvider',
    function($routeProvider, $httpProvider, $cookies){
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
            otherwise({
                redirectTo: '/'
            });

    }]);

XmlApp.run(function($rootScope, $http, $cookies){
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';

});