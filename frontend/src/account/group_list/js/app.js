import "~/account/base/js/app.js"
import '~/account/user_list/css/main.css'

// import '../../vendor/datatables/datatables.min.css'

import '~/vendor/datatables/DataTables-1.10.18/css/dataTables.bootstrap.min.css'
import '~/vendor/datatables/Responsive-2.2.2/css/responsive.bootstrap.min.css'

import 'script-loader!~/vendor/datatables/datatables.min.js'

import 'script-loader!~/vendor/datatables/DataTables-1.10.18/js/dataTables.bootstrap.js'

import 'script-loader!~/vendor/datatables/Responsive-2.2.2/js/dataTables.responsive.js'
import 'script-loader!~/vendor/datatables/Responsive-2.2.2/js/responsive.bootstrap.js'


const german_translation =
    {
      "sEmptyTable":      "Keine Daten in der Tabelle vorhanden",
      "sInfo":            "_START_ bis _END_ von _TOTAL_ Einträgen",
      "sInfoEmpty":       "Keine Daten vorhanden",
      "sInfoFiltered":    "(gefiltert von _MAX_ Einträgen)",
      "sInfoPostFix":     "",
      "sInfoThousands":   ".",
      "sLengthMenu":      "_MENU_ Einträge anzeigen",
      "sLoadingRecords":  "Wird geladen ..",
      "sProcessing":      "Bitte warten ..",
      "sSearch":          "Suchen",
      "sZeroRecords":     "Keine Einträge vorhanden",
      "oPaginate": {
          "sFirst":       "Erste",
          "sPrevious":    "Zurück",
          "sNext":        "Nächste",
          "sLast":        "Letzte"
      },
      "oAria": {
          "sSortAscending":  ": aktivieren, um Spalte aufsteigend zu sortieren",
          "sSortDescending": ": aktivieren, um Spalte absteigend zu sortieren"
      },
      "select": {
          "rows": {
              "_": "%d Zeilen ausgewählt",
              "0": "",
              "1": "1 Zeile ausgewählt"
          }
      },
      "buttons": {
          "print":    "Drucken",
          "colvis":   "Spalten",
          "copy":     "Kopieren",
          "copyTitle":    "In Zwischenablage kopieren",
          "copyKeys": "Taste <i>ctrl</i> oder <i>\u2318</i> + <i>C</i> um Tabelle<br>in Zwischenspeicher zu kopieren.<br><br>Um abzubrechen die Nachricht anklicken oder Escape drücken.",
          "copySuccess": {
              "_": "%d Spalten kopiert",
              "1": "1 Spalte kopiert"
          }
      }
  }

$(document).ready(function(){
	var dt = $('#datatable-default').DataTable( {
	  language: german_translation,
	  responsive: true,
      columnDefs: [
        {targets: 0, title: "", name: "", orderable: false},
        {targets: 1, title: "Gruppe", name: "name"},

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


    let select_html = `
        &nbsp;&nbsp;
        <label>
            <select class="form-control input-sm" id="select_action" style="min-width:160px;">
                <option value="">---------</option>
                <option value="deletion">Gruppe löschen</option> 
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
