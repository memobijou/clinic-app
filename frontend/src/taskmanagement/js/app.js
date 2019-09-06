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
        {targets: 3, title: "Gruppen", name: "groups", orderable: false},
        {targets: 4, title: "Benutzer", name: "users", orderable: false},
      ],

       // Mit ajax funktioniert muss nur angepasst werden auf REST API
       // Also filtern nach Querystring Parameter die man von Datatables bekommt
       // Und Datensätze anzeigen wie es Datatables erwartet
       serverSide: true,
       ajax: {
        url: api_url,
        type: "GET",
        headers: {  },
       },
       lengthMenu: [[5, 10, 25, 50], [5, 10, 25, 50]],
       autoWidth: false,
       initComplete: function(settings, json) {
	    const search = $(".dataTables_filter")
        const search_input = $(".dataTables_filter input")

        search_input.css("margin-left", "0.9em")

        search.removeClass("dataTables_filter")
        search.addClass("text-right")


        },
        // "order": [[1, 'asc']],
        "aaSorting": []
	} )

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

    let create_action_tag = function(){
        let select_action = document.createElement("label")
        let select_tag = document.createElement("select")
        select_tag.className = "form-control input-sm"
        select_tag.id = "select_action"
        select_tag.style.minWidth = "160px"
        select_action.appendChild(select_tag)
        let option = document.createElement("option")
        option.innerHTML = "---------"
        option.value = ""
        select_tag.appendChild(option)
        option = document.createElement("option")
        option.value = "deletion"
        option.innerHTML = "Aufgaben löschen"
        select_tag.appendChild(option)
        let action_btn = document.createElement("button")
        action_btn.className = "btn btn-primary btn-sm"
        action_btn.id = "peform_action_btn"
        action_btn.innerHTML = "Ausführen"
        let input_group = document.createElement("div")
        input_group.className = "input-group"
        let input_group_btn = document.createElement("div")
        input_group_btn.className = "input-group-btn"
        input_group_btn.appendChild(action_btn)
        input_group.appendChild(select_tag)
        input_group.appendChild(input_group_btn)
        select_action.appendChild(input_group)
        select_action.style.paddingTop = "5px"
        return select_action
    }

    let select_action = create_action_tag()


    $("#datatable-default_length").parent().append(select_action);

    $("#select_action").on("change", function(){
        if(this.value == ""){
            $("#peform_action_btn").attr("disabled", "")
        }else{
            $("#peform_action_btn").removeAttr("disabled", "")
        }
        $("#action_form").attr("action", actions[this.value])
    })

    if($("#select_action option:selected").val() == ""){
        $("#peform_action_btn").attr("disabled", "")
    }

    let config = {
        locale: 'de',
        widgetPositioning:{
            horizontal: 'auto',
            vertical: 'bottom',
        },
        useCurrent: false
    }

    $('#id_start_datetime').datetimepicker(config);

    $('#id_end_datetime').datetimepicker(config);

    $("#id_start_datetime").on("dp.change", function (e) {
        $('#id_end_datetime').data("DateTimePicker").minDate(e.date);
        $('#id_end_datetime').data("DateTimePicker").defaultDate(e.date)
        $('#id_end_datetime').select()
    });

    $("#id_end_datetime").on("dp.change", function (e) {
        $('#id_start_datetime').data("DateTimePicker").maxDate(e.date);
    });
})
