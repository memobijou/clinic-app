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

window.success_function = function(dropzone, file, response){
    let version_spans = file.previewElement.getElementsByClassName("version-span")
    let edit_spans = file.previewElement.getElementsByClassName("edit-span")
    let download_spans = file.previewElement.getElementsByClassName("download-span")

    let version_span = version_spans[0]
    let edit_span = edit_spans[0]
    let download_span = download_spans[0]

    version_span.innerHTML =  "<b>Version:</b> " + "1.00"
    download_span.innerHTML = "<a href='" + response.file +"'>Herunterladen</a>"
    edit_span.innerHTML = "<a href='" + edit_url.replace("0", response.pk) +"'>Bearbeiten</a>"

}

window.error_function = function(){

}

window.sending_function = function(formData){

}

$(document).ready(function(){
    Dropzone.autoDiscover = false;

    $.extend(window.Dropzone.prototype.defaultOptions, window.options_in_german);

    let directory = null;
    for(let i=0; i<directories.length; i++){
        directory = directories[i]
        new Dropzone(
            //id of drop zone element 1
                '#dropzone-example-' + directory.pk,  {
                maxFilesize: window.maxFileSize,
                addRemoveLinks: window.addRemoveLinks,
                dictResponseError: 'Serverfehler',
                autodiscover: false,
                previewTemplate: window.template,
                maxFiles: window.maxFiles,
                parallelUploads: 1,
                success: function(file, response){
                    file["pk"] = response.pk;
                    window.success_function(this, file, response);
                },
                init: function() {
                    let version_spans = this.previewsContainer.getElementsByClassName("version-span")
                    let edit_spans = this.previewsContainer.getElementsByClassName("edit-span")
                    let download_spans = this.previewsContainer.getElementsByClassName("download-span")

                    for(let j in directory_files[directory.pk.toString()]){
                        let file = directory_files[directory.pk.toString()][j]
                        let mockFile = { name: file.name, size: file.size, pk: file.pk, dataURL: file.url}
                        this.emit("addedfile", mockFile)
                        this.createThumbnailFromUrl(mockFile, file.url)
                        this.emit("complete", mockFile)
                        version_spans[j].innerHTML =  "<b>Version:</b> " + file.version.replace(",", ".")
                        edit_spans[j].innerHTML = "<a href='" + file.edit_view_url +"'>Bearbeiten</a>"
                        download_spans[j].innerHTML = "<a href='" + file.url +"'>Herunterladen</a>"

                    }

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
                previewsContainer: '#preview' + directory.pk

            }
        )

    }

    $("div").remove(".dz-progress");
})
