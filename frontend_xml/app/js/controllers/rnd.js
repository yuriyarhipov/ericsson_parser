var rndControllers = angular.module('rndControllers', []);

rndControllers.controller('rndCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $scope.rowCollection = [];
        $scope.rnd_network = $routeParams.network;
        $scope.show_download_panel = false;

        $http.get('/data/rnd/' + $scope.rnd_network + '/').success(function(data){
            $scope.columns = data.columns;
            $scope.table_data = $scope.displayed_data = data.data;

        });

        $scope.complete = function(){
            $scope.show_download_panel = false;
            $http.get('/data/rnd/' + $scope.rnd_network + '/').success(function(data){
                $scope.columns = data.columns;
                $scope.data = data.data;
            });
        };


  }]);

rndControllers.controller('mapCtrl', ['$scope', '$http', '$routeParams', '$location', 'leafletData',
    function ($scope, $http, $routeParams, $location, leafletData) {
        var search_params = $location.search();
        $scope.default_center = {};
        var rnd_network = $routeParams.network;

        var markerIcon = {
            iconUrl: 'static/sector_blue.png',
        }

        var get_status = function(point, params){
            for (var key in params){
                if (point[key]) {
                    if (point[key] == params[key]){
                        return true;
                    }
                }
            }
            return false;
        };

        $http.get('/data/rnd/' + rnd_network + '/').success(function(data) {
            var markers = {};
            var columns = data.columns;
            var data = data.data;


            $scope.markers = markers;
            $scope.default_center.lat = data[0].Latitud;
            $scope.default_center.lng = data[0].Longitud;
            $scope.default_center.zoom = 10;
            leafletData.getMap().then(function(map) {
                for(i=0;i<data.length;i+=1){
                    if (get_status(data[i], search_params)){
                        L.circle([data[i].Latitud, data[i].Longitud], 1000, {
                            color: '#f00',
                            opacity: 1,
                            weight: 3
                        })
                        .setDirection(data[i].Azimuth, 60)
                        .addTo(map);
                        $scope.default_center.lat = data[i].Latitud;
                        $scope.default_center.lng = data[i].Longitud;
                        $scope.default_center.zoom = 13;
                    } else {
                        L.circle([data[i].Latitud, data[i].Longitud], 1000, {
                            color: '#03f',
                            opacity: 0.5,
                            weight: 2
                        })
                        .setDirection(data[i].Azimuth, 60)
                        .addTo(map);
                    }

                };

                map.setView([$scope.default_center.lat, $scope.default_center.lng], $scope.default_center.zoom);
            });
        });
  }]);