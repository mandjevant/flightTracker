function addMarkerToGroup(group, lat, lng, html) {
    let marker = new H.map.Marker({
        lat: lat,
        lng: lng
    });
    marker.setData(html);
    group.addObject(marker);
}

function addInfoBubble(map, lat, lng, name, iata) {
    let group = new H.map.Group();
    map.addObject(group);

    group.addEventListener("tap", function (evt) {
        let bubble = new H.ui.InfoBubble(evt.target.getGeometry(), {
            content: evt.target.getData()
        });

        ui.addBubble(bubble);
    }, false);

    addMarkerToGroup(group, lat, lng, name + " (" + iata + ")");
}

let platform = new H.service.Platform({
    apikey: ""
});

let defaultLayers = platform.createDefaultLayers();

let map = new H.Map(document.getElementById("map"),
    defaultLayers.vector.normal.map,{
    center: {lat:50, lng:5},
    zoom: 4,
    pixelRatio: window.devicePixelRatio || 1
});

window.addEventListener("resize", () => map.getViewPort().resize());

let behavior = new H.mapevents.Behavior(new H.mapevents.MapEvents(map));
let ui = H.ui.UI.createDefault(map, defaultLayers);

window.onload = function () {
    for (let i = 0; i < airport_data["airports"].length; i++) {
        addInfoBubble(map,
            airport_data["airports"][parseInt(i, 10)].latitude,
            airport_data["airports"][parseInt(i, 10)].longitude,
            airport_data["airports"][parseInt(i, 10)].name,
            airport_data["airports"][parseInt(i, 10)].iata
        );
    }
};
