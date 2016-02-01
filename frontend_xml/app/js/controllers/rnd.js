var rndControllers = angular.module('rndControllers', []);

rndControllers.controller('rndCtrl', ['$scope', '$http', '$routeParams', 'usSpinnerService',
    function ($scope, $http, $routeParams, usSpinnerService) {
        $scope.rowCollection = [];
        $scope.new_val = {};
        $scope.show_edit_panel = false;
        $scope.rnd_network = $routeParams.network;
        $scope.show_download_panel = false;
        $scope.rnd_table_config = {
            enableGridMenu: true,
            enableRowHeaderSelection: false,
            enableSelectAll: false,
            exporterMenuPdf: false,
            multiSelect: false,
            exporterCsvFilename: 'export.csv',
            exporterCsvLinkElement: angular.element(document.querySelectorAll(".custom-csv-link-location")),
            onRegisterApi: function(gridApi){
                $scope.gridApi = gridApi;
                gridApi.edit.on.afterCellEdit($scope,function(rowEntity, colDef, newValue, oldValue){
                    if ($scope.rnd_network == 'wcdma'){
                        var new_data = {
                            'current_rnc': rowEntity.RNC,
                            'current_utrancell': rowEntity.Utrancell,
                            'column': colDef.name,
                            'value': newValue,
                        };

                        if (colDef.name == 'Utrancell'){
                            new_data.current_utrancell = oldValue;
                        } else if (colDef.name == 'RNC'){
                            new_data.current_rnc = oldValue;
                        }
                        $http.post('/data/rnd/table/' + $scope.rnd_network + '/', $.param(new_data)).success(function(){});
                    } else if ($scope.rnd_network == 'lte'){
                        var new_data = {
                            'current_site': rowEntity.SITE,
                            'current_utrancell': rowEntity.Utrancell,
                            'column': colDef.name,
                            'value': newValue,
                        };

                        if (colDef.name == 'Utrancell'){
                            new_data.current_utrancell = oldValue;
                        } else if (colDef.name == 'SITE'){
                            new_data.current_site = oldValue;
                        }
                        $http.post('/data/rnd/table/' + $scope.rnd_network + '/', $.param(new_data)).success(function(){});

                    } else if ($scope.rnd_network == 'gsm'){
                        var new_data = {
                            'current_bsc': rowEntity.BSC,
                            'current_cellname': rowEntity.Cell_Name,
                            'column': colDef.name,
                            'value': newValue,
                        };

                        if (colDef.name == 'Cell_Name'){
                            new_data.current_cellname = oldValue;
                        } else if (colDef.name == 'BSC'){
                            new_data.current_bsc = oldValue;
                        }
                        $http.post('/data/rnd/table/' + $scope.rnd_network + '/', $.param(new_data)).success(function(){});
                    }
                });
            }
        }
        $http.get('/data/rnd/' + $scope.rnd_network + '/').success(function(data){
            usSpinnerService.stop('spinner_map_table');
            $scope.rnd_table_config.columnDefs = [];
            $scope.columns = data.columns;
            for (id in data.columns){
                $scope.rnd_table_config.columnDefs.push({field: data.columns[id], });
            }
            $scope.rnd_table_config.data = data.data;
        });

        $scope.complete = function(){
            $scope.show_download_panel = false;
            $http.get('/data/rnd/' + $scope.rnd_network + '/').success(function(data){
                $scope.rnd_table_config.columnDefs = [];
                for (id in data.columns){
                    $scope.rnd_table_config.columnDefs.push({field: data.columns[id], });
                }
                $scope.rnd_table_config.data = data.data;
            });
        };

        $scope.onSaveRnd = function(data){
            $http.post('/data/rnd/table/' + $scope.rnd_network + '/', $.param(data)).success(function(){
                $scope.rnd_table_config.data.push(data);
                $scope.show_edit_panel = false;
            });
        }
        $scope.onDelete = function(){
            var selected_rows = $scope.gridApi.selection.getSelectedRows();
            for (var i in selected_rows){
                if ($scope.rnd_network == 'wcdma'){
                    var del_row = {'del_rnc': selected_rows[i].RNC, 'del_utrancell': selected_rows[i].Utrancell};
                } else if ($scope.rnd_network == 'lte'){
                    var del_row = {'del_site': selected_rows[i].SITE, 'del_utrancell': selected_rows[i].Utrancell};
                } else if ($scope.rnd_network == 'gsm'){
                    var del_row = {'del_bsc': selected_rows[i].BSC, 'del_cellname': selected_rows[i].Cell_Name};
                }
                $http.post('/data/rnd/table/' + $scope.rnd_network + '/', $.param(del_row));
                var id = $scope.rnd_table_config.data.indexOf(selected_rows[i]);
                $scope.rnd_table_config.data.splice(id, 1);
            }
        }
  }]);

