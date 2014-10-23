var queryControllers = angular.module('queryControllers', []);

queryControllers.controller('CreateGroupOfCellsCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.onChangeTechnology = function(){
            $http.get('/data/get_cells/' + $scope.technology).success(function(data) {
                $scope.data_cells = data;
        });
        };

  }]);
