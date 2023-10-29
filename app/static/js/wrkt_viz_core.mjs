let wrkt_viz = {};

wrkt_viz.TRANS_DURATION = 2000;
wrkt_viz.MAX_CENTROID_RADIUS = 20;
wrkt_viz.MIN_CENTROID_RADIUS = 2;
wrkt_viz.MAP_SCALE = 700;
wrkt_viz.COLORS = { palegold: "#E6BE8A" };

wrkt_viz.data = {};

wrkt_viz.ALL_DISTANCES = "All Distances";
wrkt_viz.activeDistance = wrkt_viz.ALL_DISTANCES;
wrkt_viz.ALL_STATES = "All States";
wrkt_viz.activeState = wrkt_viz.ALL_STATES;

wrkt_viz.nestDataByYear = function (entries) {
  // console.log('nestDataByYear');
  let yearGroups = d3.group(entries, (d) => d.year);
  let keyValues = Array.from(yearGroups, ([key, values]) => {
    let year = key;
    let races = values;
    races = races.sort((p1, p2) => (p1.category > p2.category ? 1 : -1));
    return { key: year, values: races };
  });
  // console.log(keyValues);
  return keyValues;
};

wrkt_viz.makeFilterAndDimensions = function (race_mileage) {
  // console.log('makeFilterAndDimensions Start');
  // ADD OUR FILTER AND CREATE DIMENSIONS
  wrkt_viz.filter = crossfilter(race_mileage);
  //Used for bar chart for total mileage per year
  wrkt_viz.yearDim = wrkt_viz.filter.dimension(function (o) {
    return o.year;
  });
  //Used for filtering to only show certain distances
  wrkt_viz.distDim = wrkt_viz.filter.dimension(function (o) {
    // console.log('wrkt_viz.distDim filter');
    return o.distance;
    // return o.dist_mi
  });
  wrkt_viz.stateDim = wrkt_viz.filter.dimension(function (o) {
    // console.log('wrkt_viz.stateDim filter');
    return o.state;
  });

  console.log('makeFilterAndDimensions End');
};

wrkt_viz.filterByDistances = function (distance) {
  // console.log('filterByDistances Start:' +distance + ':');
  wrkt_viz.activeDistance = distance;

  // console.log(wrkt_viz.yearDim.group().all());
  // console.log(wrkt_viz.distDim.group().all());
 
  if (distance == wrkt_viz.ALL_DISTANCES) {
    // console.log('filterByDistances ALL_DISTANCES:' + distance + ':');
    wrkt_viz.distDim.filterAll();
  }else {
    // console.log('filterByDistances one distance:' + distance + ':');
    wrkt_viz.distDim.filter(distance);
  }
  // console.log(wrkt_viz.yearDim.group().all());
  // console.log('filterByDistances End');
};

wrkt_viz.filterByStates = function (state) {
  console.log('filterByStates Start:' +state + ':');
  wrkt_viz.activeDistance = state;

  if (state == wrkt_viz.ALL_STATES) {
    wrkt_viz.stateDim.filterAll();
  }else {
    wrkt_viz.stateDim.filter(state);
  }
  // console.log(wrkt_viz.yearDim.group().all());
  console.log('filterByStates End');
};


wrkt_viz.getMonthlyData = function () {
  // console.log('getMonthlyData');
  let data = wrkt_viz.data.month_mileage;

  return data;
};

wrkt_viz.getRaceYearlyData = function () {
  // console.log('getRaceYearlyData Start');
  // let raceYrGroups = wrkt_viz.yearDim.group().all();
  // Group by year and sum distance
  let raceYrGroups = wrkt_viz.yearDim.group().reduceSum(function(d){
    return d.dist_mi;
  }).all();
  // console.log(raceYrGroups);

  // make main data-ball
  let data = raceYrGroups
    .map(function (c) {
      // let cData = wrkt_viz.data.race_mileage[c.key];
      let value = c.value;
      return {
        key: c.key,
        value: value,
        code: c.key,
      };
    })
    .sort(function (a, b) {
      return a.key - b.key; // ascending
    });
  // console.log('getRaceYearlyData End');
  return data;
};

wrkt_viz.getStateData = function () {
  let stateGroups = wrkt_viz.stateDim.group().all();

  // make main data-ball
  let data = stateGroups
    .map(function (c) {
      let cData = wrkt_viz.data.stateData[c.key];
      let value = c.value;
      return {
        key: c.key,
        value: value,
        // code: cData.alpha3Code,
        code: c.key,
        // population: cData.population
      };
    })
    .sort(function (a, b) {
      return b.value - a.value; // descending
    });

  return data;
};

wrkt_viz.callbacks = [];

wrkt_viz.onDataChange = function () {
  console.log('onDataChange');
  wrkt_viz.callbacks.forEach((cb) => cb());
};

export default wrkt_viz;
