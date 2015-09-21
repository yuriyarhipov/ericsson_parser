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
            selected_sector = NaN;

            var info = L.control();
            info.onAdd = function (map) {
                this._div = L.DomUtil.create('div', 'info');
                this.update();
                return this._div;
            };

            info.update = function (props) {
                console.log(props);
                this._div.innerHTML = '<h5>Sector information:</h5>';
                if (props) {
                    this._div.innerHTML = '<h5>Sector information:</h5>' +
                        '<b>RNC:</b> '+props.RNC+'<br />' +
                        '<b>SITE:</b> '+props.SITE+'<br />' +
                        '<b>Utrancell:</b> '+props.Utrancell+'<br />' +
                        '<b>Sector:</b> '+props.Sector+'<br />' +
                        '<b>LAC:</b> '+props.LAC+'<br />' +
                        '<b>RAC:</b> '+props.RAC+'<br />' +
                        '<b>SC:</b> '+props.SC+'<br />' +
                        '<b>Carrier:</b> '+props.Carrier+'<br />' +
                        '<b>Name:</b> '+props.Name+'<br />' +
                        '<b>Datum:</b> '+props.Datum+'<br />' +
                        '<b>Latitud:</b> '+props.Latitud+'<br />' +
                        '<b>Longitud:</b> '+props.Longitud+'<br />' +
                        '<b>High:</b> '+props.High+'<br />' +
                        '<b>Azimuth:</b> '+props.Azimuth+'<br />' +
                        '<b>Antenna:</b> '+props.Antenna+'<br />' +
                        '<b>Mechanical_Tilt:</b> '+props.Mechanical_Tilt+'<br />' +
                        '<b>Electrical_Tilt:</b> '+props.Electrical_Tilt;

                }
            };

            var set_marker = function(map, latitud, longitud, azimuth, color, opacity, weight, message, sector){
                L.circle([latitud, longitud], 1000, {
                            color: color,
                            opacity: opacity,
                            weight: weight,
                            sector: sector
                        })
                    .bindPopup(message)
                    .on('click', function(e){
                            var layer = e.target;
                            layer.options.old_weight=layer.options.weight;
                            layer.options.old_opacity=layer.options.opacity;
                            layer.setStyle({
                                weight: 4,
                                opacity: 1
                            });
                            if (selected_sector){
                                selected_sector.setStyle({
                                    weight: selected_sector.options.old_weight,
                                    opacity: selected_sector.options.opacity
                                });
                            }
                            selected_sector = layer;
                            info.update(layer.options.sector);
                        })
                        .setDirection(azimuth, 60)
                        .addTo(map);
            };

            $scope.markers = markers;
            $scope.default_center.lat = data[0].Latitud;
            $scope.default_center.lng = data[0].Longitud;
            $scope.default_center.zoom = 10;
            leafletData.getMap().then(function(map) {
                info.addTo(map);
                for(i=0;i<data.length;i+=1){
                    if (get_status(data[i], search_params)){
                        set_marker(map, data[i].Latitud, data[i].Longitud, data[i].Azimuth, '#f00', 0.7, 3, data[i].Utrancell, data[i]);
                        $scope.default_center.lat = data[i].Latitud;
                        $scope.default_center.lng = data[i].Longitud;
                        $scope.default_center.zoom = 13;
                    } else {
                        set_marker(map, data[i].Latitud, data[i].Longitud, data[i].Azimuth, '#03f', 0.5, 2, data[i].Utrancell, data[i]);
                    }
                };
                map.setView([$scope.default_center.lat, $scope.default_center.lng], $scope.default_center.zoom);

            });
        });
  }]);