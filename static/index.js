function loadBest(uid) {
    // ajax the JSON to the server
    $.post("receiver", cars, function () {

    });
    // stop link reloading the page
    event.preventDefault();
}

// thanks to Nico Tejera at https://stackoverflow.com/questions/1714786/query-string-encoding-of-a-javascript-object
// returns something like "uid=123&book=Emma"
function serialise(obj) {
    return Object.keys(obj).map(k => `${encodeURIComponent(k)}=${encodeURIComponent(obj[k])}`).join('&');
}

// taken from https://www.quirksmode.org/js/cookies.html
function createCookie(name, value, days) {
    if (days) {
        var date = new Date();
        date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
        var expires = "; expires=" + date.toGMTString();
    }
    else var expires = "";
    document.cookie = name + "=" + value + expires + "; path=/";
}

// taken from https://www.quirksmode.org/js/cookies.html
function readCookie(name) {
    var nameEQ = name + "=";
    var ca = document.cookie.split(';');
    for (var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) == 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
}

// taken from https://www.quirksmode.org/js/cookies.html
function eraseCookie(name) {
    createCookie(name, "", -1);
}

//totally a comment
let topN = [];
let uid = readCookie('uid');

function setup() {
    $('#emptyRatingsMessage').hide();
    $('#failedCreationText').hide();
    $('#failedLoginText').hide();
    $('#searchResultsTable').hide();
    $('#emptySearchMessage').hide();
    logged_cleanup();
    $('#loginForm').on('submit', function (formOut) {
        formOut.preventDefault();
        uid = this.elements[0].value;
        createCookie('uid', uid);
        logged_cleanup();
    });
    $('#loginLink').on('click', function () {
        eraseCookie('uid');
        uid = null;
        logged_cleanup();
    });
    $('#recsLink').on('click', refresh_recs);
    $('#myRatingsLink').on('click', refresh_history);
    $('#searchForm').on('submit', function (formOut) {
        formOut.preventDefault();
        let pattern = this.elements[0].value;
        refresh_search(pattern);
    })
}

function refresh_search(pattern) {
    $.get('/search/' + uid + '/' + pattern, function (response) {
        fill_search(response, pattern);
    });
}

function refresh_recs() {
    $.get("./getrecommendations/" + uid, function (response) {
        fill_recs(response);
    });
    refresh_history();
}

function refresh_history() {
    $.get("./gethistory/" + uid, function (response) {
        fill_history(response);
    });
}

function fill_history(json_obj) {
    let obj = JSON.parse(json_obj);
    let htmlContents = "";
    let empty = true;
    for (let index in obj.book_id) {
        empty = false;
        let title = obj.title[index];
        let book_id = obj.book_id[index];
        let avgRating = obj.average_rating[index] ? obj.average_rating[index].toFixed(2) : "n/a";
        let totalRatings = obj.ratings_count[index];
        let userRating = obj.rating[index];
        let item_html = "<tr>" +
            "<td>" + title + "</td>" +
            "<td>" + book_id + "</td>" +
            "<td>" + avgRating + "</td>" +
            "<td>" + totalRatings + "</td>" +
            "<td>" +
            "   <form id='histRatingForm" + book_id + "'>" +
            "       <input type=\"number\" min=\"1\" max=\"5\" id='ratingField" + book_id + "' value='" + userRating + "'>" +
            "   </form>" +
            "</td>" +
            "<td>" +
            "   <a id='delRating" + book_id + "'>" +
            "      <span id=\"loggedIcon\" style='font-size: 200%' class=\"glyphicon glyphicon-remove\"></span>" +
            "   </a>" +
            "</td>" +
            "</tr>";
        htmlContents += item_html;
    }
    $('#ratingsTableBody').html(htmlContents);
    for (let index in obj.book_id) {
        let book_id = obj.book_id[index];
        $("#histRatingForm" + book_id).on('submit', function (formOut) {
            formOut.preventDefault();
            let rating = this.elements[0].value;
            $.post("./rate/" + uid + '/' + book_id + '/' + rating, function (status) {
                refresh_history();
            });
        });
        $("#delRating" + book_id).on('click', function () {
            $.post("./delete/" + uid + '/' + book_id, function (status) {
                refresh_history();
            });
        })
    }
    if (empty) {
        $('#ratingsTable').hide();
        $('.emptyRatingsMessage').show();
    }
    else {
        $('#ratingsTable').show();
        $('.emptyRatingsMessage').hide();
    }

}

