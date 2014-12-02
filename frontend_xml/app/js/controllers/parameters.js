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
        $scope.lable_mo = 'MO';
        $scope.networks = ['GSM', 'WCDMA', 'LTE'];
        $scope.network = {};
        $scope.param_table = [];
        $scope.mo = {};
        $scope.min_value = '';
        $scope.max_value = '';
        $scope.param = {};
        $scope.complete = function(data){
            $scope.param_table = data;
        };
        $scope.onChangeNetwork = function(){
            $http.get('/data/get_mo/' + $scope.network.selected + '/').success(function(data) {
                $scope.tables = data;
            });
            if ($scope.network == 'GSM'){
                $scope.lable_mo = 'gsm file';
            }
            else{
                $scope.lable_mo = 'MO';
            }
        };

        $scope.onChangeMO = function(){
            $http.get('/data/get_param/' + $scope.mo.selected + '/').success(function(data) {
                $scope.columns = data;
            });
        };

        $scope.onClickAddParam = function(){
            var row = {'mo': $scope.mo.selected, 'param': $scope.param.selected, 'min_value': $scope.min_value, 'max_value':$scope.max_value}
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

        $scope.hideTable = true;
        $scope.hideForm = false;

        $scope.onChangeNetwork = function(){
            $http.get('/data/predefined_templates/').success(function(data) {
                $scope.templates = [];
                var templates_length = data.length;
                for (var i = 0; i < templates_length; i++){
                    if (data[i].network == $scope.network){
                        $scope.templates.push(data[i].template_name);
                    }
                }
                $scope.template = $scope.templates[0];
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

        $scope.onClickRun = function(){
            $scope.url='/data/run_template/?network='+ $scope.network + '&template=' + $scope.template;
            var length_cells = $scope.group_cells.length;
            for (var i = 0; i<length_cells; i++){
                $scope.url = $scope.url +'&cell=' + $scope.group_cells[i].cell;
            }
            $http.get($scope.url).success(function(data) {
                $scope.hideTable = false;
                $scope.hideForm = true;
                $scope.columns = data.columns;
                $scope.data = data.data;
                $scope.totalItems = data.count;
                $scope.itemsPerPage = 20;
            });
        };

        $scope.pageChanged = function() {
            $http.get($scope.url + '&page=' + $scope.currentPage ).success(function(data) {
                $scope.data = data.data;
            });
        };
        $scope.onClickReturn = function(){
            $scope.hideTable = true;
            $scope.hideForm = false;
        };

  }]);
