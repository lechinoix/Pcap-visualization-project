$(document).ready(function(){



/* ============================

	Views with D3.js

===============================*/


// Network View

var select, svg, diameter, tree, diagonal, nodes, node, link, links;

function displayNetwork(){
	
	diameter = 960;

	tree = d3.layout.tree()
	    .size([360, diameter / 2 - 120])
	    .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

	diagonal = d3.svg.diagonal.radial()
	    .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });


    select = d3.select("#view-wrapper");
    select.selectAll("svg").remove();
	svg = select.append("svg")
	    .attr("width", diameter)
	    .attr("height", diameter - 150)
	  .append("g")
	    .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");

	d3.json("static/parsed/flare.json", function(error, root) {
	  if (error) throw error;

	  nodes = tree.nodes(root),
	  links = tree.links(nodes);

	  link = svg.selectAll(".link")
	      .data(links)
	    .enter().append("path")
	      .attr("class", "link")
	      .attr("d", diagonal);

	  node = svg.selectAll(".node")
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

// Parallel View

var line, dragging, x, y, foreground, background, axis, margin, height, width, g;

function displayParallel(){

	// Define the window width, height and margins
	margin = {top: 30, right: 10, bottom: 10, left: 10},
	width = 960 - margin.left - margin.right,
	height = 500 - margin.top - margin.bottom;

	// Init axis
	x = d3.scale.ordinal().rangePoints([0, width], 1)
	y = {}
	    
	dragging = {};

	// Init 
	line = d3.svg.line()
	
	axis = d3.svg.axis().orient("left"),	    

	// Create the window and the g container
	select = d3.select("#view-wrapper");
	select.selectAll("svg").remove();
	svg = select.append("svg")
	    .attr("width", width + margin.left + margin.right)
	    .attr("height", height + margin.top + margin.bottom)
	  .append("g")
	    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


	// Calling the data
	d3.json("static/parsed/sessions.json", function(error, pcap) {


		// Slice data for more visiblity
		sessions = pcap.slice(0, 300);
		
	  // Extract the list of dimensions and create a scale for each.
	  x.domain(dimensions = d3.keys(sessions[0]).filter(function(d) {

		// Create ordinals dimensions
	    if(d.toLowerCase() != "id" && d.substr(0,4).toLowerCase() != "port" ){
	    	return y[d] = d3.scale.ordinal()
	    	.domain(d3.values(sessions).map(function(obj){return obj[d];}))
	    	.rangePoints([height, 0]);

	    // Create linear dimensions
	     }else if(d.substr(0,3).toLowerCase() != "id"){
			return y[d] = d3.scale.linear()
	          .domain(d3.extent(sessions, function(p) { return +p[d]; }))
	          .range([height, 0]);
	    }
		  
	  }));

	  // Add grey background lines for context.
	  background = svg.append("g")
	      .attr("class", "background")
	    .selectAll("path")
	      .data(sessions)
	    .enter().append("path")
	      .attr("d", path);

	  // Add blue foreground lines for focus.
	  foreground = svg.append("g")
	      .attr("class", "foreground")
	    .selectAll("path")
	      .data(sessions)
	    .enter().append("path")
	      .attr("d", path);

	  // Add a group element for each dimension.
	  g = svg.selectAll(".dimension")
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
	  
	  // Update side bar
	  function updateSidebar(el, i, array){
		  $('.left-bar .tab-content #hosts table tbody').append("<tr>" +
			  		"<td>" + i + "</td>" +
			  		"<td>" + el.address + "</td>" +
			  		"<td>" + el.os + "</td>" +
			  		"<td></td>" +
			  		"</tr>")
	  }
	  
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

/* ============================

	Display the datas and graphs

===============================*/


$("#parallel-btn").on("click", function(e){
	displayParallel();
	
})

$("#network-btn").on("click", function(e){
	displayNetwork();
})

$("#upload-form").on('submit', function(e){
	e.preventDefault()
	
	data = $(this).serialize()
	
	$(".status-container").html('Processing pcap parsing...')
	
	$.post(url_upload, data, function(response){

		if('success' in response){
			$(".modal-body .status-container").html(response['success'])
		}else{
			$(".modal-body .status-container").html(response['error'])
		}
	})
})

displayParallel();

})
