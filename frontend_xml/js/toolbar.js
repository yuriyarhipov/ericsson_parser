L.Control.ToolBar = L.Control.extend({
    options: {
        position: 'topright',
        handler: {}
    },

    onAdd: function(map) {
        this.controlDiv = L.DomUtil.create('div', 'toolbar');

        this.neigh3gButton = L.DomUtil.create('button', 'btn btn-default', this.controlDiv);
        this.neigh3gButton.innerHTML = '3G-3G'

        this.flushNeighButton = L.DomUtil.create('button', 'btn btn-default', this.controlDiv);
        this.flushNeighButton.innerHTML = '<span class="glyphicon glyphicon-trash" aria-hidden="true"></span>'

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
        return this.controlDiv;
    }
});

L.Map.addInitHook(function () {
    if (this.options.measureControl) {
        this.measureControl = L.Control.measureControl().addTo(this);
    }
});

L.Control.toolBar = function (options) {
    return new L.Control.ToolBar(options);
};

