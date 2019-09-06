import "~/base/js/app.js"
import '~/appointment/duty_roster/css/main.css'

// import '../../vendor/datatables/datatables.min.css'

import '~/vendor/datatables/DataTables-1.10.18/css/dataTables.bootstrap.min.css'
import '~/vendor/datatables/Responsive-2.2.2/css/responsive.bootstrap.min.css'
import '~/vendor/dropzone/5.5.1/dropzone.css'
import '~/vendor/dropzone/5.5.1/basic.css'



import 'script-loader!~/vendor/datatables/datatables.min.js'

import 'script-loader!~/vendor/datatables/DataTables-1.10.18/js/dataTables.bootstrap.js'

import 'script-loader!~/vendor/datatables/Responsive-2.2.2/js/dataTables.responsive.js'
import 'script-loader!~/vendor/datatables/Responsive-2.2.2/js/responsive.bootstrap.js'

import 'script-loader!~/vendor/dropzone/5.5.1/dropzone.js'


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
        //{targets: 0, title: "", name: "calendar_week", orderable: false},
        {targets: 0, title: "Monat", name: "calendar_week", orderable: false},
        {targets: 1, title: "Dienstplan", name: "file"},

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




    var options_in_german = {
      'dictDefaultMessage': 'Dateien hier hochladen',
      'dictFallbackMessage': 'Ihr Browser unterstützt Drag&Drop Dateiuploads nicht',
      'dictFallbackText': 'Benutzen Sie das Formular um Ihre Dateien hochzuladen',
      'dictFileTooBig': 'Die Datei ist zu groß. Die maximale Dateigröße beträgt {{maxFileSize}}MB',
      'dictInvalidFileType': 'Eine Datei dieses Typs kann nicht hochgeladen werden',
      'dictResponseError': 'Der Server hat ihre Anfrage mit Status {{statusCode}} abgelehnt',
      'dictCancelUpload': 'Hochladen abbrechen',
      'dictCancelUploadConfirmation': null,
      'dictRemoveFile': 'Datei entfernen',
      'dictMaxFilesExceeded': 'Sie können keine weiteren Dateien mehr hochladen'
    };

    $.extend(window.Dropzone.prototype.defaultOptions, options_in_german);


    window.change_form_data = function(formData){
        let month_input = document.getElementById("id_month").value
        let year_input =document.getElementById("id_year").value

        if(month_input){
            formData.append("month_input", month_input)
        }
        if(year_input){
            formData.append("year_input", year_input)
        }

    }



    Dropzone.autoDiscover = false;

    $("#duty_roster_dropzone").dropzone({
      dictDefaultMessage: 'Dienstplan hier hochladen',
      addRemoveLinks : true,
      dictResponseError: 'Fehler beim hochladen der Datei!',
      maxFiles: 1,
      headers: {
          "x-csrftoken": window.CSRF_TOKEN,
          "Authorization": "Token " + auth_token
      },
      //previewsContainer: '#preview',
      init: function(){
            this.on(
                "sending", function(file, xhr, formData) {
                    window.change_form_data(formData);
                }
            )
      },
      success: function (file, response) {
        this.removeFile(file);
        location.reload()
      },

    });
})
