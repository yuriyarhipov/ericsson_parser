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
        var filtered_data = {};
        var marker_data = [];
        $scope.default_center = {};
        var rnd_network = $routeParams.network;
        $scope.actions = ['=', '>', '<', '>=', '<='];

        $scope.map_filters = [];
        $scope.new_filter = {
            'action': {'selected': '='},
            'param': {'selected': 'Azimuth'},
            'value': {'selected': '90'},
            'color': '#00FF00'
        };

        var basic_markers = [];

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

        var info = L.control();

            info.onAdd = function (map) {
                this._div = L.DomUtil.create('div', 'info');
                this.update();
                return this._div;
            };

            info.update = function (props) {
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

        var set_marker = function(map, latitud, longitud, azimuth, color, opacity, weight, size, message, sector){
                 L.circle([latitud, longitud], size, {
                            color: color,
                            opacity: opacity,
                            weight: weight,
                            sector: sector
                        })
                    .bindPopup(message)
                    .on('click', function(e){
                            console.log('click');
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

        $http.get('/data/rnd/' + rnd_network + '/').success(function(data) {
            var markers = {};
            var columns = $scope.columns = data.columns;
            var data = marker_data = data.data;
            selected_sector = NaN;

            $scope.markers = markers;
            $scope.default_center.lat = data[0].Latitud;
            $scope.default_center.lng = data[0].Longitud;
            $scope.default_center.zoom = 10;
            leafletData.getMap().then(function(map) {
                info.addTo(map);
                map.on('zoomend', function(e){
                    var zoom = e.target._zoom;
                    map.eachLayer(function (layer) {
                        if (layer.options.sector) {
                            var r = 1200 - (zoom*60);
                            console.log(r);
                            layer.setRadius(r);
                            //layer.setStyle({
                            //    weight: 4,
                            //    opacity: 1
                            //});
                        }
                    });

                });
                for(i=0;i<data.length;i+=1){
                    var size = 1000;
                    if (data[i].Carrier == 1){
                        size = 500;
                    }
                    if (get_status(data[i], search_params)){
                        set_marker(map, data[i].Latitud, data[i].Longitud, data[i].Azimuth, '#f00', 0.7, 3, size, data[i].Utrancell, data[i]);
                        $scope.default_center.lat = data[i].Latitud;
                        $scope.default_center.lng = data[i].Longitud;
                        $scope.default_center.zoom = 13;
                    } else {
                        set_marker(map, data[i].Latitud, data[i].Longitud, data[i].Azimuth, '#03f', 0.5, 2, size, data[i].Utrancell, data[i]);
                    }
                };
                map.setView([$scope.default_center.lat, $scope.default_center.lng], $scope.default_center.zoom);

            });
        });

        $scope.onChangeParam = function(param){
            $http.get('/data/rnd/get_param_values/' + rnd_network + '/' + param + '/').success(function(data){
                $scope.values = data;
            });
        };

        $scope.onAddFilter = function(){
            $scope.map_filters.push({
                'param': $scope.new_filter.param.selected,
                'action': $scope.new_filter.action.selected,
                'value':$scope.new_filter.value.selected,
                'color': $scope.new_filter.color});

            leafletData.getMap().then(function(map){
                    map.eachLayer(function (layer) {
                        if (layer.options.sector) {
                            map.removeLayer(layer);
                        }
                    });

                    for (var sector_id in marker_data){
                        var current_sector = marker_data[sector_id];
                        for (filter_id in $scope.map_filters){
                            var current_filter = $scope.map_filters[filter_id]
                            if (current_filter.action == '='){
                                if (current_sector[current_filter.param] == current_filter.value){
                                    current_sector.color = current_filter.color;
                                    if (!(current_sector.SITE in filtered_data)){
                                        filtered_data[current_sector.SITE] = [];
                                    }
                                    filtered_data[current_sector.SITE].push(current_sector);                                }
                            }
                        }
                    }
                    leafletData.getMap().then(function(map){
                        for (var site in filtered_data){
                            var azimuths = [];
                            var size = 1000;
                            for (var sector_id in filtered_data[site]){
                                var sector = filtered_data[site][sector_id];
                                azimuths.push(sector.Azimuth);
                                if (sector.Azimuth in azimuths){
                                    size = size / 1.5;
                                }
                                set_marker(map, sector.Latitud, sector.Longitud, sector.Azimuth, sector.color, 0.5, 2, size, sector.Utrancell, sector);
                                map.setView([sector.Latitud, sector.Longitud], 13);
                            }
                    }});
                });
        };
  }]);