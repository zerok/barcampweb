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
        if ($('li', inner).length == 0) outer.hide();
        outer.css({'width': '16px'});
        label.css({'cursor':'pointer'});
        inner.appendTo('body').hide();
        label.click(function(evt) {
            var labelOffset = label.offset();
            evt.preventDefault();
            evt.stopPropagation();
            inner.css({'position': 'absolute', 'left': labelOffset.left+10, 'top': labelOffset.top+4}).toggle();
            console.log(label.offset());
            var other = $('body').data('activeDialog');
            if (other && other !== inner) other.hide();
            $('body').data('activeDialog', inner);
        });
    });
});
