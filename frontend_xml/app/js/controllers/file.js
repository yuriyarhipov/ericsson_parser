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
        $scope.TypeFile = ['Xml', 'License'];
        $scope.CurrentNetwork = $scope.Network[0];
        $scope.CurrentTypeFile = $scope.TypeFile[0];
        $scope.file_data = {};
        //$scope.complete = function(){
            //$location.path('/files_hub');
        //}
  }]);
