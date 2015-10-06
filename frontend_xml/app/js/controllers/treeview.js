var treeViewControllers = angular.module('treeViewControllers', []);

treeViewControllers.controller('TreeViewCtrl', ['$scope', '$http', '$cookies', 'activeProjectService', '$location',
    function ($scope, $http, $cookies, activeProjectService, $location) {
        $http.get('/data/treeview/' + $cookies.active_project).success(function(data){
            $scope.treedata = data;
        });

        $scope.$on('handleBroadcast', function() {
            console.log('reload');
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
                console.log($scope.tree_view.currentNode.link);
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

treeViewControllers.controller('menuCtrl', ['$scope', '$timeout', '$cookies', '$http', 'activeProjectService', 'activeFileService', '$location', '$rootScope',
    function ($scope, $timeout, $cookies, $http, activeProjectService, activeFileService, $location, $rootScope) {
        $scope.checked = false;

        $scope.onShowMenu = function(){
            $scope.checked = !$scope.checked
        }

        $scope.networks = ['GSM', 'WCDMA', 'LTE'];
        $scope.network = {};
        $scope.network.selected = 'GSM';
        $scope.root = {};

        $scope.treeOptions = {
            nodeChildren: "children",
            dirSelectable: true,
            injectClasses: {
                ul: "a1",
                li: "a2",
                liSelected: "a7",
                iExpanded: "a3",
                iCollapsed: "a4",
                iLeaf: "a5",
                label: "a6",
                labelSelected: "a8"
            }
        };
        $rootScope.$on('uploadFile', function(){
            console.log('TEST');
        });
        var loadData = function (){
            $http.get('/data/treeview/' + $cookies.active_project + '/').success(function(data){
                $scope.treedata = data;
            });
            //$timeout(loadData, 5000);
        };
        //$timeout(loadData, 0);
        loadData();
        function LoadTopology(network, root){
            $http.get('/data/topology_treeview/' + network +'/' + root + '/').success(function(data){
                $scope.topology_treedata = data;
            });

        }

        //LoadTopology('GSM', '');

        $scope.isCollapsed = false;
        $scope.width = 8;

        $scope.onClick = function(){
            $scope.isCollapsed = !$scope.isCollapsed;
            if ($scope.isCollapsed){
                $scope.width = 12;
            }
            else {
                $scope.width = 8;
            }
        };

        $scope.onChangeNetwork = function(data){
            $http.get('/data/get_topology_roots/' + $scope.network.selected +'/').success(function(data){
                $scope.roots = data;
                $scope.root.selected = $scope.roots[0];
                LoadTopology($scope.network.selected, $scope.root.selected);
            });
        };

        $scope.onChangeRoot = function(){
            LoadTopology($scope.network.selected, $scope.root.selected);
        };

        $scope.$on('handleBroadcast', function() {
            var project = activeProjectService.project;
            loadData(project);
        });

        $scope.showSelected = function(node){
            var file_type = node.type;
            var file_name = node.label;
            var link = node.link;
            activeFileService.setActiveFile(file_name, file_type);

            if (link) {
                $location.path(link);
            }

            if ((file_type == 'WCDMA RADIO OSS BULK CM XML FILE') || (file_type == 'WCDMA TRANSPORT OSS BULK CM XML FILE')){
                $location.path('/explore/' + file_name + '/');
            }
            if (file_type == 'GSM BSS CNA  OSS FILE'){
                $location.path('/explore/' + file_name + '/');
            }
        };
    }
]);
