var xmlControllers = angular.module('xmlControllers', []);

xmlControllers.controller('ProjectsCtrl', ['$scope', '$http', 'activeProjectService', '$cookies',
    function ($scope, $http, activeProjectService, $cookies) {
        $scope.setActiveProject = function(project){
            $scope.activeWCDMA = 'red';
            $scope.activeLTE = 'red';
            $scope.activeGSM = 'red';
            if ('gsm' in $cookies){
                delete $cookies['gsm'];
            }
            if ('wcdma' in $cookies){
                delete $cookies['wcdma'];
            }
            if ('lte' in $cookies){
                delete $cookies['lte'];
            }
            activeProjectService.setProject(project);
        };

        $http.get('/data/projects/').success(function(data) {
            $scope.projects = data;
        });

        $scope.onDeleteProject = function(project_name){
            $http.post('/data/delete_projects/' + project_name + '/').success(function(data) {
                $scope.projects = data;
            });
        };
  }]);

xmlControllers.controller('ActiveProjectCtrl', ['$scope', '$cookies', 'activeProjectService', '$location',
    function($scope, $cookies, activeProjectService, $location) {
        $scope.activeProject = $cookies.get('active_project');
        $scope.activeWCDMA = $cookies.get('wcdma');
        if (!$cookies.get('active_project')){
            $location.path('/projects/');
        }
        $scope.activeWCDMA = 'red';
        $scope.activeLTE = 'red';
        $scope.activeGSM = 'red';

        if ('gsm' in $cookies){
            $scope.activeGSM = 'green';
        }
        if ('lte' in $cookies){
            $scope.activeLTE = 'green';
        }
        if ('wcdma' in $cookies){
            $scope.activeWCDMA = 'green';
        }

        $scope.$on('handleBroadcast', function() {
            $scope.activeProject = activeProjectService.project;
            $scope.activeWCDMA = 'red';
        $scope.activeLTE = 'red';
        $scope.activeGSM = 'red';

        if ('gsm' in $cookies){
            $scope.activeGSM = 'green';
        }
        if ('lte' in $cookies){
            $scope.activeLTE = 'green';
        }
        if ('wcdma' in $cookies){
            $scope.activeWCDMA = 'green';
        }
        });

        $scope.$on('activeFileBroadcast', function() {
        $scope.activeWCDMA = 'red';
        $scope.activeLTE = 'red';
        $scope.activeGSM = 'red';

        if ('gsm' in $cookies){
            $scope.activeGSM = 'green';
        }
        if ('lte' in $cookies){
            $scope.activeLTE = 'green';
        }
        if ('wcdma' in $cookies){
            $scope.activeWCDMA = 'green';
        }
        });
  }]);

xmlControllers.controller('AddProjectCtrl', ['$scope', '$http', '$location', 'activeProjectService',
    function ($scope, $http, $location, activeProjectService) {
        $scope.project_data = {};

        $scope.processForm = function(){
            $http.post('/data/save_project/', $.param($scope.project_data)).success(function(){
                activeProjectService.setProject($scope.project_data['project_name']);
                $location.path('/projects');
            });

		};
  }]);