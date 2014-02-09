/* This script fix the progress bar for IE in case of overload */
$(window).load( function() {
    $('.progressspan').each( function(i) {
	var sp = $(this).filter('span').attr("style");
	var str = sp.split(':');
	var vals = str[1].split(':');
	var cur_val = vals[0].split('%;');
	
	if(parseInt(cur_val[0].trim(',')) >= 100) {
	    $(this).filter('span').attr("style","width: 100%;");
	}
    });
});
