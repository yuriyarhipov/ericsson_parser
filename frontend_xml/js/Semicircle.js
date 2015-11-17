/**
 * Semicircle extension for L.Circle.
 * Jan Pieter Waagmeester <jieter@jieter.nl>
 */

(function (L) {

	var DEG_TO_RAD = Math.PI / 180;

	// make sure 0 degrees is up (North) and convert to radians.
	function fixAngle (angle) {
		return (angle - 90) * DEG_TO_RAD;
	}

	L.Circle = L.Circle.extend({
		options: {
			startAngle: 0,
			stopAngle: 359.9999
		},

		startAngle: function () {
			return fixAngle(this.options.startAngle);
		},
		stopAngle: function () {
			return fixAngle(this.options.stopAngle);
		},

		// rotate point x,y+r around x,y with angle.
		rotated: function (angle, r) {
			return this._point.add(
				L.point(Math.cos(angle), Math.sin(angle)).multiplyBy(r)
			).round();
		},

		setStartAngle: function (angle) {
			this.options.startAngle = angle;
			return this.redraw();
		},
		setStopAngle: function (angle) {
			this.options.stopAngle = angle;
			return this.redraw();
		},
		setDirection: function (direction, degrees, inner_radius) {
			if (degrees === undefined) {
				degrees = 10;
			}
			if (inner_radius === undefined) {
				inner_radius = 0;
			}
			this.options.inner_radius = inner_radius;
			this.options.startAngle = direction - (degrees / 2);
			this.options.stopAngle = direction + (degrees / 2);

			return this.redraw();
		}
	});

	// save original getPathString function to draw a full circle.
	var originalUpdateCircle = L.SVG.prototype._updateCircle;

	L.SVG.include({
		_updateCircle: function (layer) {
			// If we want a circle, we use the original function
			if (layer.options.startAngle === 0 && layer.options.stopAngle > 359) {
				return originalUpdateCircle.call(this, layer);
			}

			var center = layer._point,
			r = layer._radius;

			var t = this._annularSector({
  				centerX:center.x, centerY:center.y,
  				startDegrees:layer.options.startAngle, endDegrees:layer.options.stopAngle,
  				innerRadius:layer.options.inner_radius, outerRadius:r
			})

			this._setPath(layer, t);
		},

		_annularSector: function (options){ // thanks a lot http://stackoverflow.com/a/11484522
  			var opts = optionsWithDefaults(options);
  			var p = [ // points
    			[opts.cx + opts.r2*Math.cos(opts.startRadians),
     				opts.cy + opts.r2*Math.sin(opts.startRadians)],
    			[opts.cx + opts.r2*Math.cos(opts.closeRadians),
     				opts.cy + opts.r2*Math.sin(opts.closeRadians)],
    			[opts.cx + opts.r1*Math.cos(opts.closeRadians),
     				opts.cy + opts.r1*Math.sin(opts.closeRadians)],
    			[opts.cx + opts.r1*Math.cos(opts.startRadians),
     				opts.cy + opts.r1*Math.sin(opts.startRadians)],
  				];

  			var angleDiff = opts.closeRadians - opts.startRadians;
  			var largeArc = (angleDiff % (Math.PI*2)) > Math.PI ? 1 : 0;
  			var cmds = [];
  			cmds.push("M"+p[0].join());                                // Move to P0
  			cmds.push("A"+[opts.r2,opts.r2,0,largeArc,1,p[1]].join()); // Arc to  P1
  			cmds.push("L"+p[2].join());                                // Line to P2
  			cmds.push("A"+[opts.r1,opts.r1,0,largeArc,0,p[3]].join()); // Arc to  P3
  			cmds.push("z");                                // Close path (Line to P0)
  			return cmds.join(' ');

  			function optionsWithDefaults(o){
    		// Create a new object so that we don't mutate the original
    			var o2 = {
	      			cx           : o.centerX || 0,
    	  			cy           : o.centerY || 0,
      				startRadians : (o.startDegrees || 0) * Math.PI/180,
      				closeRadians : (o.endDegrees   || 0) * Math.PI/180,
	    		};

	    		var t = o.thickness!==undefined ? o.thickness : 100;
    			if (o.innerRadius!==undefined)      o2.r1 = o.innerRadius;
    			else if (o.outerRadius!==undefined) o2.r1 = o.outerRadius - t;
    			else                                o2.r1 = 200           - t;
	    		if (o.outerRadius!==undefined)      o2.r2 = o.outerRadius;
    			else                                o2.r2 = o2.r1         + t;

	   		 	if (o2.r1<0) o2.r1 = 0;
    			if (o2.r2<0) o2.r2 = 0;

    			return o2;
  			}
		}
	})
})(L);
