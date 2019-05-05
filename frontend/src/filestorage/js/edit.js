let {template} = require("~/filestorage/js/templates/edit_tpl.js")
window.template = template
window.addRemoveLinks = false
window.options_in_german["dictDefaultMessage"] = "Datei hier her ziehen oder hier klicken zum aktualisieren"
window.maxFiles = 1
window.success_function = function(dropzone, file, response){
    location.reload(true)
}


import "~/filestorage/js/app.js"

window.sending_function = function(formData){
    let version = parseFloat(document.getElementById("version").value)
    let file_name =document.getElementById("file_name").value

    if(version){
        formData.append("version", version)
    }
    if(file_name){
        formData.append("name", file_name)
    }

}

window.error_function = function(file, errorMessage, xhr) {
    errorMessage = errorMessage.version[0]
    let error_field = document.getElementById("error_field")
    error_field.innerHTML = '<span style="color:red;">' + errorMessage + '</span>'
    this.removeFile(file)
    return errorMessage
}

$(document).ready(function(){
    Dropzone.autoDiscover = false;

    $.extend(window.Dropzone.prototype.defaultOptions, window.options_in_german);
    new Dropzone(
        //id of drop zone element 1
        '#dropzone',  {
        maxFilesize: window.maxFileSize,
        addRemoveLinks: window.addRemoveLinks,
        dictResponseError: 'Serverfehler',
        autodiscover: false,
        maxFiles: window.maxFiles,
        parallelUploads: 1,
        success: function(file, response){
            file["pk"] = response.pk;
            window.success_function(this, file, response);
        },
        init: function() {
            this.on("removedfile", function(file) {
                url = url.replace("0", file.pk);

                $.ajax({
                   beforeSend: function(xhr, settings) {
                        xhr.setRequestHeader("X-CSRFToken", window.CSRF_TOKEN);
                   },
                   url: url,
                   type: 'DELETE'
                });
            });

            this.on(
                "sending", function(file, xhr, formData) {
                    window.sending_function(formData);
                }
            )


            this.on(
                "error", window.error_function
            )

        },

    }
    )


    $("div").remove(".dz-progress");
})
