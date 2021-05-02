$(function() {
    window.setInterval(function(){
        loadData();
    }, 1000)
    function loadData(){
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
    }
});
$('#settings').on('click', function(){
    $('.monitoring').toggle('fast');
    $('.settings').toggle('fast');
    $('#settings img:nth-child(1)').toggle();
    $('#settings img:nth-child(2)').toggle();
});