var distanceControllers = angular.module('distanceControllers', []);

auditControllers.controller('accessDistanceCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.rbs = {};
        $scope.days = {};
        $scope.chartConfigs = {};
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
        $scope.table = [];

        $http.get('data/distance/get_logical_sectors/').success(function(data){
            $scope.sectors = data.sectors;
        });

        $scope.onSave = function(){
            $scope.table.push({
                'first_s': $scope.first_sector,
                'second_s': $scope.second_sector,
            });
        };
}]);