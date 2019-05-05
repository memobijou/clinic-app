import "~/account/base/js/app.js"
import '~/account/user_list/css/main.css'
import "~/base/js/datatables.js"

$(document).ready(function(){
	var dt = $('#datatable-default').DataTable( {
	  language: window.german_translation,
	  responsive: true,
      columnDefs: [
        {targets: 0, title: "", name: "", orderable:false, type:"checkbox"},
        {targets: 1, title: "Titel", name: "title"},
        {targets: 2, title: "Vorname", name: "first_name"},
        {targets: 3, title: "Nachname", name: "last_name"},
        {targets: 4, title: "Benutzername", name: "username"},
        {targets: 5, title: "Email", name: "email"},
        {targets: 6, title: "Mentor", name: "mentor"},
        {targets: 7, title: "Schüler", name: "students"},
        {targets: 8, title: "Fachrichtung", name: "discipline"},
        {targets: 9, title: "Aktiv", name: "is_active"}
      ],

       // Mit ajax funktioniert muss nur angepasst werden auf REST API
       // Also filtern nach Querystring Parameter die man von Datatables bekommt
       // Und Datensätze anzeigen wie es Datatables erwartet
       serverSide: true,
       ajax: "datatables",
       lengthMenu: [[5, 10, 25, 50], [5, 10, 25, 50]],
       autoWidth: false,
       initComplete: function(settings, json) {
	    const search = $(".dataTables_filter")

        search.removeClass("dataTables_filter")
        search.addClass("text-right")

        },
        select: {
            style:    'os',
            selector: 'td:first-child'
        },
        order: [[1, 'asc']],
	} )

    let select_html = `
        &nbsp;&nbsp;
        <label>
            <select class="form-control input-sm" id="select_action" style="min-width:160px;">
                <option value="">---------</option>
                <option value="activation">Benutzer aktivieren</option>    
                <option value="deactivation">Benutzer deaktivieren</option>    
            </select>
            <button class="btn btn-primary" id="peform_action_btn">Ausführen</button>
        </label>
    `
    $("#datatable-default_length").html($("#datatable-default_length").html() + select_html);

	$("#datatable-default_length").parent().removeClass().addClass("col-sm-8")
    $("#datatable-default_filter").parent().removeClass().addClass("col-sm-4")


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

})
