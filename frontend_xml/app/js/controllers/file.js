var filesControllers = angular.module('filesControllers', []);

filesControllers.controller('FilesHubCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/data/files/').success(function(data) {
            $scope.files = data;
        });
  }]);

filesControllers.controller('AddFileCtrl', ['$scope', '$http', '$location',
    function ($scope, $http, $location) {
        $scope.Network = [ '2G', '3G', '4G'];
        $scope.TypeFile = ['Txt', 'License', 'Hardware', 'WNCS', 'WMRR'];
        $scope.CurrentNetwork = $scope.Network[0];
        $scope.CurrentTypeFile = $scope.TypeFile[0];
        $scope.file_data = {};

        $scope.onChangeNetwork = function(){
            if ($scope.CurrentNetwork == '2G'){
                $scope.TypeFile = ['Txt', 'License', 'Hardware', 'WNCS', 'WMRR'];
            }
            else {
                $scope.TypeFile = ['XML', 'License', 'Hardware', 'NCS', 'MRR'];
            }
            $scope.CurrentTypeFile = $scope.TypeFile[0];
        };

        $scope.complete = function(){
            $location.path('/files_hub');
        }
  }]);

filesControllers.controller('licensesCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/data/licenses/').success(function(data) {
            $scope.files = data;
        });
  }]);

filesControllers.controller('licenseCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        var filename = $routeParams.filename;
        var table = $routeParams.table;
        $http.get('/data/license/' + filename + '/' + table + '/').success(function(data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
        });
  }]);

filesControllers.controller('hardwaresCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/data/hardwares/').success(function(data) {
            $scope.files = data;
        });
  }]);

filesControllers.controller('hardwareCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        var filename = $routeParams.filename;
        var table = $routeParams.table;
        $http.get('/data/hardware/' + filename + '/' + table + '/').success(function(data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
        });
  }]);

filesControllers.controller('compareFilesCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.network = '2g';

        function set_files_for_compare(files, main_file){
            $scope.files_for_compare = [];
            var f_length =  files.length;
                for (var i = 0; i < f_length; i++){
                    if (main_file != files[i]){
                        $scope.files_for_compare.push(files[i]);
                    }
                }
        }

        function load_files(network){
            $http.get('/data/get_files_for_compare/' + network + '/').success(function(data) {
                $scope.files = data.files;
                $scope.main_file = data.main_file;
                $scope.tables = data.tables;
                set_files_for_compare(data.files, data.main_file);
            });
        }

        function load_cells(network){
            $http.get('data/get_cells/' + network + '/').success(function(data){
                $scope.cells = data;
            });
        }


        load_files($scope.network);
        load_cells($scope.network);

        $scope.onChangeNetwork = function(){
            load_files($scope.network);
            load_cells($scope.network);
        };

        $scope.onChangeMainFile = function(){
            set_files_for_compare($scope.files, $scope.main_file);
        };
  }]);