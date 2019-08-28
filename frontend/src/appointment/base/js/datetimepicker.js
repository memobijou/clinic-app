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

        let last_start_date_event = null;

        $("#id_start_date").on("dp.change", function (e) {
            last_start_date_event = e;
        });

        $('#id_start_date').on("focusout", function (e) {
            if(last_start_date_event){
                $('#id_end_date').data("DateTimePicker").minDate(last_start_date_event.date);
                $('#id_end_date').data("DateTimePicker").defaultDate(last_start_date_event.date);
                last_start_date_event = null;
            }
            $('#id_end_date').select()
        });


        $("#id_end_date").on("dp.change", function (e) {
            $('#id_start_date').data("DateTimePicker").maxDate(e.date);
        });

    }
);