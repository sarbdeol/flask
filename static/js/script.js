$(document).ready(function(){

    var intervalId = window.setInterval(function(){
        check_every_secont()
      }, 5000);


      function check_every_secont() {
            $.ajax({
                url: '/check_page_count',
                type: 'GET',
                success: function(data) {
                    console.log(data.page_no);
                    console.log(data['Total Page']);
                    console.log(data['Page Left']);
                    // Update the HTML elements with the received data
                    $('#pageNo').text('Current Page: ' + data.page_no);
                    $('#pageLength').text('Page Length: ' + data['Page Length']);
                    $('#pageLeft').text(data['Page Length']);

                    if (data.Input === true) {
                        $("#pageNo").show();
                        $("#pageLength").show();
                        $("#pageLeft").show();
                    
                }
                    
                },
                error: function(error) {
                    console.error('Error:', error);
                }
            });
        }


    
    })