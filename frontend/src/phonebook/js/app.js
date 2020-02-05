import "~/base/js/app.js"
import "~/base/js/datatables.js"


$(document).ready(function(){
	var dt = $('#datatable-default').DataTable( {
	  language: window.german_translation,
	  responsive: true,
      columnDefs: [
        {targets: 0, title: "", name: "", orderable: false},
        {targets: 1, title: "Name", name: "last_name"},
        {targets: 2, title: "Vorname", name: "first_name"},
        {targets: 3, title: "Bezeichnung", name: "title"},
        {targets: 4, title: "Telefonnummer", name: "phone_number"},
        {targets: 5, title: "Handynummer", name: "mobile_number"},
        {targets: 6, title: "Kategorie", name: "category"},
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

        search.removeClass("dataTables_filter")
        search.addClass("text-right")


        },
        "order": [[1, 'asc']]
	} )

})
