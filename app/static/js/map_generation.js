var map;

//For generating map
var mapbox_url_parms;
var end_mark;
var start_circle_marker;
var end_circle_marker;
const METERS_TO_MILES = 0.000621371;
var tot_dist_mi = 0;
var map_coord_lst = [];
var map_line_lst = [];
var end_lat_lon = [];
var remove_first_map_line = true;
var route_id = '';
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

    map = L.map('map', {scrollWheelZoom: false} ).setView(run_map_center['pos'], run_map_center['zoom']);
    
    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: map_json.max_zoom,
      id: 'mapbox/streets-v11',
      tileSize: 512,
      zoomOffset: -1,
      accessToken: apiKey
    }).addTo(map);

    if (lat_lon.length >0){
        var polylinePoints = lat_lon;
        // map_coord_lst.push( new Map([['lat_lon',lat_lon],['dist',tot_dist_mi]]) );
        map_coord_lst.push({'lat_lon':lat_lon, 'dist':tot_dist_mi});
        
        var start_mark = {position:lat_lon[0], icon:startCircle, popup: 'Run Start'}
        end_lat_lon = lat_lon[lat_lon.length -1]
        end_mark = {position:end_lat_lon, icon:endCircle, popup: 'Run End'};
    
        let polyline = L.polyline(polylinePoints, wrktLine).addTo(map);
        map_line_lst.push(polyline);
        
        // L.marker(start_mark['position'], {icon: start_mark['icon']}).addTo(map).bindPopup(start_mark['popup']);
        start_circle_marker = L.circleMarker(start_mark['position'], start_mark['icon']) .addTo(map).bindPopup(start_mark['popup']);
        end_circle_marker = L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map).bindPopup(end_mark['popup']);
    }
    
    if ('route_id' in map_json){
        route_id = map_json.route_id;
        document.getElementById('save_btn').value = 'Update';
        document.getElementById('route_name').value = map_json.name;
        remove_first_map_line = false; //Cannot remove line from before workout loaded
    }

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
    if (end_lat_lon.length == 0){
        var start_mark = {position:[new_lat,new_lon], icon:startCircle, popup: 'Run Start'}
        start_circle_marker = L.circleMarker(start_mark['position'], start_mark['icon']) .addTo(map).bindPopup(start_mark['popup']);
        end_lat_lon = [new_lat,new_lon];
    } 
    else if (document.getElementById('follow_roads').checked){
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
    // map_coord_lst.push( new Map([['lat_lon',coordinate_lst],['dist',dist_mi]]) );
    map_coord_lst.push({'lat_lon':coordinate_lst, 'dist':dist_mi});
    // console.log(coordinate_lst);
    tot_dist_mi += dist_mi;
    document.getElementById('tot_dist').innerHTML = Math.round(tot_dist_mi *100)/ 100;
    
    // let polylinePoints = coordinate_lst;
    let polyline = L.polyline(coordinate_lst, wrktLine).addTo(map);
    map_line_lst.push(polyline);
    
    if (typeof end_circle_marker !== 'undefined'){
        map.removeLayer(end_circle_marker);
    }
    end_lat_lon = coordinate_lst[coordinate_lst.length -1];
    console.log('New End: ' + end_lat_lon);
    let end_mark = {position:end_lat_lon, icon:endCircle, popup: 'Workout End'};
    end_circle_marker = L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map).bindPopup(end_mark['popup']);
    
    console.log(map_coord_lst);
}

function undo_new_point(){
    console.log('undo_new_point');
    if (map_line_lst.length >1 || remove_first_map_line){
        if (map_line_lst.length == 0){
            //REMOVE START MARKER
            map.removeLayer(start_circle_marker);
        }else{
            let rm_line = map_line_lst.pop();
            let rm_coord_lst = map_coord_lst.pop();
            map.removeLayer(rm_line);
            map.removeLayer(end_circle_marker);
            
            
            let last_coord_lst = map_coord_lst[map_coord_lst.length-1];
            if (typeof last_coord_lst !== 'undefined'){
                console.log(last_coord_lst);
                // end_lat_lon = last_coord_lst.get('lat_lon')[last_coord_lst.get('lat_lon').length-1];
                end_lat_lon = last_coord_lst['lat_lon'][last_coord_lst['lat_lon'].length-1];

                let end_mark = {position:end_lat_lon, icon:endCircle, popup: 'Workout End'};
                end_circle_marker = L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map)   .bindPopup(end_mark['popup'])
            }else{
                end_lat_lon = [];
                end_circle_marker = undefined;
            }
            tot_dist_mi -= rm_coord_lst['dist'];
            document.getElementById('tot_dist').innerHTML = Math.round(tot_dist_mi *100)/ 100;
        }
    }else{
        alert('Cannot remove start of route');
    }
}

function save_route(){
    console.log('save_route')
    route_name = document.getElementById('route_name').value;
    console.log('Save \'' + route_name + '\' distance of ' + tot_dist_mi + ' miles.');
    console.log(map_coord_lst[0]['dist']);
    route_json = JSON.stringify(map_coord_lst) 
    console.log(route_json)
    
    route_dict = {
        route_name: route_name,
        dist: tot_dist_mi,
        route_coord_lst: route_json,
        dist_uom: 'mile'
    };
    if (route_id != ''){
        route_dict['route_id'] = route_id;
    }
    console.log(route_dict)
    $.post('/save_route', route_dict
    ).done(function(response){
        console.log('save_route response received');
    }).fail(function(){
        console.error("Error: Could not contact server.");
    })
    ;
}