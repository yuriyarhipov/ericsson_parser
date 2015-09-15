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

tableControllers.controller('mapCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {

        var markerIcon = {
            iconUrl: 'static/sector3.png',
        }

        $scope.default_center = {
            lat: 8.74085783958435,
            lng: -82.43604183197021,
            zoom: 9
        };

        $http.get('/data/map/' + $routeParams.filename + '/').success(function(data) {
            var markers = [];
            for(i=0;i<data.length;i+=1){
                markers.push({
                    'lat': data[i].lat,
                    'lng': data[i].lon,
                    'icon': markerIcon,
                    'iconAngle': data[i].rotation,
                    message: "Utrancell:" + data[i].utrancell,
                })
            };
            $scope.markers = markers;
            $scope.default_center = {
                lat: data[0].lat,
                lng: data[0].lon,
            };
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

tableControllers.controller('cellDefCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.radius = 100;
        $http.get('/data/cell_definition/').success(function(data) {
                $scope.radius = data.radius;
        });
  }]);