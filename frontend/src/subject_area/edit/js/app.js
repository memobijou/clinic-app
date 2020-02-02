import "~/base/js/app.js"


let display_edit_btn = $("#display_edit_btn") ;
let display_category_btn = $("#display_category_btn") ;

let edit_panel = $("#edit_panel");
let category_panel = $("#category_panel");


display_edit_btn.click(
    function(e){
        if(edit_panel.css("display") === "none"){
            //category_panel.css("display", "none");
            category_panel.slideUp("slow");
            $(display_category_btn).attr("class", "fa fa-caret-up")
        }
    }
);


display_category_btn.click(
    function(e){
        if(category_panel.css("display") === "none"){
            edit_panel.slideUp("slow");
            $(display_edit_btn).attr("class", "fa fa-caret-up")
        }
    }
);