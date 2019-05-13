import '~/taskmanagement/css/main.css';
import "~/base/js/app.js"
import "~/base/js/datatables.js"
import "~/vendor/bootstrap-datetimepicker/4.17.47/build/css/bootstrap-datetimepicker.css"
import "script-loader!~/vendor/moment/moment.min.js"
import "script-loader!~/vendor/bootstrap-datetimepicker/4.17.47/build/js/bootstrap-datetimepicker.min.js"

$(document).ready(function(){
	// Datatables
    var dt = $('#datatable-default').DataTable( {
	  language: german_translation,
	  responsive: true,
      columnDefs: [
        {targets: 0, title: "", name: "", orderable: false},
        {targets: 1, title: "Aufgabe", name: "name"},
        {targets: 2, title: "Beschreibung", name: "description"},
        {targets: 3, title: "Gruppen", name: "groups"},
        {targets: 4, title: "Benutzer", name: "users"},
      ],

       // Mit ajax funktioniert muss nur angepasst werden auf REST API
       // Also filtern nach Querystring Parameter die man von Datatables bekommt
       // Und Datensätze anzeigen wie es Datatables erwartet
       serverSide: true,
       ajax: api_url,
       lengthMenu: [[5, 10, 25, 50], [5, 10, 25, 50]],
       autoWidth: false,
       initComplete: function(settings, json) {
	    const search = $(".dataTables_filter")
        const search_input = $(".dataTables_filter input")

        search_input.css("margin-left", "0.9em")

        search.removeClass("dataTables_filter")
        search.addClass("text-right")


        },
        "order": [[1, 'asc']]
	} )

    // Datetimepicker
    $('.datetimepicker').datetimepicker(
            {
                locale: 'de',
                widgetPositioning:{
                    horizontal: 'auto',
                    vertical: 'bottom',
                }
            }
    );


    let button_show_inner_html = "Benutzer auswählen <span class=\"fa fa-caret-down\"></span>"
    let button_hide_inner_html = "Benutzer auswählen <span class=\"fa fa-caret-up\"></span>"

    let user_checkboxes_wrapper = document.getElementById("user_checkboxes")
    $("#show_user_checkboxes_btn").click(function(){
        if(user_checkboxes_wrapper.style.display === "none"){
            user_checkboxes_wrapper.style.display = ""
            this.innerHTML = button_show_inner_html
        }else{
            user_checkboxes_wrapper.style.display = "none"
            this.innerHTML = button_hide_inner_html
        }
    })


    if($(".errorlist:first").length > 0){
        $(".task_form_panel").css("display", "")
    }

})
