// Dummy code to prove javascript keeps running

setInterval(function () {
    let currentTime = new Date();
    console.log("Current time: " + currentTime.toLocaleTimeString());
}, 5000);


// Dummy code to prove i can catch any click

document.addEventListener('click', function (event) {
    console.log('Clicked:', event.target);
});

// Replace the current URL with the URL of the main page
function replaceURLWithMainPage() {
    var currentURL = window.location.href;
    var mainPageURL =  window.location.origin;

    // Check if the current URL is a subpage
    if (currentURL !== mainPageURL && currentURL.startsWith(mainPageURL)) {
        history.replaceState({}, "", mainPageURL);
    }
}

// Listen for the "popstate" event, which occurs when the user navigates back or forward
window.addEventListener("popstate", replaceURLWithMainPage);

// Call the function to replace the URL with the main page URL initially
replaceURLWithMainPage();