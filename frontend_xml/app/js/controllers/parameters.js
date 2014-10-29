var parameterControllers = angular.module('parameterControllers', []);

parameterControllers.controller('registerVRCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/data/version_release/').success(function(data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
        });
  }]);

parameterControllers.controller('createTemplateCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.param_table = [];
        $scope.mo = '';
        $scope.min_value = '';
        $scope.max_value = '';
        $scope.onChangeNetwork = function(){
            $http.get('/data/get_mo/' + $scope.network + '/').success(function(data) {
                $scope.tables = data;
            });
        };

        $scope.onChangeMO = function(){
            $http.get('/data/get_param/' + $scope.mo + '/').success(function(data) {
                $scope.columns = data;
            });
        };

        $scope.onClickAddParam = function(){
            var row = {'mo': $scope.mo, 'param': $scope.param, 'min_value': $scope.min_value, 'max_value':$scope.max_value}
            $scope.param_table.push(row);
            $scope.min_value = '';
            $scope.max_value = '';
        };
  }]);
