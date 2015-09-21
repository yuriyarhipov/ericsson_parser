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

        var get_color = function(point, params){
            var color='#03f';
            for (var key in params){
                if (point[key]) {
                    if (point[key] == params[key]){
                        console.log(point);
                        color ='#f00';
                        break;
                    }
                }
            }
            return color
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
                    L.circle([data[i].Latitud, data[i].Longitud], 1000, {
                color: get_color(data[i], search_params),
                opacity: 0.7,
                weight: 2
            })
                    .setDirection(data[i].Azimuth, 60)
                    .addTo(map);
                };

                map.setView([data[0].Latitud, data[0].Longitud], 11);
            });
        });
  }]);