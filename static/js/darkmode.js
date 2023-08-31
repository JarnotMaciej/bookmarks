const modeSwitch = document.getElementById('modeSwitch');

function setDarkMode() {
    modeSwitch.innerHTML = 'Dark Mode';
    document.documentElement.setAttribute('data-bs-theme', 'dark');
    document.cookie = 'theme=dark; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/';
}

function setLightMode() {
    modeSwitch.innerHTML = 'Light Mode';
    document.documentElement.removeAttribute('data-bs-theme');
    document.cookie = 'theme=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
}

document.addEventListener('DOMContentLoaded', function() {
    // Check if a theme cookie exists and set the initial theme accordingly
    const themeCookie = document.cookie.match('(^|;) ?theme=([^;]*)(;|$)');
    if (themeCookie && themeCookie[2] === 'dark') {
        setDarkMode();
    } else {
        setLightMode();
    }
});

modeSwitch.addEventListener('click', function() {
    if (modeSwitch.innerHTML === 'Light Mode') {
        setDarkMode();
    } else {
        setLightMode();
    }
});
