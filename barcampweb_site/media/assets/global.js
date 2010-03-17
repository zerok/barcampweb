jQuery.fn.defaultFormOverlay = function(){
    this.bind('click', function(ev){
        ev.preventDefault();
        $('#xhrOverlay').empty();
        var $this = $(this);
        // Load the form overlay
        $('#xhrOverlay').load($(this).attr('href'), function(data, status, xhr){
            $('form', this).attr('action', $this.attr('href'));
            $('#xhrOverlay').overlay({
               api: true,
               expose: {
                   opacity: 0.8,
                   loadSpeed: 200,
                   color: '#000'
               }
               
            }).load();
        });
    });
};