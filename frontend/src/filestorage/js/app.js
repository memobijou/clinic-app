import "~/base/js/app.js"

import "~/base/octopus/assets/vendor/jstree/themes/default/style.css"
import "~/base/octopus/assets/stylesheets/theme-custom.css"

import '~/vendor/dropzone/4.3.0/dropzone.css'


import 'script-loader!~/vendor/dropzone/4.3.0/dropzone.js'

$(document).ready(function(){
    Dropzone.autoDiscover = false;

    var options_in_german = {
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

    $.extend(window.Dropzone.prototype.defaultOptions, options_in_german);

    let directory = null;
    for(let i=0; i<directories.length; i++){
        directory = directories[i]
        new Dropzone(
            //id of drop zone element 1
                '#dropzone-example-' + directory.pk,  {
                maxFilesize: 5,
                addRemoveLinks: true,
                dictResponseError: 'Serverfehler',
                autodiscover: false,
                success: function(file, response){
                    file["pk"] = response.pk;
                },
                init: function() {
                    for(let file in directory_files[directory.pk.toString()]){
                        file = directory_files[directory.pk.toString()][file]
                        var mockFile = { name: file.name, size: file.size, pk: file.pk, dataURL: file.url};
                        this.emit("addedfile", mockFile);
                        this.createThumbnailFromUrl(mockFile, file.url);
                        this.emit("complete", mockFile);
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


                },
                previewsContainer: '#preview' + directory.pk

            }
        )

    }

    $("div").remove(".dz-progress");
})
