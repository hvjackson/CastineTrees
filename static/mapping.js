const castineCenter = { lat: 44.390492, lng: -68.804612 };
const colors = {
	blue: "#4193e0",
	green: "#0F0",
	red: "#F00",
	yellow: '#FD0',
	purple: '#F0F',
	gray: '#AAA'
}

const locationTrackingOptions = {
	enableHighAccuracy: true,
	timeout: Infinity,
	maximumAge: 0
};

function smCircleSymbol(color) {
	return {

		path: 'M -10, 0 a 10,10 0 1,1 20,0 a 10,10 0 1,1 -20,0', // smaller circle (no text)

		fillColor: color,
		fillOpacity: 1,
		strokeColor: '#666',
		strokeWeight: 1,

	};
}

function pinSymbol(color) {
	return {
		path: 'M -15, 0 a 15,15 0 1,1 30,0 a 15,15 0 1,1 -30,0', // largish circle, good for including text

		fillColor: color,
		fillOpacity: 1,
		strokeColor: '#666',
		strokeWeight: 1,

	};
}

function locationError(error) {
	if (error.code == 1) {
		//alert("Access to location denied. You may have to enable location sharing in your phone's settings.");
	} else {
		alert("Unable to get location data:\r\n" + "Error code: " + error.code + "\r\nMessage: " + error.message);
	}
}

function createTreePin(map, tag, latitude, longitude, color) {

	var marker = new google.maps.Marker({
		position: { lat: latitude, lng: longitude },
		label: tag,
		title: tag,
		url: '/inventory/tree/' + tag,
		map: map,
		icon: pinSymbol(color)

	});


	google.maps.event.addListener(marker, 'click', function() {
		window.location.href = this.url;
	});
}



var phonePositionMarker;
var watchPositionId;

function startShowingPhoneLocation(map) {
	phonePositionMarker = new google.maps.Marker({
		map: map,
		icon: smCircleSymbol(colors.purple)
	});

	function locationSuccess(position) {
		var newLatLng = new google.maps.LatLng(position.coords.latitude, position.coords.longitude);
		phonePositionMarker.setPosition(newLatLng);
	}

	watchPositionId = navigator.geolocation.watchPosition(locationSuccess, locationError, locationTrackingOptions);
}

function stopShowingPhoneLocation() {
	navigator.geolocation.clearWatch(watchPositionId);
	phonePositionMarker.setMap(null);

}