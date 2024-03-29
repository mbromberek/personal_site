import wrkt_viz from './wrkt_viz_core.mjs'
import { initMenu } from './wrkt_viz_menu.mjs'
import { initMap } from './wrkt_viz_states_map.mjs'
import './wrkt_viz_race_bar.mjs'
import './wrkt_viz_race_details.mjs'
import './wrkt_viz_race_year.mjs'


Promise.all([
  race_mileage_lst, 
  race_dist_dict, 
  states_topo_json,
  states_data,
]).then(initChart);

function initChart([race_mileage, race_dist_dict, statesMap, stateNames]) {
  console.log('initChart');
  console.log(stateNames);

  // Store Race Dataset
  wrkt_viz.data.race_mileage = race_mileage;
  // console.log(race_dist_dict);
  wrkt_viz.race_dist_mapping = race_dist_dict;
  wrkt_viz.data.stateData = stateNames;

  // Get Race Distances sorted
  let items = Object
    .keys(wrkt_viz.race_dist_mapping).map(
      (key) => {return[key,wrkt_viz.race_dist_mapping[key]] }
  );
  items.sort(
    (first, second) => {return second[1] - first[1] } //descending
  );
  wrkt_viz.RACE_DISTANCES = items.map(
    (e) => {return e[0] }
  );

  wrkt_viz.raceFill = function (category) {
    let i = wrkt_viz.RACE_DISTANCES.indexOf(category);
    return d3.schemeCategory10[i];
  };
  
  
  
  // MAKE OUR FILTER AND ITS DIMENSIONS
  wrkt_viz.makeFilterAndDimensions(race_mileage)

  // INITIALIZE MENU AND MAP
  initMenu();
  initMap(statesMap, stateNames);
  // TRIGGER UPDATE WITH FULL WINNERS' DATASET
  wrkt_viz.onDataChange()
}
