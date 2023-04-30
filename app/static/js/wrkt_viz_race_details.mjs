import wrkt_viz from "./wrkt_viz_core.mjs";

let updateList = function (data) {
  let svg, rows, cells;
  // Sort the winners' data by year
  data = data.sort(function (a, b) {
    return +b.year - +a.year;
  });
  // Bind our winners' data to the table rows

  svg = d3.select("#race_list tbody");
  rows = svg.selectAll("tr").data(data);
  // Fade out excess rows over 2 seconds

  rows.join(
    (enter) => {
      return enter.append("tr").on("click", function (event, d) {
        console.log("You clicked a row " + JSON.stringify(d));
        display_race(d);
      });
    },
    (update) => update,
    (exit) => {
      return exit
        .transition()
        .duration(wrkt_viz.TRANS_DURATION)
        .style("opacity", 0)
        .remove();
    }
  );

  cells = svg
    .selectAll("tr")
    .selectAll("td")
    .data(function (d) {
      return [d.wrkt_dt, d.training_type, d.dur];
    });
  // Append data cells, then set their text
  cells.join("td").text((d) => d);
  // Display a random winner if data is available
  if (data.length) {
    display_race(data[Math.floor(Math.random() * data.length)]);
  }
};

let display_race = function (wData) {
  console.log('display_race');
  
  let nw = d3.select("#race_det");

  nw.select("#race_name").text(wData.training_type);
  nw.style("border-color", wrkt_viz.raceFill(wData.distance));

  nw.selectAll(".property span").text(function (d) {
    var property = d3.select(this).attr("name");
    return wData[property];
  });

  /*nw.select("#biobox").html(wData.mini_bio);
  // Add an image if available, otherwise remove the old one
  if (wData.bio_image) {
    nw.select("#picbox img")
      .attr("src", "static/images/winners/" + wData.bio_image)
      .style("display", "inline");
  } else {
    nw.select("#picbox img").style("display", "none");
  }

  nw.select("#readmore a").attr(
    "href",
    "http://en.wikipedia.org/wiki/" + wData.name
  );*/
};

wrkt_viz.callbacks.push(() => {
  let data = wrkt_viz.distDim.top(Infinity);
  updateList(data);
});
