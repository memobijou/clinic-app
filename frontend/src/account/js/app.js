import '../css/main.css';
// import '../../vendor/datatables/datatables.min.css'
import '../../vendor/datatables/DataTables-1.10.18/css/dataTables.bootstrap.min.css'
import '../../vendor/datatables/Responsive-2.2.2/css/responsive.bootstrap.min.css'

import '../../vendor/datatables/datatables.min.js'
import '../../vendor/datatables/DataTables-1.10.18/js/dataTables.bootstrap.js'

import '../../vendor/datatables/Responsive-2.2.2/js/dataTables.responsive.js'
import '../../vendor/datatables/Responsive-2.2.2/js/responsive.bootstrap.js'

// import '../vendor/Bootstrap3/css/bootstrap.min.css'
// import '../vendor/Bootstrap3/css/bootstrap-theme.min.css'
// import '../vendor/Bootstrap3/js/bootstrap.min.js'

  
const data =[
  {
    "name": "Tiger Nixon",
    "position": "System Architect",
    "salary": "$320,800",
    "start_date": "2011/04/25",
    "office": "Edinburgh",
    "extn": "5421"
  },
  {
    "name": "Garrett Winters",
    "position": "Accountant",
    "salary": "$170,750",
    "start_date": "2011/07/25",
    "office": "Tokyo",
    "extn": "8422"
  },
  {
    "name": "Ashton Cox",
    "position": "Junior Technical Author",
    "salary": "$86,000",
    "start_date": "2009/01/12",
    "office": "San Francisco",
    "extn": "1562"
  }
]

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
        {targets: 0, title: "Benutzername", name: "username"},
        {targets: 1, title: "Vorname", name: "first_name"},
        {targets: 2, title: "Nachname", name: "last_name"},
        {targets: 3, title: "Email", name: "email"}
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
        const search_input = $(".dataTables_filter input")

        search_input.css("margin-left", "0.9em" )

        search.removeClass("dataTables_filter")
        search.addClass("text-right")


        }
	} )
	 
})
