var l_t_stats;
var r_t_stats;
var compute_totals = function(stats){
	t_stats = ['Total'];
	$.each(stats, function(row_num, row){
		$.each(row, function(index, value){
			if(index == 0){
				
			}else if(index==8){
				t_stats[index] = (t_stats[6]/t_stats[7]).toFixed(3);
			}else if(index == 12){
				t_stats[index] = (t_stats[10]/t_stats[11]).toFixed(3);
			}
			else if($.inArray(index, [2,3])>-1){
				t_stats[index] = 0;
			} else{
				if(value==''){
					value = 0;
				}
				if(t_stats[index]){
					t_stats[index] = parseFloat(t_stats[index])+Math.round(10*parseFloat(value))/10;
				} else {
					t_stats[index] = parseFloat(value);
				}
			}
		});
	});
	return t_stats;
}

var add_t_stats = function(table){
	stats = [];
	table.children().each(function(index){
		if(index != 0){
			st = [];
			$(this).children().each(function(index){
				st.push($(this).text());
			});
			stats.push(st);
		}
	});
	return stats;
}

var display_t_stats = function(table, stats){
	var t_stats = stats;
	t_array = [];
	$.each(t_stats, function(index, value){
		t_array.push("<td>"+value+"</td>");
	});
	thtml = "<tr>"+t_array.join()+"</tr>";
	table.parent().children('tfoot').html(thtml)
}

var set_shared = function(){
	tleft = $("#team1 .stattable tfoot").html();
	tleft = $(tleft);
	tleft.find("td:eq(0)").html($("#left .teamname").val());
	tright = $("#team2 .stattable tfoot").html();
	tright = $(tright);
	tright.find("td:eq(0)").html($("#right .teamname").val());
	$("#shared .stattable").html("<tr>"+ $("#team1 .stattable tbody :eq(0)").html() + "</tr>" + "<tr>"+tleft.html()+"</tr>" + "<tr>" + tright.html() + "</tr>");
	$("#shared .stattable tbody").children().each(function(row){
		$(this).children().each(function(column){
			console.log($(this).html())
			if($.inArray(column, [8,9,12,13,14,15,16,18])>-1){
				if(parseFloat(l_t_stats[column]) >= parseFloat(r_t_stats[column]) && row==1){
					$(this).addClass('winner');
				} else if(parseFloat(l_t_stats[column]) <= parseFloat(r_t_stats[column]) && row==2){
					$(this).addClass('winner');
				}
			} else if(column == 17){
				if(l_t_stats[column] <= r_t_stats[column] && row==1){
					$(this).addClass('winner');
				}
				else if(l_t_stats[column] >= r_t_stats[column] && row==2){
					$(this).addClass('winner');
				}
			}
		});
	});
}

var lstats = [];
var rstats = [];
$( document ).ready(function(){
	$('.pos_inp').autocomplete({
		position:{collision: "flip"},
		source: names
	});
	$('.go_btn').click(function(){
		var dt = $('#left').serializeArray();
		var rt = $('#right').serializeArray();
		$.ajax({
			url: "/sub_draft",
			data: {
				playerl: JSON.stringify(dt),
				playerr: JSON.stringify(rt),
				mode: $('#selector').val()
			},
			success: function(data){
				$('#team1 .stattable tbody').append(data.lstats);
				$('#team2 .stattable tbody').append(data.rstats);
				$('#left').children('div').each(function(index){
					if($.inArray($(this).children('input').val(), data.lnames)>-1){

						$(this).html($(this).text()+$(this).children('input').val());
					}
				});
				$('#right').children('div').each(function(index){
					if($.inArray($(this).children('input').val(), data.rnames)>-1){

						$(this).html($(this).text()+$(this).children('input').val());
					}
				});
				l_t_stats = compute_totals( add_t_stats($('#team1 .stattable tbody')));
				r_t_stats = compute_totals( add_t_stats($('#team2 .stattable tbody')));
				display_t_stats($('#team1 .stattable tbody'),l_t_stats);
				display_t_stats($('#team2 .stattable tbody'),r_t_stats);
				set_shared();
			}
		});
		return false;
	});
	$('.pos_inp').keypress(function (e){
		var key = e.which;
		if(key == 13) {
			$('#go_btn1').click();
			return false;
		}
	});
});