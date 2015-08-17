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