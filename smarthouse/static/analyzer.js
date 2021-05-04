$(function() {
    window.setInterval(function(){
        load_data();
    }, 1000)
    function load_data(){
        $.ajax({
            url: '/analyzer/data',
            type: 'GET',
            dataType: 'json',
            success: function(data){
                $('.temp .value').text(data['temp']);
                $('.hum .value').text(data['hum']);
                $('.pressure .value').text(data['pressure']);
                $('.co2 .value').text(data['co2']);
            }
        });
        $.ajax({
            url: '/analyzer/status',
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if (data['isOnline'])
                    $('#signal').html('<span id="online">Online</span>');
                else
                    $('#signal').html('<span id="offline">Offline</span>');
            }
        });
        $.ajax({
            url: '/analyzer/settings',
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if(data){
                    if(2 > data['brightness'] >= 0)
                        child = 1;
                    else if(65 > data['brightness'] >= 2)
                        child = 2;
                    else if(130 > data['brightness'] >= 65)
                        child = 3;
                    else if(190 > data['brightness'] >= 130)
                        child = 4;
                    else if(data['brightness'] >= 190)
                        child = 5;
                    else if(data['brightness'] >= 255)
                        child = 6;
                    $('.settings .brightness input:nth-child('+child+')').attr("checked", "true");
                    $('.settings .sync-container input').attr("placeholder", data['sync']);
                }
            }
        });
    }
      
});
$('#settings').on('click', function(){
    $('.monitoring').toggle('fast');
    $('.settings').toggle('fast');
    $('#settings img:nth-child(1)').toggle();
    $('#settings img:nth-child(2)').toggle();
});