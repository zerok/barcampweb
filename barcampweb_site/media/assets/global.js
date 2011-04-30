jQuery.fn.defaultFormOverlay = function(){
    this.bind('click', function(ev){
        ev.preventDefault();
        var $overlay = $('#xhrOverlay'),
            $this = $(this),
            href = $this.attr('href');
        // Load the form overlay
        $overlay.empty().load(href, function(data, status, xhr){
            $('form', this).attr('action', href);
            var overlay = $overlay.overlay({
               api: true,
               expose: {
                   opacity: 0.8,
                   loadSpeed: 200,
                   color: '#000'
               }
               
            });
            $('.cancel', $overlay).bind('click', function(ev){
                ev.preventDefault();
                overlay.close();
            });
            overlay.load();
        });
    });
};
