var map;
var lapMarkers;
var mileMarkers;

var endCircle = {
    radius: 6,
    fillColor: 'red',
    color: '#000',
    weight: 1,
    opacity: 1,
    fillOpacity: 0.7
}
var startCircle = {
    radius: 6,
    fillColor: 'green',
    color: '#000',
    weight: 1,
    opacity: 1,
    fillOpacity: 0.7
}
var blueCircle = {
    radius: 6,
    fillColor: 'blue',
    color: '#000',
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
}
var lightblueCircle = {
    radius: 6,
    fillColor: 'lightblue',
    color: '#000',
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
}
var whiteCircle = {
    radius: 6,
    fillColor: 'white',
    color: '#000',
    weight: 1,
    opacity: 1,
    fillOpacity: 0.8
}

var wrktLine = {
    color: 'blue',
    weight: 3,
    opacity: 0.6
}

var greenIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    // iconSize: [25, 41],
    iconSize: [20, 32],
    iconAnchor: [6, 20],
    popupAnchor: [1, -17],
    shadowSize: [20, 20]
});

var blueIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    // iconSize: [25, 41],
    iconSize: [20, 32],
    iconAnchor: [6, 20],
    popupAnchor: [1, -17],
    shadowSize: [20, 20]
});

mile_marker_color = 'white'
lap_marker_color = 'orange'
pause_marker_color = 'yellow'

function initMap(map_json, show_laps, show_miles, track_clicks) {
    console.log('maps.js initMap');
    show_pauses = true;
    // console.log(map_json);
    apiKey = map_json.key;
    zoom = map_json.zoom;
    center_lon = map_json.center.lon;
    center_lat = map_json.center.lat;
    lat_lon = map_json.lat_lon;

    var run_map_center = { pos:[center_lat, center_lon], zoom:zoom };
    var greenIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        // iconSize: [25, 41],
        iconSize: [12, 20],
        iconAnchor: [6, 20],
        popupAnchor: [1, -17],
        shadowSize: [20, 20]
    });


    var polylinePoints = lat_lon;
    var start_mark = {position:lat_lon[0], icon:startCircle, popup: 'Run Start'}
    var end_mark = {position:lat_lon[lat_lon.length -1], icon:endCircle, popup: 'Run End'};
    // var mile_one_mark = {position:[40.732828164473200, -89.57437014207240], icon:whiteCircle, popup: 'Mile 1'};

    var milePoints = [];
    var lapPoints = [];
    var pausePoints = []
    // console.log(map_json.mile_markers);

    map_json.mile_markers.forEach(function(marker, index){
        // console.log(marker);
        milePoints.push(create_marker(marker, mile_marker_color));
    });
    console.log(milePoints);
    map_json.lap_markers.forEach(function(marker, index){
        // console.log(marker);
        lapPoints.push(create_marker(marker, lap_marker_color));
    });
    map_json.pause_markers.forEach(function(marker, index){
        // console.log(marker);
        pausePoints.push(create_marker(marker, pause_marker_color));
    });

    map = L.map('map', {scrollWheelZoom: false} ).setView(run_map_center['pos'], run_map_center['zoom']);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: map_json.max_zoom,
      id: 'mapbox/streets-v11',
      tileSize: 512,
      zoomOffset: -1,
      accessToken: apiKey
    }).addTo(map);


    var polyline = L.polyline(polylinePoints, wrktLine).addTo(map);

    // L.marker(start_mark['position'], {icon: start_mark['icon']}).addTo(map).bindPopup(start_mark['popup']);
    L.circleMarker(start_mark['position'], start_mark['icon']) .addTo(map).bindPopup(start_mark['popup']);
    L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map).bindPopup(end_mark['popup']);

    mileMarkers = new L.geoJson(milePoints, {
        pointToLayer: function(feature, latlng) {
            return new L.CircleMarker([latlng.lng, latlng.lat],  feature.properties);
        },
        onEachFeature: function(feature, layer) {
            var mileText = L.tooltip({
                permanent: true,
                direction: 'center',
                className: 'text'
            })
            .setContent(feature.properties.text)
            .setLatLng(layer.getLatLng());
            // mileText.addTo(map);
            layer.bindTooltip(mileText);

            // var text2 = L.tooltip({
            //     direction: 'top',
            //     className: 'text'
            // })
            // .setContent('Mile ' + feature.properties.text)
            // .setLatLng(layer.getLatLng());
            // layer.bindTooltip(text2);
        }
    });
    if (show_miles == true){
        mileMarkers.addTo(map);
    }

    lapMarkers = new L.geoJson(lapPoints, {
        pointToLayer: function(feature, latlng) {
            return new L.CircleMarker([latlng.lng, latlng.lat],  feature.properties);
        },
        onEachFeature: function(feature, layer) {
            var lapText = L.tooltip({
                permanent: true,
                direction: 'center',
                className: 'text'
            })
            .setContent(feature.properties.text)
            .setLatLng(layer.getLatLng());
            layer.bindTooltip(lapText);
        }
    });
    if (show_laps == true){
        lapMarkers.addTo(map);
    }

    pauseMarkers = new L.geoJson(pausePoints, {
        pointToLayer: function(feature, latlng) {
            return new L.CircleMarker([latlng.lng, latlng.lat],  feature.properties);
        },
        onEachFeature: function(feature, layer) {
            var pauseText = L.tooltip({
                permanent: true,
                direction: 'center',
                className: 'text'
            })
            .setContent(feature.properties.text)
            .setLatLng(layer.getLatLng());
            layer.bindTooltip(pauseText);
        }
    });
    if (show_pauses == true){
        pauseMarkers.addTo(map);
    }

    if (track_clicks == true){
        map.on('click', function(ev){
            saveMapClick(ev)
        });
    }

    console.log('End: leaflet_maps initMap');
}

