var cssFile = new URLSearchParams(window.location.search).get('css');
if (cssFile) { document.getElementById("css").href = cssFile; }
