function getMap() {
    fetch('/profile/map')
        .then(response => response.text())
    .then(data => {
        const mapContainer = document.getElementById('collapseMap');
        mapContainer.innerHTML = "";
        mapContainer.insertAdjacentHTML('afterbegin', data);
    });
}

getMap();