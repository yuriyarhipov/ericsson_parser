var tableControllers = angular.module('tableControllers', []);

tableControllers.controller('TableCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $scope.filename = $routeParams.filename;
        $scope.tablename = $routeParams.table_name;
        $http.get('/data/table/' + $scope.filename + '/' + $scope.tablename + '/').success(function(data) {
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

tableControllers.controller('mapsCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $http.get('/data/maps/').success(function(data) {
            $scope.data = data;
        });
  }]);

tableControllers.controller('mapCtrl', ['$scope', '$http', '$routeParams', 'olData',
    function ($scope, $http, $routeParams, olData) {
        $http.get('/data/map/' + $routeParams.filename + '/').success(function(data) {
            var markers = data;
            angular.extend($scope, {
                center: {
                    lat: markers[0].lat,
                    lon: markers[0].lon,
                    zoom: 7
                },
                markers: markers
            });
        });
  }]);

tableControllers.controller('byTechnologyCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.network = 'GSM';
        $http.get('/data/by_technology/GSM/').success(function(data) {
            $scope.data = data;
        });

        $scope.onChangeNetwork = function(){
            $http.get('/data/by_technology/' + $scope.network).success(function(data) {
                $scope.data = data;
            });
        };

        $scope.onFilter = function(){
            $http.get('/data/by_technology/' + $scope.network + '?filter=' + $scope.file_filter).success(function(data) {
                $scope.data = data;
            });
        };
  }]);