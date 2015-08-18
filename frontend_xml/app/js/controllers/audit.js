var auditControllers = angular.module('auditControllers', []);

auditControllers.controller('setAuditTemplateCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.network = 'GSM';
        $http.get('/data/audit/get_audit_template/?network=gsm').success(function(data){
            $scope.template = data;
        });

        $scope.onChangeNetwork = function(network){
            $http.get('/data/audit/get_audit_template/?network=' + network).success(function(data){
                $scope.template = data;
            });
        };

        $scope.complete = function(data){
            $scope.template = data;
        };
  }]);

auditControllers.controller('runAuditCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $scope.network = 'GSM';
        $scope.selected_file = '';
        $http.get('/data/files/get_files/GSM/').success(function(data){
            $scope.files = data;
        });

        $scope.onChangeNetwork = function(network){
            $http.get('/data/files/get_files/' + network + '/').success(function(data){
                $scope.files = data;
            });
        };

        $scope.runAudit = function(file){
            $http.get('/data/audit/run_audit/' + $scope.network + '/' + file + '/').success(function(data){
                $scope.table = data;
            });
        };


  }]);