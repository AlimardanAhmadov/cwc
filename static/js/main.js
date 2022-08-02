const navbarMenu = document.getElementById("menu");
const burgerMenu = document.getElementById("burger");
const bgOverlay = document.querySelector(".overlay");

// Show Menu when Click the Burger
// Hide Menu when Click the Overlay
if (burgerMenu && navbarMenu && bgOverlay) {
	burgerMenu.addEventListener("click", () => {
		navbarMenu.classList.toggle("is-active");
		bgOverlay.classList.toggle("is-active");
	});

	bgOverlay.addEventListener("click", () => {
		navbarMenu.classList.toggle("is-active");
		bgOverlay.classList.toggle("is-active");
	});
}

// Hide Menu when Click the Links
document.querySelectorAll(".menu-link").forEach((link) => {
	link.addEventListener("click", () => {
		navbarMenu.classList.remove("is-active");
		bgOverlay.classList.remove("is-active");
	});
});

$(document).ready(function(){
	$( ".form-check-input" ).each(function( index ) {
		console.log(index + ": " + $(this).val());
		var inputValue = $(this).val();
		var currentValues = $("input[name='list_available_days']").val();
		console.log(currentValues)
		if(currentValues.toLowerCase().includes(inputValue.toLowerCase())){
			console.log(inputValue)
			$(this).prop('checked', true);
		}
	});
})

function getCookie(name) {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}
  
const csrftoken = getCookie('csrftoken');

$(document).on('submit', '#signupForm', function(event){
	event.preventDefault();
	var bg = $('#imagePreview').css('background-image');
    bg = bg.replace('url(','').replace(')','').replace(/\"/gi, "");
	var input_data = {
		'first_name': $('input[name="first_name"]').val(),
		'last_name': $('input[name="last_name"]').val(),
		'phone_number': $('input[name="phone_number"]').val(),
		'email': $('input[name="email"]').val(),
		'username': $('input[name="username"]').val(),
		'password1': $('input[name="password1"]').val(),
		'password2': $('input[name="password2"]').val(),
		'username': $('#username').val(),
		'image_url': bg
	}

	$('#signupForm .menu-block').html('<div class="loader"></div>');
  
	$.ajax({
		type: 'POST',
		url: '/sign-up/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function (data) {
			$('#signupForm .menu-block').html('Sign Up');
			window.location.href = "/verify-sms/" + input_data['username'];
		},
        error: function (xhr, ajaxOptions, thrownError) {
			$('#signupForm .menu-block').html('Sign Up');
			window.location.href = "#";
			var list_of_errors = xhr.responseJSON['error']
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#signupFor');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				var list_of_errors = xhr.responseJSON['error']
				if ($('.msg-danger').length > 0) {
					$('.msg-danger').remove();
					$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
				
					+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#signupForm');
					for(let i = 0; i < list_of_errors.length; i++){  
						var newItem = "<li>" + list_of_errors[i] + "</li>";
						$( "#listError" ).append( newItem );
					}
				}
				else {
					$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
				
					+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#signupForm');
					for(let i = 0; i < list_of_errors.length; i++){
						var newItem = "<li>" + list_of_errors[i] + "</li>";
						$( "#listError" ).append( newItem );
					}
				}
			}
		}
	}); 
});

