$(document).ready(function(){
    $("#logbtn").click(function() {
        $("#successMessage").show();

        // After 3 seconds, hide the success message
        setTimeout(function() {
            $('#successMessage').hide();
        }, 5000);
    });
});
