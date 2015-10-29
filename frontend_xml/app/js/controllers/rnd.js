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
                if (this._map._current_sector){
                    this._map._current_sector.setStyle({
                        weight: 2,
                        opacity: 0.7
                    });
                }
                var layer = e.target;
                layer.setStyle({
                    weight: 3,
                    opacity: 1
                });
                this._map._current_sector = layer;
                if (this._map._info_control){
                    this._map.removeControl(this._map._info_control);
                }

                this._map._info_control = create_info_control(color, sector);
                this._map._info_control.addTo(this._map);

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
                                'status': 'delete'}))
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
                                'status': 'new'}))
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
                        map.setView([wcdma_data.data[0].Latitud, wcdma_data.data[0].Longitud], 10);
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