$(document).on('submit', '.verification', function(event){
	event.preventDefault();
	var input_1 = $('.verification__input--1').val();
	var input_2 = $('.verification__input--2').val();
	var input_3 = $('.verification__input--3').val();
	var input_4 = $('.verification__input--4').val();
	var input_5 = $('.verification__input--5').val();
	var input_6 = $('.verification__input--6').val();

	var pin_no = ''.concat('', input_1, input_2, input_3, input_4, input_5, input_6);
	var data = {
		'pin': pin_no,
	}

	var url = String(document.location.href);
	let url_username = url.substr(38)
	console.log(url_username)
  
	$.post({
		type: 'POST',
		url: '/verify-sms/' + url_username,
		data: JSON.stringify(data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function () {
			window.location.href = "/#login-modal";
		},
        error: function () {
			$('<span class="error-msg" style="color: red">The code is incorrect!</span>').insertBefore('.verification__fields')
		}
	}); 
});



$(document).on('click', '.verification__send_new', function(event){
	event.preventDefault();
  
	var url = String(document.location.href);
	let url_username = url.substr(33)
	$.post({
		type: 'POST',
		url: '/resend-sms/' + url_username + '/',
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function (data) {
			$('<span class="success-msg" style="color: green">New code is sent</span>').insertBefore('.verification__fields');
		},
        error: function (xhr, ajaxOptions, thrownError) {
			$('<span class="error-msg" style="color: red">'+ xhr.responseJSON['err'] +'</span>').insertBefore('.verification__fields');
		}
	}); 
});


function checkPasswordMatch() {
    var password = $('input[name="password1"]').val();
    var confirmPassword = $('input[name="password2').val();

    if (password != confirmPassword)
		$('input[type="password"]').css('border-color', 'red');
    else
		$('input[type="password"]').css('border-color', 'green');
}

function AutoPhoneFormatter() {
	var phone = $('input[name="phone"]').val();
	phone = phone.replace (/^/,'+');
}

$(document).on('click', ".xd-message-close", function(){
	$('.xd-message').remove()
})

$(document).on('click', ".list-of-badges .badge", function(event){
	var clicked_item = $(event.target);
	if (!(clicked_item).hasClass('selected')) {
		$(".badge.selected").removeClass("selected");
	}

	if ($(this).hasClass('selected')) {
		$(this).removeClass('selected');
	}
	else {
		$(this).addClass('selected')
	}
})

$(document).on('submit', '#coachForm', function(event){
	event.preventDefault();
	$('#coachForm .menu-block').html('<div class="loader"></div>');

	var titles = $('input[name=day]:checked').map(function(idx, elem) {
		return $(elem).val();
	}).get();
 
	var days = titles.join(", "); 

	var bg = $('#imagePreview').css('background-image');
    bg = bg.replace('url(','').replace(')','').replace(/\"/gi, "");
	var input_data = {
		'username': $('#username').val(),
		'first_name': $('input[name="first_name"]').val(),
		'last_name': $('input[name="last_name"]').val(),
		'phone_number': $('input[name="phone_number"]').val(),
		'email': $('input[name="email"]').val(),
		'password1': $('input[name="password1"]').val(),
		'password2': $('input[name="password2"]').val(),
		'category': $('select[name="category"]').find(":selected").text(),
		'about': $('textarea[name="about"]').val(),
		'available_days': days,
		'timing': $('input[name="from"]').val() + ', ' + $('input[name="to"]').val(),
		'image_url': bg,
	} 

	$.ajax({
		type: 'POST',
		url: '/become-coach/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function (data) {
			$('#coachForm .menu-block').html('Sign Up');
			window.location.href = "/verify-sms/" + input_data['username'];
		},
        error: function (xhr, ajaxOptions, thrownError) {
			$('#coachForm .menu-block').html('Sign Up');
			window.location.href = "#";
			var list_of_errors = xhr.responseJSON['err']
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#coachForm');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#coachForm');
				for(let i = 0; i < list_of_errors.length; i++){
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
		}
	}); 
});

let scheduled_function = false; 
const delay_by_in_ms = 500;
const coaches_div = $('.infinite-container');
const endpoint = '/search-coaches/';   

let ajax_call = function (endpoint, request_parameters) {
	$('.search-btn').html('<div class="loader"></div>');
  	$.getJSON(endpoint, request_parameters)
    .done(response => {  
		$('.search-btn').html('Find Coach');
		if ($('#main').length == 1) {
			$('#main').css({'margin-top': '0', 'margin-bottom': '40px'})
			$('#main').html('<div class="grid infinite-container">' + response['html_from_view'] + '</div>');
			$('.cta-section').remove()
		}
		else {
			coaches_div.html(response['html_from_view']);
			coaches_div.fadeTo('fast', 1);
		}
    })
}


$(document).on('click', '.search-btn', function(event){
	event.preventDefault(); 
	var name = $('input[name="name"]').val();
	var location = $('select[name="location"]').val();
	var category = $('.list-of-badges .badge.selected').text(); 

	if (!$(name)) {
		name = '';
	}

	if (!$(location)) {
		location = '';
	}

	if (!$(category)[0] == 'All') {
		category = '';
	}

	const request_parameters = {
		"name": name,
		"location": location,
		"category": category,
	}

	if (scheduled_function) {
		clearTimeout(scheduled_function)
	} 
	scheduled_function = setTimeout(ajax_call, delay_by_in_ms, endpoint, request_parameters)
}) 

function readURL(input) {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function(e) {
            $('#imagePreview').css('background-image', 'url('+e.target.result +')');
            $('#imagePreview').hide();
            $('#imagePreview').fadeIn(650);
        }
        reader.readAsDataURL(input.files[0]);
    }
}
$("#imageUpload").change(function() {
    readURL(this);
});

$(document).on('click', '.star-rating label', function(event){
	var clicked_item = $(event.target);
	if (!(clicked_item).hasClass('selected')) {
		$(".star-rating label").removeClass("selected");
	}

	if ($(this).hasClass('selected')) {
		$(this).removeClass('selected');
	}
	else {
		$(this).addClass('selected')
	}
})

$(document).on('submit', '#rateForm', function(event){
	event.preventDefault();
	var username = $('.user-info-top').data('username');
	var selected_input = $('.star-rating .selected').attr('for');
	var input_data = {
		'review_summary': $('input[name="review_summary"]').val(),
		'review_description': $('textarea[name="review_description"]').val(),
		'rating': $('#'+ selected_input +'').val(),
	} 
	$.ajax({
		type: 'POST',
		url: '/add_review/' + username,
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function () {
			$("#reviewList").load(location.href+" #reviewList>*","");
			$("#rateForm").load(location.href+" #rateForm>*","");
		},
        error: function (xhr, ajaxOptions, thrownError) {
			$("#reviewList").load(location.href+" #reviewList>*","");
			$("#rateForm").load(location.href+" #rateForm>*","");
			var list_of_errors = xhr.responseJSON['err']
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#rateForm');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#rateForm');
				for(let i = 0; i < list_of_errors.length; i++){
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
		}
	}); 
});


$(document).on('submit', '#updateProfile', function(event){
	event.preventDefault();
	var bg = $('#imagePreview').css('background-image');
    bg = bg.replace('url(','').replace(')','').replace(/\"/gi, "");
	console.log(bg)
	var input_data = {
		'full_name': $('input[name="full_name"]').val(),
		'email': $('input[name="email"]').val(), 
		'phone_number': $('input[name="phone_number"]').val(), 
		'image_url': bg
	} 
	$('.save-changes button').html('<div class="loader"></div>');
	$.ajax({
		type: 'POST',
		url: '/update-profile/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function () {
			$('.save-changes button').html('Save Changes');
		},
        error: function (xhr, ajaxOptions, thrownError) {
			var list_of_errors = xhr.responseJSON['err']
			$('.save-changes button').html('Save Changes');
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#updateProfile');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#updateProfile');
				for(let i = 0; i < list_of_errors.length; i++){
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
		}
	}); 
});


$(document).on('submit', '#editCoachInfo', function(event){
	event.preventDefault();
	var titles = $('input[name=day]:checked').map(function(idx, elem) {
		return $(elem).val();
	}).get();
 
	var days = titles.join(", "); 
	var bg = $('#imagePreview').css('background-image');
    bg = bg.replace('url(','').replace(')','').replace(/\"/gi, "");
	var input_data = {
		'full_name': $('input[name="full_name"]').val(),
		'email': $('input[name="email"]').val(), 
		'phone_number': $('input[name="phone_number"]').val(), 
		'old_password': $('input[name="old_password"]').val(),
		'available_days': days,
		'category': $('select[name="category"]').val(), 
		'about': $('textarea[name="about"]').val(), 
		'timing': $('input[name="timing"]').val(),
		'image_url': bg
	};
	$('#editCoachInfo .menu-block').html('<div class="loader"></div>');
	$.ajax({
		type: 'POST',
		url: '/edit-profile/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function () {
			$('#editCoachInfo .menu-block').html('Save Changes');
		},
        error: function (xhr, ajaxOptions, thrownError) {
			$('#editCoachInfo .menu-block').html('Save Changes');
			var list_of_errors = xhr.responseJSON['err'];
			window.scrollTo(0, 0);
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#editCoachInfo');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#editCoachInfo');
				for(let i = 0; i < list_of_errors.length; i++){
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
		}
	}); 
});


$(document).on('submit', '#addServiceForm', function(event){
	event.preventDefault();
	var input_data = {
		'service_title': $('input[name="service_title"]').val(),
		'service_description': $('textarea[name="service_description"]').val(), 
	} 
	$.ajax({
		type: 'POST',
		url: '/add-service/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function (data) {
			window.location.href = "#";
			$(".services").load(location.href+" .services>*","");
			const nextURL = String( document.location.href ).replace( "#", "" );
			const nextTitle = 'My new page title';
			const nextState = { additionalInformation: 'Updated the URL with JS' };
  			window.history.pushState(nextState, nextTitle, nextURL);
			$('input[name="service_title"], textarea[name="service_description"]').val('');
		},
        error: function () { 
			console.log('error')
		}
	});
});


$(document).on('click', '.edit-btn', function(){
	var $div=$(this).closest('.service-item').find('.service-description, .card-body-title span'), isEditable=$div.is('.editable, .form-control');
	$(this).closest('.service-item').find('.service-description, .card-body-title span').prop('contenteditable',!isEditable).toggleClass('editable form-control');
	if ($(this).closest('.service-item').find('.save-btn').length == 0) {
		$(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-x-lg" viewBox="0 0 16 16"><path d="M2.146 2.854a.5.5 0 1 1 .708-.708L8 7.293l5.146-5.147a.5.5 0 0 1 .708.708L8.707 8l5.147 5.146a.5.5 0 0 1-.708.708L8 8.707l-5.146 5.147a.5.5 0 0 1-.708-.708L7.293 8 2.146 2.854Z"/></svg>')
		$('<button type="button" class="btn save-btn">Save</button>').insertBefore(this);
		$(this).css('background-color', '#dfdfdf'); 
	}
	else {
		$(this).html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16"><path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"></path></svg>')
		$(this).closest('.service-item').find('.save-btn').remove();
		$(this).closest('.service-item').find('.save-btn').addClass('disabled');
		$(this).css('background-color', '#fff'); 
	}
})


$(document).on('DOMSubtreeModified', '.service-description, .card-body-title span', function(){
	if ($('.editable.card-body-title span').is(':empty')) {
		$('.save-btn').addClass('disabled');
	}
	else {
		$('.save-btn').removeClass('disabled');
	}
})

$(document).on('click', '.service-actions .save-btn', function(event){
	event.preventDefault();
	var this_btn = $(this);
	var service_id = this_btn.closest('.service-item').data('id');

	var input_data = {
		'service_title': $('.card-body-title .editable.form-control').text(),
		'service_description': $('.editable.service-description').text(), 
	} 
	this_btn.html('<i class="fa fa-circle-o-notch fa-spin"></i>');
	$.ajax({
		type: 'POST',
		url: '/update-service/' + service_id,
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { "X-CSRFTOKEN": csrftoken, "Content-type": "application/json" },
		success: function () {
			$('.card-body-title .editable.form-control, .editable.service-description').prop('contenteditable',false).removeClass('editable form-control');
			$('.save-btn').remove();
			$('.edit-btn').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16"><path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"></path></svg>').css('background-color', '#fff');
		},
        error: function () {
			$('.edit-btn').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-pencil" viewBox="0 0 16 16"><path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"></path></svg>').css('background-color', '#fff');;
		}
	});
});


$(document).on('click', '.service-actions .remove-btn', function(event){
	event.preventDefault();
	var $this_btn = $(this);
	var service_id = $this_btn.closest('.service-item').data('id');

	var input_data = {
		'service_title': $('.card-body-title .editable.form-control').text(),
		'service_description': $('.editable.service-description').text(), 
	} 
	$this_btn.html('<i class="fa fa-circle-o-notch fa-spin"></i>');
	$.ajax({
		type: 'POST',
		url: '/delete-service/' + service_id,
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: {'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function () {
			$this_btn.closest('.service-item').remove();
		},
        error: function () {
			$('.remove-btn').html('<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-trash3" viewBox="0 0 16 16"><path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H2.506a.58.58 0 0 0-.01 0H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84l.853-10.66h.538a.5.5 0 0 0 0-1h-.995a.59.59 0 0 0-.01 0H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Zm-7.487 1a.5.5 0 0 1 .528.47l.5 8.5a.5.5 0 0 1-.998.06L5 5.03a.5.5 0 0 1 .47-.53Zm5.058 0a.5.5 0 0 1 .47.53l-.5 8.5a.5.5 0 1 1-.998-.06l.5-8.5a.5.5 0 0 1 .528-.47ZM8 4.5a.5.5 0 0 1 .5.5v8.5a.5.5 0 0 1-1 0V5a.5.5 0 0 1 .5-.5Z"></path></svg>').css('background-color', '#fff');
		}
	}); 
});



$(document).on('click', '.paypal-buy-now-button', function(event){
	event.preventDefault();
	$(this).html('<div class="loader"></div>')
	$.ajax({
		type: 'POST',
		url: '/purchase-subscription',
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function (data) {
			window.location.href = data.redirect_value
		},
        error: function () {
		}
	}); 
});

$(document).on('click', '#cancelBtn', function(event){
	event.preventDefault();
	var $this_btn = $(this);
	$this_btn.html('<div class="loader"></div>')
	$.ajax({
		type: 'POST',
		url: '/cancel-subscription',
		dataType: 'json',
		headers: {'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"},
		success: function () {
			window.location.href = "#";
			const nextURL = String( document.location.href ).replace( "#", "" );
			const nextTitle = 'My new page title';
			const nextState = { additionalInformation: 'Updated the URL with JS' };
  			window.history.pushState(nextState, nextTitle, nextURL);
			location.reload();
		},
        error: function () {
		}
	}); 
});


$(document).on('submit', '#changePasswordForm', function(event){
	event.preventDefault();
	var input_data = {
		'old_password': $('input[name="old_password"]').val(), 
		'password': $('input[name="password"]').val(), 
		'password2': $('input[name="password2"]').val(), 
	}
	$('#changePasswordForm button').html('<div class="loader"></div>')
	$.ajax({
		type: 'POST',
		url: '/change-password',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function () {
			window.location.href = "#";
		},
        error: function (xhr, ajaxOptions, thrownError) {
			var list_of_errors = xhr.responseJSON['err']
			$('#changePasswordForm button').html('Save')
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#changePasswordForm');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#changePasswordForm');
				for(let i = 0; i < list_of_errors.length; i++){
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
		}
	}); 
});

$(document).on('submit', '#loginForm', function(event){
	event.preventDefault();
	var input_data = {
		'username': $('input[name="username"]').val(),
		'password': $('input[name="password"]').val(),
	}

	$('#loginForm .menu-block').html('<div class="loader"></div>');
  
	$.ajax({
		type: 'POST',
		url: '/login/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function (data) {
			$('#loginForm .menu-block').html('Login');
			const nextURL = String( document.location.href ).replace( "#login-modal", "" );
			const nextTitle = 'My new page title';
			const nextState = { additionalInformation: 'Updated the URL with JS' };
  			window.history.pushState(nextState, nextTitle, nextURL);
			location.reload();
		},
        error: function (xhr, ajaxOptions, thrownError) {
			$('#loginForm .menu-block').html('Login');
			
			var list_of_errors = xhr.responseJSON['error']
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#loginForm');
				for(let i = 0; i < list_of_errors.length; i++){
					if (list_of_errors[i].includes('The phone number is not verified.')) {
						var newItem = "<li>" + list_of_errors[i] + '<a style="padding-left: 5px; color: #707070;" class="small" href="/verify-sms/'+ $('input[name="username"]').val() +'">Verify Phone Number</a>' + "</li>";
					}
					else {
						var newItem = "<li>" + list_of_errors[i] + "</li>";
					}
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#loginForm');
				for(let i = 0; i < list_of_errors.length; i++){
					if (list_of_errors[i].includes('The phone number is not verified.')) {
						var newItem = "<li>" + list_of_errors[i] + '<a style="padding-left: 5px; color: #707070;" class="small" href="/verify-sms/'+ $('input[name="username"]').val() +'">Verify Phone Number</a>' + "</li>";
					}
					else {
						var newItem = "<li>" + list_of_errors[i] + "</li>";
					}
					$( "#listError" ).append( newItem );
				}
			} 
		}
	}); 
});

$(document).on('submit', '#resetsendForm', function(event){
	event.preventDefault();
	var input_data = {
		'email': $('input[name="email"]').val(), 
	}
	console.log(input_data)
	$('#resetsendForm button').html('<div class="loader"></div>')
	$.ajax({
		type: 'POST',
		url: '/reset/password/',
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function () {
			$('#resetsendForm button').html('Submit');
			$('input[name="email"]').val('');
			$('<span>Password reset e-mail has been sent! Please check your inbox</span>').insertBefore('#resetsendForm');
			$('#resetsendForm .form-block, #resetsendForm .menu-block').remove();
		},
        error: function (xhr, ajaxOptions, thrownError) {
			var list_of_errors = xhr.responseJSON['err']
			$('#resetsendForm button').html('Submit')
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#resetsendForm');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#resetsendForm');
				for(let i = 0; i < list_of_errors.length; i++){
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
		}
	}); 
});

$(document).on('submit', '#confirmResetForm', function(event){
	event.preventDefault();
	var url = String(document.location.href).replace( "http://localhost:8000", "" );
	
	var input_data = {
		'new_password1': $('input[name="new_password1"]').val(), 
		'new_password2': $('input[name="new_password2"]').val(), 
		'uid':url.substring(24, 26),
		'token':url.substring(27, 66),
	}
	$('#confirmResetForm button').html('<div class="loader"></div>');
	$.ajax({
		type: 'POST',
		url: url,
		data: JSON.stringify(input_data),
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function () {
			window.location.href = "/";
			$('#confirmResetForm button').html('Save');
			$('input[name="email"]').val('');
		},
        error: function (xhr, ajaxOptions, thrownError) {
			var list_of_errors = xhr.responseJSON['err']
			$('#confirmResetForm button').html('Submit')
			if ($('.msg-danger').length > 0) {
				$('.msg-danger').remove();
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#confirmResetForm');
				for(let i = 0; i < list_of_errors.length; i++){  
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
			else {
				$('<div class="xd-message msg-danger"><div class="xd-message-icon"><i class="ion-close-round"></i></div><div class="xd-message-content"><ul id="listError">'
			
				+'</ul></div><a class="xd-message-close"><i class="close-icon ion-close-round"></i></a>  </div>').insertBefore('#confirmResetForm');
				for(let i = 0; i < list_of_errors.length; i++){
					var newItem = "<li>" + list_of_errors[i] + "</li>";
					$( "#listError" ).append( newItem );
				}
			}
		}
	}); 
});

$(document).on('click', '#signOut', function(event){
	event.preventDefault();
  
	$.ajax({
		type: 'POST',
		url: '/logout/',
		dataType: 'json',
		headers: { 'X-CSRFTOKEN': csrftoken, "Content-type": "application/json"  },
		success: function (data) {
			window.location.href = "";
		},
        error: function () {
			console.log("Something went wrong!")
		}
	}); 
});


$(document).on('click', '#right-slide', function(event){
	console.log("asda");
	$('.list-of-badges').animate({
		scrollLeft: "+=200px"
	}, "slow");
}) 

$(document).on('click', '#left-slide', function(event){
	event.preventDefault();
	$('.list-of-badges').animate({
		scrollLeft: "-=200px"
	}, "slow");
}) 

$(document).on('click', '.modal-close', function(){
	window.location.href = "#";
})

let copyText = document.querySelector(".copy-text");
copyText.querySelector("button").addEventListener("click", function () {
	let input = copyText.querySelector("input.text");
	input.select();
	document.execCommand("copy");
	copyText.classList.add("active");
	window.getSelection().removeAllRanges();
	setTimeout(function () {
		copyText.classList.remove("active");
	}, 2500);
});

