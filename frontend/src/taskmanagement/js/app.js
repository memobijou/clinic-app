import '~/taskmanagement/css/main.css';
import "~/base/js/app.js"
import "~/base/js/datatables.js"


$(document).ready(function(){
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

})
