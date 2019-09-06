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
        {targets: 3, title: "Nachname", name: "last_name", default: true},
        {targets: 4, title: "Benutzername", name: "username"},
        {targets: 5, title: "Email", name: "email"},
        {targets: 6, title: "Mentor", name: "mentor"},
        {targets: 7, title: "Mentee", name: "students", orderable: false},
        {targets: 8, title: "Fachrichtung", name: "discipline"},
        {targets: 9, title: "Aktiv", name: "is_active"}
      ],

       // Mit ajax funktioniert muss nur angepasst werden auf REST API
       // Also filtern nach Querystring Parameter die man von Datatables bekommt
       // Und Datensätze anzeigen wie es Datatables erwartet
       serverSide: true,
       ajax: {
                url: "datatables",
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
        select: {
            style:    'os',
            selector: 'td:first-child'
        },
        order: [[3, 'asc']],
	} )

    let create_action_tag = function(options){
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
        for(let i=0; i<options.length; i++){
            option = document.createElement("option")
            option.innerHTML = options[i][1]
            option.value = options[i][0]
            select_tag.appendChild(option)
        }
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

    let options = [["activation", "Benutzer aktivieren"], ["deactivation", "Benutzer deaktivieren"],
    ["deletion", "Benutzer löschen"]]

    let select_action = create_action_tag(options)


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
