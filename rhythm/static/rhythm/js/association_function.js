/**
 * sumbit_data_chart8_9()
 * method8: 出租车迁移关系图
 * method9：分时段目的地划分图
 */
var method_choice = "";
//绘制kdtree划分图时的坐标轴范围，由数据极值而定
var Left;
var Right;
var Top;
var Bottom;
function submit_data_chart8_9(method) {
	var csrftoken = getCookie('csrftoken');
	//包装数据

	var formData = {
		'method': method,
		'method1': "",
		'method2': "",
		'method3': "",
		'method4': "",
		'method5': "",
		'method6_1': "",
		'method6_2': "",
		'method7_1': "",
		'method7_2': "",
		'method8_1': $('input[name=method8_1]').val(),
		'method8_2': $("#method8_2  option:selected").val(),
		'method9_1': $('input[name=method9_1]').val(),
		'method9_2': $("#method9_2  option:selected").val(),
		'method10': $("#method10  option:selected").val(),
		'dataset': $('input[name=dataset]:checked').val()
	};

	//暂时给method9随机赋值
	if (formData['method'] == 'method9') {
		formData['method'] = 'method2';
		formData['method2'] = formData['method9_1'];
		formData['dataset'] = 'dataset1.csv'
	}
	//发送后submited=true，并更换加载图片，表示正在加载。

	method_choice = formData["method"];
	//	$('#image_chart3').attr('src', '/static/rhythm/img/loading.gif');

	console.log(formData);

	//发送请求
	//如果方法为method8，则直接从json中获取，而不是访问服务器。
	if (method_choice == "method8") {
		handle_method8(formData);
	} else {
		handle_method9(formData);
	}

}

function handle_method9(parameter) {
	method_choice = "";
	depth = parameter["method9_1"];
	time = parameter["method9_2"];
	url = "/static/rhythm/json/taxi_gps_one_hour_result_kdtree/2014-08-05_h" + time + "_dd" + depth + ".json";
	$.getJSON(url, function (result) {
		console.log(result);
		runMethod9(result, depth)
		//		submitted = false;
	});
}

function runMethod9(result, depth) {
	var kdtree = result.kd_tree_not_leaf_node;
	var lines = handle_data_method9(kdtree, depth);
	console.log(lines);
	var dom = document.getElementById("chart_2");
	var myChart = echarts.init(dom);
	var option = {
		title: {
			text: '分时段目的地划分图',
			left: 'center'
		},
		backgroundColor: '#ffffff',
		grid: {
			show: true
			//			borderColor: '#EE2C2C'
		},
		xAxis: {
			name: 'longitude',
			show: true,
			nameLocation: 'center',
			max: 104.6097,
			min: 103.2731,
			nameGap: 40,
			//			max: Right+0.01,
			//			min: Left-0.01,
			splitLine: {
				show: false
			}
		},
		yAxis: {
			name: 'latitude',
			show: true,
			nameLocation: 'center',
			min: 30.2906,
			max: 31.0325,
			nameGap: 40,
			//			min: Bottom-0.01,
			//			max: Top+0.01,
			splitLine: {
				show: false
			}

		},
		series: [{
			type: 'line',
			lineStyle: {
				normal: {
					color: '#fffff',
					opacity: 0,
					curveness: 0
				}
			},
			data: [{
				name: 'a',
				value: [30.290685, 103.273147]
			}, {
				name: 'aa',
				value: [30.290685, 104.609696]
			}, {
				name: 'aaa',
				value: [31.032475, 104.609696]
			}, {
				name: 'aaaa',
				value: [31.032475, 103.273147]
			}]
		}, {
			type: 'lines',
			itemStyle: {
				normal: {
					color: '#7a00e9',
					opacity: 1,
					borderWidth: 1,
					shadowBlur: 8,
					shadowColor: '#fff'
				}
			},
			coordinateSystem: 'cartesian2d',
			lineStyle: {
				normal: {
					color: '#fffff',
					opacity: 1,
					curveness: 0
				}
			},
			data: lines
		}]
	};
	myChart.setOption(option);
}

