let elevation_chart;
let TRANS_DURATION = 2000;

function initChart(wrkt_json){
    console.log('workout_chart.js initChart');
    elevation_chart = d3.select("#elevation_chart");
    // console.log(elevation_chart);
    // console.log(wrkt_json);
    let data = wrkt_json.filter(function(d){
        return d.altitude_ft > -1
    });
    console.log(data);

    let margin = { top: 20, right: 20, bottom: 45, left: 40 };
    let boundingRect = elevation_chart.node().getBoundingClientRect();
    let width = boundingRect.width - margin.left - margin.right;
    let height = boundingRect.height - margin.top - margin.bottom;
    // let width = 500 - margin.left - margin.right;
    // let height = 200 - margin.top - margin.bottom;
    let xPaddingLeft = 20; //padding for y-axis label

    // SCALES
    let xScale = d3.scaleBand()
        .range([xPaddingLeft, width]).padding(0.1)
        .domain(d3.range(0,6000))
        // .domain(d3.range(0,14))
    ;

    let ele_min_max = d3.extent(data, function(d) {return +d.altitude_ft});
    console.log(ele_min_max);
    console.log((ele_min_max[0]-20) + ' ' + (ele_min_max[1]+20));
    let yScale = d3
        .scaleLinear()
        .range([height, 0])
        // .domain(d3.range(400,d3.max(data, function(d){return d.altitude_ft})))
        // .domain(d3.range(400, 800))
        // .domain(d3.extent(data, function(d) {return +d.altitude_ft}))
        .domain([ele_min_max[0], ele_min_max[1]+20])
    ;

    // AXES
    let xAxis = d3
        .axisBottom()
        .scale(xScale)
        .tickValues(
            xScale.domain().filter(function (d, i){
                return !(d %500);
                // return !(d %2);
            })
        )
    ;

    let yAxis = d3
        .axisLeft()
        .scale(yScale)
        .ticks(10)
        .tickFormat(function (d) {
            return d;
        })
    ;

    let svg = elevation_chart
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
    ;
    // ADD AXES
    svg
        .append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
    ;
    
    // change the x and y axes smoothly with a transition
    svg
        .select(".x.axis")
        .transition()
        .duration(TRANS_DURATION)
        .call(xAxis)
        .selectAll("text")
        .style("text-anchor", "end")
        .style("font-size","10px")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        // .attr("transform", "rotate(-65)")
    ;

    svg.append("g").attr("class", "y axis").call(yAxis);

    // Setup Y Axis
    svg
        .append("g")
        .attr("class", "y axis")
        .append("text")
        .text("Elevation Feet")
        .attr("id", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", -40)
        .attr("x", -(height/2)+40)
        // .attr("x", 750)
        .attr("dy", ".71em")
        .style("font-size","15px")
        .style("text-anchor", "end")
    ;

    // Title for chart
    svg
        .append("text")
        .attr("x", width/2)
        .attr("y", 0)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .text("Workout Elevation")
    ;
    let titleHeight=15;

    let line = d3.line()
        .x(function(d) { return xScale(d.dur_sec) })
        .y(function(d) { return yScale(d.altitude_ft) })
        // .curve(d3.curveMonotoneX)
    ;

    let lines = svg
        .append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        .attr("d", line)
        .transition()
        .duration(2000)
    ;
    console.log('End initChart');

}

