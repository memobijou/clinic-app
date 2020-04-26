import "~/base/js/app.js"
import "~/base/js/datatables.js"


$(document).ready(function(){
	var dt = $('#datatable-default').DataTable( {
	  language: window.german_translation,
	  responsive: true,
      columnDefs: [
        {targets: 0, title: "", name: "", orderable: false},
        {targets: 1, title: "Bezeichnung", name: "title"},
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
       "pageLength": 25,
       autoWidth: false,
       initComplete: function(settings, json) {
	    const search = $(".dataTables_filter")

        search.removeClass("dataTables_filter")
        search.addClass("text-right")


        },
        "order": [[1, 'asc']]
	} )

})
