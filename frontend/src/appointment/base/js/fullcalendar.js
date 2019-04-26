$(document).ready(function(){
    $(function() {
      // page is now ready, initialize the calendar...

      $('#calendar').fullCalendar({
        // put your options and callbacks here

              locale: 'de',
              themeSystem: 'bootstrap3',
              weekNumbers: true,
              eventLimit: true,
              displayEventEnd: true,
              businessHours: {
                  // days of week. an array of zero-based day of week integers (0=Sunday)
                  dow: [ 1, 2, 3, 4, 5], // Monday - Thursday
                  start: '10:00', // a start time (10am in this example)
                  end: '18:00' // an end time (6pm in this example)
                },
              nowIndicator: true,
              header: {
                right: 'prev, next today',
                center: 'title',
                left: 'month, basicWeek ,basicDay, agendaWeek, agendaDay'
              },
              buttonText: {
                    agendaWeek: 'Stundenplan Woche',
                    agendaDay: 'Stundenplan Tag',
                    month: "Monat",
                    week: "Woche",
                    day: "Tag",
                    today: "Heute"
                },

                        // put your options and callbacks here
                            eventSources: [

                                // your event source
                                {
                                  url: api_url, // use the `url` property
                                  color: "#428bca",    // an option!
                                  textColor: 'white',  // an option!
                                  data: {
                                      is_conference: true
                                  }
                                },

                                // any other sources...
                                // your event source
                                {
                                  url: api_url, // use the `url` property
                                  color: "#f0ad4e",    // an option!
                                  textColor: 'white',  // an option!
                                  type: "GET",
                                  data: {
                                      is_infobox: true
                                  }
                                }

                          ],
                          eventRender: function (event, element, view) {
                                element.find(".fc-title").remove();
                                element.find(".fc-time").remove();
                                var promoter_name = event.promoter_name || "";
                                var start_date = moment(event.start_date, "YYYY-MM-DD hh:mm").toDate();
                                var start_minutes = parseInt(start_date.getMinutes());
                                if(start_date.getMinutes() < 10){
                                    start_minutes = "0" + start_date.getMinutes()
                                }
                                var start_time = start_date.getHours() + ":" + start_minutes;
                                var end_date = moment(event.end_date, "YYYY-MM-DD hh:mm").toDate();
                                var end_minutes = parseInt(end_date.getMinutes());
                                if(end_date.getMinutes() < 10){
                                    end_minutes = "0" + end_date.getMinutes()
                                }
                                var end_time = end_date.getHours() + ":" + end_minutes;
                                var date = start_time + "-" + end_time + " Uhr";



                                $(element).css("margin-top", "5px");
                                $(element).css("margin-bottom", "5px");
                                $(element).css("padding", "5px");

                                var description = event.description;

                                if(event.description == "" || event.description == null){
                                    description = "Kein Beschreibung vorhanden";
                                }

                                var title = "<b>" + event.title + "</b>";
                                if(event.promoter_name != null && event.promoter_name != ""){
                                    title += "<br/>" + event.promoter_name
                                }

                                element.append("<i>" + title + "</i>");
                                element.append("<p style='font-size:1.3em;'><b>" + date + "</b></p>")

                                $(element).popover({
                                    html: "true",
                                    title: title,
                                    content: "<p><b>Uhrzeit: " + "</b>" + date + "</p>" + description,
                                    trigger: 'hover',
                                    placement: 'top',
                                    container: 'body'
                                });

                          },
                            eventClick:  function(event, jsEvent, view) {
                                var is_infobox = event.is_infobox;
                                var is_conference = event.is_conference;

                                var start_date = moment(event.start_date, "YYYY-MM-DD hh:mm").toDate();
                                var start_date_str = start_date.toLocaleDateString("de-DE");
                                var start_date_time = start_date.toLocaleTimeString("de-DE", {hour: '2-digit', minute:'2-digit'});

                                var end_date = moment(event.end_date, "YYYY-MM-DD hh:mm").toDate();
                                var end_date_str = end_date.toLocaleDateString("de-DE");
                                var end_date_time = end_date.toLocaleTimeString("de-DE", {hour: '2-digit', minute:'2-digit'});

                                var action_url;

                                var create_and_open_event_modal = function(){
                                   if(is_infobox) {
                                        $('#edit_infobox').modal();

                                        $('input[name=infobox_edit-groups]').removeAttr("checked");

                                        for(let i=0;i<event.groups.length; i++){
                                           let group = event.groups[i]
                                           $('input[name=infobox_edit-groups][value='+ group.pk +']').prop("checked", "checked")
                                        }

                                        $('#id_infobox_edit-start_date').val(start_date_str + " " + start_date_time);

                                        $('#id_infobox_edit-end_date').val(end_date_str + " " + end_date_time);
                                        $("#id_infobox_edit-topic").val(event.title);
                                        $("#id_infobox_edit-description").val(event.description);
                                        $("#id_infobox_edit-place").val(event.place);
                                        $('#id_infobox_edit-promoter').find($('option')).attr('selected',false);

                                        $("#id_infobox_edit-promoter option").each(function() {
                                          if($(this).text() == event.promoter_name) {
                                              $(this).prop('selected', true);
                                          }
                                        });

                                        action_url = edit_infobox_action_url;
                                        action_url = action_url.replace("0", event.pk);
                                        // die 0 ist als Platzhalt weil event.pk erst nach python im frontend ausgeführt wird
                                        $('#edit_infobox_form').attr('action', action_url);

                                       const delete_wrapper = document.createElement("div")
                                       delete_wrapper.className = "text-right"
                                       const delete_btn = document.createElement("button")
                                       delete_btn.className = "btn btn-danger delete_btn"
                                       delete_btn.innerText = "Eintrag löschen"
                                       delete_btn.type = "button"
                                       delete_wrapper.appendChild(delete_btn)

                                       $('#edit_infobox .delete_btn').remove()

                                       $('#edit_infobox .modal-footer ').append(delete_wrapper)

                                       delete_btn.onclick = function(e){
                                           this.disabled = true

                                           $.post(delete_url + "?item=" + event.pk, {"csrfmiddlewaretoken": csrf_token})
                                               .always(function(){
                                                   location.reload();
                                                   this.disabled = false
                                               })
                                       }


                                    }else if(is_conference){
                                        $('#edit_conference').modal();


                                        $('input[name=conference_edit-groups]').removeAttr("checked");

                                        for(let i=0;i<event.groups.length; i++){
                                           let group = event.groups[i]
                                           $('input[name=conference_edit-groups][value='+ group.pk +']').prop("checked", "checked")
                                        }

                                        $('#id_conference_edit-start_date').val(start_date_str + " " + start_date_time);

                                        $('#id_conference_edit-end_date').val(end_date_str + " " + end_date_time);
                                        $("#id_conference_edit-topic").val(event.title);
                                        $("#id_conference_edit-description").val(event.description);
                                        $("#id_conference_edit-place").val(event.place);
                                        $('#id_conference_edit-promoter').find($('option')).attr('selected',false);

                                        $("#id_conference_edit-promoter option").each(function() {
                                          if($(this).text() == event.promoter_name) {
                                              $(this).prop('selected', true);
                                          }
                                        });

                                        action_url = edit_conference_action_url;
                                        action_url = action_url.replace("0", event.pk);
                                        // die 0 ist als Platzhalt weil event.pk erst nach python im frontend ausgeführt wird
                                        $('#edit_conference_form').attr('action', action_url);

                                        const delete_wrapper = document.createElement("div")
                                        delete_wrapper.className = "text-right"
                                        const delete_btn = document.createElement("button")
                                        delete_btn.className = "btn btn-danger delete_btn"
                                        delete_btn.innerText = "Eintrag löschen"
                                        delete_btn.type = "button"
                                        delete_wrapper.appendChild(delete_btn)

                                        $('#edit_conference .delete_btn').remove()

                                        $('#edit_conference .modal-footer ').append(delete_wrapper)

                                        delete_btn.onclick = function(e){
                                            this.disabled = true

                                            $.post(delete_url + "?item=" + event.pk, {"csrfmiddlewaretoken": csrf_token})
                                                .always(function(){
                                                    location.reload();
                                                    this.disabled = false
                                                })
                                        }

                                    }
                                };

                                create_and_open_event_modal();


                            }



      })

    });
})



