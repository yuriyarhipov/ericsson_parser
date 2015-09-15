var uploadFileModule = angular.module('uploadFileModule', []);

uploadFileModule.factory('uploadFileService', function($rootScope) {
    var uploadFile = {};
    uploadFile.onUpload = function() {
        console.log('TEST send');
        $rootScope.$broadcast('uploadFile');
    };
    return uploadFile
});