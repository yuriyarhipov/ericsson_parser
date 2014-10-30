var measurementsControllers = angular.module('measurementsControllers', []);

measurementsControllers.controller('measurementsCtrl', ['$scope', '$http', '$routeParams',
    function ($scope, $http, $routeParams) {
        function load_files(f_type){
            $http.get('/data/measurements/' + f_type + '/').success(function(data) {
                $scope.files = data;
            });
        }

        var file_type = $routeParams.file_type;
        load_files(file_type);
        $scope.selected_file_type = file_type;
        $scope.onChangeFileType = function(){
            load_files($scope.selected_file_type);
        };
  }]);
