var goals_data;
var inner_goal_radius;
var goal_radius;
var graph_color = d3.scaleOrdinal(['#4daf4a','#377eb8','#ff7f00','#984ea3','#e41a1c']);  

function initGoalChart(goal_lst) {
  console.log('initGoalChart');
  console.log(goal_lst);
  goals_data = goal_lst;
  
  let goal_chart = d3.select('#goal_chart');

  let margin = { top: 0, right: 10, bottom: 0, left: 10 }; 
  let boundingRect = goal_chart.node().getBoundingClientRect();
  let width = boundingRect.width - margin.right - margin.left;
  let height = boundingRect.height - margin.top - margin.bottom; 
  console.log('width: ' + boundingRect.width + ' height: ' + boundingRect.height);
  goal_radius = Math.min(width, height) / 2;
  inner_goal_radius = goal_radius / 2;
  
  let goal_svg = goal_chart
    .append('svg')
    .attr("width", width)
    .attr("height", height)
    .attr("style", "margin-left:"+margin.left+"px;")
    .append("g").attr("transform", "translate(" + width / 2 + "," + height / 2 + ")")
  ;
  

  update_goal_chart(0);
  
  let legendRectSize = 13;
  let legendSpacing = 7;
  let legend = d3.select('#goal_chart').selectAll('g').selectAll('.legend')
    .data(graph_color.domain())
    .enter()
    .append('g')
    .attr('class', 'circle-legend')
    .attr('transform', function (d, i) {
      var height = legendRectSize + legendSpacing;
      var offset = height * graph_color.domain().length / 2;
      var horz = -2 * legendRectSize - 13;
      var vert = i * height - offset;
      return 'translate(' + horz + ',' + vert + ')';
    })
  ;
  
  legend.append('circle') //keys
    .style('fill', graph_color)
    .style('stroke', graph_color)
    .attr('cx', 0)
    .attr('cy', 0)
    .attr('r', '.5em');
  legend.append('text') //labels
    .attr('x', legendRectSize + legendSpacing-5)
    .attr('y', legendRectSize - legendSpacing)
    .text(function (d) {
       return d;
    })
  ;
}  

function update_goal_chart(goal_val){
  // console.log('update_goal_chart');
  run_goal = goals_data[goal_val];
  let goal_data = [
      {'amt':run_goal['tot'], 'desc':'Complete', 'color':'#4daf4a', 'value_str':Math.round(run_goal['tot'])},
      {'amt':run_goal['remaining'], 'desc':'Remaining', 'color':'#377eb8', 'value_str':Math.round(run_goal['remaining'])}];
  
  document.getElementById('goal_chart_desc').innerHTML = run_goal['description'] + ' ' + run_goal['goal'] + ' ' + run_goal['uom'];

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
  
  // console.log(d3.select('#goal_chart').selectAll('path')._groups);
  // console.log(d3.select('#goal_chart').selectAll('path')._groups[0].length);
  let path;
  if (d3.select('#goal_chart').selectAll('path')._groups[0].length == 0){
    path = d3.select('#goal_chart').selectAll('g').selectAll('path')
      .data(pie)
      .enter()
      .append('path')
      .attr('d', arc)
      .attr('fill', function (d, i) {
          // return (goal_data[i]['color']);
          return graph_color(d.data.desc);
      })
      .attr('transform', 'translate(0, 0)')
    ;
  }else{
    path = d3.select('#goal_chart')
      .selectAll('path')
      .data(pie)
    ;
  }
  // console.log('path');
  // console.log(path);
  path.transition().duration(300).attr("d", arc);
  
  let text;
  if (d3.select('#goal_chart').selectAll('text')._groups[0].length == 0){
    text = d3.select('#goal_chart').selectAll('g').selectAll('text')
      .data(pie)
      .enter()
      .append('text')
      .attr('d', arc)
      
      .attr("transform", function(d){
        return "translate(" + label.centroid(d) + ")";
      })
      .text(function(d, i) {return goal_data[i]['value_str']; })
      .style('text-anchor','middle')
    ;
  }else{
    text = d3.select('#goal_chart')
      .selectAll('text')
      .data(pie)
      .attr('d', arc)
      
      .attr("transform", function(d){
        return "translate(" + label.centroid(d) + ")";
      })
      .text(function(d, i) {return goal_data[i]['value_str']; })
      .style('text-anchor','middle')
    ;
  }
  text.transition().duration(100).attr("d", arc);
  
  
  
}


