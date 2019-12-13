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
    $('#searchResults').hide();
    $('#emptyRatingsMessage').hide();
    $('#failedCreationText').hide();
    $('#failedLoginText').hide();
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
        console.log("logging out");
        logged_cleanup();
    });
    $('#createAccountForm').on('submit', function (formOut) {
        formOut.preventDefault();
        console.log("submitted");
        let uid = this.elements[0].value;
        $.post("./createUser/" + uid, function (status) {
            console.log('yeet');
            console.log("Add person status:" + status);
        });
    });
    $('#recsLink').on('click', function () {
        console.log("Loading recommendations for uid " + uid + "...");
        $.get("./getrecommendations/" + uid, function (response) {
            fill_recs(response);
        });
    });
    $('#myRatingsLink').on('click', function () {
        console.log("Loading recommendations for uid " + uid + "...");
        $.get("./gethistory/" + uid, function (response) {
            fill_history(response);
        });
    });
}

function fill_history(json_obj) {
    let obj = JSON.parse(json_obj);
    console.log(obj);
    let len = obj['book_id'].length;
    console.log(len);
    let htmlContents = "";
    let empty = true;
    for (let index in obj.book_id) {
        empty = false;
        let title = obj.title[index];
        let book_id = obj.book_id[index];
        let avgRating = obj.average_rating[index];
        let totalRatings = obj.ratings_count[index];
        let userRating = obj.rating[index];
        let item_html = "<tr>" +
            "<td>" + title + "</td>" +
            "<td>" + book_id + "</td>" +
            "<td>" + avgRating.toFixed(2) + "</td>" +
            "<td>" + totalRatings + "</td>" +
            "<td>" +
            "   <form id='ratingForm" + book_id + "'>" +
            "       <input type=\"number\" min=\"1\" max=\"5\" id='ratingField" + book_id + "' value='" + userRating + "'>" +
            "   </form>" +
            "</td>" +
            "</tr>";
        htmlContents += item_html;
    }
    $('#ratingsTableBody').html(htmlContents);
    for (let index in obj.book_id) {
        let book_id = obj.book_id[index];
        let userRating = obj.rating[index];
        $("#ratingForm" + book_id).on('submit', function (formOut) {
            formOut.preventDefault();
            console.log("Rating form " + book_id + " submitted");
            console.log("Old rating: " + userRating);
            console.log("New rating: " + this.elements[0].value)
        })
    }
    if (empty){
        $('#ratingsTable').hide();
        $('#emptyRatingsMessage').show();
    }
    else {
        $('#ratingsTable').show();
        $('#emptyRatingsMessage').hide();
    }

}

function fill_recs(json_obj) {
    let obj = JSON.parse(json_obj);
    console.log(obj);
    let len = obj['book_id'].length;
    console.log(len);
    let htmlContents = "";
    for (let index in obj.book_id) {
        let title = obj.title[index];
        let book_id = obj.book_id[index];
        let avgRating = obj.average_rating[index];
        let totalRatings = obj.ratings_count[index];
        let item_html = "<tr>" +
            "<td>" + title + "</td>" +
            "<td>" + book_id + "</td>" +
            "<td>" + avgRating.toFixed(2) + "</td>" +
            "<td>" + totalRatings + "</td>" +
            "<td>" +
            "   <form id='ratingForm" + book_id + "'>" +
            "       <input type=\"number\" min=\"1\" max=\"5\" id='ratingField" + book_id + "' value=''>" +
            "   </form>" +
            "</td>" +
            "</tr>";
        htmlContents += item_html;
    }
    $('#recsTableBody').html(htmlContents);
    for (let index in obj.book_id) {
        let book_id = obj.book_id[index];
        $("#ratingForm" + book_id).on('submit', function (formOut) {
            formOut.preventDefault();
            console.log("Rating form " + book_id + " submitted");
            console.log("Old rating: " + null);
            console.log("New rating: " + this.elements[0].value)
        })
    }

}


function logged_cleanup() {
    let uid = readCookie('uid');
    console.log('uid is ' + uid + ' - logged cleanup call');
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

console.log("finished js");