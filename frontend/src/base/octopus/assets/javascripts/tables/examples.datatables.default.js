

(function( $ ) {

	'use strict';

	var datatableInit = function() {

		$('#datatable-default').dataTable(
			{
				"language": {
					"url": "https://cdn.datatables.net/plug-ins/1.10.19/i18n/German.json"
				},
				aoColumnDefs: [{
					bSortable: false,
					aTargets: [ 0 ],

				}
			]
			}

		);

	};

	$(function() {
		datatableInit();
	});

}).apply( this, [ jQuery ]);