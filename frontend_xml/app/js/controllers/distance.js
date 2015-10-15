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
            $http.get('/data/distance/get_load_distr/' + day + '/' + rbs + '/').success(function(data){
                for (ls_id in  data.logical_sectors){
                    console.log(data.logical_sectors[ls_id]);
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
                            text: data.logical_sectors[ls_id].title
                    },


                    series: [
                            {
                                data: data.logical_sectors[ls_id].data,
                                colorByPoint: true,
                                name: 'Load Distribution',
                            }
                        ],

                });
                }
                $scope.loadDistribution = {
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
                            text: data.title
                    },


                    series: [
                            {
                                data: data.data,
                                colorByPoint: true,
                                name: 'Load Distribution',
                            }
                        ],

                };
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
        $scope.networks = ['GSM', 'WCDMA', 'LTE'];
        $scope.bands = [
            '500',
            '550',
            '600',
            '650',
            '700',
            '750',
            '800',
            '850',
            '900',
            '950',
            '1000',
            '1050',
            '1100',
            '1150',
            '1200',
            '1250',
            '1300',
            '1350',
            '1400',
            '1450',
            '1500',
            '1550',
            '1600',
            '1650',
            '1700',
            '1750',
            '1800',
            '1850',
            '1900',
            '1950',
            '2000',
            '2050',
            '2100',
            '2150',
            '2200',
            '2250',
            '2300',
            '2350',
            '2400',
            '2450',
            '2500',
            '2550',
            '2600',
            '2650',
            '2700',
            '2750',
            '2800',
            '2850',
            '2900',
            '2950',
            '3000',];

        $scope.second_sector = [];
        $scope.new_sector = [];
        $scope.selected_logical_sector = [];
        $scope.logical_sectors = [];


        $http.get('data/distance/get_logical_sectors/').success(function(data){
            $scope.sectors = data.sectors;
            $scope.sectors.sort();

        });
        $http.get('data/distance/logical_sectors/').success(function(data){
            $scope.logical_sectors = data;
        });

        $scope.onAdd = function(network, band, sectors){
            for (s in sectors){
                $scope.new_sector.push({'network':network, 'band': band, 'sector': sectors[s]})
            }
            for (sector in sectors){
                var idx = $scope.sectors.indexOf(sectors[sector]);
                $scope.sectors.splice(idx, 1);
            }
        };

        $scope.onRemove = function(sectors){
            for (i in sectors){
                $scope.sectors.push(sectors[i].sector)
                $scope.sectors.sort();
                var idx = $scope.new_sector.indexOf(sectors[sector]);
                $scope.new_sector.splice(idx, 1);
            }
        }

        $scope.onSave = function(new_sector){
            var post_data = {
                'networks': [],
                'bands': [],
                'sectors': []
            };
            for (i in new_sector){
                post_data.networks.push(new_sector[i].network);
                post_data.bands.push(new_sector[i].band);
                post_data.sectors.push(new_sector[i].sector);
            }

            $http.post('/data/distance/logical_sectors/', $.param(post_data)).success(function(data){
                $scope.logical_sectors = data;
            });

            for (i in $scope.new_sector){
                $scope.sectors.push($scope.new_sector[i].sector)
            }
            $scope.sectors.sort();
            $scope.new_sector = [];
        };

        $scope.onDelete = function(id){
            $http.delete('/data/distance/logical_sectors/'+ id + '/').success(function(data){
                $scope.logical_sectors = data;
            });
        };
}]);