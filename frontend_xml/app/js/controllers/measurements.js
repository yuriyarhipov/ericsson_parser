var measurementsControllers = angular.module('measurementsControllers', []);

measurementsControllers.controller('measurementsCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        var file_type = $routeParams.file_type;
        $http.get('/data/measurements/' + file_type).success(function(data) {
            $scope.files = data;
        });
  }]);
