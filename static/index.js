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
    $('#failedCreationText').hide();
    $('#failedLoginText').hide();
    let uid = readCookie('uid');
    console.log('uid is ' + uid + ' - setup call');
    if (uid == null) {
        $('.loggedIn').hide();
        // <li><a href="#loginTab" data-toggle="tab" id="loginLink" title="Log In!"></a></li>
        $('#loginLink').html('<span id="loggedIcon" class="glyphicon glyphicon-log-in"></span> Log in');
    }
    else {
        $('.loggedOut').hide();
        $('#loginLink').html('<span id="loggedIcon" class="glyphicon glyphicon-log-out"></span> UID' + uid + '- Log out');
    }
    $('#loginForm').on('submit', function (formOut) {
        formOut.preventDefault();
        uid = this.elements[0].value;
        createCookie('uid', uid);
        setup();
    });
    $('#loginLink').on('click', function () {
        eraseCookie('uid');
        uid = null;
        console.log("logging out");
        setup();
    });
    $('#createAccountForm').on('submit', function (formOut) {
        formOut.preventDefault();
        console.log("submitted");
        let uid = this.elements[0].value;
        $.post("./createUser", serialise({
            uid: uid
        }), function (status) {
            console.log('yeet');
            console.log("Add person status:" + status);
        });
        // refresh/update loggedin status
    });
}

window.onload = setup();

console.log("finished js");