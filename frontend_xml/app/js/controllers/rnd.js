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

        var create_sector = function(lat, lon, sector, color, size, key){
            var new_sector = L.circle([lat, lon], size, {
                            color: color,
                            opacity: 0.7,
                            weight: 2,
                            sector: sector,
                            current_base_radius: size
                    })
            .bindPopup(key, {'offset': L.Point(20, 200)})
            .setDirection(sector.Azimuth, 60)
            .on('click', function(e){
                var layer = e.target;
                layer.setStyle({
                    weight: 3,
                    opacity: 1
                });
            })
            return new_sector;
        };

        var create_rnd_layer = function(data, radius, color, lat, lon, key){
            var data = data.data;
            var sectors = [];
            for (sid in data){
                var sector = create_sector(
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
            map._layerControl = L.control.layers().addTo(map);
            $http.get('/data/rnd/gsm/').success(function(gsm_data){
                $http.get('/data/rnd/wcdma/').success(function(wcdma_data){
                    $http.get('/data/rnd/lte/').success(function(lte_data){
                        gsm_layer = create_rnd_layer(gsm_data, 1500, 'orange', 'Latitude', 'Longitude', 'Cell_Name');
                        wcdma_layer = create_rnd_layer(wcdma_data, 1200, 'blue', 'Latitud', 'Longitud', 'Utrancell');
                        lte_layer = create_rnd_layer(lte_data, 1000, 'green', 'Latitude', 'Longitude', 'Utrancell');
                        map._layerControl.addOverlay(gsm_layer, 'GSM');
                        map._layerControl.addOverlay(wcdma_layer, 'WCDMA');
                        map._layerControl.addOverlay(lte_layer, 'LTE');
                        map.addLayer(gsm_layer);
                        map.addLayer(wcdma_layer);
                        map.addLayer(lte_layer);
                    });
                });
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