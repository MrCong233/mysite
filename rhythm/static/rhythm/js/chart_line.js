/**
 * Created by 30947 on 2018/7/18.
 * sumbit_data_line: poi整体概率统计 
 */
$(function () {
	//	chart1();

})
var method_choice;
var submitted = false;

function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function submit_data_line() {
	var csrftoken = getCookie('csrftoken');
	//包装数据
	var formData = {
		'method': 'method10',
		'method10': $("#method10  option:selected").val()
	};
	console.log(formData);
	//发送后submited=true，并更换加载图片，表示正在加载。
	method_choice = formData["method"];
	//	$('#final_image').attr('src', '/static/rhythm/img/loading.gif');
	
	if (method_choice == 'method10') {
		method_choice = "";
		time = formData['method10'];
		
		//暂时数据写死
		time = '6_7';
		
		url = "/static/rhythm/json/taxi_track_one_hour_poi_road/20140803_taxi_track_" + time + "_poi_road" + ".json";
		$.getJSON(url, function (result) {
			console.log(result);
			makeChart_line(result)
		});
	}

}
//将poi频率向量转换成poi概率向量
function handle_data(data){
	var length = data.length;
	var t = [];
	var sum = 0;
	for(var i=0;i<length;i++){
		sum+=data[i];
	}
	for(var ii=0 ;ii<length;ii++){
		var tmp = data[ii]*1.0/(sum+0.0);
		t.push(tmp);
	}
	return t;
}
function makeChart_line(data) {
	var poi_types = data["poi_types"];
	
	var poi_probability = handle_data(data["whole_poi_vector"]);
	console.log(poi_probability);
//	return ;
	var myChart = echarts.init($("#chart_3")[0]);
	var len = poi_types.length;
	var option = {
		backgroundColor: "#fff",
		title: {
			text: '成都市POI概率分布',
		},
		tooltip: {
			trigger: 'axis',
			formatter: function (params, ticket, callback) {
				console.log(params[0]);
				var poi = params[0].data.poi;
				var value = params[0].value;
				var name = params[0].name;
				return value + "<br/> POI:" + poi;
			}
		},
//		xAxis: {
//			data: data.map(function (item) {
//				return item[2];
//			})
//		},
		xAxis:{
			data: poi_types
		},
		yAxis: {
			splitLine: {
				show: false
			}
		},
		dataZoom: [{
			startValue: 1
		}, {
			type: 'inside'
		}],
		visualMap: {
			type: "piecewise",
			top: 10,
			right: 10,
			pieces: [{
				gt: 0,
				lte: 0.2,
				label: "0 - 0.2",
				color: '#096'
			}, {
				gt: 0.2,
				lte: 0.4,
				label: "0.2 - 0.4",
				color: '#ffde33'
			}, {
				gt: 0.4,
				lte: 0.6,
				label: "0.4 - 0.6",
				color: '#ff9933'
			}, {
				gt: 0.6,
				lte: 0.8,
				label: "0.6 - 0.8",
				color: '#cc0033'
			}, {
				gt: 0.8,
				lte: 1.0,
				label: "0.8 - 1.0",
				color: '#660099'
			}, {
				gt: 1.0,
				label: "> 1.0",
				color: '#7e0023'
			}],
			outOfRange: {
				color: '#999'
			}
		},
		series: {
			name: 'Beijing AQI',
			type: 'line',
			data: (function () {
				var t = [];
				for (var i = 0; i < len; i++) {
					var tmp = {
						value: poi_probability[i],
						name: i+1,
						poi: poi_types[i]
					};
					t.push(tmp);
				}
				return t;
			})(),
			//            data: data.map(function (item) {
			//                return item[1];
			//            }),
			markLine: {
				silent: true,
				data: [{
					yAxis: 0.2
				}, {
					yAxis: 0.4
				}, {
					yAxis: 0.6
				}, {
					yAxis: 0.8
				}, {
					yAxis: 1.0
				}]
			}
		}
	}
	myChart.setOption(option);
	myChart.on('click', function (param) {
		console.log(param);
		//		alert(param.name+" "+param.value);
		//		makeChart_pie02(param.name, param.value);
	});
	window.addEventListener('resize', function () {
		myChart.resize();
	});
}
