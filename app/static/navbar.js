const url = window.location.href;
var parts = url.split("/");
var param = parts.pop();

let a = document.getElementsByClassName("active");
if (a.length > 0) {
    a.classList.remove("active");
}
let p = document.getElementById(param);
p.className = "active";