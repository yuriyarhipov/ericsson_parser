var tableControllers = angular.module('tableControllers', []);

tableControllers.controller('TableCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        var table_name = $routeParams.table_name;
        $http.get('/data/table/' + table_name).success(function(data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
        });
  }]);
