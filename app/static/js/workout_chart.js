let elevation_chart;
let TRANS_DURATION = 2000;
var currentLocMarker;

function initChart(wrkt_json, wrkt_miles_json){
    console.log('workout_chart.js initChart');
    elevation_chart = d3.select("#elevation_chart");
    // console.log(elevation_chart);
    // console.log(wrkt_json);
    let data = wrkt_json.filter(function(d){
        // return d.altitude_ft > -1
        return !(isNaN(d.ele_roll))
    });
    // console.log(data);

    let margin = { top: 20, right: 45, bottom: 45, left: 40 };
    let boundingRect = elevation_chart.node().getBoundingClientRect();
    let width = boundingRect.width - margin.left - margin.right;
    let height = boundingRect.height - margin.top - margin.bottom;
    let xPaddingLeft = 0; //padding for y-axis label

    let dist_max = Math.round(d3.max(data, function(d) {return +d.dist_mi})*100)/100;
    // let duration_min_max = d3.extent(data, function(d) {return +d.dur_sec});
    // console.log(duration_min_max);
    // SCALES
    let xScale = d3.scaleLinear()
        .domain([0, dist_max]) //0 to 13
        .range([xPaddingLeft, width])
    ;
    // console.log(xScale(13));

    /*
    let run2pixels = d3.scaleLinear()
        .domain([0, 42.195]) // unit: km
        .range([0, 600]) // unit: pixels
    ;
    console.log(run2pixels(42));
    */

    // let ele_min_max = d3.extent(data, function(d) {return +d.altitude_ft});
    let ele_min_max = d3.extent(data, function(d) {return +d.ele_roll});
    let hr_min_max = d3.extent(data, function(d) {return +d.hr});
    let curr_pace_minute_min_max = d3.extent(data, function(d) {return +d.curr_pace_minute});
    
    let yElevationScale = d3
        .scaleLinear()
        .range([height, 0])
        // .domain(d3.range(400,d3.max(data, function(d){return d.altitude_ft})))
        // .domain(d3.range(400, 800))
        // .domain(d3.extent(data, function(d) {return +d.altitude_ft}))
        .domain([ele_min_max[0]-10, ele_min_max[1]+190])
        // .domain([ele_min_max[0]-80, 1200])
    ;
    let yHeartRateScale = d3
        .scaleLinear()
        .range([height, 0])
        .domain([15,  hr_min_max[1]+10]) //hardcode heart rate range at 0 to 200
        // .domain([hr_min_max[0]-10, hr_min_max[1]+10]) 
    ;
    let yPaceScale = d3
        .scaleLinear()
        .range([height, 0])
        // .domain([0, 200]) //hardcode heart rate range at 0 to 200
        // .domain([curr_pace_minute_min_max[0]-1, curr_pace_minute_min_max[1]+1]) 
        .domain([curr_pace_minute_min_max[1]+3, curr_pace_minute_min_max[0]-2]) 
    ;

    // AXES
    let xAxis = d3
        .axisBottom()
        .scale(xScale)
        /*.tickValues(
            xScale.domain().filter(function (d, i){
                // return !(d %500);
                return !(d %1);
            })
        )*/
        .ticks(10)
        .tickFormat(function (d) {
            return d;
        })
    ;

    let yElevationAxis = d3
        .axisRight()
        .scale(yElevationScale)
        .ticks(10)
        .tickFormat(function (d) {
            return d;
        })
    ;

    let yHeartRateAxis = d3
        .axisRight()
        .scale(yHeartRateScale)
        .ticks(10)
        .tickFormat(function (d) {
            return d;
        })
    ;

    let yPaceAxis = d3
        .axisLeft()
        .scale(yPaceScale)
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
        .attr("dx", ".3em")
    ;
    // Label for X-axis
    svg
        .append("text")
        .attr("x", width/2)
        .attr("y", height + margin.top + 18 ) //Need to adjust
        .attr("text-anchor", "middle")
        .style("font-size", "16px")
        .text("Mileage")
    ;

    svg.append("g").attr("class", "y axis").call(yPaceAxis);

    // Setup Y Axis
    svg
        .append("g")
        .attr("class", "y axis")
        .append("text")
        .text("Pace")
        .attr("id", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", -40)
        .attr("x", -(height/2)+40)
        // .attr("x", 750)
        .attr("dy", ".71em")
        .style("font-size","15px")
        .style("text-anchor", "end")
    ;

    svg.append("g").attr("class", "y axis").attr("transform", "translate("+(width)+",0)").call(yElevationAxis);

    //svg.append("g").attr("class", "y axis").call(yHeartRateAxis);

    // Setup Y Axis Right Side Title
    svg
        .append("g")
        .attr("class", "y axis")
        .append("text")
        .text("Elevation")
        .attr("id", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", width+30)
        .attr("x", -(height/2)+40)
        // .attr("x", 750)
        .attr("dy", ".71em")
        .style("font-size","15px")
        .style("text-anchor", "end")
    ;


    // Title for chart
    /*svg
        .append("text")
        .attr("x", width/2)
        .attr("y", 0)
        .attr("text-anchor", "middle")
        .style("font-size", "20px")
        .text("Workout Elevation")
    ;
    let titleHeight=15;*/

    let lineElevation = d3.line()
        .x(function(d) { return xScale(d.dist_mi) })
        .y(function(d) { return yElevationScale(d.ele_roll) })
    ;
    let areaElevation = d3.area()
        .x(function(d) { return xScale(d.dist_mi) })
        .y0(height)
        .y1(function(d) { return yElevationScale(d.ele_roll) })
    ;

    let linesElevation = svg
        .append("path")
        .datum(data)
        // .attr("fill", "none") //Use if only show line
        .attr("fill", "lightsteelblue")
        .attr("stroke", "steelblue")
        .attr("stroke-width", 1.5)
        // .attr("d", lineElevation) //Show just line
        .attr("d", areaElevation) //Show line and fill
        .transition()
        .duration(2000)
    ;

    let lineHr = d3.line()
        .x(function(d) { return xScale(d.dist_mi) })
        .y(function(d) { return yHeartRateScale(d.hr) })
    ;

    let linesHr = svg
        .append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "red")
        .attr("stroke-width", 1.5)
        .attr("d", lineHr)
        .transition()
        .duration(2000)
    ;

    let linePace = d3.line()
        .x(function(d) { return xScale(d.dist_mi) })
        .y(function(d) { return yPaceScale(d.curr_pace_minute) })
    ;

    let linesPace = svg
        .append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "green")
        .attr("stroke-width", 1.5)
        .attr("d", linePace)
        .transition()
        .duration(2000)
    ;

    // Setup tooltip logic
    const xAxisLine = svg
        .append("g")
        .append("rect")
        .attr("class","dotted")
        .attr("stroke-width", "1px")
        .attr("width", ".5px")
        .attr("height", height)
        // .attr("x", "100px")
    ;

    


    const tooltip = d3.select('#tooltip');
    onMouseMove = function(event, d){
        const mousePosition = d3.pointer(event);
        // console.log(`Mouse Location: ${mousePosition[0]} ${mousePosition[1]}`);
        let hoverMile = xScale.invert(mousePosition[0]);
        let dist = Math.round(hoverMile*100)/100;

        if (dist in wrkt_miles_json){
            tooltip.select('#elevation').html(`Elevation: ${d3.format(".2f")(wrkt_miles_json[dist]['ele_roll'])} feet`);
            tooltip.select('#distance').html(`Distance: ${d3.format(".2f")(wrkt_miles_json[dist]['dist_mi'])} miles`);
            tooltip.select('#heartrate').html(`Heart Rate: ${d3.format(".0f")(wrkt_miles_json[dist]['hr'])}`);
            // tooltip.select('#pace').html(`Pace: ${d3.format(".2f")(wrkt_miles_json[dist]['curr_pace_minute'])} /mile`);
            tooltip.select('#pace').html(`Pace: ${wrkt_miles_json[dist]['curr_pace_str']} /mile`);
            // console.log(`lat: ${wrkt_miles_json[dist]['latitude']}, lon: ${wrkt_miles_json[dist]['longitude']}`)
            tooltip.select('#duration').html(`Lap ${wrkt_miles_json[dist]['lap']} - ${wrkt_miles_json[dist]['dur_str']}`);
        }

        // Show tooltip and have it left of mouse if close to right side of chart
        tooltip.style("top", 10 + "px");
        let toolTipPosition = mousePosition[0]+50
        if ((toolTipPosition) > (width*0.75)){
            toolTipPosition = mousePosition[0] - 150;
        }
        tooltip.style("left", toolTipPosition + "px");
        tooltip.style("opacity", 0.9);

        // Draw vertical line where mouse pointer is
        xAxisLine.attr("x", mousePosition[0]);
        xAxisLine.style("opacity", 1);

        if (dist in wrkt_miles_json){
            let currLocationDict = {
                'lat':wrkt_miles_json[dist]['latitude'],
                'lon':wrkt_miles_json[dist]['longitude'],
                'nbr':1
            };    
            currLocation = [];
            currLocation.push(create_marker(currLocationDict, 'lightblue', "0.7"));
            if (currentLocMarker !== undefined ){
                map.removeLayer(currentLocMarker);
            }
            currentLocMarker = new L.geoJson(currLocation, {
                pointToLayer: function(feature, latlng) {
                    return new L.CircleMarker([latlng.lng, latlng.lat],  feature.properties);
                } 
            });
            currentLocMarker.addTo(map);
        }

    };
    
    onMouseLeave = function(event, d){
        tooltip.style("opacity", 0);
        xAxisLine.style("opacity", 0);
        if (currentLocMarker !== undefined ){
            map.removeLayer(currentLocMarker);
        }
    };

    const listeningRect = svg
        .append("rect")
        .attr("class", "chart_listening_rect")
        .attr("width", width)
        .attr("height", height)
        .on("mousemove", onMouseMove)
        .on("mouseleave", onMouseLeave)
    ;

    console.log('End initChart');
}

