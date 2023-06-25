var goals_data;
var inner_goal_radius;
var goal_radius;
var goal_svg;
var g;
var graph_color = d3.scaleOrdinal(['#4daf4a','#377eb8','#ff7f00','#984ea3','#e41a1c']);  
var path;
var text;

function initGoalChart(goal_lst) {
  console.log('initGoalChart');
  console.log(goal_lst);
  goals_data = goal_lst;
  
  console.log(goals_data);
  // let data = [run_goal['tot'], run_goal['remaining']];
  // let data_lbl = d3.scaleOrdinal(['Total', 'Remaining']);
  
  goal_svg = d3.select("#goal_pie");
  /*var width = 300;
  var height = 400;
  goal_svg = d3.select("#goal_chart")
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
  ;*/

  let boundingRect = goal_svg.node().getBoundingClientRect();
  goal_radius = Math.min(boundingRect.width, boundingRect.height) / 2;
  inner_goal_radius = goal_radius / 2;
  g = goal_svg.append("g").attr("transform", "translate(" + boundingRect.width / 2 + "," + boundingRect.height / 2 + ")");
  
  
  
  update_goal_chart(1);
}  

function update_goal_chart(goal_val){
  console.log('update_goal_chart');
  run_goal = goals_data[goal_val];
  let goal_data = [{'amt':run_goal['tot'], 'desc':'Total', 'color':'#4daf4a'},{'amt':run_goal['remaining'], 'desc':'Remaining', 'color':'#377eb8'}];

  // Generate the pie
  let pie = d3.pie().value(function(d){
    return d.amt;
  }).sort(null)(goal_data);

  // Generate the arcs
  let arc = d3.arc()
    .innerRadius(inner_goal_radius)
    .outerRadius(goal_radius)
  ;
  let label = d3.arc()
    .outerRadius(goal_radius)
    .innerRadius(goal_radius - inner_goal_radius)
  ;
  
  console.log(d3.select('#goal_chart').selectAll('path')._groups);
  console.log(d3.select('#goal_chart').selectAll('path')._groups[0].length);
  
  if (d3.select('#goal_chart').selectAll('path')._groups[0].length == 0){
    path = goal_svg.selectAll('g').selectAll('path')
      .data(pie)
      .enter()
      .append('path')
      .attr('d', arc)
      .attr('fill', function (d, i) {
          return (goal_data[i]['color']);
      })
      .attr('transform', 'translate(0, 0)')
    ;
  }else{
    path = d3.select('#goal_chart')
      .selectAll('path')
      .data(pie)
    ;
  }
  console.log('path');
  console.log(path);
  path.transition().duration(500).attr("d", arc);
  
  if (d3.select('#goal_chart').selectAll('text')._groups[0].length == 0){
    text = goal_svg.selectAll('g').selectAll('text')
      .data(pie)
      .enter()
      .append('text')
      .attr('d', arc)
      
      .attr("transform", function(d){
        return "translate(" + label.centroid(d) + ")";
      })
      .text(function(d, i) {return goal_data[i]['desc']; })
      .style('text-anchor','middle')
      .style('font-size',10)
    ;
  }else{
    text = d3.select('#goal_chart')
      .selectAll('text')
      .data(pie)
      .attr('d', arc)
      
      .attr("transform", function(d){
        return "translate(" + label.centroid(d) + ")";
      })
      .text(function(d, i) {return goal_data[i]['desc']; })
      .style('text-anchor','middle')
      .style('font-size',10)
    ;
  }
  text.transition().duration(500).attr("d", arc);
  
  /*
  //Generate groups
  let arcs = g.selectAll("arc")
        .data(pie(goal_data))
        // .data(pie(
        //   goal_data.map((d) => d.amt)
        // ))
        .enter()
        .append("g")
        .attr("class", "arc")
  ;
  
  //Draw arc paths
  arcs.append("path")
    .attr("fill", function(d, i) {
      // return graph_color(i);
      return goal_data[i]['color'];
    })
    .attr("d", arc)
  ;
  
  
  
  arcs.append("text")
    .attr("transform", function(d){
      return "translate(" + label.centroid(d) + ")";
    })
    .text(function(d, i) {return goal_data[i]['desc']; })
    .style('text-anchor','middle')
    .style('font-size',12)
  ;
  
  arcs.append("text")
    // .text("Goal: " + run_goal['goal'] + ' ' + run_goal['uom'])
    .text("Goal")
    .text(run_goal['goal'] + ' ' + run_goal['uom'])
    .style('text-anchor','middle')
    .style('font-size',12)
  ;
  */
  
  
}


