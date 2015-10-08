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
        var sector_azimuths_size = {};
        $scope.rnd_value = {};
        $scope.rnd_param = {};
        var data_length = 0;
        var legend_info = []
        $scope.show_neighbors = false;
        var rncSource;
        var utrancellSource;
        var carrierSource;
        $scope.show_menu = false;
        var sector_size = 0;
        $scope.range_sector_size = 0;

        $scope.controls = {
                    fullscreen: {
                        position: 'topleft'
                    }
                };

        var sectorControl = L.control({position: 'topleft'});

        sectorControl.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'sector');
            return this._div;
        };

        sectorControl.update = function (sector) {
            this._div.innerHTML =
                    '<h5>Sector:</h5>'+sector+'<br>';
        };


        var legend = L.control({position: 'bottomright'});

        legend.onAdd = function (map) {
            this._div = L.DomUtil.create('div', 'legend');
            return this._div;
        };

        legend.update = function (legend_info) {
            var table = '<table>'
            for (l_i in legend_info){

                table += '<tr><td><i style="background:' + legend_info[l_i].color + '"></i> '+ legend_info[l_i].param+'='+legend_info[l_i].value+'(' + legend_info[l_i].count +')</td></tr>'
            }
            table += '</table>'
            this._div.innerHTML = table;
        };

        legend.reset = function(){
            this._div.innerHTML = '';
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
                L.Control.measureControl().addTo(map);
                info.addTo(map);
                legend.addTo(map);
                sectorControl.addTo(map);

                for (var sector_id in data){
                    var sector = data[sector_id];
                    var size = carriers_size[1];

                    if (sector.Carrier in carriers_size){
                        size = carriers_size[sector.Carrier];
                    } else {
                        size = carriers_size[1] * (11-parseFloat(sector.Carrier))/10;
                        carriers_size[sector.Carrier] = min_carrier_size = size;
                    }

                  //  if (sector.SITE in sector_azimuths_size){
                  //      if (sector.Azimuth in sector_azimuths_size[sector.SITE]){
                  //          size = sector_azimuths_size[sector.SITE][sector.Azimuth][sector_azimuths_size[sector.SITE][sector.Azimuth].length-1] * 0.9;
                  //          sector_azimuths_size[sector.SITE][sector.Azimuth].push(size)
                  //      } else {
                  //          sector_azimuths_size[sector.SITE][sector.Azimuth] = [size,];
                  //      }
                  //  } else {
                  //      var az = {}
                  //      az[sector.Azimuth] = [size,];
                  //      sector_azimuths_size[sector.SITE]=az;
                   // }

                    L.circle([sector.Latitud, sector.Longitud], size, {
                            color: '#03f',
                            opacity: 0.7,
                            weight: 2,
                            sector: sector,
                            current_radius: size,
                            base_radius: size
                    })
                    .bindPopup(sector.Utrancell, {'offset': L.Point(20, 200)})
                    .setDirection(sector.Azimuth, 60)
                    .on('mouseover', function (e) {
                        sectorControl.update(e.target.options.sector.Utrancell);
                    })
                    .on('mouseout', function (e) {
                        sectorControl.update('');
                    })
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
                            if ($scope.show_neighbors){
                                if (e.originalEvent.shiftKey){
                                    if (layer.options.color == 'orange'){
                                        layer.setStyle({'color': 'grey'});
                                        $http.post('/data/rnd/del3g3g/',$.param({
                                            'utrancellSource': utrancellSource,
                                            'utrancellTarget': layer.options.sector.Utrancell
                                        }));
                                    }
                                    else if(layer.options.color == 'grey'){
                                        layer.setStyle({'color': 'orange'});
                                        $http.post('/data/rnd/new3g3g/',$.param({
                                            'rncSource': rncSource,
                                            'utrancellSource': utrancellSource,
                                            'carrierSource': carrierSource,
                                            'rncTarget': layer.options.sector.RNC,
                                            'utrancellTarget': layer.options.sector.Utrancell,
                                            'carrierTarget': layer.options.sector.Carrier,}));
                                        }
                                } else {
                                    legend.reset();
                                    rncSource = layer.options.sector.RNC;
                                    utrancellSource = layer.options.sector.Utrancell;
                                    carrierSource = layer.options.sector.Carrier;
                                    layer.setStyle({'color': 'green'});
                                    $http.get('/data/rnd/get_rnd_neighbors/' + rnd_network + '/' + layer.options.sector.Utrancell + '/').success(function(data){
                                        $http.get('/data/rnd/get_new3g/' + rnd_network + '/' + layer.options.sector.Utrancell + '/').success(function(new3g_neighbors){
                                            map.eachLayer(function (temp_layer) {
                                                if (temp_layer.options.sector){
                                                    if (layer.options.sector.Utrancell !== temp_layer.options.sector.Utrancell){
                                                        if (data.indexOf(temp_layer.options.sector.Utrancell) >= 0) {
                                                            temp_layer.setStyle({'color': 'red'});
                                                        } else if(new3g_neighbors.indexOf(temp_layer.options.sector.Utrancell) >= 0){
                                                            temp_layer.setStyle({'color': 'orange'});
                                                        } else {
                                                            temp_layer.setStyle({'color': 'grey'});
                                                        }
                                                    }
                                                }
                                            });
                                        });
                                    });
                                }

                            }
                        })
                    .addTo(map);
                    if (sector_size == 0 || sector_size > size){
                        sector_size = size;
                        $scope.range_max = sector_size;
                        $scope.range_min = sector_size * -1;
                    }

                }
                map.setView([data[0].Latitud, data[0].Longitud], 10);

                map.on('zoomend', function(e){
                    if ($scope.range_sector_size != 0){
                        return
                    }
                    var zoom = e.target._zoom;
                    map.eachLayer(function (layer) {
                        if (layer.options.sector) {
                            zkf = ((zoom-10)*-12+100)/100
                            base_size = zkf*carriers_size[sector.Carrier];
                            var size = base_size * (11-parseFloat(layer.options.sector.Carrier))/10
                            layer.setRadius(size);
                            layer.options.current_radius = size;
                            if (sector_size == 0 || sector_size > size){
                                sector_size = size;
                                $scope.range_max = sector_size;
                                $scope.range_min = sector_size * -1;
                            }
                        }
                    });
                });

            });
            for (var s_param in search_params){
                onAddFilter(s_param, search_params[s_param]);
            }
        });

        $scope.onNeighbors = function(){
            if ($scope.show_neighbors){
                set_color_to_all_sectors('#03f');
            }
        }

        $scope.onChangeParam = function(param){
            $http.get('/data/rnd/get_param_values/' + rnd_network + '/' + param + '/').success(function(data){
                $scope.values = data;
                data.unshift('All');
            });
        };
        $scope.onSelectValue = function(item, model){
            set_color_to_all_sectors('#03f');
            legend.reset();
            onAddFilter($scope.rnd_param.selected, item);
        }

        $scope.onResetFilter = function(){
            set_color_to_all_sectors('#03f');
            legend.reset();

        };

        $scope.onFlush =function(){
            $http.post('/data/rnd/flush3g3g/');
            leafletData.getMap().then(function(map) {
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        if (layer.options.color == 'orange'){
                            layer.setStyle({'color': 'grey'});
                        }
                    }
                });
            });
        };

        $scope.onSizeSector = function(new_size){
            leafletData.getMap().then(function(map) {
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        var new_s = parseFloat(layer.options.current_radius) + parseFloat(new_size);
                        layer.setRadius(new_s);
                    }
                });
            });
        };

        $scope.onTest = function(){
            console.log('test');
        };


        var onAddFilter = function(param, value){
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
                    //map.setView([last_marker.Latitud, last_marker.Longitud], 12);
                }
                var legend_dict = []
                for (var  val_id in values_count ){
                    legend_dict.push({
                        'param': param,
                        'value': val_id,
                        'color': values_color[val_id],
                        'count': values_count[val_id]
                    })
                }
                legend.update(legend_dict);
            });
        };
        var set_color_to_all_sectors = function(color){
            leafletData.getMap().then(function(map) {
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        layer.setStyle({'color': color});
                    }
                });
            });
        }
  }]);