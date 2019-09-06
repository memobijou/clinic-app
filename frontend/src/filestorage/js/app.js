import "~/base/js/app.js"

import "~/base/octopus/assets/vendor/jstree/themes/default/style.css"
import "~/base/octopus/assets/stylesheets/theme-custom.css"

import '~/vendor/dropzone/4.3.0/dropzone.css'


import 'script-loader!~/vendor/dropzone/4.3.0/dropzone.js'

let {template} = require("~/filestorage/js/templates/base_tpl.js")

window.template = template
window.addRemoveLinks = true
window.maxFileSize = 5

window.options_in_german = {
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



const show_dropzone_html = `
    <div style="position:relative;display:none;" id="show_dropzone">
        <span id="hand_up" style="position:absolute;bottom:10px;left:15%;" class="glyphicon glyphicon-hand-up">
        </span>
        <span style="position:absolute;top:15px;left:5%;color:black;background:white;">Datei hier hochladen</span>
    </div>`

$("#dropzone_first_td").append(show_dropzone_html)

const show_dropzone_element = document.getElementById("show_dropzone")

let interval = null;

;["drag", "dragstart", "dragend", "dragleave", "dragenter", "dragover", "drop"].forEach(eventName => {
  //droparea.addEventListener(eventName, preventDefaults, false)
  $("body").on(eventName, preventDefaults);
  $(show_dropzone_html).on(eventName, preventDefaults);
})

function preventDefaults (e) {
  e=e||event;
  e.preventDefault()
  e.stopPropagation()
  e.originalEvent.preventDefault();
  e.originalEvent.stopPropagation();
}

;["drag", "dragstart", "dragenter", "dragover"].forEach(eventName => {
    //droparea.addEventListener(eventName, preventDefaults, false)
    $("body").on(eventName, function(e){
          $("#dropzone").css("background", "#f5f5f5")
          if($(show_dropzone_element).css("display") === "none"){
              $(show_dropzone_element).css({"display": ''})
          }
                if(interval == null){
          interval = setInterval(function(){
              $("#hand_up").animate({
                top: '-=5px'
              }, 800);
              $("#hand_up").animate({
                top: '+=5px'
              }, 800);
          }, 500);
      }
      });
})

;["dragend", "dragleave", "drop"].forEach(eventName => {
    //droparea.addEventListener(eventName, preventDefaults, false)
    $("#dropzone_first_td").on(eventName, function (e) {
        this.style.background = null;
    });
})

;["dragend", "dragleave", "drop"].forEach(eventName => {
    //droparea.addEventListener(eventName, preventDefaults, false)
    $("body").on(eventName, function(e){
          clearInterval(interval)
          interval = null
          $(show_dropzone_element).css("display", "none")
          $("#dropzone").css("background", "")
    });
})


const peform_upload = function(formData){
    $.ajax({
        url: window.upload_url,
        method: "POST",
        cache: false,
        contentType: false,
        processData: false,
        data: formData,
        // other attributes of AJAX
    }).always(function(){
        location.reload()
    })
}

;["drop"].forEach(eventName => {
  //droparea.addEventListener(eventName, preventDefaults, false)
  $("#dropzone_first_td").on(eventName, function(e){
    let file = e.originalEvent.dataTransfer.files[0];
    let formData = new FormData();

     //but for this example i will skip that
    formData.append('file', file);
    formData.append('csrfmiddlewaretoken', window.CSRF_TOKEN);
    peform_upload(formData)
  });
})


$("#upload_btn").click(function(){
    // Create an input element
    let inputElement = document.createElement("input");

    // Set its type to file
    inputElement.type = "file";

    // Set accept to the file types you want the user to select.
    // Include both the file extension and the mime type
    //inputElement.accept = accept;

    // set onchange event to call callback when user has selected file

    let prepare_upload = function(){
        let file = this.files[0]
        let formData = new FormData()
        formData.append('file', file)
        formData.append('csrfmiddlewaretoken', window.CSRF_TOKEN)
        peform_upload(formData)
    }

    inputElement.addEventListener("change", prepare_upload)

    // dispatch a click event to open the file dialog
    inputElement.dispatchEvent(new MouseEvent("click"));
})


$("#action_btn").click(function(e){
    const selected_action = $('#select_action').find(":selected").text();
    if(selected_action === "Löschen"){
        const delete_ids = []
        $('.action_checkbox:checked').each(function() {
            delete_ids.push($(this).val())
        });

        const delete_folders_ids = []
        $('.checkbox_folder:checked').each(function() {
            delete_folders_ids.push($(this).val())
        });

        let query_string = "csrfmiddlewaretoken=" + window.CSRF_TOKEN

        if(delete_ids.length > 0){
            for(let index in delete_ids){
                let id = delete_ids[index]
                query_string = query_string + "&item=" + id
            }
        }

        if(delete_folders_ids.length > 0){
            for(let index in delete_folders_ids){
                let id = delete_folders_ids[index]
                query_string = query_string + "&directory=" + id
            }
        }

        if(delete_ids.length > 0 || delete_folders_ids.length > 0){
            let response= $.post(delete_url, query_string)


            response.done(function () {
                let url = JSON.parse(response.responseText).url

                if(url){
                    window.location.href = url
                }else{
                    location.reload(true)
                }

            })

            response.fail(function(){
                let error_msg = JSON.parse(response.responseText).error
                document.getElementById("error_msg").innerText = error_msg
            })
        }
    }
})
