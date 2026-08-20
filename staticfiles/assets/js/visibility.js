// function reload() {
//     document.location.reload();
// }
//
// setTimeout(reload, 50000);
document.addEventListener('DOMContentLoaded',() => {
googleHybrid = L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
});

var map = L.map('map').setView([-1.29272, 36.81930], 8);
L.tileLayer('http://{s}.google.com/vt/lyrs=s,h&x={x}&y={y}&z={z}', {
    maxZoom: 20,
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3']
}).addTo(map);

let lvisnpections = JSON.parse(document.getElementById('lvinspections_json').textContent)

setInterval(() => {
  lvisnpections.forEach(lvinspection => {
    L.marker([lvinspection.latitude, lvinspection.longitude],
        {title: lvinspection.substation__name}
    ).addTo(map)
        .bindPopup("<b>SSN: </b>" + lvinspection.substation__name.bold()
            + "<br><b>Date Inspected: </b>"+ new Date(lvinspection.dtupdate)
            + "<br><b>Inspected By: </b>"+ lvinspection.inspectedby__user__stid
            + "<br><b>Poor Sags: </b>"+ lvinspection.retention_req
            + "<br><b>Vegetation spans: </b>"+ lvinspection.traceclear_span
            + "<br><b>Conductors Uprate Span: </b>"+ lvinspection.conductors_uprate_span
            + "<br><b>PME Missing in Poles: </b>"+ lvinspection.pme_missing_poles
            + "<br><b>LV Overdistance: </b>"+ lvinspection.lv_overdistance_l
            + "<br><b>Illegal Connections: </b>"+ lvinspection.illegal_connections_l
            + "<br><b>Poshomills On SPhase: </b>"+ lvinspection.poshomills_onsingle_p_n
        )

})
}, "5000");
})



  // 'SSN : ' + lvinspection.substation__name.bold()
  //           + ', Date Inspected : ' + new Date(lvinspection.dtupdate)
  //           + ', Inspected By :' + lvinspection.inspectedby__user__stid
  //           + ', Poor Sags : ' + lvinspection.retention_req
  //           + ', Vegetation spans : ' + lvinspection.traceclear_span
  //           + ', Conductors Uprate Span : ' + lvinspection.conductors_uprate_span
  //           + ', PME Missing in Poles : ' + lvinspection.pme_missing_poles
  //           + ', LV Overdistance  : ' + lvinspection.lv_overdistance_l
  //           + ', Illegal Connections : ' + lvinspection.illegal_connections_l
  //           + ', Poshomills On SPhase : ' + lvinspection.poshomills_onsingle_p_n)