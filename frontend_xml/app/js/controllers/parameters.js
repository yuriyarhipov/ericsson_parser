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
        $scope.complete = function(data){
            $scope.param_table = data;
        };
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

parameterControllers.controller('predefinedTemplatesCtrl', ['$scope', '$http', '$location',
    function ($scope, $http, $location) {
        $http.get('/data/predefined_templates/').success(function(data) {
            $scope.templates = data;
        });
        $scope.onDeleteTemplate = function(tmp){
            $http.get('/data/delete_template/' + tmp + '/');
            $location.path('/predefined_templates');

        };
  }]);

parameterControllers.controller('runTemplateCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.selected_group_cells = [];
        $scope.selected_cells = [];
        $scope.form_data = {'cells': []};
        $scope.group_cells = [];

        $scope.onChangeNetwork = function(){
            $http.get('/data/predefined_templates/').success(function(data) {
                $scope.templates = [];
                var templates_length = data.length;
                for (var i = 0; i < templates_length; i++){
                    if (data[i].network == $scope.network){
                        $scope.templates.push(data[i].template_name);
                    }
                }
                $scope.template = $scope.templates;
            });
            $http.get('/data/get_template_cells/' + $scope.network).success(function(data) {
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

        $scope.complete = function(data){
            $scope.columns = data.columns;
            $scope.data = data.data;
        };

  }]);
