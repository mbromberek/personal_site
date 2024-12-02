var yr_mileage_chart;
var chart_x, chart_y;
var chart_height, chart_width;
var chart_g;

function initYrMileageChart(yr_lst, chart_name) {
  console.log('initYrMileageChart');
  // console.log(yr_lst);
  // console.log(yr_lst.length);
  // console.log(yr_lst[0]['tot_dist']);
  // console.log(yr_lst[0].year);
  yr_lst.reverse();
  yr_mileage_chart = d3.select('#' + chart_name), 
    margin = 200,
    chart_width = yr_mileage_chart.attr("width") - margin,
    chart_height = yr_mileage_chart.attr("height") - margin;
  // console.log('width: ' + chart_width + ' height: ' + chart_height);
  
  yr_mileage_chart.append("text")
    .attr("transform", "translate(100,0)")
    .attr("x", 150)
    .attr("y", 50)
    .attr("font-size", "24px")
    .text("Running Mileage");
  
  chart_x = d3.scaleBand().range([0, chart_width]).padding(0.4),
  chart_y = d3.scaleLinear().range([chart_height, 0]);
  
  chart_g = yr_mileage_chart.append("g")
          .attr("transform", "translate(" + 100 + "," + 100 + ")");
  
  chart_x.domain(yr_lst.map(function(d) { return d.year; }));
  chart_y.domain([0, d3.max(yr_lst, function(d) { return d.tot_dist; })]);

  chart_g.append("g")
    .attr("transform", "translate(0," + chart_height + ")")
    .call(d3.axisBottom(chart_x))
    .append("text")
    // .attr("y", chart_height - 260)
    .attr("y", chart_height - 260)
    .attr("x", chart_width - 200)
    .attr("text-anchor", "end")
    .attr("fill", "black")
    .attr("font-size", "20px")
    .attr("font-family", "Saira")
    .text("Year");

  chart_g.append("g")
    .call(d3.axisLeft(chart_y).tickFormat(function(d){
      return d;
    }).ticks(10))
    .append("text")
    .attr("transform", "rotate(-90)")
    // .attr("y", 6)
    .attr("dy", "-2.1em")
    .attr("text-anchor", "end")
    .attr("fill", "black")
    .attr("font-size", "20px")
    .text("Distance");

  chart_g.selectAll(".bar")
    .data(yr_lst)
    .enter().append("rect")
    .attr("class", "bar")
    .on("mouseover", onMouseOver) //Add listener for the mouseover event
    .on("mouseout", onMouseOut)   //Add listener for the mouseout event
    .attr("x", function(d) { return chart_x(d.year); })
    .attr("y", function(d) { return chart_y(d.tot_dist); })
    .attr("width", chart_x.bandwidth())
    .transition()
    .ease(d3.easeLinear)
    .duration(400)
    .delay(function (d, i) {
      return i * 50;
    })
    .attr("height", function(d) { return chart_height - chart_y(d.tot_dist); });
}
  
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

    chart_g.append("text")
     .attr('class', 'val') 
     .attr('x', function() {
         return chart_x(d.year);
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
  
  
