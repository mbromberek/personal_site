var onering_chart;
const INIT_MAX_CHART_HEIGHT = 1800;
const RIVENDELL_DIST = 458;
const LOTHLORIEN_DIST = 920;
const ROUROS_DIST = 1309;
const MOUNTDOOM_DIST = 1779;

function initYrOneRingChart(yr_lst, chart_name) {
  let chart_height, chart_width;
  let onering_onering_chart_g;

  console.log('initYrOneRingChart');
  let data = [yr_lst[0]];
  onering_chart = d3.select('#' + chart_name), 
    margin = 200,
    chart_width = onering_chart.attr("width") - margin,
    chart_height = onering_chart.attr("height") - 100;
  // console.log('width: ' + chart_width + ' height: ' + chart_height);
  
  onering_chart.append("text")
    .attr("transform", "translate(0,0)")
    .attr("x", chart_width - 70)
    .attr("y", 25)
    .attr("font-size", "18px")
    .text("Shire to Mount Doom");

  onering_chart.append("text")
    .attr("transform", "translate(0,0)")
    .attr("x", chart_width - 30)
    .attr("y", 50)
    .attr("font-size", "16px")
    .text(MOUNTDOOM_DIST + " miles");
    
  chart_x = d3.scaleBand().range([0, chart_width]).padding(0.0),
  chart_y = d3.scaleLinear().range([chart_height, 0]);
  
  onering_chart_g = onering_chart.append("g")
          .attr("transform", "translate(" + 75 + "," + 75 + ")");
  
  chart_x.domain(data.map(function(d) { return d.year; }));
  chart_y.domain([0, d3.max([INIT_MAX_CHART_HEIGHT, data[0].tot_dist])]);

  onering_chart_g.append("g")
    .call(d3.axisLeft(chart_y).tickFormat(function(d){
      return d;
    }).ticks(10))
  
  onering_chart_g.selectAll(".bar")
    .data(data)
    .enter().append("rect")
    .attr("class", "mileage_bar")
    .attr("x", function(d) { return chart_x(d.year); })
    .attr("width", chart_x.bandwidth())
    .attr("height", function(d) { return chart_height - chart_y(0); }) //Start with bar height at 0
    .attr("y", function(d) { return chart_y(0); })
    .transition()
    .ease(d3.easeLinear)
    .duration(1000)
    .attr("y", function(d) { return chart_y(d.tot_dist); })
    .attr("height", function(d) { return chart_height - chart_y(d.tot_dist); })
    .delay(function (d, i) {
      return i * 50;
    });

  addMilestone(onering_chart_g, chart_width, chart_y, 'Shire', 0);
  addMilestone(onering_chart_g, chart_width, chart_y, 'Rivendell', RIVENDELL_DIST);
  addMilestone(onering_chart_g, chart_width, chart_y, 'Lothlorien', LOTHLORIEN_DIST);
  addMilestone(onering_chart_g, chart_width, chart_y, 'Rouros', ROUROS_DIST);
  addMilestone(onering_chart_g, chart_width, chart_y, 'Mount Doom', MOUNTDOOM_DIST);
  
}

function addMilestone(g, width, y, milestone_name, milestone_dist){
  g.append("g")
      .append("text")
      .attr("dx", "4.5em")
      // .attr("x", )
      .attr("y", y(milestone_dist))
      .attr("text-anchor", "middle")
      .attr("fill", "black")
      .attr("font-size", "14px")
      .text(milestone_name);
  g.append("g")
      .append("rect")
      .attr("class","dotted")
      .attr("stroke-width", "1px")
      .attr("width", width)
      .attr("height", ".5px")
      .attr("y", y(milestone_dist))
      .style("opacity", 0.8)
  ;
}
  
  
  
