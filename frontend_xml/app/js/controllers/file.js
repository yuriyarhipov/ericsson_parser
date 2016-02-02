var filesControllers = angular.module('filesControllers', []);

filesControllers.controller('FilesHubCtrl', ['$scope', '$http', '$timeout', 'uploadFileService', '$cookies', '$location',
    function ($scope, $http, $timeout, uploadFileService, $cookies, $location) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        $http.get('/data/files/').success(function(data) {
            $scope.files = data.files;
        });

        $scope.onDeleteFile = function(filename){
            console.log(filename);
            $http.get('/data/delete_file/' + filename + '/');
        };
  }]);

filesControllers.controller('AddFileCtrl', ['$scope', '$http', '$location','$cookies',
    function ($scope, $http, $location, $cookies) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        $scope.Network = [ 'WCDMA', 'GSM', 'LTE'];
        $scope.TypeFile = [
                    'Configuration Management XML File',
                    'WCDMA RADIO OSS BULK CM XML FILE',
                    'WCDMA TRANSPORT OSS BULK CM XML FILE',
                    'WNCS OSS FILE',
                    'WMRR OSS FILE',
                    'WCDMA LICENSE FILE OSS XML',
                    'WCDMA HARDWARE FILE OSS XML',
                    'HISTOGRAM FORMAT COUNTER',
                    'HISTOGRAM FILE COUNTER - Access Distance',
                    'Drive Test'
                ];
        $scope.CurrentNetwork = $scope.Network[0];
        $scope.CurrentTypeFile = $scope.TypeFile[0];
        $scope.file_data = {};

        $scope.onChangeNetwork = function(){
            if ($scope.CurrentNetwork == 'WCDMA'){
                $scope.TypeFile = [
                    'Configuration Management XML File',
                    'WCDMA RADIO OSS BULK CM XML FILE',
                    'WCDMA TRANSPORT OSS BULK CM XML FILE',
                    'WNCS OSS FILE',
                    'WMRR OSS FILE',
                    'WCDMA LICENSE FILE OSS XML',
                    'WCDMA HARDWARE FILE OSS XML',
                    'HISTOGRAM FORMAT COUNTER',
                    'HISTOGRAM FILE COUNTER - Access Distance',
                    'Drive Test'
                ];
            }
            if ($scope.CurrentNetwork == 'GSM'){
                $scope.TypeFile = [
                    'GSM BSS CNA  OSS FILE',
                    'GSM NCS OSS FILE',
                    'GSM MRR OSS FILE',
                    'Drive Test'
                ];
            }
            if ($scope.CurrentNetwork == 'LTE'){
                $scope.TypeFile = [
                    'LTE RADIO eNodeB BULK CM XML FILE',
                    'LTE TRANSPORT eNodeB BULK CM XML FILE',
                    'LTE LICENSE FILE OSS XML',
                    'LTE HARDWARE FILE OSS XML',
                    'Drive Test'
                ];
            }

            $scope.CurrentTypeFile = $scope.TypeFile[0];
        };

        $scope.complete = function(data){
            var id = data.id;
            $location.path('/status/' + id + '/');
        }
  }]);

filesControllers.controller('licensesCtrl', ['$scope', '$http','$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        $http.get('/data/licenses/').success(function(data) {
            $scope.files = data;
        });
  }]);

filesControllers.controller('licenseCtrl', ['$scope', '$http', '$routeParams','$cookies', '$location',
    function ($scope, $http, $routeParams, $cookies, $location) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        var filename = $routeParams.filename;
        var table = $routeParams.table;
        $http.get('/data/license/' + filename + '/' + table + '/').success(function(data) {
            $scope.columns = data.columns;
            $scope.data = data.data;
        });
  }]);

filesControllers.controller('hardwaresCtrl', ['$scope', '$http','$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        $http.get('/data/hardwares/').success(function(data) {
            $scope.files = data;
        });
  }]);

filesControllers.controller('hardwareCtrl', ['$scope', '$http', '$routeParams','$cookies', '$location',
    function ($scope, $http, $routeParams, $cookies, $location) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        $scope.filename = $routeParams.filename;
        $scope.table = $routeParams.table;
        $http.get('/data/hardware/' + $scope.filename + '/' + $scope.table + '/').success(function(data) {
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

filesControllers.controller('compareFilesCtrl', ['$scope', '$http','$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        $scope.network = 'GSM';
        $scope.hide_files = true;


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

        $scope.complete = function(data){
            if (data.compare_files){
                $scope.hide_files = false;
                $scope.compare_files = data.compare_files;
            }
            if (data.compare_table){
                $scope.compare_table = data.compare_table;
            }
        };
  }]);


filesControllers.controller('superfileCtrl', ['$scope', '$http', '$location','$cookies',
    function ($scope, $http, $location, $cookies) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        $scope.networks = ['GSM', 'LTE', 'WCDMA'];
        $scope.network = {};

        $scope.onChangeNetwork = function(){
            $http.get('/data/files/get_files/' + $scope.network.selected + '/').success(function(data){
                $scope.files = data;
            });
        };
        $scope.onSave = function(){
            $location.path('/files_hub');
        };
  }]);

filesControllers.controller('setCnaTemplateCtrl', ['$scope', '$http','$cookies', '$location',
    function ($scope, $http, $cookies, $location) {
        if (!$cookies.get('is_auth')){
            $location.path('/login')
        }
        function get_template(){
            $http.get('/data/files/get_cna_template/').success(function(data){
                $scope.tables = data;
            });
        }
        get_template();
        $scope.complete = function(data){
            $scope.tables = data;
            get_template();
        };
  }]);

filesControllers.controller('uploadFileCtrl', ['$scope', '$http', '$routeParams', '$timeout', '$location', 'Flash', 'activeProjectService', '$cookies',
    function ($scope, $http, $routeParams, $timeout, $location, Flash, activeProjectService, $cookies) {
        var id = $routeParams.id;
        var current = 1;
        $scope.dynamic = 1;
        var refer = false;
        var getStatus = function(){
            if (refer) {
                return
            }
            $http.get('/data/files/status/' + id + '/').success(function(data) {
                if (('"SUCCESS"' == data) && (current > 1)){
                    current = 0;
                    refer = true;
                    Flash.create('success', 'Import Completed');
                    activeProjectService.setProject(project);
                    $location.path('/maps');
                }
                current = data.current;
                if (current > 99){
                    current = 0;
                    refer = true;
                    Flash.create('success', 'Import Completed');
                    activeProjectService.broadcastItem($cookies.get('active_project'))
                    $location.path('/maps');
                }
                if (current){
                    $scope.dynamic = current;
                }
            });
            if (!refer) {
                $timeout(getStatus, 5000);
            }
        };
        $timeout(getStatus, 0);
  }]);

filesControllers.controller('driveTestLegendCtrl', ['$scope', '$http',
    function ($scope, $http) {
        function get_legend(){
            $http.get('/data/files/get_drive_test_legend/').success(function(data){
                $scope.legend = data;
            });
        }
        get_legend();
        $scope.complete = function(data){
            $scope.legend = data;
        };

}]);