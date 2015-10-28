L.Control.ToolBar = L.Control.extend({
    options: {
        position: 'topright',
        handler: {}
    },


    onAdd: function(map) {
        this.controlDiv = L.DomUtil.create('div', 'toolbar col-md-12');
        this.buttonsDiv = L.DomUtil.create('div', 'col-md-12', this.controlDiv);

        var fDiv = this.filterDiv = L.DomUtil.create('div', 'col-md-12 hide', this.controlDiv);
        this.selectDiv = L.DomUtil.create('div', 'col-md-6', this.filterDiv);
        var sFilter = this.select_filter = L.DomUtil.create('select', 'form-control', this.selectDiv);
        for (id in map.columns){
            var option = document.createElement("option");
            option.value = map.columns[id];
            option.text = map.columns[id];
            this.select_filter.appendChild(option);
        }
        this.select_filter.selectedIndex = '-1';

        this.valuesDiv = L.DomUtil.create('div', 'col-md-5', this.filterDiv);
        var sValues = this.select_values = L.DomUtil.create('select', 'form-control', this.valuesDiv);
        this.delFiltersDiv = L.DomUtil.create('div', 'col-md-1', this.filterDiv);
        this.resetFiltersButton = L.DomUtil.create('button', 'btn btn-danger', this.delFiltersDiv);
        this.resetFiltersButton.innerHTML = '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'


        this.rangeDiv = L.DomUtil.create('div', 'col-md-6', this.buttonsDiv);
        this.secondDiv = L.DomUtil.create('div', 'col-md-6', this.buttonsDiv);
        var sSize = this.sectorSize = L.DomUtil.create('input', 'range_sector', this.rangeDiv);
        this.sectorSize.setAttribute('type', 'range');
        this.sectorSize.setAttribute('min', -1);
        this.sectorSize.setAttribute('max', 1);
        this.sectorSize.setAttribute('value',0);
        this.sectorSize.setAttribute('step', '0.1');
        map.sectro_size = this.sectorSize;

        this.neigh3gButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.neigh3gButton.innerHTML = '3G-3G'

        this.flushNeighButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.flushNeighButton.innerHTML = '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'

        this.filterNeighButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.filterNeighButton.innerHTML = '<span class="glyphicon glyphicon-filter" aria-hidden="true"></span>'

        map.measure = this.measureButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.measureButton.innerHTML = '<img src="/static/measure-control.png">'

        map.zoomButton = this.zoomButton = L.DomUtil.create('button', 'btn btn-default', this.secondDiv);
        this.zoomButton.innerHTML = '<span class="glyphicon glyphicon-search" aria-hidden="true"></span>'

        var stop = L.DomEvent.stopPropagation;
        L.DomEvent
            .addListener(this.controlDiv, 'mousedown', L.DomEvent.stopPropagation)
            .addListener(this.controlDiv, 'click', L.DomEvent.stopPropagation)
            .addListener(this.controlDiv, 'click', L.DomEvent.preventDefault)
            .addListener(this.neigh3gButton, 'click', function () {
                map.show_neighbors_3g();
            })
            .addListener(this.flushNeighButton, 'click', function () {
                map.flush_neighbors();
            })
            .addListener(this.select_filter, 'change', function (e) {
                values = [];
                for (id in map.data){
                    var filter_val = map.data[id][e.target.value];
                    if (values.indexOf(filter_val) < 0){
                        values.push(filter_val);
                    }
                }

                while (sValues.firstChild) {
                    sValues.removeChild(sValues.firstChild);
                }

                var option = document.createElement("option");
                option.value = 'All';
                option.text = 'All';
                sValues.appendChild(option);

                for (id in values){
                    var option = document.createElement("option");
                    option.value = values[id];
                    option.text = values[id];
                    sValues.appendChild(option);
                }
                sValues.selectedIndex = '-1';

            })
            .addListener(this.select_values, 'change', function (event) {
                map.set_color_to_all_sectors('#03f');
                map.legend.reset();
                map.add_filter(sFilter.value, event.target.value);
            })
            .addListener(this.resetFiltersButton, 'click', function () {
                map.onResetFilter();
                sValues.selectedIndex = '-1';
                sFilter.selectedIndex = '-1';
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