rndControllers.controller('mapCtrl', ['$scope', '$http', 'leafletData', '$location', '$cookies', '$uibModal', 'usSpinnerService',
    function ($scope, $http, leafletData, $location, $cookies, $uibModal, usSpinnerService) {
        var onAddFilter = function(network, param, value){
            var color = randomColor({hue: 'random',luminosity: 'dark'});
            var values = {};
            var last_marker = {};


            leafletData.getMap().then(function(map) {
                map._legend.reset_legend();
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        if ((layer.options.sector[param] == value) && (network == layer.options.network)){
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
                        } else if (!(value=='All')){
                            layer.setStyle({'color': '#808080'});
                            if (!(value in values)){
                                values[value] = {
                                    'param_name': param,
                                    'color': color,
                                    'sectors': []}
                            }
                            if ('other' in values){
                                values['other'].sectors.push(layer);
                            } else {
                                values['other'] = {
                                    'param_name': param,
                                    'color': '#808080',
                                    'sectors': [layer, ]}
                            }
                        }
                        if (value=='All'){
                            if (network == layer.options.network){
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
                            } else {
                                layer.setStyle({'color': '#808080'});
                            }
                        }
                    }
                });

                if (value != 'All'){
                    if ('Latitud' in last_marker){
                        map.setView([last_marker.Latitud, last_marker.Longitud], 12);
                        map.set_zoom(12);
                    } else if ('Latitude' in last_marker){
                        map.setView([last_marker.Latitude, last_marker.Longitude], 12);
                        map.set_zoom(12);
                    }
                }
                if (map._newlegend){
                    var window_div = map._newlegend.getContainer();
                    while (window_div.firstChild) {
                        window_div.removeChild(window_div.firstChild);
                    }

                } else {
                    map._newlegend = L.control.window(map,{position: 'left',});
                    map._newlegend.show();
                    map._newlegend.on('close', function(){
                        delete map._newlegend
                    });
                }
                var window_div = map._newlegend.getContainer();
                set_legend(map, window_div, values)
                //map._legend.set_legend(values);
            });
        };

        var set_legend = function(map, div, values){
            var table = L.DomUtil.create('table', 'table_legend', div);
            var sectors = [];
            for (val in values){
                sectors = sectors.concat(values[val].sectors);
                var row_value = L.DomUtil.create('tr', 'col-md-12', table);
                var cell_btn = L.DomUtil.create('td', 'col-md-1', row_value);
                var color_value = L.DomUtil.create('input', '', cell_btn);
                color_value.setAttribute('type', 'color');
                //color_value.setAttribute('value', values[val].color);
                color_value.value = values[val].color;

                color_value.sectors = values[val].sectors;
                var cell_value = L.DomUtil.create('td', 'col-md-11', row_value);
                var cell_link = L.DomUtil.create('span', 'span-legend', cell_value);
                cell_link.innerHTML =  values[val].param_name + '=' + val + '('+values[val].sectors.length+')';
                cell_link.sectors = values[val].sectors;
                cell_link.next_sector_index = 0;

                var stop = L.DomEvent.stopPropagation;
                L.DomEvent
                    .addListener(color_value, 'change', function(e){
                        var color = e.target.value;
                        for (id in e.target.sectors){
                            e.target.sectors[id].setStyle({'color': color});
                        }
                    })
                    .addListener(cell_link, 'click', function(e){
                        console.log(e.target);
                        map.select_sector(e.target.sectors[e.target.next_sector_index]);
                        var sector = e.target.sectors[e.target.next_sector_index].options.sector;
                        if (e.target.next_sector_index + 1 < e.target.sectors.length){
                            e.target.next_sector_index += 1;
                        } else {
                            e.target.next_sector_index = 0;
                        }
                        if ('Latitud' in sector){
                            map.setView([sector.Latitud, sector.Longitud], 14);
                            map.set_zoom(14);
                        } else if ('Latitude' in sector){
                            map.setView([sector.Latitude, sector.Longitude], 14);
                            map.set_zoom(14);
                        }
                    })
            };
        };

        var set_pd = function(div){
            var colors = [
                ['#ff0000', '90% to 100%'],
                ['#ff6d37', '80% to 90%'],
                ['#ffb59a', '70% to 80%'],
                ['#ffff00', '60% to 70%'],
                ['#ffba00', '50% to 60%'],
                ['#7ace00', '40% to 50%'],
                ['#00ff00', '30% to 40%'],
                ['#00ffff', '20% to 30%'],
                ['#0000ff', '10% to 20%'],
                ['#c07eff', ' 1% to 10%'],
                ['#ffffff', ' 0% to  1%'],
            ]
            var table = L.DomUtil.create('table', 'table_pd', div);
            for (i in colors){
                var row_value = L.DomUtil.create('tr', 'col-md-12', table);
                var cell_btn = L.DomUtil.create('td', 'col-md-12', row_value);
                cell_btn.innerHTML ='<i class="pd_i" style="background:' + colors[i][0] + '"></i> ' + colors[i][1] + '<br>';
            }
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

            legend.set_pd = function(){

                L.DomUtil.removeClass(this._div, 'hide');
                var colors = [
                    ['#ff0000', '90% to 100%'],
                    ['#ff6d37', '80% to 90%'],
                    ['#ffb59a', '70% to 80%'],
                    ['#ffff00', '60% to 70%'],
                    ['#ffba00', '50% to 60%'],
                    ['#7ace00', '40% to 50%'],
                    ['#00ff00', '30% to 40%'],
                    ['#00ffff', '20% to 30%'],
                    ['#0000ff', '10% to 20%'],
                    ['#c07eff', ' 1% to 10%'],
                    ['#ffffff', ' 0% to  1%'],

                ]
                var table = L.DomUtil.create('table', 'col-md-12', this._div);
                for (i in colors){
                    var row_value = L.DomUtil.create('tr', 'col-md-12', table);
                    var cell_btn = L.DomUtil.create('td', 'col-md-12', row_value);
                    cell_btn.innerHTML ='<i style="background:' + colors[i][0] + '"></i> ' + colors[i][1] + '<br>';
                }

            };

            legend.set_legend = function(values){
                L.DomUtil.removeClass(this._div, 'hide');
                for (val in values){
                    this.sectors = legend.sectors.concat(values[val].sectors);
                    var table = L.DomUtil.create('table', 'col-md-12', this._div);
                    var row_value = L.DomUtil.create('tr', 'col-md-12', table);
                    var cell_btn = L.DomUtil.create('td', 'col-md-1', row_value);
                    var color_value = L.DomUtil.create('input', '', cell_btn);
                    color_value.setAttribute('type', 'color');
                    color_value.value = values[val].color;

                    color_value.sectors = values[val].sectors;
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
                        .addListener(color_value, 'change', function(e){
                            var color = e.target.value;
                            for (id in e.target.sectors){
                                e.target.sectors[id].setStyle({'color': color});
                            }
                        })
                        .addListener(cell_link, 'click', function(e){
                            legend._map.select_sector(e.target.sectors[e.target.next_sector_index]);
                            var sector = e.target.sectors[e.target.next_sector_index].options.sector;
                            if (e.target.next_sector_index + 1 < e.target.sectors.length){
                                e.target.next_sector_index += 1;
                            } else {
                                e.target.next_sector_index = 0;
                            }
                            if ('Latitud' in sector){
                                legend._map.setView([sector.Latitud, sector.Longitud], 14);
                                legend._map.set_zoom(14);
                            } else if ('Latitude' in sector){
                                legend._map.setView([sector.Latitude, sector.Longitude], 14);
                                legend._map.set_zoom(14);
                            }
                        })
                    };
            };
            return legend;
        };

        var create_info_control = function(color, sector){
            var info_div = L.DomUtil.create('div', 'info');
            info_div.setAttribute('style', 'border-color: '+color+';')
            columns = Object.keys(sector);
            columns.sort();

            for (id in columns){
                info_div.innerHTML += '<b>' + columns[id] + ':</b> ' + sector[columns[id]] + '<br />';
            }
            return info_div.outerHTML;
        };

        var latlng_control = function(){
            var latlng = L.control({position: 'bottomleft'});

            latlng.onAdd = function (map) {
                this._div = L.DomUtil.create('div', 'latlng');
                return this._div;
            };

            latlng.set_latlng = function (lat, lng) {
                this._div.innerHTML = 'Lat: ' + lat + '  Lng: ' + lng;
            };

            return latlng
        };

        var create_sector = function(network, lat, lon, sector, color, size, key, zoom_k){
            var stop = L.DomEvent.stopPropagation;
            var new_sector = L.circle([lat, lon], size, {
                            color: color,
                            default_color: color,
                            opacity: 0.7,
                            weight: 2,
                            sector: sector,
                            current_base_radius: size,
                            zoom: 10,
                            network: network,
                            zoom_k: zoom_k
                    })
            .bindPopup(key, {'offset': L.Point(20, 200)})
            .setDirection(parseFloat(sector.Azimuth)-90, 60)


            .on('click', function(e){
                var self = this;
                layer = e.target
                layer._map.select_sector(layer);
                if (layer._map._show_pd){
                    layer.show_pd();
                }


                if (this._map._show_neighbors && (layer.options.network == 'wcdma')){
                    if (e.originalEvent.shiftKey){
                        if (layer.options.color == 'orange'){
                            $http.post('/data/rnd/del3g3g/',$.param({
                                'utrancellSource': layer.options.sector.Utrancell,
                                'utrancellTarget': utrancellSource
                            }))
                            $http.post('/data/rnd/del3g3g/',$.param({
                                'utrancellSource': utrancellSource,
                                'utrancellTarget': layer.options.sector.Utrancell
                            })).success(function(){
                                layer.setStyle({'color': 'grey'});
                            });
                        } else if (layer.options.color == 'purple'){
                            $http.post('/data/rnd/del3g3g/',$.param({
                                'utrancellSource': utrancellSource,
                                'utrancellTarget': layer.options.sector.Utrancell
                            })).success(function(){
                                layer.setStyle({'color': 'red'});
                            });
                        } else if (layer.options.color == 'red'){
                            $http.post('/data/rnd/new3g3g/',$.param({
                                'rncSource': layer.options.sector.RNC,
                                'utrancellSource': layer.options.sector.Utrancell,
                                'carrierSource': layer.options.sector.Carrier,
                                'rncTarget': rncSource,
                                'utrancellTarget': utrancellSource,
                                'carrierTarget': carrierSource,
                                'status': 'Delete'}));
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
                                'rncSource': layer.options.sector.RNC,
                                'utrancellSource': layer.options.sector.Utrancell,
                                'carrierSource': layer.options.sector.Carrier,
                                'rncTarget': rncSource,
                                'utrancellTarget': utrancellSource,
                                'carrierTarget': carrierSource,
                                'status': 'Add'}));
                            $http.post('/data/rnd/new3g3g/',$.param({
                                'rncSource': rncSource,
                                'utrancellSource': utrancellSource,
                                'carrierSource': carrierSource,
                                'rncTarget': layer.options.sector.RNC,
                                'utrancellTarget': layer.options.sector.Utrancell,
                                'carrierTarget': layer.options.sector.Carrier,
                                'status': 'Add'}))
                            .success(function(){
                                layer.setStyle({'color': 'orange'});
                            });
                        }
                    } else {
                        layer.show_neighbours();
                    }
                }
                L.DomEvent.stopPropagation(e);
            })
            new_sector.show_neighbours = function(){
                var layer = this;
                rncSource = layer.options.sector.RNC;
                utrancellSource = layer.options.sector.Utrancell;
                carrierSource = layer.options.sector.Carrier;
                layer.setStyle({'color': 'green'});
                $http.get('/data/rnd/get_rnd_neighbors/' + layer.options.network + '/' + layer.options.sector.Utrancell + '/').success(function(data){
                    $http.get('/data/rnd/get_new3g/' + layer.options.network + '/' + layer.options.sector.Utrancell + '/').success(function(new3g_neighbors){
                        layer._map.eachLayer(function (temp_layer) {
                            if ((temp_layer.options.sector) && (temp_layer.options.network == 'wcdma')){
                                if (layer.options.sector.Utrancell !== temp_layer.options.sector.Utrancell){
                                    if(new3g_neighbors[temp_layer.options.sector.Utrancell]){
                                        if (new3g_neighbors[temp_layer.options.sector.Utrancell] == 'Add'){
                                            temp_layer.setStyle({'color': 'orange'});
                                        } else {
                                            temp_layer.setStyle({'color': 'purple'});
                                        }
                                    } else if (data.indexOf(temp_layer.options.sector.Utrancell) >= 0) {
                                        temp_layer.setStyle({'color': 'red'});
                                    } else {
                                        temp_layer.setStyle({'color': 'grey'});
                                    }
                                }
                            }
                        });
                    });
                });
            };
            new_sector.show_pd = function(){
                var layer = this;
                for (i in layer._map._pd){
                    layer._map._pd[i].removeFrom(layer._map);
                }
                layer._map._pd = [];
                $http.get('/data/rnd/get_rnd_pd/' + layer.options.network + '/' + layer.options.sector.Utrancell + '/' + layer._map._pd_date_from.value + '/' + layer._map._pd_date_to.value + '/').success(function(data){
                    var s_radius = 0;

                if (layer._map._newlegend){
                    var window_div = layer._map._newlegend.getContainer();
                    while (window_div.firstChild) {
                        window_div.removeChild(window_div.firstChild);
                    }
                } else {
                    layer._map._newlegend = L.control.window(layer._map,{position: 'left',});
                    layer._map._newlegend.show();
                    layer._map._newlegend.on('close', function(){
                        delete layer._map._newlegend
                    });
                }
                var window_div = layer._map._newlegend.getContainer();
                set_pd(window_div);


                    var pd_data = data[0];
                    var distances = data[2];

                    for (id in pd_data){
                        var dc_vector = parseFloat(pd_data[id][0]);
                        if (dc_vector + 1 in distances){
                            var size = distances[dc_vector + 1] * 1000;
                        } else {
                            var size = distances[dc_vector] + distances[dc_vector] - distances[dc_vector-1];
                            size = size * 1000;
                        }
                        var value = parseFloat(pd_data[id][1]);
                        var color = 'blue';
                        var fill_opacity = 0.5;
                        var opacity = 0.7;
                        var weight = 2;
                        if (value == 0){
                            fill_opacity = 0;
                            weight = 0;
                            opacity = 0;
                        }else if ((value <=1) && (value > 0)){
                            color = '#ffffff';
                        } else if ((value > 1) && (value <= 10)){
                            color = '#c07eff';
                        } else if ((value > 10) && (value <= 20)){
                            color = '#0000ff';
                        } else if ((value > 20) && (value <= 30)){
                            color = '#00ffff';
                        } else if ((value > 30) && (value <= 40)){
                            color = '#00ff00';
                        } else if ((value > 40) && (value <= 50)){
                            color = '#7ace00';
                        } else if ((value > 50) && (value <= 60)){
                            color = '#ffba00';
                        } else if ((value > 60) && (value <= 70)){
                            color = '#ffff00';
                        } else if ((value > 70) && (value <= 80)){
                            color = '#ffb59a';
                        } else if ((value > 80) && (value <= 90)){
                            color = '#ff6d37';
                        } else if ((value > 90) && (value <= 100)){
                            color = '#ff0000';
                        }
                        var new_pd = L.circle(layer._latlng, size, {
                            color: color,
                            fillOpacity: fill_opacity,
                            defaultOpacity: fill_opacity,
                            weight: weight,
                            opacity: opacity,
                            azimuth: layer.options.sector.Azimuth
                        })
                        .bindPopup('DC Vector: '+ pd_data[id][0] +'('+distances[dc_vector]+'km), value:' + value , {'offset': L.Point(20, 200)})
                        .setDirection(parseFloat(layer.options.sector.Azimuth)-90, 60, s_radius);
                        new_pd.addTo(layer._map);
                        layer._map._pd.push(new_pd);
                        s_radius = new_pd._radius;
                    }
                });
            };
            return new_sector;
        };

        var create_rnd_layer = function(data, network, base_radius, color, lat, lon, key){
            var data = data.data;
            var gsm_bands = ['GSM1900', 'GSM850', ];
            var sectors = [];
            for (sid in data){
                var zoom_k = 1;
                if (network == 'gsm'){
                    data.sort(function(a,b){
                        return parseFloat(a.Band) - parseFloat(b.Band);
                    });
                    if (!data[sid].Band in gsm_bands) {
                        gsm_bands.push(data[sid].Band);
                    }
                    zoom_k = gsm_bands.indexOf(data[sid].Band) +1;
                    radius = base_radius * (11-zoom_k)/10;
                } else {
                    data.sort(function(a,b){
                        return parseFloat(a.Carrier) - parseFloat(b.Carrier);
                    });
                    if (parseFloat(data[sid].Carrier)){
                        zoom_k = parseFloat(data[sid].Carrier)
                        radius = base_radius * (11-parseFloat(data[sid].Carrier))/10;
                    }
                }

                var sector = create_sector(
                    network,
                    data[sid][lat],
                    data[sid][lon],
                    data[sid],
                    color,
                    radius,
                    data[sid][key],
                    zoom_k);
                sectors.push(sector);
            }
            return L.layerGroup(sectors);
        }

        leafletData.getMap().then(function(map) {
            L.Control.toolBar().addTo(map);
            L.control.scale().addTo(map);
            L.Control.measureControl({ position:'topright' }).addTo(map);
            map._layerControl = L.control.layers().addTo(map);
            map._show_neighbors = false;
            map._show_pd = false;
            map._add_filter = onAddFilter;
            map._legend = create_legend_control();
            map._legend.addTo(map);
            map._latlng = latlng_control();
            map._latlng.addTo(map);
            var control = L.control.zoomBox({ modal: true, });
            control.init(map);

            var radius_wcdma = 1500;
            var radius_gsm = 1200;
            var radius_lte = 1800;

            if ($cookies.get('radius_gsm')){
                radius_gsm = $cookies.get('radius_gsm');
            }
            if ($cookies.get('radius_wcdma')){
                radius_wcdma = $cookies.get('radius_wcdma');
            }
            if ($cookies.get('radius_lte')){
                radius_lte = $cookies.get('radius_lte');
            }

            map.flush_neighbors = function(){
                if (map._show_neighbors){
                    $http.post('/data/rnd/flush3g3g/');
                    map.eachLayer(function (layer) {
                        if (layer.options.sector) {
                            if ((layer.options.color == 'orange') || (layer.options.color == 'purple')){
                                layer.setStyle({'color': 'grey'});
                            }
                        }
                    });
                }
            };

            map._init_pd = function(){
                $http.get('/data/distance/get_dates/').success(function(data){
                    while (map._pd_date_from.firstChild) {
                        map._pd_date_from.removeChild(map._pd_date_from.firstChild);
                    }
                    while (map._pd_date_to.firstChild) {
                        map._pd_date_to.removeChild(map._pd_date_to.firstChild);
                    }
                    var data2 = data.slice()
                    for (id in data){
                        var option = document.createElement("option");
                        option.value = data[id];
                        option.text = data[id];
                        map._pd_date_from.appendChild(option);
                        var option2 = document.createElement("option");
                        option2.value = data2[id];
                        option2.text = data2[id];
                        map._pd_date_to.appendChild(option2);
                    }
                    map._pd_date_to.selectedIndex = data2.length - 1;
                });
            }
            $http.get('/data/rnd/init_map/').success(function(data){
                map.setView(data.point, 10);
            });

            $http.get('/data/rnd/gsm/').success(function(gsm_data){
                $http.get('/data/rnd/wcdma/').success(function(wcdma_data){
                    $http.get('/data/rnd/lte/').success(function(lte_data){
                        usSpinnerService.stop('spinner_map');
                        gsm_layer = create_rnd_layer(gsm_data, 'gsm', radius_gsm, 'orange', 'Latitude', 'Longitude', 'Cell_Name');
                        wcdma_layer = create_rnd_layer(wcdma_data, 'wcdma', radius_wcdma, 'blue', 'Latitude', 'Longitude', 'Utrancell');
                        lte_layer = create_rnd_layer(lte_data, 'lte', radius_lte, 'green', 'Latitude', 'Longitude', 'Utrancell');
                        map._layerControl.addOverlay(gsm_layer, '<span class="label label-warning">GSM</span>');
                        map._layerControl.addOverlay(wcdma_layer, '<span class="label label-primary">WCDMA</span>');
                        map._layerControl.addOverlay(lte_layer, '<span class="label label-success">LTE</span>');
                        map.addLayer(gsm_layer);
                        map.addLayer(wcdma_layer);
                        map.addLayer(lte_layer);

                        map._gsm_data = gsm_data;
                        map._wcdma_data = wcdma_data;
                        map._lte_data = lte_data;


                        map.set_zoom(10);
                        map._select_filter.selectedIndex = '-1';
                        map._network_filter.selectedIndex = '-1';
                    });
                });
            });

            map.set_zoom = function(zoom_value){
                map.eachLayer(function (layer) {
                    if ((layer.options.sector) && (layer.options.zoom !== zoom_value)) {
                        var radius = layer.options.current_base_radius;
                        if (map.sector_size.value != 0) {
                            radius += radius * parseFloat(map.sector_size.value);
                            layer.options.current_base_radius = radius;
                        }
                        zkf = ((zoom_value-10)*-12+100)/100
                        var current_size = radius * (11-parseFloat(layer.options.zoom_k))/10;
                        var size = zkf*current_size;

                        //if (size > 1){
                            layer.setRadius(size);
                            layer.options.zoom = zoom_value;
                        //}
                    }
                });
                map.sector_size.value = 0;
                var pd_size = 0;
                for (i in map._pd){
                    pd = map._pd[i];
                    pd.setDirection(parseFloat(pd.options.azimuth)-90, 60, pd_size);
                    pd_size = pd._radius;
                }

            };

            map.on('moveend', function(e){
                map.refresh_drive_test();
            });

            map.on('zoomend', function(e){
                var zoom = e.target._zoom;
                map.set_zoom(zoom);
            });

            map.on('mousemove', function(e){
                var pos = e.latlng;
                map._latlng.set_latlng(pos.lat, pos.lng);
            });

            map.on('click', function(e){
                if (layer._map._current_sector){
                    layer._map._current_sector.setStyle({
                        weight: 2,
                        opacity: 0.7
                    });
                }
            });


            map.select_sector = function(layer){
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
                    layer._map._info_control.content(create_info_control(layer.options.default_color, layer.options.sector))
                } else {
                    layer._map._info_control =  L.control.window(map,{position: 'left',});
                    layer._map._info_control.content(create_info_control(layer.options.default_color, layer.options.sector))
                    layer._map._info_control.show();
                    layer._map._info_control.on('close', function(){
                        delete layer._map._info_control
                    });
                }


            };

            map.refresh_drive_test = function(){
                if (map._is_drive_test){
                    usSpinnerService.spin('spinner_map');
                    map_bounds = map.getBounds();
                    var params = {
                        'bounds': map_bounds.toBBoxString(),
                        'zoom': map._zoom,
                    };

                    $http.post('/data/drive_test/', $.param(params)).success(function(data){
                        for (i in data){
                            var circle = L.circle(data[i], 1, {
                                color: 'black',
                                fillColor: 'black',
                                fillOpacity: 1,
                                opacity:1,
                            });
                            circle.addTo(map)
                        }

                        usSpinnerService.stop('spinner_map');
                    });
                }
            };

            map.drive_test = function(){
                if (map._is_drive_test){
                    map._is_drive_test = false;
                } else {
                    map._is_drive_test = true;
                    usSpinnerService.spin('spinner_map');
                    $http.get('/data/drive_test_init/').success(function(data){
                        $scope.mobile_stations = data.mobile_stations;
                        $scope.kpi = data.kpi;
                        map.setView(data.start_point, 17);
                        usSpinnerService.stop('spinner_map');
                    });
                }
            };

        });
}]);


