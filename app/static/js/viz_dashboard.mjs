import wrkt_viz from './wrkt_viz_core.mjs'
import { initMenu } from './wrkt_viz_menu.mjs'
// import { initMap } from './nbviz_map.mjs'
import './wrkt_viz_mthly_bar.mjs'
// import './wrkt_viz_race_bar.mjs'
// import './nbviz_details.mjs'
// import './nbviz_time.mjs'

// Test Data
/*let month_mileage_lst = [
  {code: '2023-02', value:97.4},
  {code: '2023-01', value:217.3},
  {code: '2022-12', value:174.8},
  {code: '2022-11', value:78.5},
  {code: '2022-10', value:215.8}
];*/
initChart(month_mileage_lst);


function initChart(month_mileage) {
  console.log('initChart');
  // console.log(month_mileage);
  // STORE OUR COUNTRY-DATA DATASET
  wrkt_viz.data.month_mileage = month_mileage;
  // wrkt_viz.data.race_mileage = race_mileage;
  // console.log(race_dist_dict);
  // wrkt_viz.race_dist_mapping = race_dist_dict;
  // wrkt_viz.race_dist_mapping = d3.json(race_dist_dict);
  // nbviz.data.winnersData = winnersData
  // MAKE OUR FILTER AND ITS DIMENSIONS
  // wrkt_viz.makeFilterAndDimensions(race_mileage)
  // INITIALIZE MENU AND MAP
  initMenu();
  // initMap(worldMap, countryNames)
  // TRIGGER UPDATE WITH FULL WINNERS' DATASET
  wrkt_viz.onDataChange()
}
