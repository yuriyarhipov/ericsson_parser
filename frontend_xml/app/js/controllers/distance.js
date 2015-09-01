var distanceControllers = angular.module('distanceControllers', []);

auditControllers.controller('accessDistanceCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.sector = {};
        $http.get('/data/distance/get_sectors').success(function(data){
            $scope.sectors = data.sectors;
            $scope.sector.selected = $scope.sectors[0];
            $scope.onSelectDay('none', NaN)

        });

        $scope.onSelect = function($item, $model){
            $http.get('/data/distance/get_dates/' + $item + '/').success(function(data){
                $scope.dates = data;
            });
        };

        $scope.onSelectDay = function($item, $model){
            var day = $item;
            var sector = $scope.sector.selected;
            $http.get('/data/distance/get_chart/' + day + '/' + sector + '/').success(function(data){
                $scope.table = data.table;
                $scope.chartConfig = {
                    options: {
                        chart: {
                            type: 'column'
                        },
                        tooltip: {
                            formatter: function () {
                                return 'Distance: <b>' + this.point.category + '</b><br/>' +
                                'Propagation Delay: <b>'+this.point.y+'%</b> ';
                            }

                        },
                    },
                    series: [
                        {
                            data: data.chart,
                            name: 'Distance',
                            dataLabels: {
                                enabled: true,
                                rotation: -90,
                                color: '#FFFFFF',
                                align: 'right',
                                x: 4,
                                y: 10,
                                style: {
                                    fontSize: '13px',
                                    fontFamily: 'Verdana, sans-serif',
                                    textShadow: '0 0 3px black'
                                }
                            }
                        }
                    ],
                    title: {
                        text: 'Propagation Delay'
                    },
                    xAxis: {
                        type: 'category',
                        labels: {
                            rotation: -45,
                            align: 'right',
                            y: 50,
                            style: {
                                fontSize: '13px',
                                fontFamily: 'Verdana, sans-serif'
                            }
                        }
                    },
                    yAxis: {
                        min: 0,
                        title: {
                            text: '% Samples'
                        }
                    },
                    legend: {
                        enabled: false
                    },
                };
            });
            };
  }]);