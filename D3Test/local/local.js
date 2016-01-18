$(document).ready(function(){

	// $('#left-tab a').click(function (e) {
	//   e.preventDefault()
	//   $('this').tab('show')
	// })

	var line, dragging, x, y;

function displayNetwork(){
	
	var diameter = 960;

	var tree = d3.layout.tree()
	    .size([360, diameter / 2 - 120])
	    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

	var diagonal = d3.svg.diagonal.radial()
	    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });


    var select = d3.select("#view-wrapper");
    select.selectAll("svg").remove();
	var svg = select.append("svg")
	    .attr("width", diameter)
	    .attr("height", diameter - 150)
	  .append("g")
	    .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

	d3.json("data/flare.json", function(error, root) {
	  if (error) throw error;

	  var nodes = tree.nodes(root),
	      links = tree.links(nodes);

	  var link = svg.selectAll(".link")
	      .data(links)
	    .enter().append("path")
	      .attr("class", "link")
	      .attr("d", diagonal);

	  var node = svg.selectAll(".node")
	      .data(nodes)
	    .enter().append("g")
	      .attr("class", "node")
	      .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; })

	  node.append("circle")
	      .attr("r", 4.5);

	  node.append("text")
	      .attr("dy", ".31em")
	      .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
	      .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
	      .text(function(d) { return d.name; });
	});

	d3.select(self.frameElement).style("height", diameter - 150 + "px");

}

function displayParallel(){

	// Define the window width, height and margins
	var margin = {top: 30, right: 10, bottom: 10, left: 10},
	    width = 960 - margin.left - margin.right,
	    height = 500 - margin.top - margin.bottom;

	// Init axis
	x = d3.scale.ordinal().rangePoints([0, width], 1)
	y = {}
	    
	dragging = {};

	// Init 
	line = d3.svg.line()
	
	var axis = d3.svg.axis().orient("left"),
	    background,
	    foreground;

	// Create the window and the g container
	var select = d3.select("#view-wrapper");
	select.selectAll("svg").remove();
	var svg = select.append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


	// Calling the data
	d3.csv("data/test_pcap.csv", function(error, pcap) {


		// Slice data for more visiblity
		cars = pcap.slice(0, 300);
		
	  // Extract the list of dimensions and create a scale for each.
	  x.domain(dimensions = d3.keys(cars[0]).filter(function(d) {

		// Create ordinals dimensions
	    if(d.substr(0,4).toLowerCase() == "sour" || d.substr(0,4).toLowerCase() == "dest" || d.substr(0,4).toLowerCase() == "prot" ){
	    	return y[d] = d3.scale.ordinal()
	    	.domain(d3.values(cars).map(function(obj){return obj[d];}))
	    	.rangePoints([height, 0]);

	    // Create linear dimensions
	    }else if(d.substr(0,3).toLowerCase() != "no." && d.substr(0,4).toLowerCase() != "time" && d.substr(0,4).toLowerCase() != "info"){
			return y[d] = d3.scale.linear()
	          .domain(d3.extent(cars, function(p) { return +p[d]; }))
	          .range([height, 0]);
	    }
		  
	  }));

	  // Add grey background lines for context.
	  background = svg.append("g")
	      .attr("class", "background")
	    .selectAll("path")
	      .data(cars)
	    .enter().append("path")
	      .attr("d", path);

	  // Add blue foreground lines for focus.
	  foreground = svg.append("g")
	      .attr("class", "foreground")
	    .selectAll("path")
	      .data(cars)
	    .enter().append("path")
	      .attr("d", path);

	  // Add a group element for each dimension.
	  var g = svg.selectAll(".dimension")
	      .data(dimensions)
	    .enter().append("g")
	      .attr("class", "dimension")
	      .attr("transform", function(d) { return "translate(" + x(d) + ")"; })
	      .call(d3.behavior.drag()
	        .origin(function(d) { return {x: x(d)}; })
	        .on("dragstart", function(d) {
	          dragging[d] = x(d);
	          background.attr("visibility", "hidden");
	        })
	        .on("drag", function(d) {
	          dragging[d] = Math.min(width, Math.max(0, d3.event.x));
	          foreground.attr("d", path);
	          dimensions.sort(function(a, b) { return position(a) - position(b); });
	          x.domain(dimensions);
	          g.attr("transform", function(d) { return "translate(" + position(d) + ")"; })
	        })
	        .on("dragend", function(d) {
	          delete dragging[d];
	          transition(d3.select(this)).attr("transform", "translate(" + x(d) + ")");
	          transition(foreground).attr("d", path);
	          background
	              .attr("d", path)
	            .transition()
	              .delay(500)
	              .duration(0)
	              .attr("visibility", null);
	        }));

	  // Add an axis and title.
	  g.append("g")
	      .attr("class", "axis")
	      .each(function(d) { d3.select(this).call(axis.scale(y[d])); })
	    .append("text")
	      .style("text-anchor", "middle")
	      .attr("y", -9)
	      .text(function(d) { return d; });

	  // Add and store a brush for each axis.
	  g.append("g")
	      .attr("class", "brush")
	      .each(function(d) {
	        d3.select(this).call(y[d].brush = d3.svg.brush().y(y[d]).on("brushstart", brushstart).on("brush", brush));
	      })
	    .selectAll("rect")
	      .attr("x", -8)
	      .attr("width", 16);
	});

}

function position(d) {
  var v = dragging[d];
  return v == null ? x(d) : v;
}

function transition(g) {
  return g.transition().duration(500);
}

// Returns the path for a given data point.
function path(d) {
  return line(dimensions.map(function(p) { return [position(p), y[p](d[p])]; }));
}

function brushstart() {
  d3.event.sourceEvent.stopPropagation();
}

// Handles a brush event, toggling the display of foreground lines.
function brush() {
  var actives = dimensions.filter(function(p) { return !y[p].brush.empty(); }),
      extents = actives.map(function(p) { return y[p].brush.extent(); });
  foreground.style("display", function(d) {
    return actives.every(function(p, i) {
      return extents[i][0] <= d[p] && d[p] <= extents[i][1];
    }) ? null : "none";
  });
}

$("#parallel-btn").on("click", function(e){
	displayParallel();
})

$("#network-btn").on("click", function(e){
	displayNetwork();
})

})
