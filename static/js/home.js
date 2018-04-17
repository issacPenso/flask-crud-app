function validateForm2using_jQuery() {
    var book_title = document.forms.addBookForm.title.value;
    if (book_title === "") {
        document.getElementById("add_book_submit_msg").innerHTML = 'Title can\'t be empty !';
        return false;
    }
    var should_submit = false;
    $.ajax({
        dataType: "json",
        url: "/api/is-book-title-valid?title=" + book_title,
        async: false,
        success: function(validation_result) {
            $("#add_book_submit_msg").html(validation_result.reason);
            should_submit = validation_result.status
        }
    });
    return should_submit;
}
function validateForm() {
    var book_title = document.forms.addBookForm.title.value;
    if (book_title === "") {
        document.getElementById("add_book_submit_msg").innerHTML = 'Title can\'t be empty !';
        return false;
    }
    var url = "/api/is-book-title-valid?title=" + book_title
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.responseType = 'json';
    xhr.onreadystatechange = function() {
        if (xhr.readyState == 4 && xhr.status) { //Done with status 200
            console.log(xhr.response);
            if (!xhr.response.status){
                $("#add_book_submit_msg").html(xhr.response.reason);
            } else {
                //$( "#addBookForm" ).submit(function( event ){
                // Stop form from submitting normally
                    //event.preventDefault();
                    // Get some values from elements on the page:
                    //var $form = $( this ),
                    //title = $form.find( "input[name='title']" ).val(),
                    //img = $form.find( "input[name='img']" ).val(),
                    //storage_type = $form.find( "input[name='storage_type']" ).val(),
                    //url = $form.attr( "action" );
                    // Send the data using post
                    //var posting = $.post( url, { title: title,img: img, storage_type: storage_type } );
                    //var posting = $.post( url );
                    // Put the results in a div
                    //posting.done(function( data ) {
                        //console.log(data);
                        //$( "#add_book_submit_msg" ).empty().append( "book was added successfully" );
                        $("#add_book_submit_msg").html("Book was added successfully");
                    }
                }
            }
    xhr.send();
}


function monkey_patch_autocomplete() {
  // Don't really need to save the old fn,
  // but I could chain if I wanted to
  var oldFn = $.ui.autocomplete.prototype._renderItem;

  $.ui.autocomplete.prototype._renderItem = function( ul, item) {
      var label = item.label;
      var term = this.term;
      if(!$('#case_sensitive').is(":checked")){
        label = label.toLowerCase();
        term = term.toLowerCase();;
      }
      let index = label.indexOf(term);
      let middle_str = item.label.substring(index,index + term.length);
      let new_item = index == -1 ? item.label : `${item.label.substring(0,index)}<span style="font-weight:bold;color:Blue;">${middle_str}</span>${item.label.substring(term.length + index)}`;

      return $( "<li></li>" )
          .data( "item.autocomplete", item )
          .append( "<a>" + new_item + "</a>" )
          .appendTo( ul );
  };
}

//function prepare_items(search_result) {
//   let result = []
//   for(var i = 0; i < search_result.length; i++) {
//     var e = search_result[i];
//     result.push(e[CLAZZ]);
//   }
//   let temp = new Set(result);
//   return Array.from(temp)
//}

$(document).ready(function() {
    $("#search_term").autocomplete({
                    source: function( request, response ) {
                        var url = "/api/search?search_term=" + $('#search_term').val()
                        $.ajax({
                            dataType: "json",
                            url: url,
                            success: function(data) {
                                //$('input.suggest-user').removeClass('ui-autocomplete-loading');
                                // hide loading image
                                var items = data.search_result;
                                response(items);
                            },
                            error: function(data) {
                                $('input.suggest-user').removeClass('ui-autocomplete-loading');
                            }
                        });
                    },
                    minLength: 3,
                    open: function() {},
                    close: function() {},
                    focus: function(event,ui) {},
                    select: function(event, ui) {
                        var data = ui.item.value;
                        $("#search_result").html("Book " + data + " was successfully selected");
                    }
                });
                monkey_patch_autocomplete();
})

