
// Function that gets user map from /dashboard/students via fetch
function getMap(type) {
    if (type !== 'students' && type !== 'groups') {
        console.log('Error: Invalid type. Supperted is "students" and "groups"');
        return;
    }

    if (type === "students") {
        document.getElementById('mapToolbarBtnStudents').disabled = true;
        document.getElementById('mapToolbarBtnGroups').disabled = false;
    }

    if (type === "groups") {
        document.getElementById('mapToolbarBtnStudents').disabled = false;
        document.getElementById('mapToolbarBtnGroups').disabled = true;
    }

    fetch('/dashboard/map/' + type)
    .then(response => response.text())
    .then(data => {
        const mapContainer = document.getElementById('mapContainer');
        mapContainer.innerHTML = "";
        mapContainer.insertAdjacentHTML('afterbegin', data);
    })
}

getMap('students');