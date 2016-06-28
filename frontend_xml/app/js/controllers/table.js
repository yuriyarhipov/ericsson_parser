var tableControllers = angular.module('tableControllers', []);

tableControllers.controller('TableCtrl', ['$scope', '$http', '$routeParams', '$cookies', '$location', 'uiGridConstants', 'usSpinnerService',
    function ($scope, $http, $routeParams, $cookies, $location, uiGridConstants, usSpinnerService) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.tablename = $routeParams.table_name;
        var columns = [];
        $scope.table_config = {
            columnDefs: columns,
            enableGridMenu: true,
            enableSelectAll: true,
            enableFiltering: true,
            flatEntityAccess: true,
            showGridFooter: true,
        }
        $scope.excel_url = '/data/table/' + $scope.tablename + '/?excel=true'
        $http.get('/data/table/' + $scope.tablename + '/').success(function(data) {
            for (col_id in data.columns){
                columns.push({
                    field: data.columns[col_id],
                    name: data.columns[col_id],
                    width:100
                })
            }
            $scope.table_config.data = data.data;
            usSpinnerService.stop('spinner_table');
        });
    }]
);

tableControllers.controller('exploreCtrl', ['$scope', '$http', '$routeParams', '$cookies', '$location',
    function ($scope, $http, $routeParams, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $http.get('/data/explore/' + $routeParams.filename + '/').success(function(data) {
            $scope.tables = data;
        });
  }]);

tableControllers.controller('byTechnologyCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.vendors = ['Ericsson', 'Nokia', 'Huawei'];
        $scope.vendor = 'Ericsson';

        $scope.networks = ['GSM', 'WCDMA', 'LTE'];
        $scope.network = 'WCDMA';
        $scope.filter = ''
        $scope.filename = 'Topology'
        $scope.check_tables = {};
        $scope.tables_params = '';

        $scope.refreshData = function(vendor, network, filter){
            $http.get('/data/by_technology/' + vendor + '/' + network + '/?filter=' + filter).success(function(data) {
                $scope.data = data;
                for (i in data){
                    $scope.check_tables[data[i]] = true;   
                    $scope.tables_params = $scope.tables_params + '&table=' + data[i]; 
                }                
            });
        };
        
        $scope.refreshData('Ericsson', 'WCDMA', '');
        $scope.select_all = true;
        $scope.onSelectAll = function(status){
            if (status){
                for (i in $scope.data){
                    $scope.check_tables[$scope.data[i]] = true;   
                }               
            } else {
                for (i in $scope.data){
                    $scope.check_tables[$scope.data[i]] = false;   
                }
            }            
        };
        $scope.onChangeTable = function(){            
            $scope.tables_params = '';
            for (i in $scope.check_tables){                
                if ($scope.check_tables[i]){                    
                    $scope.tables_params = $scope.tables_params + '&table=' + i;             
                }
            };
        }; 
        
  }]);

tableControllers.controller('cellDefCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.radius = 100;
        $http.get('/data/cell_definition/').success(function(data) {
                $scope.radius = data.radius;
        });
}]);

tableControllers.controller('excelCtrl', ['$scope', '$http', '$routeParams', '$timeout', '$cookies', '$location',
    function ($scope, $http, $routeParams, $timeout, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        params = {
            'project_id':  $routeParams.project_id,
            'filename': $routeParams.filename,
            'table': $routeParams.table
        };
        $scope.is_ready = false;
        $http.post('/data/excel/',$.param(params)).success(function(data){
            var getStatus = function(){
                $http.get('/data/excel_status/' + $routeParams.project_id + '/' + $routeParams.filename + '/' + $routeParams.table + '/').success(function(status_data){
                    if (status_data.url){
                        $scope.file_url = status_data.url;
                        $scope.is_ready = true;
                    } else {
                        $scope.value = status_data.value;
                        $scope.message = status_data.message;
                        $timeout(getStatus, 5000);
                    }
                })
            }
            $timeout(getStatus, 0);
        });
}]);

tableControllers.controller('universalTablesCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.tables = [
            'GsmGsm', 'GsmLte', 'GsmWcdma', 
            'WcdmaWcdma', 'WcdmaGsm', 'WcdmaLte', 
            'LteLte', 'LteGsm', 'LteWcdma',
            'RND3G'
        ]
}]);

tableControllers.controller('universalTableCtrl', ['$scope', '$http', '$routeParams', '$cookies', '$location', 'usSpinnerService',
    function ($scope, $http, $routeParams, $cookies, $location, usSpinnerService) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        
        $scope.tablename = $routeParams.table_name;
        var columns = [];
        $scope.table_config = {
            columnDefs: columns,
            enableGridMenu: true,
            enableSelectAll: true,
            enableFiltering: true,
            flatEntityAccess: true,
            showGridFooter: true,
        }
        $scope.excel_url = '/data/universal_table/' + $routeParams.table_name + '/?excel=true' 
        $http.get('/data/universal_table/' + $routeParams.table_name + '/').success(function(data) {
            for (col_id in data.columns){
                columns.push({
                    field: data.columns[col_id],
                    name: data.columns[col_id],
                    width:100
                })
            }
            $scope.table_config.data = data.data;
            usSpinnerService.stop('spinner_table');
        });
        
        
}]);
