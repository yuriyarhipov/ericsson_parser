var auditControllers = angular.module('auditControllers', []);

auditControllers.controller('setAuditTemplateCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.network = 'GSM';
        $http.get('/data/audit/get_audit_template/?network=gsm').success(function(data){
            $scope.template = data;
        });

        $scope.onChangeNetwork = function(network){
            $http.get('/data/audit/get_audit_template/?network=' + network).success(function(data){
                $scope.template = data;
            });
        };

        $scope.complete = function(data){
            $scope.template = data;
        };
  }]);

auditControllers.controller('runAuditCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.network = 'GSM';
        $scope.selected_file = '';
        $http.get('/data/files/get_files/GSM/').success(function(data){
            $scope.files = data;
        });

        $scope.onChangeNetwork = function(network){
            $http.get('/data/files/get_files/' + network + '/').success(function(data){
                $scope.files = data;
            });
        };

        $scope.runAudit = function(file){
            $http.get('/data/audit/run_audit/' + $scope.network + '/' + file + '/').success(function(data){
                $scope.table = data.table;
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
                            data: data.chart,
                            name: 'Parameter',
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
                        text: 'Parameter'
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
                            text: 'Complaint'
                        }
                    },
                    legend: {
                        enabled: false
                    },
                };
            });
        };
  }]);

auditControllers.controller('powerAuditCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $http.get('/data/files/get_files/WCDMA/').success(function(data){
            $scope.files = data;
        });

        $scope.runAudit = function(file){
            $http.get('/data/audit/power_audit/' + file + '/').success(function(data){
                $scope.table = data.table;
                $scope.chartConfig = {
                    options: {
                        chart: {
                            type: 'column'
                        },
                    },
                    series: [
                        {
                            data: data.chart,
                            name: 'Criteria Fulfillment',
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
                        text: 'Criteria Fulfillment'
                    },
                    xAxis: {
                        categories: ['Yes', 'No'],
                        crosshair: true,
                    },

                    legend: {
                        enabled: false
                    },
                };
            });
        };
  }]);

auditControllers.controller('auditParamCtrl', ['$scope', '$http', '$routeParams', '$cookies', '$location',
    function ($scope, $http, $routeParams, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $http.get('/data/audit/audit_param/' + $routeParams.network + '/' + $routeParams.filename + '/' + $routeParams.param_name + '/').success(function(data){
            $scope.template = data;
        });


  }]);
