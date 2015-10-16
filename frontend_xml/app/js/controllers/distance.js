var distanceControllers = angular.module('distanceControllers', []);

auditControllers.controller('accessDistanceCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.rbs = {};
        $scope.days = {};
        $scope.chartConfigs = {};
        $scope.lsConfigs = [];
        $scope.day = 'none';
        $http.get('/data/distance/get_rbs').success(function(data){
            $scope.rbs_data = data.rbs;
            $scope.rbs.selected = $scope.rbs_data[0];
            $scope.onSelectDay('none', NaN);
            $http.get('/data/distance/get_dates/' + $scope.rbs.selected + '/').success(function(data){
                $scope.dates = data;
            });
        });

        $scope.get_config = function(sector){
                return $scope.chartConfigs[sector];
        };

        $scope.onSelect = function($item, $model){
            $http.get('/data/distance/get_dates/' + $item + '/').success(function(data){
                $scope.dates = data;
                if (!$scope.days.selected) {
                    $scope.onSelectDay('none', NaN);
                }
                else {
                    $scope.onSelectDay($scope.days.selected, NaN);
                }
            });
        };

        $scope.onSelectDay = function($item, $model){
            var day = $scope.day = $item;
            var rbs = $scope.rbs.selected;
            $scope.lsConfigs = [];
            $http.get('/data/distance/get_load_distr/' + day + '/' + rbs + '/').success(function(data){
                for (ls_id in  data){
                    $scope.lsConfigs.push({
                    options: {
                        chart: {
                            type: 'pie'
                        },
                        tooltip: {
                            pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b></br> Samples: <b>{point.y}</b>'
                        },
                        legend: {
                            enabled: true
                        },
                        plotOptions: {
                            pie: {
                                allowPointSelect: true,
                                cursor: 'pointer',
                                dataLabels: {
                                    enabled: true,
                                    format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                                    style: {
                                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                                    }
                                }
                            }
                        },
                    },
                    title: {
                            text: data[ls_id].logical_sector,
                    },
                    series: [
                            {
                                data: data[ls_id].data,
                                colorByPoint: true,
                                name: 'Load Distribution',
                            }
                        ],

                });
                }

            });

            $http.get('/data/distance/get_charts/' + day + '/' + rbs + '/').success(function(data){
                $scope.utrancells = Object.keys(data);
                $scope.utrancells.sort();

                var distances = data[$scope.utrancells[0]].distances;


                for (var id in $scope.utrancells){
                    var sector = $scope.utrancells[id];
                    $scope.chartConfigs[sector] = {
                        options: {
                            chart: {
                                type: 'column'
                            },
                            tooltip: {
                                formatter: function () {
                                    return 'Distance: <b>' + distances[this.point.category] + '</b><br/>' +
                                    'DC Vector: <b>' + this.point.category + '</b><br/>' +
                                    'Propagation Delay: <b>'+this.point.y+'%</b> ';
                                }

                            },
                        },
                        series: [
                            {
                                data: data[sector].chart,
                                name: 'DC Vector',
                            }
                        ],
                        title: {
                            text: 'Propagation Delay ' + data[sector].title
                        },
                        xAxis: {
                            type: 'category',
                        },
                        yAxis: {
                            min: 0,
                            title: {
                                text: '% Samples'
                            }
                        },
                        legend: {
                            enabled: true
                        },
                    };
                }
            });
            };
  }]);

filesControllers.controller('logicalSectorCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.associated_sectors = [];
        $scope.networks = ['GSM', 'WCDMA', 'LTE'];
        $scope.network = 'GSM';
        $scope.logical_sectors = [
            'LogicalSector1', 'LogicalSector2', 'LogicalSector3',
            'LogicalSector4', 'LogicalSector5', 'LogicalSector6',
            'LogicalSector7', 'LogicalSector8', 'LogicalSector9',
            'LogicalSector10', 'LogicalSector11', 'LogicalSector12',
            'LogicalSector13', 'LogicalSector14', 'LogicalSector15',
            'LogicalSector16', 'LogicalSector17', 'LogicalSector18',
            'LogicalSector19', 'LogicalSector20'
        ];
        $scope.logical_sector = 'LogicalSector1';
        $scope.bands = ['850', '900', '1800', '1900', '2100']
        $scope.band = '850';
        var default_sectors = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N',
        'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'];
        $scope.sectors = [];
        $http.get('data/distance/logical_sectors/').success(function(data){
            show_logical_sector('LogicalSector1', data);
        });

        $scope.onAdd = function(logical_sector, network, band, sectors){
            for (s_id in sectors){
                $http.post('/data/distance/logical_sectors/', $.param({
                    'logical_sector': logical_sector,
                    'technology': network,
                    'band': band,
                    'sector': sectors[s_id],
                })).success(function(data){
                    show_logical_sector(logical_sector, data);
                });
            }

        };

        $scope.onRemove = function(logical_sector, sectors){
            for (s_id in sectors){
                $http.delete('/data/distance/logical_sectors/' + logical_sector + '/' + sectors[s_id] + '/')
                .success(function(data){
                    show_logical_sector(logical_sector, data);
                });
            }
        }

        $scope.onChangeLogicalSector = function(logical_sector){
            $http.get('data/distance/logical_sectors/').success(function(data){
                show_logical_sector(logical_sector, data);
            });
        };

        var show_logical_sector = function(logical_sector, data){
            $scope.sectors = default_sectors.slice(0);
            $scope.associated_sectors = [];
            for (row_id in data){
                var row = data[row_id];
                if (row.logical_sector == logical_sector){
                    $scope.associated_sectors.push(row);
                }
                idx = $scope.sectors.indexOf(row.sector);
                if (idx >= 0){
                    $scope.sectors.splice(idx, 1);
                }
            }
            $scope.associated_sectors.sort(function (a, b) {
                if (a.label > b.label) {
                    return 1;
                }});

        };


}]);