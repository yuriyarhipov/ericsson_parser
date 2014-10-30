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

        //$scope.complete = function(){
        //    $location.path('/files_hub');
        //}
  }]);

filesControllers.controller('licensesCtrl', ['$scope', '$http',
    function ($scope, $http) {
        $http.get('/data/licenses/').success(function(data) {
            $scope.files = data;
        });
  }]);