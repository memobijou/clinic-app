// datetimepicker = require("~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js")

$(document).ready(function(){
    $('.datetimepicker').datetimepicker(
            {
                locale: 'de',
                widgetPositioning:{
                    horizontal: 'auto',
                    vertical: 'bottom',
                }
            }
        );
    }
);