var activeProjectModule = angular.module('activeProjectModule', []);

activeProjectModule.factory('activeProjectService', function($rootScope, $cookies) {
    var activeProject = {};

    activeProject.project = $cookies.active_project;

    activeProject.setProject = function(msg) {
        console.log(msg);
        this.project = msg;
        $cookies.put('active_project', msg);
        this.broadcastItem();
    };

    activeProject.broadcastItem = function() {
        $rootScope.$broadcast('handleBroadcast');
    };

    return activeProject;
});

