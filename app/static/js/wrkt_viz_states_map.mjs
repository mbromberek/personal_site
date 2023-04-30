import wrkt_viz from './wrkt_viz_core.mjs'

let defaultMapWidth = 960,
  defaultMapHeight = 480;

// DIMENSIONS AND SVG
let mapContainer = d3.select("#race_map");
let boundingRect = mapContainer.node().getBoundingClientRect();
console.log('boundingRect:'+boundingRect.width + ' '+boundingRect.height);
let width = boundingRect.width,
  height = boundingRect.height;

let svg = mapContainer.append("svg").attr("class", "us_map");

/*let MANUAL_CENTROIDS = {
  France: [2, 46],
  "United States": [-98, 35, 39.5],
};*/

// A FEW D3 PROJECTIONS
// default scale = 153
let projection_eq = d3
  .geoEquirectangular()
  .scale(193 * (height / 480))
  .center([15, 15])
  // .translate([0.9* width / 2, 1.2* height / 2])
  .translate([width / 2, height / 2])
  .precision(0.1)
;

let projection_cea = d3
  .geoConicEqualArea()
  .center([0, 26])
  .scale(128)
  .translate([width / 2, height / 2])
  .precision(0.1);

let projection_ceq = d3
  .geoConicEquidistant()
  .center([0, 22])
  .scale(128)
  .translate([width / 2, height / 2])
  .precision(0.1);

let projection_merc = d3
  .geoMercator()
  .scale((width + 1) / 2 / Math.PI)
  .translate([width / 2, height / 2])
  .precision(0.1);

let projection_state = d3
  .geoAlbersUsa()
  .scale(700)
  .translate([width /2, height/2 ])
;


  // END PROJECTIONS

let projection = projection_state;

let path = d3.geoPath().projection(projection);

// ADD GRATICULE (MAP GRID)
let graticule = d3.geoGraticule().step([20, 20]);

// svg.append("path").datum(graticule).attr("class", "graticule").attr("d", path);

let getCentroid = function (mapData) {
  // console.log("getCentroid: "+mapData.name);
  let lat = wrkt_viz.data.stateData[mapData.name].lat;
  let lng = wrkt_viz.data.stateData[mapData.name].lon;
  // console.log("lng:"+lng +" lat:"+lat);
  // console.log(projection([lng, lat]));
  return projection([lng, lat]);
};

let radiusScale = d3
  .scaleSqrt()
  .range([wrkt_viz.MIN_CENTROID_RADIUS, wrkt_viz.MAX_CENTROID_RADIUS]);

let cnameToState = {};

export let initMap = function (us_country, names) {
  console.log('initMap');
  // console.log(us_country);
  // geojson objects extracted from topojson features
  let land = topojson.feature(us_country, us_country.objects.nation), 
    states = topojson.feature(us_country, us_country.objects.states).features,
    borders = topojson.mesh(us_country, us_country.objects.states, function (a, b) {
      return a !== b;
    })
  ;

  let idToState = {};
  states.forEach(function (c) {
    idToState[c.id] = c;
  });

  cnameToState = {};
  for (let n in names){
    cnameToState[names[n].name] = idToState[names[n].id];
  }

  // MAIN WORLD MAP
  svg
    .insert("path", ".graticule")
    .datum(land)
    .attr("class", "land")
    .attr("d", path);

  // WINNING COUNTRIES
  svg.insert("g", ".graticule").attr("class", "states");

  // COUNTRIES VALUE-INDICATORS
  svg.insert("g").attr("class", "centroids");

  // BOUNDRY MARKS
  svg
    .insert("path", ".graticule")
    // filter separates exterior from interior arcs...
    .datum(borders)
    .attr("class", "boundary")
    .attr("d", path);
};

let tooltip = d3.select("#race_map_tooltip");
let updateMap = function (stateData) {
  console.log('updateMap');
  let mapData = (wrkt_viz.mapData = stateData
    .filter((d) => d.value > 0)
    .map(function (d) {
      return {
        geo: cnameToState[d.key],
        name: d.key,
        number: d.value,
      };
    }));

  let maxWinners = d3.max(mapData.map((d) => d.number));
  // DOMAIN OF VALUE-INDINCATOR SCALE
  radiusScale.domain([0, maxWinners]);

  let states = svg
    .select(".states")
    .selectAll(".state")
    .data(mapData, (d) => d.name);

  states
    .join(
      (enter) => {
        return enter
          .append("path")
          .attr("class", "state")
          .attr("name", (d) => d.name)
          .on("mouseenter", function (event) {
            // console.log('Entered ' + d.name);
            let state = d3.select(this);
            if (!state.classed("visible")) {
              return;
            }

            let cData = state.datum();
            let prize_string =
              cData.number === 1 ? " race in " : " races in ";
            tooltip.select("h2").text(cData.name);
            tooltip
              .select("p")
              .text(cData.number + prize_string + wrkt_viz.activeDistance);
            let borderColor =
              wrkt_viz.activeDistance === wrkt_viz.ALL_DISTANCES
                ? "goldenrod"
                : wrkt_viz.raceFill(wrkt_viz.activeDistance);
            tooltip.style("border-color", borderColor);

            let w = parseInt(tooltip.style("width")),
              h = parseInt(tooltip.style("height"));

            let mouseCoords = d3.pointer(event);
            tooltip.style("top", mouseCoords[1] - h + "px");
            tooltip.style("left", mouseCoords[0] - w / 2 + "px");

            d3.select(this).classed("active", true);
          })
          .on("mouseout", function (d) {
            tooltip.style("left", "-9999px");
            d3.select(this).classed("active", false);
          });
      },
      (update) => update,
      (exit) => {
        return exit
          .classed("visible", false)
          .transition()
          .duration(wrkt_viz.TRANS_DURATION)
          .style("opacity", 0);
      }
    )
    .classed("visible", true)
    .transition()
    .duration(wrkt_viz.TRANS_DURATION)
    .style("opacity", 1)
    .attr("d", (d) => path(d.geo))
  ;

  let centroids = svg
    .select(".centroids")
    .selectAll(".centroid")
    .data(mapData, (d) => d.name);

  centroids
    .join(
      (enter) => {
        return enter
          .append("circle")
          .attr("class", "centroid")
          .attr("name", (d) => d.name)
          .attr("cx", (d) => getCentroid(d)[0])
          .attr("cy", (d) => getCentroid(d)[1]);
      },
      (update) => update,
      (exit) => exit.style("opacity", 0)
    )
    .classed("active", (d) => d.name === wrkt_viz.activeDistance)
    .transition()
    .duration(wrkt_viz.TRANS_DURATION)
    .style("opacity", 1)
    .attr("r", (d) => radiusScale(+d.number));
};

wrkt_viz.callbacks.push(() => {
  let data = wrkt_viz.getStateData();
  updateMap(data);
});
