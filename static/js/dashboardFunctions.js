let shownMapType = 'students';


function switchMapType(type) {
    getMap(type);
    document.getElementById('mapSearchInput').value = "";
}

// Function that gets user map from /dashboard/students via fetch
function getMap(type, searchString) {
    if (type !== 'students' && type !== 'groups') {
        console.log('Error: Invalid type. Supported is "students" and "groups"');
        return;
    }

    if (type === "students") {
        document.getElementById('mapToolbarBtnStudents').disabled = true;
        document.getElementById('mapToolbarBtnGroups').disabled = false;
        shownMapType = "students";
    }

    if (type === "groups") {
        document.getElementById('mapToolbarBtnStudents').disabled = false;
        document.getElementById('mapToolbarBtnGroups').disabled = true;
        shownMapType = "groups";
    }

    let fetchUrl = '/dashboard/map/' + type;
    if (searchString !== undefined && searchString !== "") {
        fetchUrl = fetchUrl + "?" + new URLSearchParams({
            search_string: searchString
        }).toString();
    }

    fetch(fetchUrl)
    .then(response => response.text())
    .then(data => {
        const mapContainer = document.getElementById('mapContainer');
        mapContainer.innerHTML = "";
        mapContainer.insertAdjacentHTML('afterbegin', data);
    })
}

// Function that triggers a timer of 500 Milliseconds when the input with id mapSearchInput is changed. When the timer finishes the function getMap is called with the value of the input as parameter.
let timer;
function mapSearchInputChanged() {
    const input = document.getElementById('mapSearchInput');
    clearTimeout(timer);
    timer = setTimeout(function() {
        getMap(shownMapType, input.value);
    }, 500);
}

getMap('students');