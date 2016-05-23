var parameterControllers = angular.module('parameterControllers', []);

parameterControllers.controller('registerVRCtrl', ['$scope', '$http', '$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true') {
            $location.path('/login')
        }
        $http.get('/data/version_release/').success(function (data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
        });
    }]);

parameterControllers.controller('createTemplateCtrl', ['$scope', '$http', '$location', '$cookies',
    function ($scope, $http, $location, $cookies) {
        if ($cookies.get('is_auth') != 'true') {
            $location.path('/login')
        }
        $scope.lable_mo = 'MO';
        $scope.networks = ['GSM', 'WCDMA', 'LTE'];
        $scope.network = {};
        $scope.param_table = [];
        $scope.mo = {};
        $scope.min_value = '';
        $scope.max_value = '';
        $scope.param = {};
        $scope.excel_complete = function (data) {
            $scope.param_table = data;
        };

        $scope.complete = function (data) {
            $location.path('/predefined_templates');
        };
        $scope.onChangeNetwork = function () {
            $http.get('/data/get_param/' + $scope.network.selected + '/').success(function (data) {
                $scope.columns = data;
            });
        };

        $scope.onClickAddParam = function () {
            var row = { 'param': $scope.param.selected, 'min_value': $scope.min_value, 'max_value': $scope.max_value }
            $scope.param_table.push(row);
            $scope.min_value = '';
            $scope.max_value = '';
        };
    }]);


parameterControllers.controller('editTemplateCtrl', ['$scope', '$http', '$location', '$routeParams', '$cookies',
    function ($scope, $http, $location, $routeParams, $cookies) {
        if ($cookies.get('is_auth') != 'true') {
            $location.path('/login')
        }
        console.log('OK1');
        var template = $routeParams.template;
        $http.get('/data/edit_template/' + template + '/').success(function (data) {
            $scope.network.selected = data.network;
            $scope.template_name = template;
            $scope.param_table = data.param_table
        });

        $scope.lable_mo = 'MO';
        $scope.networks = ['GSM', 'WCDMA', 'LTE'];
        $scope.network = {};
        $scope.param_table = [];
        $scope.mo = {};
        $scope.min_value = '';
        $scope.max_value = '';
        $scope.param = {};
        $scope.excel_complete = function (data) {
            $scope.param_table = data;
        };
        $scope.complete = function () {

            $location.path('/predefined_templates/');
        };
        $scope.onChangeNetwork = function () {

            $http.get('/data/get_mo/' + $scope.network.selected + '/').success(function (data) {
                $scope.tables = data;
            });
        };

        $scope.onChangeMO = function () {
            $http.get('/data/get_param/' + $scope.mo.selected + '/').success(function (data) {
                $scope.columns = data;
            });
        };

        $scope.onClickAddParam = function () {
            var row = { 'mo': $scope.mo.selected, 'param': $scope.param.selected, 'min_value': $scope.min_value, 'max_value': $scope.max_value }
            $scope.param_table.push(row);
            $scope.min_value = '';
            $scope.max_value = '';
        };
    }]);

parameterControllers.controller('predefinedTemplatesCtrl', ['$scope', '$http', '$location', '$cookies',
    function ($scope, $http, $location, $cookies) {
        if ($cookies.get('is_auth') != 'true') {
            $location.path('/login')
        }
        $http.get('/data/predefined_templates/').success(function (data) {
            $scope.templates = data;
        });
        $scope.onDeleteTemplate = function (tmp) {
            $http.get('/data/delete_template/' + tmp + '/').success(function () {
                $http.get('/data/predefined_templates/').success(function (data) {
                    $scope.templates = data;
                });
            });
        };
    }]);

parameterControllers.controller('ExcelDialogCtrl', ['$scope', '$mdDialog',
    function ($scope, $mdDialog) {
        console.log('OK');
}]);

