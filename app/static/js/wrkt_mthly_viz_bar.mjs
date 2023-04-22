import wrkt_viz from './wrkt_viz_core.mjs'

let chartHolder = d3.select("#monthly_mileage_bar");

let margin = { top: 20, right: 20, bottom: 45, left: 40 };
let boundingRect = chartHolder.node().getBoundingClientRect();
let width = boundingRect.width - margin.left - margin.right;
let height = boundingRect.height - margin.top - margin.bottom;
let xPaddingLeft = 20; //padding for y-axis label
console.log('Width:'+width);
console.log('Height:'+height);

// SCALES
let xScale = d3.scaleBand().range([xPaddingLeft, width]).padding(0.1);

let yScale = d3.scaleLinear().range([height, 0]);

// AXES
let xAxis = d3.axisBottom().scale(xScale);

let yAxis = d3
  .axisLeft()
  .scale(yScale)
  .ticks(10)
  .tickFormat(function (d) {
    return d;
  });

let svg = chartHolder
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
// ADD AXES
svg
  .append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
;

// Setup Y Axis
svg
  .append("g")
  .attr("class", "y axis")
  .append("text")
  .text("Miles")
  .attr("id", "y-axis-label")
  .attr("transform", "rotate(-90)")
  .attr("y", -40)
  .attr("x", -(height/2)+40)
  .attr("dy", ".71em")
  .style("font-size","15px")
  .style("text-anchor", "end")
;
// Label for X-axis
/*svg
  .append("text")
  .attr("x", width/2)
  .attr("y", height + margin.top ) //Need to adjust
  .attr("text-anchor", "middle")
  .style("font-size", "16px")
  .text("Year-Month")
;*/
// Title for chart
svg
  .append("text")
  .attr("x", width/2)
  .attr("y", 0)
  .attr("text-anchor", "middle")
  .style("font-size", "20px")
  .text("Mileage by Month")
;
let titleHeight=15;



let updateBarChart = function (data) {
  console.log('updateBarChart');
  // console.log(data);
  /*// filter out any countries with zero prizes by value
  data = data.filter(function (d) {
    return d.value > 0;
  });*/
  // change the scale domains to reflect the newly filtered data
  xScale.domain(data.map((d) => d.code));
  yScale.domain([0, d3.max(data, (d) => d.value)+titleHeight]);

  // change the x and y axes smoothly with a transition
  svg
    .select(".x.axis")
    .transition()
    .duration(wrkt_viz.TRANS_DURATION)
    .call(xAxis)
    .selectAll("text")
    .style("text-anchor", "end")
    .style("font-size","10px")
    .attr("dx", "-.8em")
    .attr("dy", ".15em")
    .attr("transform", "rotate(-65)");

  svg.select(".y.axis").transition().duration(wrkt_viz.TRANS_DURATION).call(yAxis);

  let bars = svg
    .selectAll(".bar")
    .data(data, (d) => d.code)
    .join(
      (enter) => {
        return enter
          .append("rect")
          .attr("class", "bar")
          .attr("x", xPaddingLeft);
      }
      // (update) => update,
      // (exit) => {
      //   return exit.remove()
      // }
    )
    /*.classed("active", function (d) {
      return d.key === wrkt_viz.activeCountry;
    })*/
    .transition()
    .duration(wrkt_viz.TRANS_DURATION)
    .attr("x", (d) => xScale(d.code))
    .attr("width", xScale.bandwidth())
    .attr("y", (d) => yScale(d.value))
    .attr("height", (d) => height - yScale(d.value))
  ;

  console.log('End updateBarChart');
};

wrkt_viz.callbacks.push(() => {
  let data = wrkt_viz.getMonthlyData();
  updateBarChart(data);
});
