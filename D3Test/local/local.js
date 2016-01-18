$(document).ready(function(){

	$('#hosts-btn a').click(function (e) {
	  e.preventDefault()
	  $('this').tab('show')
	  $('#hosts-tab').tab('show')
	})

	$('#services-btn a').click(function (e) {
	  e.preventDefault()
	  $('this').tab('show')
	  $('#services-tab').tab('show')
	})
	
})
