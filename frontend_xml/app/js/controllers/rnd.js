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
                $scope.table_data = $scope.displayed_data = data.data;
            });
        };
  }]);

rndControllers.controller('mapCtrl', ['$scope', '$http', '$routeParams', 'leafletData', '$location',
    function ($scope, $http, $routeParams, leafletData, $location) {
        var search_params = $location.search();
        var rnd_network = $routeParams.network;
        var carriers_size = {'1': 1500};
        var min_carrier_size = 1500;
        var sector_azimuths_size = {};
        $scope.rnd_value = {};
        $scope.rnd_param = {};
        var data_length = 0;
        var legend_info = []

        $scope.controls = {
                    fullscreen: {
                        position: 'topleft'
                    }
                };

        var legend = L.control({position: 'bottomright'});

        legend.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'legend');
            return this._div;
        };

        legend.update = function (param, value, color, cnt) {
            this._div.innerHTML +=
                    '<i style="background:' + color + '"></i> '+ param+'='+value+'(' + cnt +')<br>';

        };

        $http.get('/data/rnd/' + rnd_network + '/').success(function(data) {
            $scope.columns = data.columns;
            var data = data.data;
            data_length = data.length;
            $scope.rnd_param['selected'] = $scope.columns[0];
            $scope.onChangeParam($scope.columns[0]);
            var sectors = {};
            var selected_sector;

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

            data.sort(function(a,b){
                return parseFloat(a.Carrier) - parseFloat(b.Carrier);
            });

            for (var id in data){
                if (data[id].SITE in sectors){
                    sectors[data[id].SITE].push(data[id])
                } else {
                    sectors[data[id].SITE]= [data[id], ];
                }
            }

            leafletData.getMap().then(function(map) {
                L.control.scale().addTo(map);
                info.addTo(map);
                legend.addTo(map);

                for (var sector_id in data){
                    var sector = data[sector_id];
                    var size = 1000;

                    if (sector.Carrier in carriers_size){
                        size = carriers_size[sector.Carrier];
                    } else {
                        size = min_carrier_size * 0.9;
                        carriers_size[sector.Carrier] = min_carrier_size = size;
                    }

                    if (sector.SITE in sector_azimuths_size){
                        if (sector.Azimuth in sector_azimuths_size[sector.SITE]){
                            size = sector_azimuths_size[sector.SITE][sector.Azimuth][sector_azimuths_size[sector.SITE][sector.Azimuth].length-1] * 0.9;
                            sector_azimuths_size[sector.SITE][sector.Azimuth].push(size)
                        } else {
                            sector_azimuths_size[sector.SITE][sector.Azimuth] = [size,];
                        }
                    } else {
                        var az = {}
                        az[sector.Azimuth] = [size,];
                        sector_azimuths_size[sector.SITE]=az;
                    }

                    L.circle([sector.Latitud, sector.Longitud], size, {
                            color: '#03f',
                            opacity: 0.7,
                            weight: 2,
                            sector: sector,
                            base_radius: size
                    })
                    .bindPopup(sector.Utrancell)
                    .setDirection(sector.Azimuth, 60)
                    .on('click', function(e){
                            var layer = e.target;
                            layer.options.old_weight=layer.options.weight;
                            layer.options.old_opacity=layer.options.opacity;
                            layer.setStyle({
                                weight: 3,
                                opacity: 1
                            });
                            if (selected_sector){
                                selected_sector.setStyle({
                                    weight: selected_sector.options.old_weight,
                                    opacity: selected_sector.options.old_opacity
                                });
                            }
                            selected_sector = layer;
                            info.update(layer.options.sector);
                        })
                    .addTo(map);
                }
                map.setView([data[0].Latitud, data[0].Longitud], 10);

                map.on('zoomend', function(e){
                    var zoom = e.target._zoom;
                    map.eachLayer(function (layer) {
                        if (layer.options.sector) {
                            zkf = ((zoom-10)*-12+100)/100
                            layer.setRadius(zkf*layer.options.base_radius);
                        }
                    });
                });

            });
            for (var s_param in search_params){
                $scope.onAddFilter(s_param, search_params[s_param]);
            }
        });

        $scope.onChangeParam = function(param){
            $http.get('/data/rnd/get_param_values/' + rnd_network + '/' + param + '/').success(function(data){
                $scope.values = data;
                data.unshift('All');
                $scope.rnd_value['selected']='All';
            });
        };

        $scope.onAddFilter = function(param, value){
            var color = randomColor({hue: 'random',luminosity: 'dark'});
            var values_color = {};
            var last_marker = {};
            var values_count = {}

            leafletData.getMap().then(function(map) {
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        if(layer.options.sector[param] == value){
                            layer.setStyle({'color': color});
                            last_marker.Latitud = layer.options.sector.Latitud;
                            last_marker.Longitud = layer.options.sector.Longitud;
                            values_color[value] = color
                            if (value in values_count){
                                values_count[value] += 1;
                            } else {
                                values_count[value] = 1;
                            }
                        }
                        if (value=='All'){
                            if (layer.options.sector[param] in values_color){
                                layer.setStyle({'color': values_color[layer.options.sector[param]]});
                                last_marker.Latitud = layer.options.sector.Latitud;
                                last_marker.Longitud = layer.options.sector.Longitud;
                                values_count[layer.options.sector[param]] += 1;
                            } else {
                                values_color[layer.options.sector[param]] = randomColor({hue: 'random',luminosity: 'dark'});
                                layer.setStyle({'color': values_color[layer.options.sector[param]]});
                                last_marker.Latitud = layer.options.sector.Latitud;
                                last_marker.Longitud = layer.options.sector.Longitud;
                                values_count[layer.options.sector[param]] = 1;
                            }
                        }
                    }
                });
                if (last_marker){
                    map.setView([last_marker.Latitud, last_marker.Longitud], 12);
                }

                for (var  val_id in values_count ){
                    legend.update(param, val_id, values_color[val_id], values_count[val_id]);
                }
            });
        };
  }]);