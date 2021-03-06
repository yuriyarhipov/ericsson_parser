var activeFileModule = angular.module('activeFileModule', []);

activeFileModule.factory('activeFileService', function($rootScope, $cookies) {
    var activeFile = {};

    activeFile.wcdma = $cookies.get('wcdma');
    activeFile.lte = $cookies.get('lte');
    activeFile.gsm = $cookies.get('gsm');

    activeFile.setActiveFile = function(filename, file_type) {
        if ((file_type == 'WCDMA RADIO OSS BULK CM XML FILE') || (file_type == 'WCDMA TRANSPORT OSS BULK CM XML FILE')){
            $cookies.get('wcdma') = filename;
        }
        if ((file_type == 'LTE RADIO eNodeB BULK CM XML FILE') || (file_type == 'LTE TRANSPORT eNodeB BULK CM XML FILE')){
            $cookies.get('lte') = filename;
        }
        if (file_type == 'GSM BSS CNA  OSS FILE'){
            $cookies.get('gsm') = filename;
        }

        this.broadcastItem();
    };

    activeFile.broadcastItem = function() {
        $rootScope.$broadcast('activeFileBroadcast');
    };

    return activeFile;
});

