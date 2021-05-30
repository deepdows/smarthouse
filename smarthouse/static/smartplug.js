$(function() {
    window.setInterval(function(){
        load_data();
    }, 1000)
    function load_data(){
        $.ajax({
            url: '/smartplug/data',
            type: 'GET',
            dataType: 'json',
            success: function(data){
                $('.temp .value').text(data['temperature'].toFixed(1));
                $('.hum .value').text(data['humidity']);
                $('.pressure .value').text(data['pressure'].toFixed(1));
                $('.co2 .value').text(data['co2']);
            }
        });
        $.ajax({
            url: '/smartplug/status',
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if (data['is_online'])
                    $('#signal').html('<span id="online">Online</span>');
                else
                    $('#signal').html('<span id="offline">Offline</span>');
            }
        });
        $.ajax({
            url: '/smartplug/settings',
            type: 'GET',
            dataType: 'json',
            success: function(data){
                if(!$.isEmptyObject(data)){
                    $('#radio'+child).attr("checked", "true");
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