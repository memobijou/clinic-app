// datetimepicker = require("~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js")

$(document).ready(function(){
        let config = {
            locale: 'de',
            widgetPositioning:{
                horizontal: 'auto',
                vertical: 'bottom',
            },
            useCurrent: false
        }


        $('#id_start_date').datetimepicker(config);


        $('#id_end_date').datetimepicker(config);

        $("#id_start_date").on("dp.change", function (e) {
            $('#id_end_date').data("DateTimePicker").minDate(e.date);
            $('#id_end_date').data("DateTimePicker").defaultDate(e.date)
            $('#id_end_date').select()
        });

        $("#id_end_date").on("dp.change", function (e) {
            $('#id_start_date').data("DateTimePicker").maxDate(e.date);
        });

    }
);