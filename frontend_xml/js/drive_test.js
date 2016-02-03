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
        this.legend_main_div = L.DomUtil.create('div', 'col-md-12', this.drive_test_div);
        return this.drive_test_div;
    },
    set_mobile_stations: function(map, ms){
        var ms_div = L.DomUtil.create('div', 'col-md-12', this.ms_main_div);
        var ms_select = L.DomUtil.create('select', 'form-control', ms_div);
        for (i in ms){
            var ms_option = L.DomUtil.create('option', '', ms_select);
            ms_option.setAttribute('value', ms[i]);
            ms_option.innerHTML=ms[i];
        }
        L.DomEvent
            .addListener(this.drive_test_div, 'mousedown', L.DomEvent.stopPropagation)
            .addListener(this.drive_test_div, 'click', L.DomEvent.stopPropagation)
            .addListener(this.drive_test_div, 'click', L.DomEvent.preventDefault)
            .addListener(ms_select, 'change', function (e) {
                map._drive_test._ms = e.target.value;
                map.refresh_drive_test();
            })

    },


    set_parameters: function(map, kpi){
        var kpi_div = L.DomUtil.create('div', 'col-md-12', this.kpi_main_div);
        kpi_select = L.DomUtil.create('select', 'form-control', kpi_div);
        for (i in kpi){
            var kpi_option = L.DomUtil.create('option', '', kpi_select);
            kpi_option.setAttribute('value', kpi[i]);
            kpi_option.innerHTML=kpi[i];
        };
        L.DomEvent
            .addListener(kpi_div, 'mousedown', L.DomEvent.stopPropagation)
            .addListener(kpi_div, 'click', L.DomEvent.stopPropagation)
            .addListener(kpi_div, 'click', L.DomEvent.preventDefault)
            .addListener(kpi_select, 'change', function (e) {
                map._drive_test._parameter = e.target.value;
                map.refresh_drive_test();
            })
    },
    set_legends: function(map, legends){
        var legend_div = L.DomUtil.create('div', 'col-md-12', this.legend_main_div);
        legend_select = L.DomUtil.create('select', 'form-control', legend_div);
        for (i in legends){
            var legend_option = L.DomUtil.create('option', '', legend_select);
            legend_option.setAttribute('value', legends[i]);
            legend_option.innerHTML=legends[i];
        };
        L.DomEvent
            .addListener(legend_div, 'mousedown', L.DomEvent.stopPropagation)
            .addListener(legend_div, 'click', L.DomEvent.stopPropagation)
            .addListener(legend_div, 'click', L.DomEvent.preventDefault)
            .addListener(legend_select, 'change', function (e) {
                map._drive_test._legend = e.target.value;
                map.refresh_drive_test()
            })
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

