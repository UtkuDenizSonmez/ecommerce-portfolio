$(document).keydown(function (e) {
    if (e.key === " ") {
        document.getElementById("all-contents").style.marginLeft = "25%";
        document.getElementById("navigation").style.marginLeft = "25%";
        document.getElementById("side-bar").style.width = "25%";
        document.getElementById("side-bar").style.display = "block";
    }  else if (e.key === "Enter") {
        document.getElementById("side-bar").style.display = "none";
        document.getElementById("all-contents").style.marginLeft = "10%";
        document.getElementById("navigation").style.marginLeft = "10%";
    }
});
