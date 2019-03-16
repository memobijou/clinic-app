let {template} = require("~/filestorage/js/templates/edit_tpl.js")
window.template = template
window.addRemoveLinks = false
window.options_in_german["dictDefaultMessage"] = "Datei hier hochladen um zu aktualisieren"
window.maxFiles = 1
window.success_function = function(dropzone, file, response){
    location.reload()
}
window.sending_function = function(formData){
    let version = document.getElementById("version").value
    formData.append("version", version)
}

window.error_function = function(file, errorMessage, xhr) {
    errorMessage = errorMessage.version[0]
    let error_field = document.getElementById("error_field")
    error_field.innerHTML = '<span style="color:red;">' + errorMessage + '</span>'
    this.removeFile(file)
    return errorMessage
}

import "~/filestorage/js/app.js"
