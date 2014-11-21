var treeViewControllers = angular.module('dashControllers', []);

treeViewControllers.controller('dashWcdmaCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/data/dash_num_sectors/').success(function(data) {
            $scope.chartConfig = {
                options: {
                    chart: {
                        type: 'column'
                    }
                },
                series: [
                    {
                        data: data,
                        name: 'Number of sectors',
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
                    text: 'Number of sectors by RNC'
                },
                tooltip: {
                    pointFormat: '<b>{point.y} </b>'
                },
                xAxis: {
                    type: 'category',
                    labels: {
                        rotation: -45,
                        align: 'right',
                        style: {
                            fontSize: '13px',
                            fontFamily: 'Verdana, sans-serif'
                        }
                    }
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: 'Number of sectors'
                    }
                },
                legend: {
                    enabled: false
                }
            }
        });

    }
]);
