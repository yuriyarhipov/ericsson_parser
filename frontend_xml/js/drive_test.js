L.Control.DriveTest = L.Control.extend({
    options: {
        position: 'topleft',
        handler: {}
    },

    onAdd: function(map) {
        this.drive_test_div = L.DomUtil.create('div', 'drive_test main_drive_test');
        this.ms_main_div = L.DomUtil.create('div', 'col-md-12', this.drive_test_div);
        var ms_header = L.DomUtil.create('div', 'col-md-12', this.ms_main_div);
        ms_header.innerHTML = '<h5>Mobile Stations</h5>'
        this.kpi_main_div = L.DomUtil.create('div', 'col-md-12', this.drive_test_div);
        var kpi_header = L.DomUtil.create('div', 'col-md-12', this.kpi_main_div);
        kpi_header.innerHTML = '<h5>Parameters:</h5>'
        return this.drive_test_div;
    },
    set_mobile_stations: function(map, ms){
        var ms_div = L.DomUtil.create('div', 'col-md-12', this.ms_main_div);
        ms_select = L.DomUtil.create('select', 'form-control', ms_div);
        for (i in ms){
            var ms_option = L.DomUtil.create('option', '', ms_select);
            ms_option.setAttribute('value', ms[i]);
            ms_option.innerHTML=ms[i];
        }

    },
    set_kpi: function(map, kpi){
        var kpi_div = L.DomUtil.create('div', 'col-md-12', this.kpi_main_div);
        kpi_select = L.DomUtil.create('select', 'form-control', kpi_div);
        for (i in kpi){
            var kpi_option = L.DomUtil.create('option', '', kpi_select);
            kpi_option.setAttribute('value', kpi[i]);
            kpi_option.innerHTML=kpi[i];
        }
    }
});

L.Map.addInitHook(function () {
    if (this.options.driveTest) {
        this.driveTest = L.Control.driveTest().addTo(this);
    }
});

L.Control.driveTest = function (options) {
    return new L.Control.DriveTest(options);
};

