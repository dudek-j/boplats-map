function windowContentFor(listing) {
    return ("<div>" + 
            `<h1>${listing['street']} ${listing['streetNumber']}</h1>` + 
            `<p><b>Area:</b> ${listing["area"]} </p>` +
            `<p><b>Pris:</b> ${listing["price"]} kr</p>`+ 
            `<p><b>Storlek:</b> ${listing["size"]} &#13217</p>` + 
            `<p><b>Publ:</b> ${listing["publ"]}</p>` + 
            `<a href=${listing["url"]} target="_blank" > Boplats link</a>` +
            "</div>")

}

function setupPickers() {

  var price = document.getElementById("price");
  
  var option = document.createElement("option");
  option.text = ""
  price.add(option);

  for (let i of [...Array(20).keys()]) {
    var option = document.createElement("option");
    option.text = (i + 1) * 1000
    price.add(option);
  }

  var size = document.getElementById("size");
  
  var option = document.createElement("option");
  option.text = ""
  size.add(option);

  for (let i of [...Array(10).keys()]) {
    var option = document.createElement("option");
    option.text = 10 * (i + 1)
    size.add(option);
  }

  var rooms = document.getElementById("rooms");

  var option = document.createElement("option");
  option.text = ""
  rooms.add(option);

  for (let i of [...Array(10).keys()]) {
    var option = document.createElement("option");
    option.text = (i + 1)
    rooms.add(option);
  }

  var publ = document.getElementById("publ");

  var option = document.createElement("option");
  option.text = ""
  publ.add(option)

  var option = document.createElement("option");
  option.text = "Idag"
  publ.add(option)
}

var markers = [];



function createMarkerFor(listing) {
  const todayImg =
    "https://developers.google.com/maps/documentation/javascript/examples/full/images/beachflag.png";

  let marker = new google.maps.Marker({
    position: new google.maps.LatLng(listing['lat'], listing['lon']),
    map: map,
    icon: listing["publ"] == "idag" ? todayImg : undefined,
  });

  marker.addListener('click', () => {
    infowindow.setContent(windowContentFor(listing));
    infowindow.open({
      anchor: marker,
      map,
      shouldFocus: false,
    });
  });

  markers.push(marker)
}



function applyFilters() {

  for (let marker of markers) {
    marker.setMap(null)
  }

  markers = []

  let selectedPrice = document.getElementById("price").value
  let selectedSize = document.getElementById("size").value
  let selectedRooms = document.getElementById("rooms").value
  let selectedPubl = document.getElementById("publ").value


  for (let listing of listings) {
    if (selectedPrice && parseInt(listing["price"]) > selectedPrice){
      continue;
    }

    if (selectedSize && parseInt(listing["size"]) < selectedSize){
      continue;
    }

    if (selectedRooms && parseInt(listing["rooms"]) < selectedRooms){
      continue;
    }

    if (selectedPubl && listing["publ"] != "idag"){
      continue;
    }

    createMarkerFor(listing)
  }

}

function clearFilters() {
  for (let listing of listings) {
    createMarkerFor(listing)
  }

  document.getElementById("price").value = ""
  document.getElementById("size").value = ""
  document.getElementById("rooms").value = ""
  document.getElementById("publ").value = ""
}


function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 57.7089, lng: 11.9746 },
    zoom: 12,
  });

  infowindow = new google.maps.InfoWindow({});

  google.maps.event.addListener(map, "click", function(event) {
    infowindow.close();
  });

  google.maps.event.addListener(map, "drag", function(event) {
    infowindow.close();
  });

  clearFilters()
  setupPickers()

  var apply = document.getElementById("apply");
  var clear = document.getElementById("clear");

  apply.addEventListener("click", applyFilters);
  clear.addEventListener("click", clearFilters);

}

window.initMap = initMap;