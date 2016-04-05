var xmlControllers = angular.module('xmlControllers', []);

xmlControllers.controller('ProjectsCtrl', ['$scope', '$http', 'activeProjectService', '$cookies', '$location',
    function ($scope, $http, activeProjectService, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.setActiveProject = function(project){
            $scope.activeWCDMA = 'red';
            $scope.activeLTE = 'red';
            $scope.activeGSM = 'red';
            if ('gsm' in $cookies){
                delete $cookies['gsm'];
            }
            if ('wcdma' in $cookies){
                delete $cookies['wcdma'];
            }
            if ('lte' in $cookies){
                delete $cookies['lte'];
            }
            activeProjectService.setProject(project);
        };

        $http.get('/data/projects/').success(function(data) {
            $scope.projects = data;
        });

        $scope.onDeleteProject = function(project_name){
            $http.post('/data/delete_projects/' + project_name + '/').success(function(data) {
                $scope.projects = data;
            });
        };
  }]);

xmlControllers.controller('ActiveProjectCtrl', ['$scope', '$cookies', 'activeProjectService', '$location',
    function($scope, $cookies, activeProjectService, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.activeProject = $cookies.get('active_project');
        $scope.activeWCDMA = $cookies.get('wcdma');
        if (!$cookies.get('active_project')){
            $location.path('/projects/');
        }
        $scope.activeWCDMA = 'red';
        $scope.activeLTE = 'red';
        $scope.activeGSM = 'red';

        if ('gsm' in $cookies){
            $scope.activeGSM = 'green';
        }
        if ('lte' in $cookies){
            $scope.activeLTE = 'green';
        }
        if ('wcdma' in $cookies){
            $scope.activeWCDMA = 'green';
        }

        $scope.$on('handleBroadcast', function() {
            $scope.activeProject = activeProjectService.project;
            $scope.activeWCDMA = 'red';
        $scope.activeLTE = 'red';
        $scope.activeGSM = 'red';

        if ('gsm' in $cookies){
            $scope.activeGSM = 'green';
        }
        if ('lte' in $cookies){
            $scope.activeLTE = 'green';
        }
        if ('wcdma' in $cookies){
            $scope.activeWCDMA = 'green';
        }
        });

        $scope.$on('activeFileBroadcast', function() {
        $scope.activeWCDMA = 'red';
        $scope.activeLTE = 'red';
        $scope.activeGSM = 'red';

        if ('gsm' in $cookies){
            $scope.activeGSM = 'green';
        }
        if ('lte' in $cookies){
            $scope.activeLTE = 'green';
        }
        if ('wcdma' in $cookies){
            $scope.activeWCDMA = 'green';
        }
        });
  }]);

xmlControllers.controller('AddProjectCtrl', ['$scope', '$http', '$location', 'activeProjectService', '$cookies', '$location',
    function ($scope, $http, $location, activeProjectService, $cookies, $location) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }
        $scope.project_data = {};
        $scope.processForm = function(){
            $http.post('/data/save_project/', $.param($scope.project_data)).success(function(){
                activeProjectService.setProject($scope.project_data['project_name']);
                $location.path('/projects');
            });

		};
  }]);


xmlControllers.controller('authCtrl', ['$scope', '$http', '$cookies', '$location', 'authService',
    function ($scope, $http, $cookies, $location, authService) {
        $scope.onLogin = function(login, pass){
             $http.post('/data/login/', $.param({'login': login, 'pass': pass})).success(function(data){
                if (data.status == 'ok'){
                    $cookies.put('is_auth', true);
                    $cookies.put('username', login);
                    $location.path('/projects');
                    authService.setAuth(true, login);
                } else {
                    $cookies.put('is_auth', false);
                    authService.setAuth(false, '');
                }

            });
        };
}]);

xmlControllers.controller('changePassCtrl', ['$scope', '$http', '$cookies', '$location', 'authService', '$routeParams', 'Flash',
    function ($scope, $http, $cookies, $location, authService, $routeParams, Flash) {
        var user_name = $routeParams.user_name;
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }

        $scope.btn_disabled = true;
        $scope.change_pass = function(){
            if (($scope.new_pass == $scope.confirm_pass) && ($scope.new_pass.length > 0) && ($scope.confirm_pass.length > 0)){
                $scope.btn_disabled = false;
            } else {
                $scope.btn_disabled = true;
            }
        };
        $scope.onSave = function(old_pass, new_pass){
            $http.post('/data/change_pass/', $.param({'old_pass': old_pass, 'new_pass': new_pass, 'user_name': user_name })).success(function(data){
                if (data.status == 'ok'){
                    Flash.create('success', 'Password changed');
                } else {
                    Flash.create('danger', 'Error');
                }
            });
        };
}]);

xmlControllers.factory('authService', function($rootScope, $cookies) {
    var status = {};
    status.is_auth = $cookies.get('is_auth');
    status.username = $cookies.get('username');
    status.setAuth = function(is_auth, username) {
        $cookies.put('is_auth', is_auth);
        status.is_auth = is_auth;
        status.username = username;
        this.broadcastItem();
    };


    status.broadcastItem = function() {
        $rootScope.$broadcast('authBroadcast');
    };
    return status;
});

xmlControllers.controller('mainMenuCtrl', ['$scope', 'authService', 'activeProjectService', '$location', '$cookies',
    function ($scope, authService, activeProjectService, $location, $cookies) {
        if ($cookies.get('is_auth') == 'true'){
            $scope.username = authService.username;
            $scope.project_name = activeProjectService.project;
            $scope.show_menu = true;
        } else {
            $scope.show_menu = false;
        }

        $scope.$on('authBroadcast', function() {
            if ($cookies.get('is_auth') == 'true'){
                $scope.username = authService.username;
                $scope.show_menu = true;
            } else {
                $scope.show_menu = false;
            }
        });

        $scope.$on('handleBroadcast', function() {
            $scope.project_name = activeProjectService.project;
        });

        $scope.onMenuClick = function(url,e){
            if (url == '/logout'){
                url = '/login';
                $cookies.put('is_auth', false);
                authService.setAuth(false, '');
            }
            $location.path(url);
        };
}]);

xmlControllers.controller('changelogCtrl', ['$scope', 'authService','$location', '$cookies', '$http', 'usSpinnerService',
    function ($scope, authService, $location, $cookies, $http, usSpinnerService) {
        if ($cookies.get('is_auth') != 'true'){
            $location.path('/login')
        }

        $scope.table_config = {
            columnDefs: [
                { field: 'mo' },
                { field: 'rnc' },
                { field: 'site'},
                { field: 'utrancell' },
                { field: 'parameter' },
                { field: 'new_value' },
                { field: 'old_value' },
                { field: 'date' }
            ],
            enableGridMenu: true,
            enableSelectAll: true,
            enableFiltering: true,
            flatEntityAccess: true,
            showGridFooter: true,
        }

        $http.get('/data/changelog/').success(function(data){
            $scope.table_config.data = data;
            usSpinnerService.stop('spinner_table');
        });

}]);
