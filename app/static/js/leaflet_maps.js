function initMap(apiKey) {
    console.log('leaflet_maps initMap');

    var run_map_center = { pos:[40.751895024, -89.5914150775], zoom:13 };
    var greenIcon = new L.Icon({
        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
        // iconSize: [25, 41],
        iconSize: [12, 20],
        iconAnchor: [6, 20],
        popupAnchor: [1, -17],
        shadowSize: [20, 20]
    });
    var redIcon = new L.Icon({
      iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
      shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
      iconSize: [12, 20],
      iconAnchor: [6, 20],
      popupAnchor: [1, -17],
      shadowSize: [20, 20]
    });

    var start_mark = {position:[40.746675403788700, -89.57505594938990], icon:greenIcon, popup: 'Run Start'}
    var end_mark = {position:[40.74646594002840, -89.57534370012580], icon:redIcon, popup: 'Run End'};

    var map = L.map('map').setView(run_map_center['pos'], run_map_center['zoom']);

    L.tileLayer('https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token={accessToken}', {
      attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
      maxZoom: 18,
      id: 'mapbox/streets-v11',
      tileSize: 512,
      zoomOffset: -1,
      accessToken: apiKey
    }).addTo(map);

    L.marker(start_mark['position'], {icon: start_mark['icon']}).addTo(map).bindPopup(start_mark['popup']);
    L.marker(end_mark['position'], {icon: end_mark['icon']}).addTo(map)        .bindPopup(end_mark['popup']);

    
}
