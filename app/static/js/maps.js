var map;
var lapMarkers;
var mileMarkers;

//For generating map
var mapbox_url_parms;
var end_mark;
var end_circle_marker;
const METERS_TO_MILES = 0.000621371;
var tot_dist_mi = 0;
var map_coord_lst = [];
var map_line_lst = [];
//End of For generating map

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
    end_mark = {position:lat_lon[lat_lon.length -1], icon:endCircle, popup: 'Run End'};
    // var mile_one_mark = {position:[40.732828164473200, -89.57437014207240], icon:whiteCircle, popup: 'Mile 1'};

    var milePoints = [];
    var lapPoints = [];
    var pausePoints = []
    // console.log(map_json.mile_markers);

    map_json.mile_markers.forEach(function(marker, index){
        // console.log(marker);
        milePoints.push(create_marker(marker, mile_marker_color));
    });
    // console.log(milePoints);
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

function create_marker(marker, marker_color, fill_opacity){
    if (fill_opacity === undefined){
        fill_opacity = "0.8";
    }
    let mile_marker_json = {
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
            "fillOpacity": fill_opacity
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

function showMap(map_json, track_clicks) {
    console.log('maps.js showMap');

    apiKey = map_json.key;
    zoom = map_json.zoom;
    center_lon = map_json.center.lon;
    center_lat = map_json.center.lat;
    lat_lon = map_json.coordinates;
    mapbox_url_parms = map_json.mapbox_url_parms;
    
    tot_dist_mi = map_json.total_distance;
    tot_dist_elem = document.getElementById('tot_dist');
    tot_dist_elem.innerHTML = Math.round(tot_dist_mi *100)/100;
    
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
    map_coord_lst.push( new Map([['lat_lon',lat_lon],['dist',tot_dist_mi]]) );
    
    var start_mark = {position:lat_lon[0], icon:startCircle, popup: 'Run Start'}
    end_lat_lon = lat_lon[lat_lon.length -1]
    end_mark = {position:end_lat_lon, icon:endCircle, popup: 'Run End'};


    map = L.map('map', {scrollWheelZoom: false} ).setView(run_map_center['pos'], run_map_center['zoom']);
    
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: map_json.max_zoom,
      id: 'mapbox/streets-v11',
      tileSize: 512,
      zoomOffset: -1,
      accessToken: apiKey
    }).addTo(map);
    
    
    let polyline = L.polyline(polylinePoints, wrktLine).addTo(map);
    map_line_lst.push(polyline);
    
    // L.marker(start_mark['position'], {icon: start_mark['icon']}).addTo(map).bindPopup(start_mark['popup']);
    L.circleMarker(start_mark['position'], start_mark['icon']) .addTo(map).bindPopup(start_mark['popup']);
    end_circle_marker = L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map).bindPopup(end_mark['popup']);
    


    if (track_clicks == true){
        map.on('click', function(ev){
            saveMapClick(ev)
        });
    }
    
    console.log('End: showMap');

}

function saveMapClick(ev){
    logMapClick(ev);
    //TODO Might need a check for double click and ignore second click. 
    console.log('Current End: ' + end_lat_lon);
    let lat_lon = map.mouseEventToLatLng(ev.originalEvent);
    let new_lat = Math.round(lat_lon.lat *10000) /10000;
    let new_lon = Math.round(lat_lon.lng *10000) /10000;
    if (document.getElementById('follow_roads').checked){
        let url_coord = end_lat_lon[1] + ',' + end_lat_lon[0] + ';' + new_lon + ',' + new_lat;
        console.log('url_coord:' + url_coord);
        
        base_url = 'https://api.mapbox.com/directions/v5/mapbox/walking'
        url = base_url + '/' + url_coord + '?' + mapbox_url_parms
        console.log(url);
        
        //Call OpenBox to get direction from current end point to new point
        $.get(url
        ).done(function(response){
            new_directions(response);
        }).fail(function(){
            console.error("Error: Could not contact server.");
        })
        ;
    }else{
        //Draw straight line between end coord and new point
        new_point_to_point(end_lat_lon, [new_lat,new_lon]);
    }
}

