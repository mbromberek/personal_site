
function initGoalChart(goal_lst) {
  console.log('initGoalChart');
  console.log(goal_lst);
  
  run_goal = goal_lst[0];
  let data = [run_goal['tot'], run_goal['remaining']];
  let data_lbl = d3.scaleOrdinal(['Total', 'Remaining']);
  
  let goal_svg = d3.select("#goal_pie");
  let boundingRect = goal_svg.node().getBoundingClientRect();
    // width = goal_svg.attr("width"),
    // height = goal_svg.attr("height"),
  let radius = Math.min(boundingRect.width, boundingRect.height) / 2;
  let inner_radius = radius / 2;
  let g = goal_svg.append("g").attr("transform", "translate(" + boundingRect.width / 2 + "," + boundingRect.height / 2 + ")");
  console.log(boundingRect.width + ' ' + boundingRect.height);
  
  let graph_color = d3.scaleOrdinal(['#4daf4a','#377eb8','#ff7f00','#984ea3','#e41a1c']);
  console.log(graph_color);
  
  // Generate the pie
  let pie = d3.pie();
  
  // Generate the arcs
  let arc = d3.arc()
    .innerRadius(inner_radius)
    .outerRadius(radius)
  ;
  let label = d3.arc()
    .outerRadius(radius)
    .innerRadius(radius - inner_radius)
  ;
  
  //Generate groups
  let arcs = g.selectAll("arc")
        .data(pie(data))
        .enter()
        .append("g")
        .attr("class", "arc")
  ;
  
  //Draw arc paths
  arcs.append("path")
    .attr("fill", function(d, i) {
      return graph_color(i);
    })
    .attr("d", arc)
  ;
  
  arcs.append("text")
    .attr("transform", function(d){
      return "translate(" + label.centroid(d) + ")";
    })
    .text(function(d, i) {return data_lbl(i); })
  ;
  
  arcs.append("text")
    // .text("Goal: " + run_goal['goal'] + ' ' + run_goal['uom'])
    .text("Goal")
    .text(run_goal['goal'] + ' ' + run_goal['uom'])
  ;
  
}
