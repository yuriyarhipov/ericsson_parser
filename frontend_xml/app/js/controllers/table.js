var tableControllers = angular.module('tableControllers', []);

tableControllers.controller('TableCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $scope.filename = $routeParams.filename
        $scope.tablename = $routeParams.table_name
        $http.get('/data/table/' + $scope.filename + '/' + $scope.tablename).success(function(data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
            $scope.totalItems = data.count;
            $scope.itemsPerPage = 20;
        });
        $scope.pageChanged = function() {
            $http.get('/data/table/' + $scope.filename + '/' + $scope.tablename + '?page=' + $scope.currentPage ).success(function(data) {
                $scope.data = data.data;
            });
        };
  }]);

tableControllers.controller('exploreCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $http.get('/data/explore/' + $routeParams.filename + '/').success(function(data) {
            $scope.tables = data;
        });
  }]);