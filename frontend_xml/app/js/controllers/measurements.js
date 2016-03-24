var measurementsControllers = angular.module('measurementsControllers', []);

measurementsControllers.controller('measurementsCtrl', ['$scope', '$http', '$routeParams', '$cookies', '$location',
    function ($scope, $http, $routeParams, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        function load_files(f_type){
            $http.get('/data/measurements/' + f_type + '/').success(function(data) {
                $scope.files = data;
            });
        }

        var file_type = $routeParams.file_type;
        load_files(file_type);
        $scope.selected_file_type = file_type;
        $scope.onChangeFileType = function(){
            load_files($scope.selected_file_type);
        };
  }]);


measurementsControllers.controller('wncsCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.table_config = {
            enableGridMenu: true,
            enableRowHeaderSelection: false,
            enableSelectAll: false,
            exporterMenuPdf: false,
            multiSelect: false,
            columnDefs: [
                { name:'CellName', field: 'cell_name' },
                { name:'NbCellName', field: 'nb_cell_name' },
                { name:'SC', field: 'sc', type: 'number'},
                { name:'Events', field: 'events', type: 'number'},
                { name:'Drop call', field: 'drop', type: 'number'},
                { name:'Distance[km]', field: 'distance', type: 'number'},
            ],
        };

        var chart_data = [];


        $http.get('/data/measurements/wncs/').success(function(data){
            $scope.table_config.data = data.data;
        });

        $http.get('/data/measurements/wncs_top/').success(function(data){
            var cats = [];
            var chart_data = []
            for (var i=0;i<20;i++){
                    cats.push(data.data[i]['cell_name']);
                    chart_data.push(data.data[i]['drop']);
            }
            $scope.chart_config = {
                options: {
                    chart: {
                        type: 'column'
                    },
                    xAxis: {
                        categories: cats,
                        crosshair: true
                    },
                    legend: {
                        enabled: true
                    }},
                title: {
                    text: 'Top 20 Drop call',
                },
                series: [{'data': chart_data, 'name': 'Drop'}, ],
            };
        });

        $scope.onexcel = function(){

        };

        $scope.change = function(){
            $http.get('/data/measurements/wncs/?distance='+ $scope.distance+'&drop='+$scope.min_numbers_drop+'&cells='+$scope.cells).success(function(data){
                $scope.table_config.data = data.data;
            });

            $http.get('/data/measurements/wncs_top/?distance='+ $scope.distance+'&drop='+$scope.min_numbers_drop+'&cells='+$scope.cells).success(function(data){
                var cats = [];
                var chart_data = []
                var l = 20
                if (data.data.length < 20){
                    l = data.data.length
                }
                for (var i=0;i<l;i++){
                        cats.push(data.data[i]['cell_name']);
                        chart_data.push(data.data[i]['drop']);
                }
                $scope.chart_config = {
                    options: {
                        chart: {
                            type: 'column'
                        },
                        xAxis: {
                            categories: cats,
                            crosshair: true
                        },
                        legend: {
                            enabled: true
                        }},
                    title: {
                        text: 'Top 20 Drop call',
                    },
                    series: [{'data': chart_data, 'name': 'Drop'}, ],
                };
            });
        };
  }]);
