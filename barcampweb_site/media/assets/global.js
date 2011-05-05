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

$(function() {
    $('body').click(function(evt) {
        var dialog = $(this).data('activeDialog');
        if (dialog) dialog.hide();
    });
    $('.actions.collapsable').each(function() {
        var outer = $(this),
            inner = $('> ul', outer),
            label = $('> .label', outer);
        outer.css({'position': 'relative', 'width': '16px'});
        inner.css({'position': 'absolute', 'bottom': '0', 'right': '0'}).hide();
        label.click(function(evt) {
            evt.preventDefault();
            evt.stopPropagation();
            inner.toggle();
            var other = $('body').data('activeDialog');
            if (other) other.hide();
            $('body').data('activeDialog', inner);
        });
    });
});
