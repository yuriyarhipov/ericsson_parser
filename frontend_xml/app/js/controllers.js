var xmlControllers = angular.module('xmlControllers', []);

xmlControllers.controller('ProjectsCtrl', ['$scope', '$http', '$cookies',
    function ($scope, $http, $cookies) {
        $scope.activeProject = function(project){
            $cookies.active_project = project;
        };

        $http.get('/data/projects/').success(function(data) {
            $scope.projects = data;
        });
  }]);

xmlControllers.controller('ActiveProjectCtrl', ['$scope', '$cookies',
    function($scope, $cookies) {
        $scope.activeProject =$cookies.active_project;
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