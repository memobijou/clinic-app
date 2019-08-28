// datetimepicker = require("~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js")


$(document).ready(function(){

        let setup_connected_datepickers = function(start_datepicker_id, end_datepicker_id, force_end_date_change){
            start_datepicker_id = "#" + start_datepicker_id;
            end_datepicker_id = "#" + end_datepicker_id;

            let config = {
                locale: 'de',
                widgetPositioning:{
                    horizontal: 'auto',
                    vertical: 'bottom',
                },
                useCurrent: false
            };

            $(start_datepicker_id).datetimepicker(config);
            $(end_datepicker_id).datetimepicker(config);

            let last_start_date_event = null;

            $(start_datepicker_id).on("dp.change", function (e) {
                last_start_date_event = e;
            });

            $(start_datepicker_id).on("focusout", function (e) {
                if(last_start_date_event){
                    $(end_datepicker_id).val("");
                    $(end_datepicker_id).data("DateTimePicker").minDate(last_start_date_event.date);
                    $(end_datepicker_id).data("DateTimePicker").defaultDate(last_start_date_event.date);
                    last_start_date_event = null;
                }
                $(end_datepicker_id).select();
            });


            $(end_datepicker_id).on("dp.change", function (e) {
                $(start_datepicker_id).data("DateTimePicker").maxDate(e.date);
            });


        };

        setup_connected_datepickers("id_start_date", "id_end_date", false);
        setup_connected_datepickers("id_conference_edit-start_date", "id_conference_edit-end_date", true);


    }
);