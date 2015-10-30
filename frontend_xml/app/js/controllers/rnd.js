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

rndControllers.controller('mapCtrl', ['$scope', '$http', 'leafletData', '$location', '$cookies', '$uibModal',
    function ($scope, $http, leafletData, $location, $cookies, $uibModal) {

        var onAddFilter = function(param, value){
            var color = randomColor({hue: 'random',luminosity: 'dark'});
            var values = {};
            var last_marker = {};

            leafletData.getMap().then(function(map) {
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        if(layer.options.sector[param] == value){
                            layer.setStyle({'color': color});
                            last_marker = layer.options.sector;
                            if (value in values){
                                values[value].sectors.push(layer);
                            } else {
                                values[value] = {
                                    'param_name': param,
                                    'color': color,
                                    'sectors': [layer, ]}
                            }
                        }
                        if (value=='All'){
                            last_marker = layer.options.sector;
                            if (layer.options.sector[param] in values){
                                layer.setStyle({'color': values[layer.options.sector[param]].color});
                                values[layer.options.sector[param]].sectors.push(layer);
                            } else {
                                if (layer.options.sector[param]){
                                    values[layer.options.sector[param]] = {
                                        'param_name': param,
                                        'color':color = randomColor({hue: 'random',luminosity: 'dark'}),
                                        'sectors':[layer, ]};
                                    layer.setStyle({'color': values[layer.options.sector[param]].color});
                                }
                            }
                        }
                    }
                });

                if (value != 'All'){
                    if ('Latitud' in last_marker){
                        map.setView([last_marker.Latitud, last_marker.Longitud], 12);
                    } else if ('Latitude' in last_marker){
                        map.setView([last_marker.Latitude, last_marker.Longitude], 12);
                    }
                }
                map._legend.reset_legend();
                map._legend.set_legend(values);
            });
        };

        var create_legend_control = function(){
            var legend = L.control({position: 'bottomright'});

            legend.onAdd = function (map) {
                legend._map = map;
                this._div = L.DomUtil.create('div', 'legend hide');
                this.sectors = [];
                return this._div;
            };

            legend.reset_legend = function(){
                L.DomUtil.addClass(this._div, 'hide');
                while (this._div.firstChild) {
                    this._div.removeChild(this._div.firstChild);
                }
                for (id in this.sectors){
                    var layer = this.sectors[id];
                    layer.setStyle({'color': layer.options.default_color});
                }
                this.sectors = [];
            };

            legend.set_legend = function(values){
                L.DomUtil.removeClass(this._div, 'hide');
                for (val in values){
                    this.sectors = legend.sectors.concat(values[val].sectors);
                    var table = L.DomUtil.create('table', 'col-md-12', this._div);
                    var row_value = L.DomUtil.create('tr', 'col-md-12', table);
                    var cell_btn = L.DomUtil.create('td', 'col-md-1', row_value);
                    var button_value = L.DomUtil.create('button', 'btn btn-legend', cell_btn);
                    button_value.setAttribute('style', 'background-color: '+values[val].color);
                    button_value.sectors = values[val].sectors;
                    var cell_value = L.DomUtil.create('td', 'col-md-11', row_value);
                    var cell_link = L.DomUtil.create('span', 'span-legend', cell_value);
                    cell_link.innerHTML =  values[val].param_name + '=' + val + '('+values[val].sectors.length+')';
                    cell_link.sectors = values[val].sectors;
                    cell_link.next_sector_index = 0;

                    var stop = L.DomEvent.stopPropagation;
                    L.DomEvent
                        .addListener(this._div, 'contextmenu', stop)
                        .addListener(this._div, 'click', stop)
                        .addListener(this._div, 'mousedown', stop)
                        .addListener(this._div, 'touchstart', stop)
                        .addListener(this._div, 'dblclick', stop)
                        .addListener(this._div, 'mousewheel', stop)
                        .addListener(this._div, 'MozMousePixelScroll', stop)
                        .addListener(button_value, 'click', function(e){
                            var color = randomColor({hue: 'random',luminosity: 'dark'});
                            e.target.setAttribute('style', 'background-color: '+color);
                            for (id in e.target.sectors){
                                e.target.sectors[id].setStyle({'color': color});
                            }
                        })
                        .addListener(cell_link, 'click', function(e){
                            select_sector(e.target.sectors[e.target.next_sector_index]);
                            var sector = e.target.sectors[e.target.next_sector_index].options.sector;
                            if (e.target.next_sector_index + 1 < e.target.sectors.length){
                                e.target.next_sector_index += 1;
                            } else {
                                e.target.next_sector_index = 0;
                            }
                            if ('Latitud' in sector){
                                legend._map.setView([sector.Latitud, sector.Longitud], 14);
                            } else if ('Latitude' in sector){
                                legend._map.setView([sector.Latitude, sector.Longitude], 14);
                            }
                        })
                    };
            };
            return legend;
        };

        var select_sector = function(layer){
            if (layer._map._current_sector){
                layer._map._current_sector.setStyle({
                    weight: 2,
                    opacity: 0.7
                });
            }
            layer.setStyle({
                weight: 4,
                opacity: 1
            });
            layer._map._current_sector = layer;
            if (layer._map._info_control){
                layer._map.removeControl(layer._map._info_control);
            }
            layer._map._info_control = create_info_control(layer.options.default_color, layer.options.sector);
            layer._map._info_control.addTo(layer._map);

        };


        var create_info_control = function(color, sector){
            var info = L.control();
            info.onAdd = function (map) {
                this._div = L.DomUtil.create('div', 'info');
                this._div.setAttribute('style', 'border-color: '+color+';')
                columns = Object.keys(sector);
                columns.sort();

                for (id in columns){
                    this._div.innerHTML += '<b>' + columns[id] + ':</b> ' + sector[columns[id]] + '<br />';
                }

                var stop = L.DomEvent.stopPropagation;
                L.DomEvent
                    .on(this._div, 'contextmenu', stop)
                    .on(this._div, 'click', stop)
                    .on(this._div, 'mousedown', stop)
                    .on(this._div, 'touchstart', stop)
                    .on(this._div, 'dblclick', stop)
                    .on(this._div, 'mousewheel', stop)
                    .on(this._div, 'MozMousePixelScroll', stop)
                return this._div;
            };

            return info
        };

        var create_sector = function(network, lat, lon, sector, color, size, key){
            var new_sector = L.circle([lat, lon], size, {
                            color: color,
                            default_color: color,
                            opacity: 0.7,
                            weight: 2,
                            sector: sector,
                            current_base_radius: size,
                            zoom: 10,
                            network: network
                    })
            .bindPopup(key, {'offset': L.Point(20, 200)})
            .setDirection(sector.Azimuth, 60)
            .on('click', function(e){
                var self = this;
                select_sector(e.target);

                if (this._map._show_neighbors && (layer.options.network == 'wcdma')){
                    if (e.originalEvent.shiftKey){
                        if (layer.options.color == 'orange'){
                            $http.post('/data/rnd/del3g3g/',$.param({
                                'utrancellSource': utrancellSource,
                                'utrancellTarget': layer.options.sector.Utrancell
                            })).success(function(){
                                layer.setStyle({'color': 'grey'});
                            });
                        } else if (layer.options.color == 'red'){
                            $http.post('/data/rnd/new3g3g/',$.param({
                                'rncSource': rncSource,
                                'utrancellSource': utrancellSource,
                                'carrierSource': carrierSource,
                                'rncTarget': layer.options.sector.RNC,
                                'utrancellTarget': layer.options.sector.Utrancell,
                                'carrierTarget': layer.options.sector.Carrier,
                                'status': 'Delete'}))
                            .success(function(){
                                layer.setStyle({'color': 'purple'});
                            });
                        } else if(layer.options.color == 'grey'){
                            $http.post('/data/rnd/new3g3g/',$.param({
                                'rncSource': rncSource,
                                'utrancellSource': utrancellSource,
                                'carrierSource': carrierSource,
                                'rncTarget': layer.options.sector.RNC,
                                'utrancellTarget': layer.options.sector.Utrancell,
                                'carrierTarget': layer.options.sector.Carrier,
                                'status': 'New'}))
                            .success(function(){
                                layer.setStyle({'color': 'orange'});
                            });
                        }
                    } else {
                        rncSource = layer.options.sector.RNC;
                        utrancellSource = layer.options.sector.Utrancell;
                        carrierSource = layer.options.sector.Carrier;
                        layer.setStyle({'color': 'green'});
                        $http.get('/data/rnd/get_rnd_neighbors/' + layer.options.network + '/' + layer.options.sector.Utrancell + '/').success(function(data){
                            $http.get('/data/rnd/get_new3g/' + layer.options.network + '/' + layer.options.sector.Utrancell + '/').success(function(new3g_neighbors){
                                self._map.eachLayer(function (temp_layer) {
                                    if ((temp_layer.options.sector) && (temp_layer.options.network == 'wcdma')){
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
            return new_sector;
        };

        var create_rnd_layer = function(data, network, radius, color, lat, lon, key){
            var data = data.data;
            var sectors = [];
            for (sid in data){
                var sector = create_sector(
                    network,
                    data[sid][lat],
                    data[sid][lon],
                    data[sid],
                    color,
                    radius,
                    data[sid][key]);
                sectors.push(sector);
            }
            return L.layerGroup(sectors);
        }

        leafletData.getMap().then(function(map) {
            L.Control.toolBar().addTo(map);
            L.control.scale().addTo(map);
            map._layerControl = L.control.layers().addTo(map);
            map._show_neighbors = false;
            map._add_filter = onAddFilter;
            map._legend = create_legend_control();
            map._legend.addTo(map);

            $http.get('/data/rnd/gsm/').success(function(gsm_data){
                $http.get('/data/rnd/wcdma/').success(function(wcdma_data){
                    $http.get('/data/rnd/lte/').success(function(lte_data){
                        gsm_layer = create_rnd_layer(gsm_data, 'gsm', 1500, 'orange', 'Latitude', 'Longitude', 'Cell_Name');
                        wcdma_layer = create_rnd_layer(wcdma_data, 'wcdma', 1200, 'blue', 'Latitud', 'Longitud', 'Utrancell');
                        lte_layer = create_rnd_layer(lte_data, 'lte', 1000, 'green', 'Latitude', 'Longitude', 'Utrancell');
                        map._layerControl.addOverlay(gsm_layer, '<span class="label label-warning">GSM</span>');
                        map._layerControl.addOverlay(wcdma_layer, '<span class="label label-primary">WCDMA</span>');
                        map._layerControl.addOverlay(lte_layer, '<span class="label label-success">LTE</span>');
                        map.addLayer(gsm_layer);
                        map.addLayer(wcdma_layer);
                        map.addLayer(lte_layer);

                        map._gsm_data = gsm_data;
                        map._wcdma_data = wcdma_data;
                        map._lte_data = lte_data;

                        map.setView([wcdma_data.data[0].Latitud, wcdma_data.data[0].Longitud], 10);
                        var columns = [];
                        for (id in gsm_data.columns){
                            if (columns.indexOf((gsm_data.columns[id])) < 0){
                                columns.push(gsm_data.columns[id]);
                            }
                        }
                        for (id in wcdma_data.columns){
                            if (columns.indexOf((wcdma_data.columns[id])) < 0){
                                columns.push(wcdma_data.columns[id]);
                            }
                        }
                        for (id in lte_data.columns){
                            if (columns.indexOf((lte_data.columns[id])) < 0){
                                columns.push(lte_data.columns[id]);
                            }
                        }
                        columns.sort();
                        for (id in columns){
                            var option = document.createElement("option");
                            option.value = columns[id];
                            option.text = columns[id];
                            map._select_filter.appendChild(option);
                        }
                        map._select_filter.selectedIndex = '-1';
                    });
                });
            });

            map.on('zoomend', function(e){
                    var zoom = e.target._zoom;

                    map.eachLayer(function (layer) {
                        var radius = layer.options.current_base_radius;
                        if (e.target.sectro_size.value != 0) {
                            radius += radius * parseFloat(e.target.sectro_size.value);
                        }
                        if (layer.options.sector) {
                            zkf = ((zoom-10)*-12+100)/100
                            var current_size = radius * (11-parseFloat(1))/10;
                            var size = zkf*current_size;
                            layer.setRadius(size);
                            layer.options.current_base_radius = zkf*radius;
                            layer.options.zoom = zoom;
                        }
                    });
                    e.target.sectro_size.value = 0;
                });
        });
}]);


rndControllers.controller('mapSettingsCtrl', ['$scope', '$http', '$cookies',
    function ($scope, $http, $cookies) {
        $scope.radius_wcdma = 1500;
        $scope.radius_gsm = 1200;
        $scope.radius_lte = 1800;

        $scope.onSaveMapSettings = function(){
            $cookies.put('radius_wcdma', $scope.radius_wcdma);
            $cookies.put('radius_gsm', $scope.radius_gsm);
            $cookies.put('radius_lte', $scope.radius_lte);
        };
}]);


rndControllers.controller('ModalFilterCtrl', ['$scope', '$http',
    function ($scope, $http) {
        console.log('Test');
  }]);