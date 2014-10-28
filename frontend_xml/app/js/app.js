var XmlApp = angular.module(
    'xmlApp',
    [
        'ngRoute',
        'ngCookies',
        'ui.bootstrap',
        'xmlControllers',
        'filesControllers',
        'ngUpload',
        'angularTreeview',
        'treeViewControllers',
        'activeProjectModule',
        'queryControllers',
        'tableControllers',
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
            when('/table/:table_name',{
                templateUrl: 'templates/tables/table.html',
                controller: 'TableCtrl'
            }).
            otherwise({
                redirectTo: '/'
            });

    }]);

XmlApp.run(function($rootScope, $http, $cookies){
    // set the CSRF token here
    $http.defaults.headers.post['X-CSRFToken'] = $cookies.csrftoken;
    $http.defaults.headers.post['Content-Type'] = 'application/x-www-form-urlencoded';

});