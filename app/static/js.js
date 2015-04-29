var streak = 0;
var last_streak = 0;
//var max_streak = 0;
var u_name;

var submittedd = false;
var prompt_submit = true;

var choose_prompt = function(){
	$.ajax({
		url: "/get_user_max",
		success: function(data){
			if(data.score > -1){
				$.ajax({
					url: "/submit_score",
					data: {
						score: last_streak,
						name:  u_name
					}
				});
			} else{
				if(last_streak > data.score){
					setTimeout(prompt_submission, 400);
				}
			}
		}
	});
}

var prompt_submission = function(){
	$('#score_placement').html(last_streak);
	$('#myModal').modal('show');
}

var display_streak = function(){
	max_streak = Math.max(streak, max_streak);
	$("#streak").html(streak);
	$('#maxstreak').html(max_streak);
}

function autoClose(selector, delay) {
   var alert = $(selector).alert();
   window.setTimeout(function() { alert.alert('close') }, delay);
}

var print_result = function(wl){
	var message;
	if(wl == 1){
		message = '<h1 class="alert alert-success fade in res" role="alert">YOU ARE RIGHT.</h1>'; //PUT THE TAGS IN THE HTML NOT THE JS
	}else{
		message = '<h1 class="alert alert-danger fade in res" role="alert">YOU ARE WRONG!!!!</h1>';
	}
	$('#resMessage').html(message);
	autoClose('.res', 3000);

}

var wikipediaize = function(player_name){
	return('http://en.wikipedia.org/wiki/' + player_name);
}

var display_loss = function(player_name, stats){
	message = '<h1 class="alert alert-danger fade in res" role="alert">YOU GAVE UP.  The player was <a target="_blank" href="' + wikipediaize(player_name) + '"">' + player_name + '</a>!!!!</h1>';
	$('#resMessage').html(message);
	nextbtn = '<button id="next" class="btn btn-default"> NEXT </button>'
	currentcontents=$('#input_stuff').html();
	$('#input_stuff').html(nextbtn);
	$('#next').click(function(){
		$('#input_stuff').html(currentcontents);
		replace_table(stats);
		prep_buttons();
		$("#player").focus();
		autoClose('.res', 3000);
	})
}

var replace_table = function(newtable){
	$('#stattable').html(newtable);
}

var prep_buttons = function(){
	$('#go_btn').click(function(){
		//console.log('button press!' + $('#player').val());
		if(submittedd != true){
			//console.log('button goin in');
			submittedd = true;
			//console.log('true set');
			var player = $('#player').val();
			if(player!=''){
				console.log('player!=nothing')
				$.ajax({
					url: "/submit",
					data: {
						player_name: player,
						p_num: pnum,
						mode: mode
					},
					success: function(data){
						submittedd = false;
						print_result(data.successCode);
						if(data.successCode == 1){
							replace_table(data.stats);
							pnum = data.pnum;
							//console.log('set it to nothing');
							$('#player').val('');
							streak++;
							display_streak();
						} else {
							$('#player').select();
							last_streak = streak;
							streak = 0;
							display_streak();
							if(last_streak > 0){
								choose_prompt();
							}
						}
						submittedd = false;
						console.log('false set');
					},
					error: function(data){
						console.log(data);
						alert('please try again');
						submittedd = false;
						console.log('false set error');
					},
					/*always: function(){

					}*/
				}).always(function(){submittedd=false;});
			} else {
				submittedd = false;
			}
		}
	});


	$('#give_btn').click(function(){
		$.ajax({
			url: "/giveup",
			data: {
				p_num: pnum,
				mode: mode
			},
			success: function(data){
				pnum = data.pnum;
				display_loss(data.player_name, data.stats);
				last_streak = streak;
				streak = 0;
				display_streak();
				if(last_streak > 0){
					choose_prompt();
				}
			}
		});
	});

	$('#player').keypress(function (e){
		var key = e.which;
		if(key == 13) {
			$('#go_btn').click();
			return false;
		}
	});

	$('#player').autocomplete({
		position:{my: "left bottom", at: "left top", collision: "flip"},
		source: names
	});
}

$(document).ready(function(){
	//alert("bitch");
	$('#myModal').on('shown.bs.modal', function () {
  		$('#user_name').focus();
	});
	$('#submit_score').click(function(){
		//alert('i was clicked');
		u_name = $('#user_name').val();
		if(/[^a-zA-Z0-9 _]/.test(u_name)){
			$('#helpblock').html('Please enter a name with only letters, numbers, and underscores.');
			$('#submit_form').addClass('has-error');
		} else {
			$('#submit_form').removeClass('has-error');
			//alert('test passed');
			$.ajax({
				url: "/submit_score",
				data: {
					score: last_streak,
					name:  u_name
				},
				success: function(data){
					$('#myModal').modal('hide');
				}
			});
			$('#helpblock').html('');
		}
	});
	$('#leaderboard_btn').click(function(){
		//alert('i was clicked');
		$.ajax({
				url: "/leaderboard",
				success: function(data){
					$('#leaderboard_table').html(data);
				}
			});
	});
	$('#user_name').keypress(function (e){
		var key = e.which;
		if(key == 13) {
			$('#submit_score').click();
			return false;
		}
	});
	prep_buttons();

});