document.addEventListener('DOMContentLoaded', function() {
    const modeSwitch = document.getElementById('modeSwitch');
    modeSwitch.addEventListener('click', function() {
        if (modeSwitch.innerHTML === 'Light Mode') {
            modeSwitch.innerHTML = 'Dark Mode';
            document.documentElement.setAttribute('data-bs-theme', 'dark');
            document.cookie = 'theme=dark; expires=Fri, 31 Dec 9999 23:59:59 GMT; path=/';
        } else {
            modeSwitch.innerHTML = 'Light Mode';
            document.documentElement.removeAttribute('data-bs-theme');
            document.cookie = 'theme=; expires=Thu, 01 Jan 1970 00:00:00 GMT; path=/';
        }
    });

    // Check if a theme cookie exists and set the initial theme accordingly
    const themeCookie = document.cookie.match('(^|;) ?theme=([^;]*)(;|$)');
    if (themeCookie && themeCookie[2] === 'dark') {
        modeSwitch.innerHTML = 'Dark Mode';
        document.documentElement.setAttribute('data-bs-theme', 'dark');
    }
});