function handle_data_method9(kdtree, depth) {
	var lines = [];
	var length = kdtree.length;
	console.log(kdtree, 'here');
	//	console.log(length);
	for (var i = 0; i < length; i++) {

		var node = kdtree[i];
		var left = node["hrect"][0][1];
		var right = node["hrect"][1][1];
		var top = node["hrect"][1][0];
		var bottom = node["hrect"][0][0];
		//		if(i==0){
		//			Left = left;
		//			Right = right;
		//			Top = top;
		//			Bottom = bottom;
		//			
		//		}else{
		//			Left = (Left<left?Left:left);
		//			Right = (Right>right?Right:right);
		//			Top =(Top>top?Top:top);
		//			Bottom = (Bottom<bottom?Bottom:bottom);
		//		}
		//		console.log(left,bottom , right ,top);
		var tmp1 = {
			coords: [
				[left, bottom],
				[left, top]
			]
		};
		var tmp2 = {
			coords: [
				[left, top],
				[right, top]
			]
		};
		var tmp3 = {
			coords: [
				[right, top],
				[right, bottom]
			]
		};
		var tmp4 = {
			coords: [
				[right, bottom],
				[left, bottom]
			]
		};
		lines.push(tmp1);
		lines.push(tmp2);
		lines.push(tmp3);
		lines.push(tmp4);
	}
	return lines;


	//图的经纬度范围
	//	var left = 30.290685;
	//	var right = 31.032475;
	//	var top = 104.609696;
	//	var bottom = 103.273147;
	//	dfs_method9(0, 0, left, right, top, bottom);

	console.log(lines)
	return lines;

	//深搜，遍历整个树，每个中间节点生成一条线，保存在lines中
	function dfs_method9(depth, index, left, right, top, bottom) {
		//只有中间节点才需要画线
		if (kdtree[index].left_nodeptr == -1 || kdtree[index].right_nodeptr == -1) {
			return;
		}
		//depth%2==0时绘制横线，下面是左子树，上面是右子树
		//depth%2==0时绘制竖线，左面是左子树，右面是右子树
		if (depth % 2 == 0) {
			var tmp = kdtree[index];
			var x = kdtree[index]['hrect'][0];
			var y = kdtree[index]['hrect'][1];
			var line = {
				coords: [
					[left, y],
					[right, y]
				]
			};
			lines.push(line);
			//下面是左子树
			dfs_method9(depth + 1, kdtree[index].left_nodeptr, left, right, y, bottom);
			//上面是右子树
			dfs_method9(depth + 1, kdtree[index].right_nodeptr, left, right, top, y);
		} else {
			var tmp = kdtree[index];
			var x = kdtree[index]['hrect'][0];
			var y = kdtree[index]['hrect'][1];
			var line = {
				coords: [
					[x, top],
					[y, bottom]
				]
			};
			lines.push(line);
			//左边是左子树
			dfs_method9(depth + 1, kdtree[index].left_nodeptr, left, x, top, bottom);
			//右边是右子树
			dfs_method9(depth + 1, kdtree[index].right_nodeptr, left, y, top, top);
		}
		return;
	}
}


function handle_method8(parameter) {
	method_choice = "";
	depth = parameter["method8_1"];
	time = parameter["method8_2"];
	url = "/static/rhythm/json/taxi_gps_one_hour_result_kdtree/2014-08-05_h" + time + "_dd" + depth + ".json";
	$.getJSON(url, function (result) {
		console.log(result);
		runMethod8(result, depth)
		//		submitted = false;
	});
}

