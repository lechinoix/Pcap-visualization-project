$(document).ready(function(){


/* ============================

	Initiating socket

===============================*/

	
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.on('connect', function() {
        
    });
    
    // Catching sessions on first load
    var sessions = loadedSessions;
	
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

var line, dragging, x, y, foreground, background, axis, margin, height, width, g, slicedData;

function displayParallel(data){
	

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

	slicedData = data.slice(0, 300);	
	
  // Extract the list of dimensions and create a scale for each.
  x.domain(dimensions = d3.keys(slicedData[0]).filter(function(d) {

	// Create ordinals dimensions
    if(d.toLowerCase() != "id" && d.substr(0,4).toLowerCase() != "port" && d.substr(0,4).toLowerCase() != "nomb" ){
    	return y[d] = d3.scale.ordinal()
    	.domain(d3.values(slicedData).map(function(obj){return obj[d];}))
    	.rangePoints([height, 0]);

    // Create linear dimensions
     }else if(d.substr(0,3).toLowerCase() != "id"){
		return y[d] = d3.scale.linear()
          .domain(d3.extent(slicedData, function(p) { return +p[d]; }))
          .range([height, 0]);
    }
	  
  }));

  // Add grey background lines for context.
  background = svg.append("g")
      .attr("class", "background")
    .selectAll("path")
      .data(slicedData)
    .enter().append("path")
      .attr("d", path);

  // Add blue foreground lines for focus.
  foreground = svg.append("g")
      .attr("class", "foreground")
    .selectAll("path")
      .data(slicedData)
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
    	if(d[p].toString().split('.').length > 3){
    		return extents[i][0] <= y[p](d[p]) && y[p](d[p]) <= extents[i][1];
    	}else{
    		return extents[i][0] <= d[p] && d[p] <= extents[i][1];
    	}
    }) ? null : "none";
  });
}

/* ============================

	Events and connectors

===============================*/


$("#parallel-btn").on("click", function(e){
	displayParallel(sessions);
})

$("#network-btn").on("click", function(e){
	displayNetwork();
})

$("form#upload-form").on('submit', function(e){
	e.preventDefault();

	$('.status-container').html('Upload and Process to parse pcap');
    
    socket.emit('uploadPcap', {fileContent: $(this)[0][0].files[0]});
	
});

// Update side bar
function appendUser(user){
	  $('.left-bar .tab-content #hosts table tbody').append("<tr>" +
		  		"<td>" + user['id'] + "</td>" +
		  		"<td>" + user['address'] + "</td>" +
		  		"<td>" + user['exchanged']["Volume"] + "</td>" +
		  		"<td></td>" +
		  		"</tr>");
}

// Update side bar
function appendStat(stat){
	  $('.left-bar .tab-content #services table tbody').append("<tr>" +
		  		"<td>" + stat['id'] + "</td>" +
		  		"<td>" + stat['name'] + "</td>" +
		  		"<td>" + stat['value'] + "</td>" +
		  		"<td></td>" +
		  		"</tr>");
}

socket.on('successfullUpload', function(data){
	$('#upModal').modal('hide');
	$('.status-container').html(data['success']);
})

socket.on('newData', function(data){
	data = JSON.parse(data);
	if('users' in data){
		$('.left-bar .tab-content #hosts table tbody').html('');
		users = data['users'];
		for(i=0;i<users.length;i++){
			if(!users[i]['exchanged']){
				users[i]['exchanged'] = {};
				users[i]['exchanged']['Volume'] = 'None';
			}
			console.log(users[i]);
			appendUser(users[i]);
		}
	}
	if('stats' in data){
		$('.left-bar .tab-content #services table tbody').html('');
		stats = data['stats'];
		for(i=0;i<stats.length;i++){
			console.log(stats[i]);
			appendStat(stats[i]);
		}
	}
	if('sessions' in data){
		sessions = data['sessions']
		displayParallel(sessions);
	}
})

displayParallel(sessions);

// Unused

//$('#upload-form :file').change(function(){
//    var file = this.files[0];
//    var name = file.name;
//    var size = file.size;
//    var type = file.type;
//    
//    console.log(type);
//    
//});

})
