var queryControllers = angular.module('queryControllers', []);

queryControllers.controller('CreateGroupOfCellsCtrl', ['$scope', '$http', '$location',
    function ($scope, $http, $location) {
        $scope.selected_group_cells = [];
        $scope.selected_cells = [];
        $scope.form_data = {'cells': []};
        $scope.group_cells = [];


        $scope.complete = function(data){
            $scope.group_cells = data;
        };

        $scope.onChangeNetwork = function(){
            $http.get('/data/get_cells/' + $scope.form_data.network).success(function(data) {
                data.sort();
                $scope.data_cells = data;
            });
        };

        $scope.onAddCell = function(){
            $scope.group_cells = $scope.group_cells.concat($scope.selected_cells);
            var cells_length = $scope.selected_cells.length;
            for (var i=0; i< cells_length; i++){
                var index = $scope.data_cells.indexOf($scope.selected_cells[i]);
                $scope.data_cells.splice(index, 1);
            }
            $scope.group_cells.sort();
        };

        $scope.onDeleteCell = function(){

            var cells_length = $scope.selected_group_cells.length;
            for (var i=0; i< cells_length; i++){
                var index = $scope.group_cells.indexOf($scope.selected_group_cells[i]);
                $scope.group_cells.splice(index, 1);
            }
            $scope.data_cells = $scope.data_cells.concat($scope.selected_group_cells);
            $scope.data_cells.sort();
        };

        $scope.saveGroupOfCells = function(){
            var cells = [];
            var cells_length = $scope.group_cells.length;
            for (var i = 0; i < cells_length; i++){
                cells.push($scope.group_cells[i].cell);
            }
            $scope.form_data.cells = cells;
            $http.post('/data/save_group_of_cells/', $.param($scope.form_data)).success(function(){
            });
            $location.path('/groups');
        };


  }]);

queryControllers.controller('GroupsCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/data/get_groups/').success(function(data) {
                $scope.projects = data;
            });

  }]);