function fill_recs(json_obj) {
    let obj = JSON.parse(json_obj);
    let htmlContents = "";
    for (let index in obj.book_id) {
        let title = obj.title[index];
        let book_id = obj.book_id[index];
        let avgRating = obj.average_rating[index] ? obj.average_rating[index].toFixed(2) : "n/a";
        let totalRatings = obj.ratings_count[index];
        let item_html = "<tr>" +
            "<td>" + title + "</td>" +
            "<td>" + book_id + "</td>" +
            "<td>" + avgRating + "</td>" +
            "<td>" + totalRatings + "</td>" +
            "<td>" +
            "   <form id='recsRatingForm" + book_id + "'>" +
            "       <input type=\"number\" min=\"1\" max=\"5\" id='ratingField" + book_id + "' value=''>" +
            "   </form>" +
            "</td>" +
            "</tr>";
        htmlContents += item_html;
    }
    $('#recsTableBody').html(htmlContents);
    for (let index in obj.book_id) {
        let book_id = obj.book_id[index];
        $("#recsRatingForm" + book_id).on('submit', function (formOut) {
            formOut.preventDefault();
            let rating = this.elements[0].value;
            $.post("./rate/" + uid + '/' + book_id + '/' + rating, function (status) {
                refresh_recs();
            });
        })
    }
}

function fill_search(json_obj, pattern) {
    let obj = JSON.parse(json_obj);
    let htmlContents = "";
    let empty = true;
    for (let index in obj.book_id) {
        empty = false;
        let title = obj.title[index];
        let book_id = obj.book_id[index];
        let avgRating = obj.average_rating[index] ? obj.average_rating[index].toFixed(2) : "n/a";
        let totalRatings = obj.ratings_count[index];
        let userRating = obj.rating[index];
        let item_html = "<tr>" +
            "<td>" + title + "</td>" +
            "<td>" + book_id + "</td>" +
            "<td>" + avgRating + "</td>" +
            "<td>" + totalRatings + "</td>" +
            "<td>" +
            "   <form id='searchRatingForm" + book_id + "'>" +
            "       <input type=\"number\" min=\"1\" max=\"5\" id='ratingField" + book_id + "' value='" + userRating + "'>" +
            "   </form>" +
            "</td>" +
            "</tr>";
        htmlContents += item_html;
    }
    $('#searchResultsTableBody').html(htmlContents);
    for (let index in obj.book_id) {
        let book_id = obj.book_id[index];
        $("#searchRatingForm" + book_id).on('submit', function (formOut) {
            formOut.preventDefault();
            let rating = this.elements[0].value;
            $.post("./rate/" + uid + '/' + book_id + '/' + rating, function (status) {
                refresh_search(pattern);
            });
        })
    }
    if (empty) {
        $('#searchResultsTable').hide();
        $('#emptySearchMessage').show();
    }
    else {
        $('#searchResultsTable').show();
        $('#emptySearchMessage').hide();
    }
}


function logged_cleanup() {
    let uid = readCookie('uid');
    if (uid == null) {
        $('.loggedIn').hide();
        $('.loggedOut').show();
        $('#loginLink').html('<span id="loggedIcon" class="glyphicon glyphicon-log-in"></span> Log in');
    }
    else {
        $('.loggedOut').hide();
        $('.loggedIn').show();
        $('#loginLink').html('<span id="loggedIcon" class="glyphicon glyphicon-log-out"></span> UID' + uid + '- Log out');
    }
}

window.onload = setup();

