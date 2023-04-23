import wrkt_viz from './wrkt_viz_core.mjs'
import { initMenu } from './wrkt_viz_menu.mjs'
// import { initMap } from './nbviz_map.mjs'
import './wrkt_viz_race_bar.mjs'
// import './nbviz_details.mjs'
// import './nbviz_time.mjs'


initChart(race_mileage_lst, race_dist_dict);


function initChart(race_mileage, race_dist_dict) {
  console.log('initChart');

  // Store Race Dataset
  wrkt_viz.data.race_mileage = race_mileage;
  console.log(race_dist_dict);
  wrkt_viz.race_dist_mapping = race_dist_dict;

  // MAKE OUR FILTER AND ITS DIMENSIONS
  wrkt_viz.makeFilterAndDimensions(race_mileage)

  // INITIALIZE MENU AND MAP
  initMenu();
  // initMap(worldMap, countryNames)
  // TRIGGER UPDATE WITH FULL WINNERS' DATASET
  wrkt_viz.onDataChange()
}
