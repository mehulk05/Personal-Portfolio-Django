//Theme-2
$(document).ready(function() {
    
    $('.chart').easyPieChart({		
		barColor:'#03A9F4',
		trackColor: '#e8e8e8',
		scaleColor: false,
		lineWidth : 5,
		animate: 2000,
		onStep: function(from, to, percent) {
			$(this.el).find('span').text(Math.round(percent));
		}
	});    

});