rndControllers.controller('mapSettingsCtrl', ['$scope', '$http', '$cookies',
    function ($scope, $http, $cookies) {
        $scope.radius_wcdma = 1500;
        $scope.radius_gsm = 1200;
        $scope.radius_lte = 1800;

        if ($cookies.get('radius_gsm')){
                $scope.radius_gsm = $cookies.get('radius_gsm');
            }
            if ($cookies.get('radius_wcdma')){
                $scope.radius_wcdma = $cookies.get('radius_wcdma');
            }
            if ($cookies.get('radius_lte')){
                $scope.radius_lte = $cookies.get('radius_lte');
            }

        $scope.onSaveMapSettings = function(){
            $cookies.put('radius_wcdma', $scope.radius_wcdma);
            $cookies.put('radius_gsm', $scope.radius_gsm);
            $cookies.put('radius_lte', $scope.radius_lte);
        };
}]);


rndControllers.controller('sameNeighborCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.neighbor_table_config = {
            columnDefs: [
                { field: 'utrancell_source' },
                { field: 'utrancell_target'},
            ],
            enableGridMenu: true,
            enableSelectAll: true,
            exporterMenuPdf: false,
            exporterCsvFilename: 'neighbors.csv',
            exporterCsvLinkElement: angular.element(document.querySelectorAll(".custom-csv-link-location")),
            onRegisterApi: function(gridApi){
                $scope.gridApi = gridApi;
            }
        }

        $http.get('/data/rnd/same_neighbor/').success(function(data){
            $scope.neighbor_table_config.data = data;
        });
  }]);