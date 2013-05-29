// Document Ready
$(document).ready(function(){
	vertical_center();
});

function vertical_center() {
	var container = $("#vertical-center");
	if (container) {
		var margin_top = ($(window).height() - container.height()) / 2;
		container.css("margin-top", margin_top);
	}
}