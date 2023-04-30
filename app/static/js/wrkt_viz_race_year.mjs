import wrkt_viz from "./wrkt_viz_core.mjs";
//BASED OFF nbvis_time.mjs

var chartHolder = d3.select("#race_year");

// var margin = { top: 20, right: 20, bottom: 30, left: 40 };
var margin = { top: 20, right: 20, bottom: 35, left: 125 };
var boundingRect = chartHolder.node().getBoundingClientRect();
var width = boundingRect.width - margin.left - margin.right,
  height = boundingRect.height - margin.top - margin.bottom;

var svg = chartHolder
  .append("svg")
  .attr("width", width + margin.left + margin.right)
  .attr("height", height + margin.top + margin.bottom)
  .append("g")
  .attr("class", "chart")
  .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

// SCALES
var xScale = d3
  .scaleBand()
  .range([0, width])
  .padding(0.1)
  .domain(d3.range(2014, 2024)) //TODO make year range dynamic
  ;

//13 for range since unlikely to run more than 13 races in a year
var yScale = d3.scaleBand().range([height, 0]).domain(d3.range(13));

// AXIS
var xAxis = d3
  .axisBottom()
  .scale(xScale)
  .tickValues(
    xScale.domain().filter(function (d, i) {
      return (d);
    })
  );

var yAxis = d3
  .axisLeft()
  .scale(yScale)
  .ticks(7)
  .tickFormat(function (d) {
    // return !(d % 2);
    return d;
  })
;

svg
  .append("g")
  .attr("class", "x axis")
  .attr("transform", "translate(0," + height + ")")
  .call(xAxis)
  .selectAll("text")
  .style("text-anchor", "end")
  .attr("dx", "-.8em")
  .attr("dy", ".15em")
  .attr("transform", "rotate(-65)");

svg.append("g").attr("class", "y axis").call(yAxis);


// Title for chart
svg
  .append("text")
  .attr("x", width/2)
  .attr("y", margin.top-10)
  .attr("text-anchor", "middle")
  .style("font-size", "20px")
  .text("Races by Year")
;
let titleHeight=15;


let updateRaceLabels = function(){
  // LABELS
  let raceLabels = chartHolder
    .select("svg")
    .append("g")
    .attr("class", "labels")
    .attr("transform", "translate(10, "+ (margin.top+10) +")") //Want legend to start a little below top of chart
    .selectAll("label")
    .data(wrkt_viz.RACE_DISTANCES)
    .join("g")
    .attr("transform", function (d, i) {
      return "translate(0," + i * 20 + ")";
    })
  ;
  
  raceLabels
    .append("circle")
    .attr("fill", wrkt_viz.raceFill)
    .attr("r", xScale.bandwidth() / 2);

  raceLabels
    .append("text")
    .text((d) => d)
    .attr("dy", "0.4em")
    .attr("x", 10);
};

let updateTimeChart = function (data) {
  console.log('updateTimeChart Start');
  updateRaceLabels();//TODO Can I move this somewhere else so it is not run every time?
  console.log(data);
  let years = svg.selectAll(".year").data(data, (d) => d.key);

  years
    .join("g")
    .classed("year", true)
    .attr("name", (d) => d.key)
    .attr("transform", function (year) {
      return "translate(" + xScale(+year.key) + ",0)";
    });

  let races = svg
    .selectAll(".year")
    .selectAll("circle")
    .data(
      (d) => d.values,
      (d) => d.name
    );

  races
    .join((enter) => {
      return enter.append("circle").attr("cy", height);
    })
    .attr("fill", function (d) {
      return wrkt_viz.raceFill(d.distance);
    })
    .attr("cx", xScale.bandwidth() / 2)
    .attr("r", xScale.bandwidth() / 2)
    .transition()
    .duration(2000)
    .attr("cy", (d, i) => yScale(i));
};

wrkt_viz.callbacks.push(() => {
  let data = wrkt_viz.nestDataByYear(wrkt_viz.yearDim.top(Infinity));
  updateTimeChart(data);
});
