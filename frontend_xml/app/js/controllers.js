var xmlControllers = angular.module('xmlControllers', []);

xmlControllers.controller('ProjectsCtrl', ['$scope', '$http', 'activeProjectService',
    function ($scope, $http, activeProjectService) {
        $scope.setActiveProject = function(project){
            activeProjectService.setProject(project);
        };

        $http.get('/data/projects/').success(function(data) {
            $scope.projects = data;
        });
  }]);

xmlControllers.controller('ActiveProjectCtrl', ['$scope', '$cookies', 'activeProjectService','activeFileService' , '$location',
    function($scope, $cookies, activeProjectService, $location, activeFileService) {
        $scope.activeProject = $cookies.active_project;
        $scope.activeWCDMA = $cookies.wcdma;
        if (!$cookies.active_project){
            $location.path('/projects/');
        }

        $scope.$on('handleBroadcast', function() {
            $scope.activeProject = activeProjectService.project;
        });

        $scope.$on('activeFileBroadcast', function() {
            $scope.activeWCDMA = $cookies.wcdma;
            $scope.activeLTE = $cookies.lte;
            $scope.activeGSM = $cookies.gsm;
        });
  }]);

xmlControllers.controller('AddProjectCtrl', ['$scope', '$http', '$location',
    function ($scope, $http, $location) {
        $scope.project_data = {};

        $scope.processForm = function(){
            $http.post('/data/save_project/', $.param($scope.project_data)).success(function(){
                $location.path('/projects');
            });

		};
  }]);