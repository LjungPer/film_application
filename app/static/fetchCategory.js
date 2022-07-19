
function loadTableData(data) {
    const table = document.getElementById("testBody");
    for (var i = 0; i < data.length; i++) {
        var tr = table.insertRow();
        tr.className = 'topRow';

        for (var j = 0; j < 4; j++) {
            var cell = tr.insertCell();
            cell.className = 'topColumn';
            if (j==1 || j == 2) {
                cell.innerHTML = Number.parseFloat(data[i][j]).toFixed(2); // 0: name, 1: average rating, 2: biased rating, 3: nr films 
            }
            else {
                if (j == 0) {
                    cell.innerHTML = (i+1).toString() + ".  " + data[i][j];
                }
                else {
                    cell.innerHTML = data[i][j]; // 0: name, 1: average rating, 2: biased rating, 3: nr films 
                }
            }
        }
    }
}

var fetchCategory = function (title, sorting_type) {
    $.ajax({
        type: "GET",
        url: "/categories/" + title + '/' + sorting_type
    }).done(function (jsonData) {
        var elements = document.getElementsByClassName("topColumn");
        for (var i = 0; i < elements.length; i++) {
            elements.item(i).style.opacity = 0.6;
        };
        var element = document.getElementById("year");
        element.style.opacity = 1;
        var element = document.getElementById(sorting_type);
        element.style.opacity = 1;
        document.getElementById('testBody').innerHTML = '';
        loadTableData(jsonData);
    });
}