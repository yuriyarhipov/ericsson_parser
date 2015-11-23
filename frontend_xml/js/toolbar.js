L.Control.ToolBar = L.Control.extend({
    options: {
        position: 'topright',
        handler: {}
    },

    onAdd: function(map) {
        this.controlDiv = L.DomUtil.create('div', 'toolbar col-md-12');
        this.buttonsDiv = L.DomUtil.create('div', 'col-md-12', this.controlDiv);
        map._appsDiv = L.DomUtil.create('div', 'col-md-12 hide', this.controlDiv);
        map._3gDiv = L.DomUtil.create('div', 'col-md-12 hide', this.controlDiv);

        var fDiv = this.filterDiv = L.DomUtil.create('div', 'col-md-12 hide', this.controlDiv);

        this.networkDiv = L.DomUtil.create('div', 'col-md-3', this.filterDiv);
        map._network_filter = L.DomUtil.create('select', 'form-control', this.networkDiv);
        this.gsm_option = L.DomUtil.create('option', '', map._network_filter);
        this.gsm_option.setAttribute('value', 'gsm');
        this.gsm_option.innerHTML='GSM';
        this.wcdma_option = L.DomUtil.create('option', '', map._network_filter);
        this.wcdma_option.setAttribute('value', 'wcdma');
        this.wcdma_option.innerHTML='WCDMA';
        this.lte_option = L.DomUtil.create('option', '', map._network_filter);
        this.lte_option.setAttribute('value', 'lte');
        this.lte_option.innerHTML='LTE';

        this.selectDiv = L.DomUtil.create('div', 'col-md-3', this.filterDiv);
        map._select_filter = L.DomUtil.create('select', 'form-control', this.selectDiv);

        this.valuesDiv = L.DomUtil.create('div', 'col-md-5', this.filterDiv);
        var sValues = this.select_values = L.DomUtil.create('select', 'form-control', this.valuesDiv);
        this.delFiltersDiv = L.DomUtil.create('div', 'col-md-1', this.filterDiv);
        this.resetFiltersButton = L.DomUtil.create('button', 'btn btn-danger', this.delFiltersDiv);
        this.resetFiltersButton.innerHTML = '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>';


        this.rangeDiv = L.DomUtil.create('div', 'col-md-6', this.buttonsDiv);
        this.secondDiv = L.DomUtil.create('div', 'col-md-6', this.buttonsDiv);
        var sSize = this.sectorSize = L.DomUtil.create('input', 'range_sector', this.rangeDiv);
        this.sectorSize.setAttribute('type', 'range');
        this.sectorSize.setAttribute('min', -1);
        this.sectorSize.setAttribute('max', 1);
        this.sectorSize.setAttribute('value',0);
        this.sectorSize.setAttribute('step', '0.1');
        map.sector_size = this.sectorSize;

        this.neigh2gButton = L.DomUtil.create('button', 'btn btn-default', map._appsDiv);
        this.neigh2gButton.innerHTML = '2G-2G';

        this.neigh3gButton = L.DomUtil.create('button', 'btn btn-default', map._appsDiv);
        this.neigh3gButton.innerHTML = '3G-3G';

        this.neigh4gButton = L.DomUtil.create('button', 'btn btn-default', map._appsDiv);
        this.neigh4gButton.innerHTML = '4G-4G';


        //pd section
        this.pdButton = L.DomUtil.create('button', 'btn btn-default', map._appsDiv);
        this.pdButton.innerHTML = 'PD';
        map._pdDiv = L.DomUtil.create('div', 'col-md-12 hide', this.controlDiv);
        this.pd_button_Div = L.DomUtil.create('div', 'col-md-2', map._pdDiv);
        this.closePdButton = L.DomUtil.create('button', 'btn btn-default', this.pd_button_Div);
        this.closePdButton.innerHTML = 'PD <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>';
        this.date_from_Div = L.DomUtil.create('div', 'col-md-5', map._pdDiv);
        this.date_to_Div = L.DomUtil.create('div', 'col-md-5', map._pdDiv);
        map._pd_date_from = L.DomUtil.create('select', 'form-control', this.date_from_Div);
        map._pd_date_to = L.DomUtil.create('select', 'form-control', this.date_to_Div);

        map._appButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        map._appButton.innerHTML = '<span class="glyphicon glyphicon-th" aria-hidden="true"></span>';

        this.close3gButton = L.DomUtil.create('button', 'btn btn-default', map._3gDiv);
        this.close3gButton.innerHTML = '3G <span class="glyphicon glyphicon-remove" aria-hidden="true"></span>';

        map._arrowLeftButton = L.DomUtil.create('button', 'btn btn-default', map._3gDiv);
        map._arrowLeftButton.innerHTML = '<span class="glyphicon glyphicon-arrow-left" aria-hidden="true"></span>';

        map._arrowRightButton = L.DomUtil.create('button', 'btn btn-default', map._3gDiv);
        map._arrowRightButton.innerHTML = '<span class="glyphicon glyphicon-arrow-right" aria-hidden="true"></span>';

        this.flushNeighButton = L.DomUtil.create('button', 'btn btn-default', map._3gDiv);
        this.flushNeighButton.innerHTML = '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>';

        this.filterNeighButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.filterNeighButton.innerHTML = '<span class="glyphicon glyphicon-filter" aria-hidden="true"></span>';

        map.measure = this.measureButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.measureButton.innerHTML = '<img src="/static/measure-control.png">';

        map.zoomButton = this.zoomButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.zoomButton.innerHTML = '<span class="glyphicon glyphicon-search" aria-hidden="true"></span>';

        var stop = L.DomEvent.stopPropagation;
        L.DomEvent
            .addListener(this.controlDiv, 'mousedown', L.DomEvent.stopPropagation)
            .addListener(this.controlDiv, 'click', L.DomEvent.stopPropagation)
            .addListener(this.controlDiv, 'click', L.DomEvent.preventDefault)
            .addListener(this.neigh3gButton, 'click', function () {
                L.DomUtil.addClass(map._appsDiv, 'hide');
                L.DomUtil.removeClass(map._3gDiv, 'hide');
                map._show_neighbors = !map._show_neighbors;
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        if (map._show_neighbors){
                            if (layer.options.network == 'wcdma'){
                                layer.setStyle({'color': 'grey'});
                            } else {
                                layer.setStyle({'color': 'black'});
                            }

                        } else {
                            layer.setStyle({'color': layer.options.default_color});
                        }
                    }
                });
            })
            .addListener(this.close3gButton, 'click', function () {
                L.DomUtil.addClass(map._3gDiv, 'hide');
                map._show_neighbors = false;
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        layer.setStyle({'color': layer.options.default_color});
                    }
                });
            })
            .addListener(this.flushNeighButton, 'click', function () {
                map.flush_neighbors();
            })
            .addListener(map._network_filter, 'change', function (e) {
                var network = e.target.value;
                map._network_filter.network = network;

                while (map._select_filter.firstChild) {
                    map._select_filter.removeChild(map._select_filter.firstChild);
                }
                if ((network) == 'gsm') {
                    map._gsm_data.columns.sort();
                    for (id in map._gsm_data.columns){
                        var option = document.createElement("option");
                        option.value = map._gsm_data.columns[id];
                        option.text = map._gsm_data.columns[id];
                        map._select_filter.appendChild(option);
                    }
                } else if ((network) == 'wcdma') {
                    map._wcdma_data.columns.sort();
                    for (id in map._wcdma_data.columns){
                        var option = document.createElement("option");
                        option.value = map._wcdma_data.columns[id];
                        option.text = map._wcdma_data.columns[id];
                        map._select_filter.appendChild(option);
                    }
                } else if ((network) == 'lte') {
                    map._lte_data.columns.sort();
                    for (id in map._lte_data.columns){
                        var option = document.createElement("option");
                        option.value = map._lte_data.columns[id];
                        option.text = map._lte_data.columns[id];
                        map._select_filter.appendChild(option);
                    }
                }
                map._select_filter.selectedIndex = '-1';
            })
            .addListener(map._select_filter, 'change', function (e) {
                values = [];
                var load_values = function(data, column){
                    for (id in data){
                        var val = data[id][e.target.value];
                        if (values.indexOf(val) < 0){
                            values.push(val);
                        }
                    }
                };
                if ((map._network_filter.network == 'gsm') && (map._gsm_data.columns.indexOf(e.target.value) >= 0)){
                    load_values(map._gsm_data.data, e.target.value);
                }

                if ((map._network_filter.network == 'wcdma') && (map._wcdma_data.columns.indexOf(e.target.value) >= 0)){
                    load_values(map._wcdma_data.data, e.target.value);
                }
                if ((map._network_filter.network == 'lte') && (map._lte_data.columns.indexOf(e.target.value) >= 0)){
                    load_values(map._lte_data.data, e.target.value);
                }

                if (!isNaN(values[0])){
                    values.sort(function(a, b){return a - b});
                } else {
                    values.sort();
                }

                while (sValues.firstChild) {
                    sValues.removeChild(sValues.firstChild);
                }

                var option = document.createElement("option");
                option.value = 'All';
                option.text = 'All';
                sValues.appendChild(option);

                for (id in values){
                    if (values[id]){
                        var option = document.createElement("option");
                        option.value = values[id];
                        option.text = values[id];
                        sValues.appendChild(option);
                    }
                }
                sValues.selectedIndex = '-1';

            })
            .addListener(this.select_values, 'change', function (event) {
                map._add_filter(map._network_filter.network, map._select_filter.value, event.target.value);
            })
            .addListener(this.resetFiltersButton, 'click', function () {
                map._legend.reset_legend();
                sValues.selectedIndex = '-1';
                map._select_filter.selectedIndex = '-1';
            })
            .addListener(this.sectorSize, 'change', function (event) {

                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        var radius = layer.options.current_base_radius;
                        var new_radius = radius + radius * parseFloat(event.target.value);
                        zkf = ((layer.options.zoom-10)*-12+100)/100
                        var current_size = new_radius * (11-parseFloat(1))/10;
                        var new_s = zkf*current_size;
                        layer.setRadius(new_s);
                    }
                });
            })
            .addListener(this.filterNeighButton, 'click', function () {
                if (L.DomUtil.hasClass(fDiv, 'hide')){
                    L.DomUtil.removeClass(fDiv, 'hide');
                } else {
                    L.DomUtil.addClass(fDiv, 'hide');
                }
            })
            .addListener(this.pdButton, 'click', function () {
                map._show_pd = !map._show_pd;
                L.DomUtil.addClass(map._appsDiv, 'hide');
                L.DomUtil.removeClass(map._pdDiv, 'hide');
                map._init_pd();

            })
            .addListener(this.closePdButton, 'click', function () {
                map._show_pd = false;
                for (i in map._pd){
                    map._pd[i].removeFrom(map);
                }
                L.DomUtil.addClass(map._pdDiv, 'hide');
                L.DomUtil.removeClass(map._appsDiv, 'hide');
            })
            .addListener(map._appButton, 'click', function () {
                if (L.DomUtil.hasClass(map._appsDiv, 'hide')){
                    L.DomUtil.removeClass(map._appsDiv, 'hide');
                } else {
                    L.DomUtil.addClass(map._appsDiv, 'hide');
                }
            })
            .addListener(map._arrowLeftButton, 'click', function(){
                var utrancells = [];
                for (i in map._wcdma_data.data){
                    utrancells.push(map._wcdma_data.data[i].Utrancell);
                }
                utrancells.sort();
                var idx = utrancells.indexOf(map._current_sector.options.sector.Utrancell);
                if (idx == 0){
                    idx = utrancells.length - 1;
                } else {
                    idx = idx - 1;
                }
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        if (layer.options.sector.Utrancell == utrancells[idx]){
                            layer.show_neighbours();
                            map.select_sector(layer);
                        }
                    }
                });
            })
            .addListener(map._arrowRightButton, 'click', function(){
                var utrancells = [];
                for (i in map._wcdma_data.data){
                    utrancells.push(map._wcdma_data.data[i].Utrancell);
                }
                utrancells.sort();
                var idx = utrancells.indexOf(map._current_sector.options.sector.Utrancell);
                idx = idx + 1;
                if (idx == utrancells.length){
                    idx = 0;
                }
                map.eachLayer(function (layer) {
                    if (layer.options.sector) {
                        if (layer.options.sector.Utrancell == utrancells[idx]){
                            layer.show_neighbours();
                            map.select_sector(layer);
                        }
                    }
                });
            })


        return this.controlDiv;
    }
});

L.Map.addInitHook(function () {
    if (this.options.toolBar) {
        this.toolBar = L.Control.toolBar().addTo(this);
    }
});

L.Control.toolBar = function (options) {
    return new L.Control.ToolBar(options);
};

