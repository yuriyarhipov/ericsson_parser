var uploadFileModule = angular.module('uploadFileModule', []);

uploadFileModule.factory('uploadFileService', function($rootScope) {
    var uploadFile = {};
    uploadFile.onUpload = function() {        
        $rootScope.$broadcast('uploadFile');
    };
    return uploadFile
});
