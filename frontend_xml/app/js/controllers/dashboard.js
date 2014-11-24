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
            };
        });
        $http.get('/data/dash_model_eq/').success(function(data) {
            $scope.chartConfigModelEq = {
                options: {
                    chart: {
                        type: 'column'
                    }
                },
                series: [
                    {
                        data: data,
                        name: 'Model of Equipment',
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
                    text: 'Model of Equipment by RNC'
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
                        text: 'Model of Equipment'
                    }
                },
                legend: {
                    enabled: false
                }
            };
        });

        $http.get('/data/dash_cells_lac/').success(function(data) {
            $scope.chartConfigCellsLac = {
                options: {
                    chart: {
                        type: 'column'
                    }
                },
                series: [
                    {
                        data: data,
                        name: 'Number of Cells',
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
                    text: 'Number of Cells by LAC'
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
                        text: 'Number of Cells'
                    }
                },
                legend: {
                    enabled: false
                }
            };
        });

    }
]);
