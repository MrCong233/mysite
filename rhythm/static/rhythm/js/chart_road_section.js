/**
 * Created by 30947 on 2018/7/18.
 */
$(function () {
	//	chart1();
	
	var new_element = document.createElement("script");
	new_element.setAttribute("type", "text/javascript");
	new_element.setAttribute("src", "/static/rhythm/js/coordinate_transformation.js"); // 在这里引入了a.js
	document.body.appendChild(new_element);
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

function submit_data_lines() {
	var csrftoken = getCookie('csrftoken');
	//包装数据
	var formData = {
		'method': 'method11',
		'method11': $("#method11  option:selected").val(),
	};
	console.log(formData);

	method_choice = formData["method"];
	//	$('#final_image').attr('src', '/static/rhythm/img/loading.gif');

	if (method_choice == 'method11') {
		method_choice = "";
		 var time = formData['method11'];

		//暂时数据写死
//		time = '6_7';

		var url = "/static/rhythm/json/taxi_track_one_hour_poi_road/20140803_taxi_track_" + time + "_poi_road" + ".json";
		$.getJSON(url, function (result) {
			console.log(result);
			makeChart_roadsection(result);
		});
	}
}

//处理路段坐标数据
function handle_road_list(data) {
	//rlength:路段数量
	var rlength = data.length;
	var t = [];
	for (var i = 0; i < rlength; i++) {
		//coords表示路段的wgs84坐标序列
		var coords = data[i]['road_coords'];
		var clength = coords.length;
		var tmp = [];
		for (var j = 0; j < clength; j++) {
			var gcj = wgs84togcj02(coords[j][0], coords[j][1]);
			var bd = gcj02tobd09(gcj[0], gcj[1]);
			tmp.push(bd);
		}
		t.push(tmp);
	}
	return t;
}

function makeChart_roadsection(data) {
	console.log(data,'data');

	var road_list = handle_road_list(data['road_line_poi_list']);
	//length:路段数
	var length = road_list.length;
	console.log(road_list,'road_list');
	
	var myChart = echarts.init(document.getElementById("chart_lines_1"));
	var app = {};
	var option = null;
	app.title = '北京公交路线 - 百度地图';


	
	var option = {
		tooltip: {
			show: true,
			trigger: 'item',
//			formatter: '{b}'
			formatter: function (params, ticket, callback) {
				console.log(params);
//				var poi = params[0].data.poi;
//				var value = params[0].value;
//				var name = params[0].name;
//				return value + "<br/> POI:" + poi;
				return params.data.name;
			}
		},
		bmap: {
			center: [104.07, 30.68],
			zoom: 13,
			roam: true,
			mapStyle: {
				styleJson: [{
					'featureType': 'water',
					'elementType': 'all',
					'stylers': {
						'color': '#d1d1d1'
					}
				}, {
					'featureType': 'land',
					'elementType': 'all',
					'stylers': {
						'color': '#f3f3f3'
					}
				}, {
					'featureType': 'railway',
					'elementType': 'all',
					'stylers': {
						'visibility': 'off'
					}
				}, {
					'featureType': 'highway',
					'elementType': 'all',
					'stylers': {
						'color': '#fdfdfd'
					}
				}, {
					'featureType': 'highway',
					'elementType': 'labels',
					'stylers': {
						'visibility': 'off'
					}
				}, {
					'featureType': 'arterial',
					'elementType': 'geometry',
					'stylers': {
						'color': '#fefefe'
					}
				}, {
					'featureType': 'arterial',
					'elementType': 'geometry.fill',
					'stylers': {
						'color': '#fefefe'
					}
				}, {
					'featureType': 'poi',
					'elementType': 'all',
					'stylers': {
						'visibility': 'off'
					}
				}, {
					'featureType': 'green',
					'elementType': 'all',
					'stylers': {
						'visibility': 'off'
					}
				}, {
					'featureType': 'subway',
					'elementType': 'all',
					'stylers': {
						'visibility': 'off'
					}
				}, {
					'featureType': 'manmade',
					'elementType': 'all',
					'stylers': {
						'color': '#d1d1d1'
					}
				}, {
					'featureType': 'local',
					'elementType': 'all',
					'stylers': {
						'color': '#d1d1d1'
					}
				}, {
					'featureType': 'arterial',
					'elementType': 'labels',
					'stylers': {
						'visibility': 'off'
					}
				}, {
					'featureType': 'boundary',
					'elementType': 'all',
					'stylers': {
						'color': '#fefefe'
					}
				}, {
					'featureType': 'building',
					'elementType': 'all',
					'stylers': {
						'color': '#d1d1d1'
					}
				}, {
					'featureType': 'label',
					'elementType': 'labels.text.fill',
					'stylers': {
						'color': '#999999'
					}
				}]
			}
		},
		series: [{
			type: 'lines',
			coordinateSystem: 'bmap',
			polyline: true, //表示曲线
			//			data:busLines,
			data: (function () {
				var t = [];
				for (var i = 0; i < length; i++) {
					var tmp = {
						name: '名称:'+data['road_line_poi_list'][i]['road_name']+'\n长度:'+data['road_line_poi_list'][i]['road_length'].toFixed(2)+' m',
						coords: road_list[i],
						number: i,
						lineStyle: {
							color: (function () {
								var colorList = ['#EE1289', '#DC143C', '	#E066FF', '#FF1493', '#FF6347', '#FF0000', '#B23AEE', '#BA55D3', '#C71585', '#9B30FF', '#969696', '#8E388E', '#8B008B', '#7D9EC0', '#7A7A7A', '#7A67EE', '#696969', '#515151', '#404040', '#12121', '#191970', '#00CD66', '#0000EE', '#00CDCD', '#7D26CD', '#71C671', '#76EE00', '#87CEFA', '#698B22', '#7171C6', '#ADADAD', '#DEB887'];
								return colorList[Math.floor(Math.random() * colorList.length)];
							})(),
							opacity: 0.5,
							width: 4,
							curveness: 1
						}
					}
					t.push(tmp);
				}

				return t;
			})(),
			silent: false, //
//			effect: {
//				show: true,
//				symbol: 'circle',
//				symbolSize: 4,
//
//			},
			symbol: 'circle',
			progressiveThreshold: 500,
			progressive: 200,
			animation: false
		}]
	};
	console.log(option.series[0].data);
    myChart.setOption(option)


	myChart.off('click');
	myChart.on('click', function (param) {
		console.log(param);
		submit_data_roadsection_2(param.data.number,data);

	});


	//	myChart.on('click', function (param) {
	//		console.log(param);
	//		//		alert(param.name+" "+param.value);
	//		//		makeChart_pie02(param.name, param.value);
	//	});
	window.addEventListener('resize', function () {
		myChart.resize();
	});
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
function submit_data_roadsection_2(index,data) {
	var poi_types = data["poi_types"];
	
	var poi_probability = handle_data(data["road_line_poi_list"][index]["poi_vector"]);
	console.log(poi_probability);
	
	//生成一段序列
	var ls = [];
	var lg = data['poi_types'].length;
	for(var i=0;i<lg;i++){
		ls.push(i+1);
	}
	
	var myChart = echarts.init($("#chart_lines_2")[0]);
	var len = poi_types.length;
	var option = {
		backgroundColor: "#fff",
		title: {
			text: '成都市分路段POI概率分布',
		},
		tooltip: {
			trigger: 'axis',
			formatter: function (params, ticket, callback) {
				console.log(params[0]);
				var poi = params[0].data.poi;
				var value = params[0].value;
				var name = params[0].name;
				return  '序号:' + name+ "<br/>名称:" + poi+ '<br/>出现频率:' + value;
			}
		},
		xAxis:{
			data: ls,
			name: '编号'
		},
		yAxis: {
			splitLine: {
				show: false,
				
			},
			name: '频率'
		},
		dataZoom: [{
			startValue: 1
		}, {
			type: 'inside'
		}],
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
			})()
		}
	};
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
