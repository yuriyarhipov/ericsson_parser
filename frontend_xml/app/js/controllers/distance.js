var distanceControllers = angular.module('distanceControllers', []);

auditControllers.controller('accessDistanceCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.sector = {};
        $http.get('/data/distance/get_sectors').success(function(data){
            $scope.sectors = data.sectors;
        });

        $scope.onSelect = function($item, $model){
            $http.get('/data/distance/get_dates/' + $item + '/').success(function(data){
                $scope.dates = data;
            });
        };

        $scope.onClick = function(date, sector){
            $http.get('/data/distance/get_chart/' + date + '/' + sector + '/').success(function(data){
                $scope.chartConfig = {
                    options: {
                        chart: {
                            type: 'column'
                        },
                        tooltip: {
                            pointFormat: 'Complaint <b>{point.y}</b>'
                        },
                    },
                    series: [
                        {
                            data: data,
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