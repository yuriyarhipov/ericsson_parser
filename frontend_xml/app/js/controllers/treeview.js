var treeViewControllers = angular.module('treeViewControllers', []);

treeViewControllers.controller('TreeViewCtrl', ['$scope', '$http', '$cookies', 'activeProjectService', '$location',
    function ($scope, $http, $cookies, activeProjectService, $location) {
        $http.get('/data/treeview/' + $cookies.active_project).success(function(data){
            $scope.treedata = data;
        });

        $scope.$on('handleBroadcast', function() {
            var project = activeProjectService.project;
            $http.get('/data/treeview/' + project).success(function(data){
                $scope.treedata = data;
            });
        });
        $scope.$on('uploadFile', function() {
            $http.get('/data/treeview/' + $cookies.active_project).success(function(data){
            $scope.treedata = data;

        });
        });
        $scope.$watch( 'tree_view.currentNode', function( newObj, oldObj ) {
            if( $scope.tree_view && angular.isObject($scope.tree_view.currentNode) ) {
                var node_type = $scope.tree_view.currentNode.type;
                var network = $scope.tree_view.currentNode.network;
                if ((node_type == 'xml') && (network == '3g')){
                    var wcdma = $scope.tree_view.currentNode.id;
                    $cookies.wcdma = wcdma;
                    $cookies.active_file = wcdma;
                    $location.path('/explore/' + wcdma + '/');
                }
                if ((node_type == 'xml') && (network == 'LTE')){
                    var lte = $scope.tree_view.currentNode.id;
                    $cookies.lte = lte;
                    $cookies.active_file = lte;
                    $location.path('/explore/' + lte + '/');
                }
                if ((node_type == 'txt') && (network == 'GSM')){
                    $location.path('/table/'+$scope.tree_view.currentNode.label+'/' + $scope.tree_view.currentNode.label);
                }

                if (node_type == 'topology'){
                    $location.path('/table/'+$scope.tree_view.currentNode.file+'/topology');
                }
                if (node_type == '3g_neighbors_wcdma'){
                    $location.path('/table/'+$scope.tree_view.currentNode.file+'/threegneighbors');
                }
                if (node_type == 'rnd_wcdma'){
                    $location.path('/table/'+$scope.tree_view.currentNode.file+'/rnd_wcdma');
                }
                if (node_type == 'license'){
                    $location.path('/licenses/');
                }
                if (node_type == 'hardware'){
                    $location.path('/hardwares/');
                }
                if ((node_type == 'wncs') || (node_type == 'ncs') || (node_type == 'wmrr') || (node_type == 'mrr')) {
                    $location.path('/measurements/' + node_type + '/');
                }
                if ($scope.tree_view.currentNode.id == 'GSM'){
                    $cookies.network = 'GSM'
                }
                if ($scope.tree_view.currentNode.id == 'WCDMA'){
                    $cookies.network = 'WCDMA'
                }
                if ($scope.tree_view.currentNode.id == 'LTE'){
                    $cookies.network = 'LTE'
                }
            }
        }, false);
    }
]);
