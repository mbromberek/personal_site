function initMap(map_json) {
    console.log('maps.js initMap');
    // map_det = JSON.parse(map_json);
    console.log(map_json);
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

    var redCircle = {
        radius: 6,
        fillColor: 'red',
        color: '#000',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }
    var greenCircle = {
        radius: 6,
        fillColor: 'green',
        color: '#000',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    }
    var blueCircle = {
        radius: 6,
        fillColor: 'blue',
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

    var blueLine = {
        color: 'blue',
        weight: 3,
        opacity: 0.6
    }

    var polylinePoints = lat_lon;
    var start_mark = {position:lat_lon[0], icon:greenCircle, popup: 'Run Start'}
    var end_mark = {position:lat_lon[lat_lon.length -1], icon:redCircle, popup: 'Run End'};
    // var mile_one_mark = {position:[40.732828164473200, -89.57437014207240], icon:whiteCircle, popup: 'Mile 1'};

    var milePoints = [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [40.732828164473200, -89.57437014207240]
            },
            "properties": {
                "text": "1",
                "radius": 7,
                "fillColor": 'white',
                "color": '#000',
                "weight": 1,
                "opacity": 1,
                "fillOpacity": "0.8"
            }
        },
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [40.72476368397470, -89.58295689895750]
            },
            "properties": {
                "text": "2",
                "radius": 7,
                "fillColor": 'white',
                "color": '#000',
                "weight": 1,
                "opacity": 1,
                "fillOpacity": "0.8"
            }
        }
    ];

    var map = L.map('map').setView(run_map_center['pos'], run_map_center['zoom']);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      id: 'mapbox/streets-v11',
      tileSize: 512,
      zoomOffset: -1,
      accessToken: apiKey
    }).addTo(map);

    var polyline = L.polyline(polylinePoints, blueLine).addTo(map);

    // L.marker(start_mark['position'], {icon: start_mark['icon']}).addTo(map).bindPopup(start_mark['popup']);
    L.circleMarker(start_mark['position'], start_mark['icon']) .addTo(map).bindPopup(start_mark['popup']);
    L.circleMarker(end_mark['position'], end_mark['icon']) .addTo(map).bindPopup(end_mark['popup']);

    var mileMarkers = new L.geoJson(milePoints, {
        pointToLayer: function(feature, latlng) {
            // console.log(latlng.lat + ' ' + latlng.lng);
            // return new L.CircleMarker([latlng.lng, latlng.lat], {radius: feature.properties.radius});
            return new L.CircleMarker([latlng.lng, latlng.lat],  feature.properties);
        },
        onEachFeature: function(feature, layer) {
            var text = L.tooltip({
                permanent: true,
                direction: 'center',
                className: 'text'
            })
            .setContent(feature.properties.text)
            .setLatLng(layer.getLatLng());
            text.addTo(map);


            var text2 = L.tooltip({
                direction: 'top',
                className: 'text'
            })
            .setContent('Mile ' + feature.properties.text)
            .setLatLng(layer.getLatLng());
            layer.bindTooltip(text2);
        }
    }).addTo(map);

    console.log('End: leaflet_maps initMap');
}