parameterControllers.controller('runTemplateCtrl', ['$scope', '$http', 'Flash', '$cookies', '$location', '$mdDialog', '$window',
    function ($scope, $http, Flash, $cookies, $location, $mdDialog, $window) {
        if ($cookies.get('is_auth') != 'true') {
            $location.path('/login')
        }

        $scope.selected_group_cells = [];
        $scope.selected_cells = [];
        $scope.form_data = { 'cells': [] };
        $scope.group_cells = [];

        $scope.hideTable = true;
        $scope.hideForm = false;
        $scope.show_excel_dialog = false; 
        $scope.onChangeNetwork = function () {
            $http.get('/data/get_templates/' + $scope.network + '/').success(function (data) {
                $scope.templates = data;
                if (data.length > 0) {
                    $scope.template = $scope.templates[0];
                }
            });

            $http.get('/data/get_network_files/' + $scope.network + '/').success(function (data) {
                $scope.files = data.files;
                $scope.file = data.files[0];
                $http.get('/data/get_template_cells/' + $scope.network + '/' + $scope.file + '/').success(function (data) {
                    $scope.data_cells = data;
                });
            });
        };

        $scope.onChangeFile = function () {
            $http.get('/data/get_template_cells/' + $scope.network + '/' + $scope.file + '/').success(function (data) {
                $scope.data_cells = data;
            });

        };

        $scope.onAddCell = function () {
            $scope.group_cells = $scope.group_cells.concat($scope.selected_cells);
            var cells_length = $scope.selected_cells.length;
            for (var i = 0; i < cells_length; i++) {
                var index = $scope.data_cells.indexOf($scope.selected_cells[i]);
                $scope.data_cells.splice(index, 1);
            }
            $scope.group_cells.sort();
        };

        $scope.onDeleteCell = function () {

            var cells_length = $scope.selected_group_cells.length;
            for (var i = 0; i < cells_length; i++) {
                var index = $scope.group_cells.indexOf($scope.selected_group_cells[i]);
                $scope.group_cells.splice(index, 1);
            }
            $scope.data_cells = $scope.data_cells.concat($scope.selected_group_cells);
            $scope.data_cells.sort();
        };

        $http.get('/data/get_templates/').success(function (data) {
            $scope.templates = data;
        });

        $scope.complete = function (data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
        };

        $scope.check_hide = function (data) {
            console.log(data)
            console.log(data.length);
            return data.length == 0;
        };
        $scope.onClickExcel = function () {
            $scope.show_excel_dialog = false;
            Flash.create('success', 'Please wait');
            $scope.url = '/data/run_template/?template=' + $scope.template + '&file=' + $scope.file;
            var length_cells = $scope.group_cells.length;
            for (var i = 0; i < length_cells; i++) {
                $scope.url = $scope.url + '&cell=' + $scope.group_cells[i].cell;
            }
            $scope.url += '&excel=' + $scope.excelFileName;           
            $window.location.href = $scope.url; 
        };

        $scope.onClickRun = function () {
            Flash.create('success', 'Please wait');
            $scope.url = '/data/run_template/?template=' + $scope.template + '&file=' + $scope.file;
            var length_cells = $scope.group_cells.length;
            for (var i = 0; i < length_cells; i++) {
                $scope.url = $scope.url + '&cell=' + $scope.group_cells[i].cell;
            }
            $http.get($scope.url).success(function (data) {
                $scope.data = data;
                $scope.table_configs = {}
                for (i in data) {
                    columns = [];
                    for (col_id in data[i].columns) {
                        columns.push({
                            field: data[i].columns[col_id],
                            name: data[i].columns[col_id],
                            width: 100
                        })
                    }

                    $scope.table_configs[i] = $scope.table_config = {
                        columnDefs: columns,
                        enableGridMenu: true,
                        enableSelectAll: true,
                        enableFiltering: true,
                        flatEntityAccess: true,
                        showGridFooter: true,
                        data: data[i].data
                    }
                }

            });
        };
    }]);



