import wrkt_viz from "./wrkt_viz_core.mjs";

/*
let catList = [nbviz.ALL_CATS].concat(nbviz.CATEGORIES);

let catSelect = d3.select("#cat-select select");

catSelect
  .selectAll("option")
  .data(catList)
  .join("option")
  .attr("value", (d) => d)
  .html((d) => d);

catSelect.on("change", function (d) {
  let category = d3.select(this).property("value");
  nbviz.filterByCategory(category);
  nbviz.onDataChange();
});

d3.select("#gender-select select").on("change", function (d) {
  let gender = d3.select(this).property("value");
  if (gender === "All") {
    // Reset the filter to all genders
    nbviz.genderDim.filter();
  } else {
    nbviz.genderDim.filter(gender);
  }
  nbviz.onDataChange();
});
*/

// Distance selector

export let initMenu = function () {
  
  let MARATHON_RACES = "Marathon";
  let HALF_MARATHON_RACES = "Half Marathon";

  // let races_dist = wrkt_viz.distDim.group().all();  
  let nats = (wrkt_viz.distSelectGroups = wrkt_viz.distDim
    .group()
    .all()
    .map(function (c) {
      return {
        key: c.key,
        value: c.value,
        dist_val: wrkt_viz.race_dist_mapping[c.key]
      };
    })
    .sort(function (a, b) {
      return b.dist_val - a.dist_val; // descending
    }));

  let fewWinners = { 1: [], 2: [] };
  let selectData = [wrkt_viz.ALL_DISTANCES];

  nats.forEach(function (o) {
    selectData.push(o.key);
  });

  let distSelect = d3.select("#dist_select select");

  distSelect
    .selectAll("option")
    .data(selectData)
    .join("option")
    .attr("value", (d) => d)
    .html((d) => d);

  distSelect.on("change", function (d) {
    console.log("distSelect change Start");

    let distance = d3.select(this).property("value");
    console.log('distance: ' + distance);

    wrkt_viz.filterByDistances(distance);
    wrkt_viz.onDataChange();
    console.log("distSelect change End");
  });


  let state_lst = (wrkt_viz.stateSelectGroups = wrkt_viz.stateDim
    .group()
    .all()
    .map(function (c) {
      return {
        key: c.key,
        value: c.value,
        // dist_val: wrkt_viz.race_dist_mapping[c.key]
      };
    })
    .sort(function (a, b) {
      return b.dist_val - a.dist_val; // descending
    }));

  let stateSelectData = [wrkt_viz.ALL_STATES];
  state_lst.forEach(function (o) {
    stateSelectData.push(o.key);
  });

  let stateSelect = d3.select("#state_select select");

  stateSelect
    .selectAll("option")
    .data(stateSelectData)
    .join("option")
    .attr("value", (d) => d)
    .html((d) => d)
  ;

  stateSelect.on("change", function (d) {
    console.log("stateSelect change Start");

    let state = d3.select(this).property("value");
    console.log('state: ' + state);

    wrkt_viz.filterByStates(state);
    wrkt_viz.onDataChange();
    console.log("stateSelect change End");
  });

};
