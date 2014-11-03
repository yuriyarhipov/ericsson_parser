var tableControllers = angular.module('tableControllers', []);

tableControllers.controller('TableCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        var table_name = $routeParams.table_name;
        var filename = $routeParams.filename;
        var table_data = [];
        $http.get('/data/table/' + filename + '/' + table_name).success(function(data) {
            $scope.columns = data.columns;
            table_data = data.data;
            $scope.data = table_data.slice(0,20);
            $scope.totalItems = table_data.length;
            $scope.currentPage = 1;
            $scope.itemsPerPage = 20;
        });
        $scope.pageChanged = function() {
            var index = $scope.currentPage * 20;
            $scope.data = table_data.slice(index -20,index);
        };
  }]);

tableControllers.controller('exploreCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $http.get('/data/explore/' + $routeParams.filename + '/').success(function(data) {
            $scope.tables = data;
        });
  }]);