var distanceControllers = angular.module('distanceControllers', []);

auditControllers.controller('accessDistanceCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.sector = {};
        $scope.days = {};
        $scope.day = 'none';
        $http.get('/data/distance/get_sectors').success(function(data){
            $scope.sectors = data.sectors;
            $scope.sector.selected = $scope.sectors[0];
            $scope.onSelectDay('none', NaN);
            $http.get('/data/distance/get_dates/' + $scope.sectors[0] + '/').success(function(data){
                $scope.dates = data;
            });
        });

        $scope.onSelect = function($item, $model){
            $http.get('/data/distance/get_dates/' + $item + '/').success(function(data){
                $scope.dates = data;
            });
        };


        $scope.onSelectDay = function($item, $model){
            var day = $scope.day = $item;
            var sector = $scope.sector.selected;
            $http.get('/data/distance/get_chart/' + day + '/' + sector + '/').success(function(data){
                $scope.table = data.table;
                $scope.chart = data.chart;
                var distances = data.distances;
                console.log(distances);
                $scope.chartConfig = {
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
                            data: data.chart,
                            name: 'DC Vector',
                        }
                    ],
                    title: {
                        text: 'Propagation Delay ' + data.title
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
            });
            };
  }]);