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


$(document).ready(function(){

	var dt = $('#datatable-default').DataTable( {
	  responsive: true,
    data: data,
    columnDefs: [
      {targets: 0, title: "Benutzername", name: "username"},
      {targets: 1, title: "Vorname", name: "first_name"},
      {targets: 2, title: "Nachname", name: "last_name"},
      {targets: 3, title: "Email", name: "email"}
    ],
    // columns: [
    //     { name: 'username' },
    //     { name: 'first_name' },
    //     { name: 'last_name' },
    //     { name: 'email' }
    // ],

       // Mit ajax funktioniert muss nur angepasst werden auf REST API
       // Also filtern nach Querystring Parameter die man von Datatables bekommt
       // Und Datensätze anzeigen wie es Datatables erwartet
       processing: true,
       serverSide: true,
       ajax: "datatables"
	} )
	 
})
