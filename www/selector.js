function init() {
	document.getElementById("os").value = guess_os();

	update_selection(); // nb this will also remove the body.noscript class
	document.getElementById("os").addEventListener("change", update_selection, false);
	document.getElementById("build").addEventListener("change", update_selection, false);
}
window.addEventListener("DOMContentLoaded", init, false);

function update_selection() {
	document.body.className = document.getElementById("os").value + ' ' + document.getElementById("build").value;
}

function guess_os() {
	if (navigator.platform.indexOf("Win") >= 0) {
		return "win";
	} else if (navigator.platform.indexOf("Linux") >= 0) {
		return "lin";
	} else if (navigator.platform.indexOf("FreeBSD") >= 0) {
		return "lin";
	} else if (navigator.platform.indexOf("Mac") >= 0) {
		return "osx";
	} else {
		return "win";
	}
}
