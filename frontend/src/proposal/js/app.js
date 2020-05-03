import '~/base/css/main.css';
import "~/base/js/app.js"


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
        {targets: 1, title: "Vorname", name: "first_name"},
        {targets: 2, title: "Nachname", name: "last_name"},
        {targets: 3, title: "Antragstyp", name: "title"},
        {targets: 4, title: "Startdatum", name: "start_date"},
        {targets: 5, title: "Enddatum", name: "end_date"},
        {targets: 6, title: "Status", name: "confirmed"},
      ],

       // Mit ajax funktioniert muss nur angepasst werden auf REST API
       // Also filtern nach Querystring Parameter die man von Datatables bekommt
       // Und Datensätze anzeigen wie es Datatables erwartet
       serverSide: true,
       ajax: {
        url: api_url,
        type: "GET",
        headers: {},
       },
       lengthMenu: [[5, 10, 25, 50], [5, 10, 25, 50]],
       pageLength: 25,
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
        option.innerHTML = "Anträge löschen"
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
})
