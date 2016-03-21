$(document).ready(function(){

/* ============================
  Initiating socket
===============================*/

  // Catching sessions on first load
  var sessions = loadedSessions;
  var users = loadedUsers.sort(function(a, b){
    return b.exchanged.Volume - a.exchanged.Volume;
  });

  var treemap = loadedTreemap;
  var packets = loadedPackets;

  var insecuredProtocol = ['SMTP','IMAP','POP3','POP2','HTTP','LDAP','FTP'];

/* ============================
  Views with D3.js
===============================*/

//Treemap View

var defaults = {
    margin: {top: 20, right: 10, bottom: 0, left: 10},
    rootname: "Hosts",
    format: ",d",
    title: "",
    width: 900,
    height: 578
};

function mainTreemap(o, data) {

  var root,
      opts = $.extend(true, {}, defaults, o),
      formatNumber = d3.format(opts.format),
      rname = opts.rootname,
      margin = opts.margin,
      theight = 36 + 16;

  var width = opts.width - margin.left - margin.right,
      height = opts.height - margin.top - margin.bottom - theight,
      transitioning;

  var color = d3.scale.category20c();

  var x = d3.scale.linear()
      .domain([0, width])
      .range([0, width]);

  var y = d3.scale.linear()
      .domain([0, height])
      .range([0, height]);

  var treemap = d3.layout.treemap()
      .children(function(d, depth) { return depth ? null : d.values; })
			.value(function(d){return d.Volumeout;})
      .sort(function(a, b) { return a.Volumeout - b.Volumeout; })
      .ratio(height / width * 0.5 * (1 + Math.sqrt(5)))
      .round(false);

  d3.select("#view-wrapper").selectAll("*").remove();

  var svg = d3.select("#view-wrapper").append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.bottom + margin.top)
      .style("margin-left", -margin.left + "px")
      .style("margin.right", -margin.right + "px")
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .style("shape-rendering", "crispEdges");

  var grandparent = svg.append("g")
      .attr("class", "grandparent");

  grandparent.append("rect")
      .attr("y", -margin.top)
      .attr("width", width)
      .attr("height", margin.top);

  grandparent.append("text")
      .attr("x", 6)
      .attr("y", 6 - margin.top)
      .attr("dy", ".75em");

  if (opts.title) {
    $("#view-wrapper").prepend("<p class='title'>" + opts.title + "</p>");
  }
  if (data instanceof Array) {
    root = { key: rname, values: data };
  } else {
    root = data;
  }

  initializeTreemap(root);
  accumulateTreemap(root);
  layoutTreemap(root);
  displayTreemap(root);

  if (window.parent !== window) {
    var myheight = document.documentElement.scrollHeight || document.body.scrollHeight;
    window.parent.postMessage({height: myheight}, '*');
  }

  function initializeTreemap(root) {
    root.x = root.y = 0;
    root.dx = width;
    root.dy = height;
    root.depth = 0;
  }

  // Aggregate the values for internal nodes. This is normally done by the
  // treemap layout, but not here because of our custom implementation.
  // We also take a snapshot of the original children (values) to avoid
  // the children being overwritten when when layout is computed.
  function accumulateTreemap(d) {
    return (d.values = d.values)
        ? d.Volumeout = d.values.reduce(function(p, v) { return p + accumulateTreemap(v); }, 0)
        : d.Volumeout;
  }

  // Compute the treemap layout recursively such that each group of siblings
  // uses the same size (1×1) rather than the dimensions of the parent cell.
  // This optimizes the layout for the current zoom state. Note that a wrapper
  // object is created for the parent node for each group of siblings so that
  // the parent’s dimensions are not discarded as we recurse. Since each group
  // of sibling was laid out in 1×1, we must rescale to fit using absolute
  // coordinates. This lets us use a viewport to zoom.
  function layoutTreemap(d) {
    if (d.values) {
      treemap.nodes({values: d.values});
      d.values.forEach(function(c) {
        c.x = d.x + c.x * d.dx;
        c.y = d.y + c.y * d.dy;
        c.dx *= d.dx;
        c.dy *= d.dy;
        c.parent = d;
        layoutTreemap(c);
      });
    }
  }

  function displayTreemap(d) {
    grandparent
        .datum(d.parent)
        .on("click", transitionTreemap)
      .select("text")
        .text(nameTreemap(d));

    var g1 = svg.insert("g", ".grandparent")
        .datum(d)
        .attr("class", "depth");

    var g = g1.selectAll("g")
        .data(d.values)
      .enter().append("g");

    g.filter(function(d) { return d.values; })
        .classed("children", true)
        .on("click", transitionTreemap);

    var children = g.selectAll(".child")
        .data(function(d) { return d.values || [d]; })
      .enter().append("g");

    children.append("rect")
        .attr("class", "child")
        .call(rectTreemap)
      .append("title")
        .text(function(d) { return d.key + " (" + formatNumber(d.Volumeout) + ")"; });
    children.append("text")
        .attr("class", "ctext")
        .text(function(d) { return d.key; })
        .call(text2Treemap);

    g.append("rect")
        .attr("class", "parent")
        .call(rectTreemap);

    var t = g.append("text")
        .attr("class", "ptext")
        .attr("dy", ".75em");

    t.append("tspan")
        .text(function(d) { return d.key; });
    t.append("tspan")
        .attr("dy", "1.0em")
        .text(function(d) { return formatNumber(d.Volumeout) + " bytes"; });
    t.call(textTreemap);

    g.selectAll("rect")
        .style("fill", function(d) { return color(d.key); });

    function transitionTreemap(d) {
      if (transitioning || !d) return;
      transitioning = true;

      var g2 = displayTreemap(d),
          t1 = g1.transition().duration(750),
          t2 = g2.transition().duration(750);

      // Update the domain only after entering new elements.
      x.domain([d.x, d.x + d.dx]);
      y.domain([d.y, d.y + d.dy]);

      // Enable anti-aliasing during the transition.
      svg.style("shape-rendering", null);

      // Draw child nodes on top of parent nodes.
      svg.selectAll(".depth").sort(function(a, b) { return a.depth - b.depth; });

      // Fade-in entering text.
      g2.selectAll("text").style("fill-opacity", 0);

      // Transition to the new view.
      t1.selectAll(".ptext").call(textTreemap).style("fill-opacity", 0);
      t1.selectAll(".ctext").call(text2Treemap).style("fill-opacity", 0);
      t2.selectAll(".ptext").call(textTreemap).style("fill-opacity", 1);
      t2.selectAll(".ctext").call(text2Treemap).style("fill-opacity", 1);
      t1.selectAll("rect").call(rectTreemap);
      t2.selectAll("rect").call(rectTreemap);

      // Remove the old node when the transition is finished.
      t1.remove().each("end", function() {
        svg.style("shape-rendering", "crispEdges");
        transitioning = false;
      });
    }

    return g;
  }

  function textTreemap(text) {
    text.selectAll("tspan")
        .attr("x", function(d) { return x(d.x) + 6; });
    text.attr("x", function(d) { return x(d.x) + 6; })
        .attr("y", function(d) { return y(d.y) + 6; })
        .style("opacity", function(d) { return this.getComputedTextLength() < x(d.x + d.dx) - x(d.x) ? 1 : 0; });
  }

  function text2Treemap(text) {
    text.attr("x", function(d) { return x(d.x + d.dx) - this.getComputedTextLength() - 6; })
        .attr("y", function(d) { return y(d.y + d.dy) - 6; })
        .style("opacity", function(d) { return this.getComputedTextLength() < x(d.x + d.dx) - x(d.x) ? 1 : 0; });
  }

  function rectTreemap(rect) {
    rect.attr("x", function(d) { return x(d.x); })
        .attr("y", function(d) { return y(d.y); })
        .attr("width", function(d) { return x(d.x + d.dx) - x(d.x); })
        .attr("height", function(d) { return y(d.y + d.dy) - y(d.y); });
  }

  function nameTreemap(d) {
    return d.parent
        ? nameTreemap(d.parent) + " / " + d.key + " (" + formatNumber(d.Volumeout) + ")"
        : d.key + " (" + formatNumber(d.Volumeout) + ")";
  }

}

// Parallel View

var line, dragging, x, y, foreground, background, axis, margin, height, width, g, data, activeSessions;

function displayParallel(data){

  // Define the window width, height and margins
  margin = {top: 30, right: 10, bottom: 10, left: 10};
  width = 960 - margin.left - margin.right;
  height = 500 - margin.top - margin.bottom;
  tension = (typeof tension !== 'undefined') ? tension : 0.75;

  // Init axis
  x = d3.scale.ordinal().rangePoints([0, width], 1);
  y = {};

  dragging = {};

  // Init
  line = d3.svg.line()
  .interpolate("cardinal")
  .tension(tension);

  axis = d3.svg.axis().orient("left");

  // Create the window and the g container
  select = d3.select("#view-wrapper");
  select.selectAll("*").remove();

  slider = select.append("div").attr("id", "sliderWrapper");

  labelSlider = slider.append("label")
    .html("Tension : " + tension)
    .attr("class", "labelSlider");

  slider.append("input")
    .attr("type", "range")
    .attr("id", "slider")
    .attr("min", "0")
    .attr("max", "1")
    .attr("step", "0.05")
    .attr("value", tension)
    .on("input", function(){
      tension = +this.value;
      line.tension(tension);
      labelSlider.html("Tension : " + tension);
      background.attr("d", path);
      foreground.attr("d", path);
    });

  svg = select.append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Extract the list of dimensions and create a scale for each.
  x.domain(dimensions = d3.keys(data[0]).filter(function(d) {

  // Create ordinals dimensions
    if(d.toLowerCase() != "id" && d.substr(0,4).toLowerCase() != "port" && d.substr(0,4).toLowerCase() != "nomb" ){
      return y[d] = d3.scale.ordinal()
      .domain(d3.values(data).sort(function(a, b) {return d3.ascending(a[d], b[d]); }).map(function(obj){return obj[d];}))
      .rangePoints([height, 0]);

    // Create linear dimensions
     }else if(d.substr(0,3).toLowerCase() != "id"){
    return y[d] = d3.scale.linear()
          .domain(d3.extent(data, function(p) { return +p[d]; }))
          .range([height, 0]);
    }

  }));

  // Add grey background lines for context.
  background = svg.append("g")
      .attr("class", "background")
    .selectAll("path")
      .data(data)
    .enter().append("path")
      .attr("d", path)
      .attr("data-session", function(d){return d.id;});

  // Add blue foreground lines for focus.
  foreground = svg.append("g")
      .attr("class", "foreground")
    .selectAll("path")
      .data(data)
    .enter().append("path")
      .attr("d", path)
      .attr("class", function(d){ return (insecuredProtocol.indexOf(d.protocol)) >= 0 ? "insecured" : null ;})
      .attr("data-session", function(d){return d.id;});

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
          g.attr("transform", function(d) { return "translate(" + position(d) + ")"; });
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
        d3.select(this).call(y[d].brush = d3.svg.brush().y(y[d]).on("brushstart", brushstart).on("brushend", brushend).on("brush", brush));
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
      extents = actives.map(function(p) { return y[p].brush.extent(); }),
      isSelected = false;
      activeSessions = [];
  foreground.style("display", function(d) {
    isSelected = actives.every(function(p, i) {
      if(typeof y[p].rangePoints === "function"){
        return extents[i][0] <= y[p](d[p]) && y[p](d[p]) <= extents[i][1];
      }else{
        return extents[i][0] <= d[p] && d[p] <= extents[i][1];
      }
    });
    if(isSelected){
      activeSessions.push(d.id);
      return null;
    }else{
      return "none";
    }
  });
}

function brushend(){
  var selectedPackets = [];
  for(var i=0;i<packets.length;i++){
    if(activeSessions.indexOf(packets[i].sessionId) >= 0){
      selectedPackets.push(packets[i]);
    }
  }
  displayPackets(selectedPackets);
}

function displayPackets(packets){
  $('.packet-wrapper table tbody').html('');
  for(i=0;i<packets.length;i++){
    if (packets[i].data != {}){
      $('.packet-wrapper table tbody').append("<tr>" +
          "<td>" + packets[i].sessionId + "</td>" +
          "<td>" + packets[i].hostSrc + "</td>" +
          "<td>" + packets[i].portSrc + "</td>" +
          "<td>" + packets[i].hostDest + "</td>" +
          "<td>" + packets[i].portDest + "</td>" +
          "<td>" + packets[i].protocol + "</td>" +
          "<td> No Data </td>" +
          "<td>" + packets[i].timestamp + "</td>" +
          "</tr>");
    } else {
      $('.packet-wrapper table tbody').append("<tr>" +
          "<td>" + packets[i].sessionId + "</td>" +
          "<td>" + packets[i].hostSrc + "</td>" +
          "<td>" + packets[i].portSrc + "</td>" +
          "<td>" + packets[i].hostDest + "</td>" +
          "<td>" + packets[i].portDest + "</td>" +
          "<td>" + packets[i].protocol + "</td>" +
          "<td>" +
          "<button> </button>" +
          "</td>" +
          "<td>" + packets[i].timestamp + "</td>" +
          "</tr>");
    }
  }
}

/* ============================
  Events and connectors
===============================*/


$("#parallel-btn").on("click", function(e){
  displayParallel(sessions);
});

$("#network-btn").on("click", function(e){
  displayNetwork();
});

$("#treemap-btn").on("click", function(e){
  mainTreemap({}, treemap);
});

// Update side bar
function updateUsers(){
  for(i=0;i<users.length;i++){
    $('.left-bar .tab-content #hosts table tbody').append("<tr>" +
        "<td>" + (i+1) + "</td>" +
        "<td>" + users[i].address + "</td>" +
        "<td>" + users[i].exchanged.Volume + "</td>" +
        "<td></td>" +
        "</tr>");
  }
}

// Update side bar
function updateStats(stats){
  for(i=0;i<stats.length;i++){
    $('.left-bar .tab-content #services table tbody').append("<tr>" +
        "<td>" + (i+1) + "</td>" +
        "<td>" + stats[i].name + "</td>" +
        "<td>" + stats[i].value + "</td>" +
        "<td><input id=\"" + stats[i].name + "\" class=\"check-prot\" type=\"checkbox\" value=\"checkbox\"></td>" +
        "</tr>");
  }
}

$('.check-all').on('change', function(){
  if($('.check-all').prop('checked')){
    $('.check-prot').prop("checked", true);
  }else{
    $('.check-prot').prop("checked", false);
  }
});

 //Update Views depending of checkboxes
// Il faut boucler sur les services, et si la checkbox est cochée,
// On appelle updateview avecun tableau de booleans ?
// La fonction

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function() {

  $("form#upload-form").on('submit', function(e){
    e.preventDefault();

    $('.status-container').html('Upload and Process to parse pcap');

      socket.emit('uploadPcap', {fileContent: $(this)[0][0].files[0]});

  });

  $('#refreshButton').click(function(e){
    e.preventDefault();

    var prot = [];
    var length = $('.check-prot').length;
    var id  = '';

    $('.check-prot').each(function(){
      id = $(this).attr('id');
      //Problème : Check is undefined
      var checked = $(this).prop("checked");
      //console.log('checked ? '+checked)
      if(checked === true){
        prot.push(id);
      }
    });
    //A voir
    socket.emit('refreshView',{'fileContent': prot});

    //Call the app.py refreshView Function
  });

  socket.on('successfullUpload', function(data){
    $('#upModal').modal('hide');
    $('.status-container').html(data.success);
  });

  socket.on('newData', function(data){
    data = JSON.parse(data);
    if('treemap' in data){
      treemap = data.treemap;
      mainTreemap({}, treemap);
    }
    if('stats' in data){
      $('.left-bar table tbody').html('');
      stats = data.stats.sort(function(a, b){
        return b.value - a.value;
      });
      updateStats(stats);
    }
    if('sessions' in data){
      sessions = data.sessions;
      displayParallel(sessions);
    }
    if('packets' in data){
      packets = data.packets;
      displayPackets(packets);
    }
  });

  $(window).on('beforeunload', function(){
      socket.close();
  });

});


displayParallel(sessions);

updateUsers();

});
