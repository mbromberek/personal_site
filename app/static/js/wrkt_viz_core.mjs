let wrkt_viz = {};
// nbviz.ALL_CATS = "All Categories";
wrkt_viz.TRANS_DURATION = 2000;
// nbviz.MAX_CENTROID_RADIUS = 30;
// nbviz.MIN_CENTROID_RADIUS = 2;
wrkt_viz.COLORS = { palegold: "#E6BE8A" };

wrkt_viz.data = {};
// nbviz.valuePerCapita = 0;
// nbviz.activeCountry = null;
// nbviz.activeCategory = nbviz.ALL_CATS;

// nbviz.CATEGORIES = [
//   "Chemistry",
//   "Economics",
//   "Literature",
//   "Peace",
//   "Physics",
//   "Physiology or Medicine",
// ];

// nbviz.categoryFill = function (category) {
//   let i = nbviz.CATEGORIES.indexOf(category);
//   return d3.schemeCategory10[i];
// };
/*
nbviz.nestDataByYear = function (entries) {
  let yearGroups = d3.group(entries, (d) => d.year);
  let keyValues = Array.from(yearGroups, ([key, values]) => {
    let year = key;
    let prizes = values;
    prizes = prizes.sort((p1, p2) => (p1.category > p2.category ? 1 : -1));
    return { key: year, values: prizes };
  });
  console.log(keyValues);
  return keyValues;
};*/

wrkt_viz.makeFilterAndDimensions = function (race_mileage) {
  // ADD OUR FILTER AND CREATE CATEGORY DIMENSIONS
  wrkt_viz.filter = crossfilter(race_mileage);
  wrkt_viz.yearDim = wrkt_viz.filter.dimension(function (o) {
    return o.year;
  });
  wrkt_viz.distDim = wrkt_viz.filter.dimension(function (o) {
    return o.dist_mi;
  });
  /*
  nbviz.categoryDim = nbviz.filter.dimension(function (o) {
    return o.category;
  });

  nbviz.genderDim = nbviz.filter.dimension(function (o) {
    return o.gender;
  });*/
};
/*
nbviz.filterByCountries = function (countryNames) {
  if (!countryNames.length) {
    nbviz.countryDim.filter();
  } else {
    nbviz.countryDim.filter(function (name) {
      return countryNames.indexOf(name) > -1;
    });
  }

  if (countryNames.length === 1) {
    nbviz.activeCountry = countryNames[0];
  } else {
    nbviz.activeCountry = null;
  }
};

nbviz.filterByCategory = function (cat) {
  nbviz.activeCategory = cat;

  if (cat === nbviz.ALL_CATS) {
    nbviz.categoryDim.filter();
  } else {
    nbviz.categoryDim.filter(cat);
  }
};*/

wrkt_viz.getMonthlyData = function () {
  console.log('getMonthlyData');
  let data = wrkt_viz.data.month_mileage;
  /*let countryGroups = nbviz.countryDim.group().all();

  // make main data-ball
  let data = countryGroups
    .map(function (c) {
      let cData = nbviz.data.countryData[c.key];
      let value = c.value;
      // if per-capita value then divide by pop. size
      if (nbviz.valuePerCapita) {
        value /= cData.population;
      }
      return {
        key: c.key,
        value: value,
        code: cData.alpha3Code,
        // population: cData.population
      };
    })
    .sort(function (a, b) {
      return b.value - a.value; // descending
    });*/

  return data;
};

wrkt_viz.getRaceYearlyData = function () {
  console.log('getRaceYearlyData');
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
      // if per-capita value then divide by pop. size
      /*if (nbviz.valuePerCapita) {
        value /= cData.population;
      }*/
      return {
        key: c.key,
        value: value,
        code: c.key,
        // population: cData.population
      };
    })
    .sort(function (a, b) {
      return a.key - b.key; // ascending
    });

  return data;
};

wrkt_viz.callbacks = [];

wrkt_viz.onDataChange = function () {
  console.log('onDataChange');
  wrkt_viz.callbacks.forEach((cb) => cb());
};

export default wrkt_viz;
