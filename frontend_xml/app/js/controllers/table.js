var tableControllers = angular.module('tableControllers', []);

tableControllers.controller('TableCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $scope.filename = $routeParams.filename;
        $scope.tablename = $routeParams.table_name;
        $http.get('/data/table/' + $scope.filename + '/' + $scope.tablename + '/').success(function(data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
            $scope.totalItems = data.count;
            $scope.itemsPerPage = 20;
        });
        $scope.pageChanged = function() {
            $http.get('/data/table/' + $scope.filename + '/' + $scope.tablename + '?page=' + $scope.currentPage ).success(function(data) {
                $scope.data = data.data;
            });
        };
  }]);

tableControllers.controller('exploreCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        $http.get('/data/explore/' + $routeParams.filename + '/').success(function(data) {
            $scope.tables = data;
        });
  }]);

tableControllers.controller('byTechnologyCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.network = 'GSM';
        $http.get('/data/by_technology/GSM/').success(function(data) {
            $scope.data = data;
        });

        $scope.onChangeNetwork = function(){
            $http.get('/data/by_technology/' + $scope.network).success(function(data) {
                $scope.data = data;
            });
        };

        $scope.onFilter = function(){
            $http.get('/data/by_technology/' + $scope.network + '?filter=' + $scope.file_filter).success(function(data) {
                $scope.data = data;
            });
        };
  }]);

tableControllers.controller('cellDefCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.radius = 100;
        $http.get('/data/cell_definition/').success(function(data) {
                $scope.radius = data.radius;
        });
}]);

tableControllers.controller('excelCtrl', ['$scope', '$http', '$routeParams', '$timeout',
    function ($scope, $http, $routeParams, $timeout) {
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