var distanceControllers = angular.module('distanceControllers', []);

auditControllers.controller('accessDistanceCtrl', ['$scope', '$http', 'usSpinnerService',
    function ($scope, $http, usSpinnerService) {
        $scope.showComapreFilters = false;
        $scope.distance = {};
        $scope.rbs = {};
        $scope.days = {};
        $scope.chartConfigs = {};
        $scope.chartConfigs2 = {};
        $scope.lsConfigs = [];
        $scope.day = 'none';
        $scope.low_prop_percent = 20;
        $scope.low_sectors = [];
        $scope.over_prop_percent = 20;
        $scope.low_sectors = [];
        $scope.low_data_config = {
            columnDefs: [
                { field: 'RNC' },
                { field: 'Utrancell'},
                { field: 'Day From' },
                { field: 'Day To' },
                { field: 'DC Vector' },
                { field: 'Percentage'},
                { field: 'Percentage below'}
            ],
            enableGridMenu: true,
            enableSelectAll: true,
            exporterMenuPdf: false,
            exporterCsvFilename: 'export.csv',

            exporterCsvLinkElement: angular.element(document.querySelectorAll(".custom-csv-link-location")),
            onRegisterApi: function(gridApi){
                $scope.gridApi = gridApi;
            }
        };

        var chart_data = {};
        var chart_data2 = {};
        $http.get('/data/distance/get_rbs').success(function(data){
            $scope.rbs_data = data.rbs;
            $scope.rbs.selected = $scope.rbs_data[0];
            $http.get('/data/distance/get_dates/' + $scope.rbs.selected + '/').success(function(data){
                $scope.dates = data;
                $scope.days.selected_from = data[0];
                $scope.days.selected_to = data[data.length-1];
                $scope.onSelectDay();
            });
        });

        $scope.low_percent  = function(distance, percent, day_from, day_to){
            usSpinnerService.spin('spinner_low_coverage');

            $http.get('/data/distance/get_low_coverage/' + day_from + '/' + day_to + '/' + distance + '/').success(function(data){
                var temp_sectors = [];
                for (id in data){
                    var sector = data[id];
                    var sector_percent = parseFloat(sector.dist_sum)/parseFloat(sector.date_sum) * 100;
                    if (sector_percent <= percent){
                        temp_sectors.push({
                            'RNC': sector.rnc,
                            'Utrancell': sector.utrancell,
                            'Day From': $scope.days.selected_from,
                            'Day To': $scope.days.selected_to,
                            'DC Vector': distance,
                            'Percentage': percent,
                            'Percentage below': sector_percent.toFixed(2)});
                    }
                    usSpinnerService.stop('spinner_low_coverage');
                }
                $scope.low_data_config.data = temp_sectors;
            });
        };

        $scope.over_percent  = function(distance, percent){
            $scope.over_sectors = [];
            for (sector in chart_data){
                sum = 0;
                for (id in chart_data[sector].chart){
                    if (parseFloat(chart_data[sector].chart[id][0]) >= parseFloat(distance)){
                        sum += parseFloat(chart_data[sector].chart[id][1]);
                    }
                }
                if (sum >= percent){
                    $scope.over_sectors.push(sector);
                }
            }
            if ($scope.over_sectors.length > 0) {
                $scope.showOverDistance($scope.over_sectors[0], distance);
                $scope.selectedOverSector = $scope.over_sectors[0];
            }
        };


        $scope.onDistance = function($item, $model, percent){
            $scope.low_percent(parseFloat($item), percent, $scope.days.selected_from, $scope.days.selected_to);
        };

        $scope.onOverDistance = function($item, $model, percent){
            $scope.over_percent(parseFloat($item), percent);
        };

        $scope.get_config = function(sector){
                return $scope.chartConfigs[sector];
        };

        $scope.get_config2 = function(sector){
                return $scope.chartConfigs2[sector];
        };

        $scope.onSelect = function($item, $model){
            $http.get('/data/distance/get_dates/' + $item + '/').success(function(data){
                $scope.dates = data;
                $scope.days.selected_from = data[0];
                $scope.days.selected_to = data[-1];
                $scope.onSelectDay();

            });
        };

        $scope.onDayFrom = function($item, $model){
            $scope.days.selected_from = $item;
            $scope.onSelectDay();
        }

        $scope.onDayTo = function($item, $model){
            $scope.days.selected_to = $item;
            $scope.onSelectDay();
        }

        $scope.onDayFrom2 = function($item, $model){
            $scope.days.selected_from2 = $item;
            $scope.onSelectDay();
        }

        $scope.onDayTo2 = function($item, $model){
            $scope.days.selected_to2 = $item;
            $scope.onSelectDay();
        }

        $scope.showLowDistance = function(sector, distance){
            var low_propagation = [];
            var cats = []
            var sector_data = [];
            var sector_data2 = [];
            cats = [];
            var distances = chart_data[sector].distances;
            for (id in chart_data[sector].chart){
                var dc_vector = parseFloat(chart_data[sector].chart[id][0]);
                var value = chart_data[sector].chart[id][1];
                if (dc_vector <= parseFloat(distance)){
                    sector_data.push(value);
                    cats.push(dc_vector);
                }
            }
            low_propagation.push({
                'name': $scope.days.selected_from + ' - ' + $scope.days.selected_to,
                'data': sector_data
            });

            if ($scope.showComapreFilters){
                for (id in chart_data2[sector].chart){
                    var dc_vector = parseFloat(chart_data2[sector].chart[id][0]);
                    var value = chart_data2[sector].chart[id][1];
                    if (dc_vector <= parseFloat(distance)){
                        sector_data2.push(value);
                    }
                }
                low_propagation.push({
                    'name': $scope.days.selected_from2 + ' - ' + $scope.days.selected_to2,
                    'data': sector_data2
                });
            }
            $scope.low_config = {
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
                    xAxis: {
                        categories: cats,
                        crosshair: true
                    },
                    legend: {
                        enabled: true
                    }},
                    title: {
                            text: 'Low propagation',
                    },
                    series: low_propagation,
            }
        };

        $scope.showOverDistance = function(sector, distance){
            var over_propagation = [];
            var cats = []
            var sector_data = [];
            var sector_data2 = [];
            cats = [];
            var distances = chart_data[sector].distances;
            for (id in chart_data[sector].chart){
                var dc_vector = parseFloat(chart_data[sector].chart[id][0]);
                var value = chart_data[sector].chart[id][1];
                if (dc_vector >= parseFloat(distance)){
                    sector_data.push(value);
                    cats.push(dc_vector);
                }
            }
            over_propagation.push({
                'name': $scope.days.selected_from + ' - ' + $scope.days.selected_to,
                'data': sector_data
            });

            if ($scope.showComapreFilters){
                for (id in chart_data2[sector].chart){
                    var dc_vector = parseFloat(chart_data2[sector].chart[id][0]);
                    var value = chart_data2[sector].chart[id][1];
                    if (dc_vector >= parseFloat(distance)){
                        sector_data2.push(value);
                    }
                }
                over_propagation.push({
                    'name': $scope.days.selected_from2 + ' - ' + $scope.days.selected_to2,
                    'data': sector_data2
                });
            }
            $scope.over_config = {
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
                    xAxis: {
                        categories: cats,
                        crosshair: true
                    },
                    legend: {
                        enabled: true
                    }},
                    title: {
                            text: 'Over propagation',
                    },
                    series: over_propagation,
            }
        };

        $scope.onSelectDay = function(){
            $scope.distance.selected = '';
            $scope.over_sectors = [];
            $scope.low_sectors = [];
            $scope.over_config = {};
            $scope.low_config = {};

            var day_from = $scope.days.selected_from;
            var day_to = $scope.days.selected_to;
            var day_from2 = $scope.days.selected_from2;
            var day_to2 = $scope.days.selected_to2;
            var rbs = $scope.rbs.selected;
            $scope.lsConfigs = [];
            $http.get('/data/distance/get_load_distr/' + day_from + '/'+ day_to + '/' + rbs + '/').success(function(data){
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

            $http.get('/data/distance/get_charts/' + day_from + '/' + day_to + '/' + rbs + '/').success(function(data){
                $scope.utrancells = Object.keys(data);
                $scope.utrancells.sort();
                chart_data = data;

                var distances = data[$scope.utrancells[0]].distances;
                $scope.distances = Object.keys(distances);
                if (!$scope.showComapreFilters){
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
                                    name: day_from + ' - ' + day_to,
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
                } else {
                    $http.get('/data/distance/get_charts/' + day_from2 + '/' + day_to2 + '/' + rbs + '/').success(function(data2){
                        chart_data2 = data2;
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
                                    name: day_from + ' - ' + day_to,
                                },
                                {
                                    data: data2[sector].chart,
                                    name: day_from2 + ' - ' + day_to2,
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
                }
            });
        };
  }]);

filesControllers.controller('logicalSectorCtrl', ['$scope', '$http', '$cookies',
    function ($scope, $http, $cookies) {
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


        $scope.radius_gsm = 1200;
        $scope.radius_lte = 1800;
        $scope.radius_wcdma = 1500;

        if ($cookies.get('radius_gsm')){
            $scope.radius_gsm = $cookies.get('radius_gsm');
        }
        if ($cookies.get('radius_wcdma')){
            $scope.radius_wcdma = $cookies.get('radius_wcdma');
        }
        if ($cookies.get('radius_lte')){
            $scope.radius_lte = $cookies.get('radius_lte');
        }



        $scope.onSaveMapSettings = function(radius_wcdma, radius_lte, radius_gsm){
            $cookies.put('radius_wcdma', radius_wcdma);
            $cookies.put('radius_gsm', radius_gsm);
            $cookies.put('radius_lte', radius_lte);
        };

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