function logMapClick(ev){
    /**
    Log latitude and longitude of point clicked on map
    */
    let latlng = map.mouseEventToLatLng(ev.originalEvent);
    console.log(latlng.lat + ', ' + latlng.lng);
}

function new_directions(response){
    // console.log(response);
    let route = response['routes'][0];
    let leg = route['legs'][0];
    let steps = leg['steps'];
    let coordinate_lst = [];
    new_dist_m = 0;
    // console.log(steps);
    for (i=0; i<steps.length; i++){
        new_dist_m += steps[i]['distance'];
        coordinates = steps[i]['geometry']['coordinates']
        // console.log(coordinates);
        for (j=0; j<coordinates.length; j++){
            coordinate = coordinates[j];
            // longitude, latitude
            coordinate_lst.push([coordinate[1],coordinate[0]]);
        }
    }
    new_end_point(coordinate_lst, new_dist_m*METERS_TO_MILES);
}

function new_point_to_point(start_pt, end_pt){
    let dist_m = get_distance(start_pt, end_pt);
    
    new_end_point([start_pt, end_pt], dist_m*METERS_TO_MILES);
}

/**
Uses Haverstine method to get distance between start_pt and end_pt
distance is returned in meters
 */
function get_distance(start_pt, end_pt){
    const R = 6371e3; // metres
    const lat = 0;
    const lon = 1

    let lat_radian_1 = start_pt[lat]  * Math.PI/180;
    let lat_radian_2 = end_pt[lat]  * Math.PI/180;
    // const φ1 = lat1 * Math.PI/180; // φ, λ in radians
    // const φ2 = lat2 * Math.PI/180;
    // const Δφ = (lat2-lat1) * Math.PI/180;
    // const Δλ = (lon2-lon1) * Math.PI/180;
    const delta_lat = (end_pt[lat] - start_pt[lat]) * Math.PI/180;
    const delta_lon = (end_pt[lon] - start_pt[lon]) * Math.PI/180;
    
    const a = Math.sin(delta_lat/2) * Math.sin(delta_lat/2) +
              Math.cos(lat_radian_1) * Math.cos(lat_radian_2) *
              Math.sin(delta_lon/2) * Math.sin(delta_lon/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    
    const d = R * c; // in metres
    return d;
}

function new_end_point(coordinate_lst, dist_mi){
    map_coord_lst.push( new Map([['lat_lon',coordinate_lst],['dist',dist_mi]]) );
    // console.log(coordinate_lst);
    tot_dist_mi += dist_mi;
    document.getElementById('tot_dist').innerHTML = Math.round(tot_dist_mi *100)/ 100;
    
    // let polylinePoints = coordinate_lst;
    let polyline = L.polyline(coordinate_lst, wrktLine).addTo(map);
    map_line_lst.push(polyline);
    
    map.removeLayer(end_circle_marker);
    end_lat_lon = coordinate_lst[coordinate_lst.length -1];
    console.log('New End: ' + end_lat_lon);
    let end_mark = {position:end_lat_lon, icon:endCircle, popup: 'Workout End'};
    end_circle_marker = L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map).bindPopup(end_mark['popup']);
    
    console.log(map_coord_lst);
}

function undo_new_point(){
    console.log('undo_new_point');
    if (map_line_lst.length >1){
        let rm_line = map_line_lst.pop();
        let rm_coord_lst = map_coord_lst.pop();
        map.removeLayer(rm_line);
        map.removeLayer(end_circle_marker);
        
        
        let last_coord_lst = map_coord_lst[map_coord_lst.length-1];
        console.log(last_coord_lst);
        end_lat_lon = last_coord_lst.get('lat_lon')[last_coord_lst.get('lat_lon').length-1];
        
        tot_dist_mi -= rm_coord_lst.get('dist');
        document.getElementById('tot_dist').innerHTML = Math.round(tot_dist_mi *100)/ 100;
        
        let end_mark = {position:end_lat_lon, icon:endCircle, popup: 'Workout End'};
        end_circle_marker = L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map)   .bindPopup(end_mark['popup']);
        console.log(map_coord_lst);
    }else{
        alert('Cannot remove initial line');
    }
}

