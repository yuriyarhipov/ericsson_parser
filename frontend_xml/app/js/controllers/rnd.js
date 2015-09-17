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

rndControllers.controller('mapCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $scope.default_center = {};
        $scope.layers = {
                    baselayers: {
                        mapbox_light: {
                            name: 'Mapbox Light',
                            url: 'http://api.tiles.mapbox.com/v4/{mapid}/{z}/{x}/{y}.png?access_token={apikey}',
                            type: 'xyz',
                            layerOptions: {
                                apikey: 'pk.eyJ1IjoiYnVmYW51dm9scyIsImEiOiJLSURpX0pnIn0.2_9NrLz1U9bpwMQBhVk97Q',
                                mapid: 'bufanuvols.lia22g09'
                            }
                        },
                        osm: {
                            name: 'OpenStreetMap',
                            url: 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                            type: 'xyz'
                        }
                    }
                }
        var rnd_network = $routeParams.network;

        var markerIcon = {
            iconUrl: 'static/sector_blue.png',
        }


        $http.get('/data/rnd/' + rnd_network + '/').success(function(data) {
            var markers = {};
            var data = data.data;
            var columns = data.columns;



            for(i=0;i<data.length;i+=1){
                markers[data[i].Utrancell] = {
                    'lat': data[i].Latitud,
                    'lng': data[i].Longitud,
                    'icon': markerIcon,
                    'iconAngle': data[i].Azimuth,
                    message: "Utrancell:" + data[i].Utrancell,
                }

            };

            $scope.markers = markers;
            $scope.default_center.lat = data[0].Latitud;
            $scope.default_center.lng = data[0].Longitud;
            $scope.default_center.zoom = 10;


        });
  }]);