var rndControllers = angular.module('rndControllers', []);

rndControllers.controller('rndCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $scope.rnd_network = $routeParams.network;
        $scope.show_download_panel = false;


        $http.get('/data/rnd/' + $scope.rnd_network + '/').success(function(data){
            $scope.columns = data.columns;
            $scope.data = data.data;
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

        var get_icon = function(columns, point, params){
            var icon = {
                iconUrl: 'static/sector_blue.png'
            }
            for (var i=0;i<columns.length;i+=1){
                if (params[columns[i]]) {
                    if (point[columns[i]] == params[columns[i]]){
                        icon.iconUrl ='static/sector_red.png';
                        break;
                    }
                }
            }
            return icon
        };

        $http.get('/data/rnd/' + rnd_network + '/').success(function(data) {
            var markers = {};
            var columns = data.columns;
            var data = data.data;

            for(i=0;i<data.length;i+=1){
                markers[data[i].Utrancell] = {
                    'lat': data[i].Latitud,
                    'lng': data[i].Longitud,
                    'icon': get_icon(columns, data[i], search_params),
                    'iconAngle': data[i].Azimuth,
                    message: "Utrancell:" + data[i].Utrancell,
                }

            };

            $scope.markers = markers;
            $scope.default_center.lat = data[0].Latitud;
            $scope.default_center.lng = data[0].Longitud;
            $scope.default_center.zoom = 10;
            //leafletData.getMap().then(function(map) {
            //    marker = new L.circle([51.5, -0.09], 500, {
            //        startAngle: 45,
            //        stopAngle: 135,
            //
            //         });
            //    marker.addTo(map);
            //    map.setView([51.505, -0.09], 13);
            //});
        });
  }]);