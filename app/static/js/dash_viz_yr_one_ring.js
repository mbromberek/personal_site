var onering_chart;
const INIT_MAX_CHART_HEIGHT = 1800
const RIVENDELL_DIST = 458

function initYrOneRingChart(yr_lst, chart_name) {
  // let chart_x, chart_y;
  let chart_height, chart_width;
  let onering_onering_chart_g;

  console.log('initYrOneRingChart');
  let data = [yr_lst[0]];
  onering_chart = d3.select('#' + chart_name), 
    margin = 100,
    chart_width = onering_chart.attr("width") - margin,
    chart_height = onering_chart.attr("height") - 150;
  // console.log('width: ' + chart_width + ' height: ' + chart_height);
  
  onering_chart.append("text")
    .attr("transform", "translate(0,0)")
    .attr("x", chart_width - 225)
    .attr("y", 40)
    .attr("font-size", "24px")
    .text("Shire to Mount Doom");
  
  chart_x = d3.scaleBand().range([0, chart_width]).padding(0.4),
  chart_y = d3.scaleLinear().range([chart_height, 0]);
  
  onering_chart_g = onering_chart.append("g")
          .attr("transform", "translate(" + 75 + "," + 75 + ")");
  
  chart_x.domain(data.map(function(d) { return d.year; }));
  // chart_y.domain([0, d3.max(data, function(d) { return d.tot_dist; })]);
  chart_y.domain([0, d3.max([INIT_MAX_CHART_HEIGHT, data[0].tot_dist])]);

/*  
  onering_chart_g.append("g")
    .attr("transform", "translate(0," + chart_height + ")")
    .call(d3.axisBottom(chart_x))
    .append("text")
    // .attr("y", chart_height - 260)
    .attr("y", chart_height - 200)
    .attr("x", chart_width - 200)
    // .attr("text-anchor", "end")
    // .attr("fill", "black")
    // .attr("font-size", "20px")
    // .attr("font-family", "Saira")
    // .text("Year")
  ;*/
    

  onering_chart_g.append("g")
    .call(d3.axisLeft(chart_y).tickFormat(function(d){
      return d;
    }).ticks(10))
    // .append("text")
    // .attr("transform", "rotate(-90)")
    // .attr("x", chart_height - 300)
    // .attr("dy", "-2.1em")
    // .attr("text-anchor", "end")
    // .attr("fill", "black")
    // .attr("font-size", "20px")
    // .text("Distance");

  

    
    onering_chart_g.selectAll(".bar")
      .data(data)
      .enter().append("rect")
      .attr("class", "bar")
      .on("mouseover", onMouseOver) //Add listener for the mouseover event
      .on("mouseout", onMouseOut)   //Add listener for the mouseout event
      .attr("x", function(d) { return chart_x(d.year); })
      .attr("width", chart_x.bandwidth())
      .attr("height", function(d) { return chart_height - chart_y(0); }) //Start with bar height at 0
      .attr("y", function(d) { return chart_y(0); })
    // onering_chart_g.selectAll("rect")
      .transition()
      .ease(d3.easeLinear)
      .duration(500)
      .attr("y", function(d) { return chart_y(d.tot_dist); })
      .attr("height", function(d) { return chart_height - chart_y(d.tot_dist); })
      .delay(function (d, i) {
        return i * 50;
      });

    addMilestone(onering_chart_g, chart_width, chart_y, 'Shire', 0);
    addMilestone(onering_chart_g, chart_width, chart_y, 'Rivendell', RIVENDELL_DIST);
    addMilestone(onering_chart_g, chart_width, chart_y, 'Lothlorien', 920);
    addMilestone(onering_chart_g, chart_width, chart_y, 'Rouros', 1309);
    addMilestone(onering_chart_g, chart_width, chart_y, 'Mount Doom', 1779);
    
    //mouseover event handler function
    function onMouseOver(i, d) {
        d3.select(this).attr('class', 'highlight');
        //Animation for making hovered bar wider and taller
        /*d3.select(this)
          .transition()     // adds animation
          .duration(400)
        .attr('width', chart_x.bandwidth() + 5)
        .attr("y", function(d) { return chart_y(d.tot_dist) - 10; })
        .attr("height", function(d) { return chart_height - chart_y(d.tot_dist) + 10; });*/
    
        onering_chart_g.append("text")
         .attr('class', 'val') 
         .attr('x', function() {
             return chart_x(d.year) + 50;
         })
         .attr('y', function() {
             return chart_y(d.tot_dist) - 15;
         })
         .text(function() {
             return [ '' +d.tot_dist];  // Value of the text
         });
    }
    
    //mouseout event handler function
    function onMouseOut(i, d) {
        // use the text label class to remove label on mouseout
        d3.select(this).attr('class', 'bar');
        //Animation for making hovered bar wider and taller
        /*d3.select(this)
          .transition()     // adds animation
          .duration(400)
          .attr('width', chart_x.bandwidth())
          .attr("y", function(d) { return chart_y(d.tot_dist); })
          .attr("height", function(d) { return chart_height - chart_y(d.tot_dist); });*/
    
        d3.selectAll('.val')
          .remove()
    }

}

function addMilestone(g, width, y, milestone_name, milestone_dist){
  g.append("g")
      .append("text")
      // .attr("dx", "-4em")
      .attr("dx", "12em")
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
      // .attr("dx", "-4em")
      .attr("width", width)
      .attr("height", ".5px")
      .attr("y", y(milestone_dist))
      .style("opacity", 0.8)
  ;
}
  
  
  
