//Theme-1
$(document).ready(function() {
    
    $('.chart').easyPieChart({		
		barColor:'#00BCD4',
		trackColor: '#e8e8e8',
		scaleColor: false,
		lineWidth : 5,
		animate: 2000,
		onStep: function(from, to, percent) {
			$(this.el).find('span').text(Math.round(percent));
		}
	});    

});