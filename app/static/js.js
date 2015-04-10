var streak = 0;2
var max_streak = 0;
var u_name;

var submittedd = false;
var prompt_submit = true;

var prompt_submission = function(){
	$('#myModal').modal('show');
}

var display_streak = function(){
	max_streak = Math.max(streak, max_streak);
	$("#streak").html(streak);
	$('#maxstreak').html(max_streak);
}

var print_result = function(wl){
	var message;
	if(wl == 1){
		message = '<h1 class="alert alert-success">YOU ARE RIGHT.</h1>';
	}else{
		message = '<h1 class="alert alert-danger">YOU ARE WRONG!!!!</h1>';
	}
	$('#resMessage').html(message);
}

var wikipediaize = function(player_name){
	return('http://en.wikipedia.org/wiki/' + player_name);
}

var display_loss = function(player_name, stats){
	message = '<h1 class="alert alert-danger">YOU GAVE UP.  The player was <a target="_blank" href="' + wikipediaize(player_name) + '"">' + player_name + '</a>!!!!</h1>';
	$('#resMessage').html(message);
	nextbtn = '<button id="next" class="btn btn-default"> NEXT </button>'
	currentcontents=$('#input_stuff').html();
	$('#input_stuff').html(nextbtn);
	$('#next').click(function(){
		$('#input_stuff').html(currentcontents);
		replace_table(stats);
		prep_buttons();
		$("#player").focus();
	})
}

var replace_table = function(newtable){
	$('#stattable').html(newtable);
}

var prep_buttons = function(){
	$('#go_btn').click(function(){
		if(submittedd != true){
			submittedd = true;
			var player = $('#player').val();
			if(player!=''){
				$.ajax({
					url: "/submit",
					data: {
						player_name: player,
						p_num: pnum
					},
					success: function(data){
						print_result(data.successCode);
						if(data.successCode == 1){
							replace_table(data.stats);
							pnum = data.pnum;
							$('#player').val('');
							streak++;
							display_streak();
						} else {
							$('#player').select();
							streak = 0;
							display_streak();
							setTimeout(prompt_submission, 400);
						}
						submittedd = false;
					},
					error: function(data){
						console.log(data);
						submittedd = false;
					}
				});
			}
		}
	});


	$('#give_btn').click(function(){
		$.ajax({
			url: "/giveup",
			data: {
				p_num: pnum
			},
			success: function(data){
				pnum = data.pnum;
				display_loss(data.player_name, data.stats);
				streak = 0;
				display_streak();
				setTimeout(prompt_submission, 400);
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

	prep_buttons();

});