function create_marker(marker, marker_color){
    var mile_marker_json = {
        "type": "Feature",
        "geometry": {
            "type": "Point",
            "coordinates": [marker.lat, marker.lon]
        },
        "properties": {
            "text": marker.nbr.toString(),
            "radius": 7,
            "fillColor": marker_color,
            "color": '#000',
            "weight": 1,
            "opacity": 1,
            "fillOpacity": "0.8"
        }
    };
    return mile_marker_json
}

function toggleMapMarker(chkId){
    // console.log('toggleMapMarker');
    if (document.getElementById(chkId).checked){
        console.log(chkId + " is checked");
        if (chkId == 'show_laps'){
            lapMarkers.addTo(map);
        }else if (chkId == 'show_miles'){
            mileMarkers.addTo(map);
        }
    }else{
        console.log(chkId + " is not checked");
        if (chkId == 'show_laps'){
            map.removeLayer(lapMarkers);
        }else if (chkId == 'show_miles'){
            map.removeLayer(mileMarkers);
        }

    }
}

function locationMap(map_json, lat, lon, radius){
    zoom = map_json.zoom;
    apiKey = map_json.key;
    center_lon = lon;
    center_lat = lat;
    // lat_lon = map_json.lat_lon;
    var run_map_center = { pos:[center_lat, center_lon], zoom:zoom };
    map = L.map('map', {scrollWheelZoom: false} ).setView(run_map_center['pos'], run_map_center['zoom']);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: map_json.max_zoom,
      id: 'mapbox/streets-v11',
      tileSize: 512,
      zoomOffset: -1,
      accessToken: apiKey
    }).addTo(map);


    radiusCircle = lightblueCircle;
    radiusCircle['radius'] = radius*1609.3;
    radiusCircle['fillOpacity'] = 0.5;
    radiusCircle['color'] = 'blue';
    var radius_mark = {position:[lat, lon], icon:radiusCircle};
    L.circle(radius_mark['position'], radius_mark['icon']).addTo(map);

    var location_mark = {position:[lat, lon], icon:startCircle};
    L.circleMarker(location_mark['position'], location_mark['icon']).addTo(map);
}

function logMapClick(ev){
    /**
    Log latitude and longitude of point clicked on map
    */
    var latlng = map.mouseEventToLatLng(ev.originalEvent);
    console.log(latlng.lat + ', ' + latlng.lng);
}

function saveMapClick(ev){
    logMapClick(ev);
}


function initEventMap(map_json, track_clicks) {
    console.log('maps.js initEventMap');
    // console.log(map_json);
    apiKey = map_json.key;
    zoom = map_json.zoom;
    center_lon = map_json.center.lon;
    center_lat = map_json.center.lat;
    lat_lon = map_json.lat_lon;

    var run_map_center = { pos:[center_lat, center_lon], zoom:zoom };


    var polylinePoints = lat_lon;
    // var end_mark = {position:lat_lon[lat_lon.length -1], icon:endCircle, popup: 'Run End'};
    // var mile_one_mark = {position:[40.732828164473200, -89.57437014207240], icon:whiteCircle, popup: 'Mile 1'};

    var milePoints = [];
    // console.log(map_json.mile_markers);

    map_json.mile_markers.forEach(function(marker, index){
        // console.log(marker);
        milePoints.push(create_marker(marker, mile_marker_color));
    });
    console.log(milePoints);

    map = L.map('map', {scrollWheelZoom: false} ).setView(run_map_center['pos'], run_map_center['zoom']);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: map_json.max_zoom,
      id: 'mapbox/streets-v11',
      tileSize: 512,
      zoomOffset: -1,
      accessToken: apiKey
    }).addTo(map);

    var polyline = L.polyline(polylinePoints, wrktLine).addTo(map);

    startCircle['radius']=8

    var hotel_mark = {position:map_json.loc_lst[0], icon:blueIcon, popup: map_json.loc_lst[0].name, marker:'marker'}
    var start_mark = {position:map_json.loc_lst[1], icon:startCircle, popup: map_json.loc_lst[1].name, marker:'circle'}


    L.marker(hotel_mark['position'], {icon: hotel_mark['icon']}).addTo(map).bindPopup(hotel_mark['popup']);
    L.circleMarker(start_mark['position'], start_mark['icon']) .addTo(map).bindPopup(start_mark['popup']);

    mileMarkers = new L.geoJson(milePoints, {
        pointToLayer: function(feature, latlng) {
            return new L.CircleMarker([latlng.lng, latlng.lat],  feature.properties);
        },
        onEachFeature: function(feature, layer) {
            var mileText = L.tooltip({
                permanent: true,
                direction: 'center',
                className: 'text'
            })
            .setContent(feature.properties.text)
            .setLatLng(layer.getLatLng());
            // mileText.addTo(map);
            layer.bindTooltip(mileText);

            // var text2 = L.tooltip({
            //     direction: 'top',
            //     className: 'text'
            // })
            // .setContent('Mile ' + feature.properties.text)
            // .setLatLng(layer.getLatLng());
            // layer.bindTooltip(text2);
        }
    });
    mileMarkers.addTo(map);

    if (track_clicks == true){
        map.on('click', function(ev){
            saveMapClick(ev)
        });
    }

    console.log('End: initEventMap');
}

function mapSize(fullScreen){
    console.log(fullScreen);

    map = document.getElementById('map');
    map.style.height='1000px';
}
