import '~/base/css/main.css'

/* CSS */
import '~/vendor/bootstrap/css/bootstrap.css'
import '~/vendor/font-awesome/css/font-awesome.css'
import '~/vendor/magnific-popup/magnific-popup.css'
import '~/vendor/bootstrap-datepicker/css/datepicker3.css'
import '~/vendor/bootstrap-multiselect/bootstrap-multiselect.css'
import '~/vendor/morris/morris.css'



import '~/base/octopus/assets/stylesheets/theme.css'
import '~/base/octopus/assets/stylesheets/skins/default.css'
import '~/base/octopus/assets/stylesheets/theme-custom.css'


/* JS */
import '~/base/octopus/assets/vendor/modernizr/modernizr.js'


import '~/vendor/jquery/jquery.js'
import '~/vendor/jquery-browser-mobile/jquery.browser.mobile.js'
import '~/vendor/bootstrap/js/bootstrap.js'
import '~/vendor/nanoscroller/nanoscroller.js'
import '~/vendor/bootstrap-datepicker/js/bootstrap-datepicker.js'
import '~/vendor/magnific-popup/magnific-popup.js'
import '~/vendor/jquery-placeholder/jquery.placeholder.js'


import '~/base/octopus/assets/javascripts/theme.js'
import '~/base/octopus/assets/javascripts/theme.custom.js'
import '~/base/octopus/assets/javascripts/theme.init.js'

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
