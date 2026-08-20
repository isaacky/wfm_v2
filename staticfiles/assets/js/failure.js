var osmMap = L.tileLayer.provider('OpenStreetMap.Mapnik')
var stamenMap = L.tileLayer.provider('Stamen.Watercolor')

var baseMaps = {OSM:osmMap,
'stamen Watercolor' : stamenMap};

// var map = L.map('map_failure').setView([-1.219297210470321, 36.88853168842854], 13);
//
// L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
//     maxZoom: 19,
//     attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
// }).addTo(map);
 var map = L.map('map_failure',{
     center:[-1.2194152012443695, 36.88841367083097],
     zoom:5,
     layers:[osmMap]
 });
var mapLayers = L.control.layers(baseMaps).addTo(map);

