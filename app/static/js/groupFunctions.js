var confirmed = false;

function confirmLeave(event) {
    if (confirmed) {
        event.parentElement.requestSubmit();
    } else {
        event.innerText = "Bestätigen";
        confirmed = true;
    }
}
