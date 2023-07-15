const mdExport = document.getElementById('mdExport');
const jsonExport = document.getElementById('jsonExport');

mdExport.addEventListener('click', function() {
    window.location.href = '/bookmarks-markdown';
});

jsonExport.addEventListener('click', function() {
    window.location.href = '/bookmarks-json-export';
});