function runMethod8(result, depth) {
	var len = Math.pow(2, depth); //点的数量
	var x = new Array(); //点的经度
	for (i = 0; i < len; i++) {
		x[i] = result["idx_gps"][i][1];
	}
	var y = new Array(); //点的纬度
	for (i = 0; i < len; i++) {
		y[i] = result["idx_gps"][i][0];
	}
	var maps = result["sum_matrix"];
	var value = new Array();
	for (i = 0; i < len; i++) {
		value[i] = maps[i][i];
	}

	var xMax = 0;
	var xMin = 200;
	var yMax = 0;
	var yMin = 200;
	var valueMax = 0;
	var valueMin = 10000000000;
	var mapsMax = 0;
	var mapsMin = 10000000000;
	for (var i = 0; i < len; i++) {
		for (var j = 0; j < len; j++) {
			if (maps[i][j] > mapsMax) {
				mapsMax = maps[i][j];
			}
			if (maps[i][j] < mapsMin) {
				mapsMin = maps[i][j];
			}
		}
	}
	for (var i = 0; i < len; i++) {
		if (x[i] > xMax) {
			xMax = x[i];
		}
	}
	for (var i = 0; i < len; i++) {
		if (x[i] < xMin) {
			xMin = x[i];
		}
	}
	for (var i = 0; i < len; i++) {
		if (y[i] > yMax) {
			yMax = y[i];
		}
	}
	for (var i = 0; i < len; i++) {
		if (y[i] < yMin) {
			yMin = y[i];
		}
	}
	for (var i = 0; i < len; i++) {
		if (value[i] > valueMax) {
			valueMax = value[i];
		}
	}
	for (var i = 0; i < len; i++) {
		if (value[i] < valueMin) {
			valueMin = value[i];
		}
	}


	//	$("#final_image").hide();
	//	$("#chart_1").addClass("div_method8")
	var dom = document.getElementById("chart_1");

	var myChart = echarts.init(dom);
	myChart.clear();

	option = {
		tooltip: {
			trigger: 'item',
			show: true,

		},
		bmap: {
			center: [104.1, 30.68],
			zoom: 13,
			roam: true,
			height: '90%'
		},
		series: [{
			type: 'graph',
			layout: 'none', //使用x，y作为位置
			legendHoverLink: true,
			coordinateSystem: 'bmap',
			roam: true, //可缩放和平移漫游
			focusNodeAdjacency: true, //选取某节点时高亮相邻的边和节点
			symbol: "circle", //节点形状
			symbolSize: (value, params) => { //设置节点大小
				//根据数据params中的data来判定数据大小
				var tmp = params.data.value[2];
				if (depth >= 5) {
					return (tmp - valueMin) / (valueMax - valueMin) * 20 + 20;
				} else {
					return (tmp - valueMin) / (valueMax - valueMin) * 30 + 30;
				}
			},
			data: (function () {
				var t = [];
				for (var i = 1; i <= len; i++) {
					var tmp = {
						number: 'No' + i,
						fax: value[i - 1],
						name: 'No' + i,
						value: [x[i - 1], y[i - 1], value[i - 1]],
						itemStyle: {
							color: (function () {
								var colorList = ['#EE1289', '#DC143C', '	#E066FF', '#FF1493', '#FF6347', '#FF0000', '#B23AEE', '#BA55D3', '#C71585', '#9B30FF', '#969696', '#8E388E', '#8B008B', '#7D9EC0', '#7A7A7A', '#7A67EE', '#696969', '#515151', '#404040', '#12121', '#191970', '#00CD66', '#0000EE', '#00CDCD', '#7D26CD', '#71C671', '#76EE00', '#87CEFA', '#698B22', '#7171C6', '#ADADAD', '#DEB887'];
								return colorList[Math.floor(Math.random() * colorList.length)];
							})()

						},
						label: { //节点显示的标识
							normal: {
								show: true,
								formatter: (function () {
									return maps[i - 1][i - 1] + "";
								})()
							}
						},
						tooltip: {
							formatter: (function () {
								return 'No' + i + ':' + value[i - 1] + ',(' + x[i - 1] + ',' + y[i - 1] + ')';
							})(),
							textStyle: {
								fontFamily: 'Verdana, sans-serif',
								fontSize: 15,
								fontWeight: 'bold'
							}
						}
					}
					t.push(tmp);
				}
				return t;
			})(),
			// links: [],
			links: (function () {
				var t = [];

				for (var i = 0; i < len; i++) {
					for (var j = 0; j < len; j++) {
						if (maps[i][j] != 0 && i != j && maps[i][j] > mapsMax * 0.2) {
							var tmp = {
								source: i,
								target: j,
								value: maps[i][j],
								symbolSize: [0.1, 10],
								symbol: ['none', 'arrow'],
								lineStyle: {
									normal: {
										width: 4,
										curveness: 0.4,
										color: 'source',
									},
									emphasis: {
										width: (function () {
											return (maps[i][j] - mapsMin) / (mapsMax - mapsMin) * 2 + 2;
										})(),
									}

								},
								label: {
									normal: {
										show: true,
										position: 'middle',
										fontSize: 15,
										formatter: ' {@value}'
									},
									emphasis: {
										show: true
									}
								}
							}
							t.push(tmp);
						}
					}
				}
				return t;
			})()
		}]
	};

	myChart.setOption(option, true);

}

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
