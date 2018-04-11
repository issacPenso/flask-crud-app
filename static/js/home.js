function validateForm() {
    var book_title = document.forms.addBook.title.value;
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