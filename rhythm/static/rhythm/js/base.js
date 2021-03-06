/**
 * Created by 30947 on 2018/7/20.
 */
//var myChart = echarts.init(document.getElementById("chart1"));
var submitted = false; //submitted变量用于保证加载过程中不能重复提交
var method_choice; //提交的方法
$(function () {
	nav();
})
//导航条点击添加样式
function nav() {
	initdata();
	//	dom = document.getElementById("div_img_show");
	//	myChart = echarts.init(dom);
	$(".nav>ul>li").hover(function () {
		$(this).find(".li_ul").stop(true, true).slideDown("slow");
		stop();
	}, function () {
		$(this).find(".li_ul").slideUp("slow");
	})
}
//将数据初始化成默认值
function initdata() {
	$('#information_entropy').text('. . .');
	$('#varience').text('. . .');
	$('#standard_deviation').text('. . .');
	$('#mean').text('. . .');
	$('#max').text('. . .');
	$('#min').text('. . .');
	$('#skew').text('. . .');
	$('#kurtosis').text('. . .');
	$('#len').text('. . .');
}

function hiddenall() {
	$("#method1").addClass("hide");
	$("#method2").addClass("hide");
	$("#method3").addClass("hide");
	$("#method4").addClass("hide");
	$("#method5").addClass("hide");
	$("#method6_1").addClass("hide");
	$("#method6_2").addClass("hide");
	$("#method7_1").addClass("hide");
	$("#method7_2").addClass("hide");
	//	$("#method8_1").addClass("hide");
	//	$("#method8_2").addClass("hide");
	//	$("#method9").addClass("hide");
}
// function change_checked_state(id) {
// 	var $radios =  $('input:radio[name=method]');
// 	$radios.filter('[value=method1]').prop('checked', false);
// 	$id.prop('checked', true);
// }
function onchangeradio(id, method) {
	hiddenall();
	// change_checked_state(id);
	if (method == 1) {
		$("#method1").removeClass("hide");
	} else if (method == 2) {
		$("#method2").removeClass("hide");
	} else if (method == 3) {
		$("#method3").removeClass("hide");
	} else if (method == 4) {
		$("#method4").removeClass("hide");
	} else if (method == 5) {
		$("#method5").removeClass("hide");
	} else if (method == 6) {
		$("#method6_1").removeClass("hide");
		$("#method6_2").removeClass("hide");
	} else if (method == 7) {
		$("#method7_1").removeClass("hide");
		$("#method7_2").removeClass("hide");
	}
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

function sumbit_data() {
	var csrftoken = getCookie('csrftoken');
	//包装数据
	var formData = {
		'method': $('input[name=method]:checked').val(),
		'method1': $('input[name=method1]').val(),
		'method2': $('input[name=method2]').val(),
		'method3': $('input[name=method3]').val(),
		'method4': $('input[name=method4]').val(),
		'method5': $('input[name=method5]').val(),
		'method6_1': $('input[name=method6_1]').val(),
		'method6_2': $('input[name=method6_2]').val(),
		'method7_1': $('input[name=method7_1]').val(),
		'method7_2': $('input[name=method7_2]').val(),
		'method8_1': $('input[name=method8_1]').val(),
		'method8_2': $("#method8_2  option:selected").val(),
		'method9': $('input[name=method9]').val(),
		//		'method10': $("#method10  option:selected").val(),
		'dataset': $('input[name=dataset]:checked').val()
	};
	//如果正在加载则不能重复提交
	if (submitted == true) {
		alert("正在加载请耐心等待！");
		return;
	}
	//判断是否选择了方法和数据集
	var flags = true;
	if (formData["method"] == undefined && formData["dataset"] == undefined) {
		alert("请选择方法和数据集！");
		flags = false;
	} else if (formData["method"] == undefined) {
		alert("请选择想要运行的方法!");
		flags = false;
	} else if (formData["dataset"] == undefined) {
		alert("请选择数据集！");
		flags = false;
	}
	if (flags == false) {
		return;
	}

	console.log(formData);
	//发送后submited=true，并更换加载图片，表示正在加载。
	submitted = true;
	method_choice = formData["method"];
	$('#final_image').attr('src', '/static/rhythm/img/loading.gif');

	//发送请求
	$.ajaxSetup({
		beforeSend: function (xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
  
	//访问服务器。
	$.ajax({
		//几个参数需要注意一下
		type: "POST", //方法类型
		dataType: "json", //预期服务器返回的数据类型
		url: "select/", //url
		//		url:"/static/rhythm/demo_test.txt",
		//		url: "/static/rhythm/dataset.txt",
		data: formData,
		success: function (result) {
			//有返回值
			submitted = false;
			handle(result);
		},
		error: function () {
			alert("异常！");
			submitted = false;
			$('#final_image').attr('src', '/static/rhythm/img/instruction.png');
		}
	});

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

function handle(result) {

	console.log(result); //打印服务端返回的数据(调试用)
	//method8加载echarts，否则销毁echarts加载图片

	method_choice = "";
	//销毁echarts，重新加入图片
//	var compareChart = echarts.getInstanceByDom(document.getElementById("div_img_show"));
//	if (compareChart == undefined) {
//		console.log("nothing");
//	} else {
//		echarts.dispose(compareChart);
//		$("#div_img_show").prepend("<img id='final_image' class='images' >");
//	}
	$('#final_image').attr('src', '/static/rhythm/img/instruction.png');
	var image_full_name = result["image_full_name"];
	img_address = "/static/rhythm/img/generated/" + image_full_name;
	$('#final_image').attr('src', img_address);

	//显示参数
	var extra_information = jQuery.parseJSON(result["extra_information"]);
	console.log(extra_information);
	$('#information_entropy').text(extra_information["information_entropy"]);
	$('#varience').text(extra_information["varience"]);
	$('#standard_deviation').text(extra_information["standard_deviation"]);
	$('#mean').text(extra_information["mean"]);
	$('#max').text(extra_information["max"]);
	$('#min').text(extra_information["min"]);
	$('#skew').text(extra_information["skew"]);
	$('#kurtosis').text(extra_information["kurtosis"]);
	$('#len').text(extra_information["len"]);
//}
//	var image_full_name = result["image_full_name"];
//	var extra_information = jQuery.parseJSON(result["extra_information"]);
//	var extra_information = result["extra_information"];
//	//	img_address = "/static/rhythm/img/generated/" + image_full_name
//	//	$('#final_image').attr('src', img_address);
//	$('#information_entropy').text(extra_information["information_entropy"]);
//	$('#varience').text(extra_information["varience"]);
//	$('#standard_deviation').text(extra_information["standard_deviation"]);
//	$('#mean').text(extra_information["mean"]);
//	$('#max').text(extra_information["max"]);
//	$('#min').text(extra_information["min"]);
//	$('#skew').text(extra_information["skew"]);
//	$('#kurtosis').text(extra_information["kurtosis"]);
//	$('#len').text(extra_information["len"]);


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

function sumbit_data_02(method) {
	var csrftoken = getCookie('csrftoken');
	//包装数据

	var formData = {
		'method': method,
		'method1': $('input[name=method1]').val(),
		'method2': $('input[name=method2]').val(),
		'method3': $('input[name=method3]').val(),
		'method4': $('input[name=method4]').val(),
		'method5': $('input[name=method5]').val(),
		'method6_1': $('input[name=method6_1]').val(),
		'method6_2': $('input[name=method6_2]').val(),
		'method7_1': $('input[name=method7_1]').val(),
		'method7_2': $('input[name=method7_2]').val(),
		'method8_1': $('input[name=method8_1]').val(),
		'method8_2': $("#method8_2  option:selected").val(),
		'method9_1': $('input[name=method9_1]').val(),
		'method9_2': $("#method9_2  option:selected").val(),
		'method10': $("#method10  option:selected").val(),
		'dataset': $('input[name=dataset]:checked').val()
	};
	
	//暂时给method9随机赋值
	if(formData['method']=='method9'){
		formData['method']='method2';
		formData['method2']=formData['method9_1'];
		formData['dataset']='dataset1.csv'
	}
	console.log(formData);
	//发送后submited=true，并更换加载图片，表示正在加载。

	method_choice = formData["method"];
//	$('#image_chart3').attr('src', '/static/rhythm/img/loading.gif');

	//发送请求
	$.ajaxSetup({
		beforeSend: function (xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
	//如果方法为method8，则直接从json中获取，而不是访问服务器。
	if (method_choice == "method8") {
		handle_method8(formData);
	} else {
		$.ajax({
			//几个参数需要注意一下
			type: "POST", //方法类型
			dataType: "json", //预期服务器返回的数据类型
			url: "select/", //url
			//		url:"/static/rhythm/demo_test.txt",
			//		url: "/static/rhythm/dataset.txt",
			data: formData,
			success: function (result) {
				//有返回值
				submitted = false;
				handle_method9(result);
			},
			error: function () {
				alert("异常！");
				//				submitted = false;
				$('#image_chart3').attr('src', '/static/rhythm/img/instruction.png');
			}
		});
	}

}

function handle_method9(result){
	console.log(result); //打印服务端返回的数据(调试用)
	//method8加载echarts，否则销毁echarts加载图片

	method_choice = "";

	$('#image_chart3').attr('src', '/static/rhythm/img/instruction.png');
	var image_full_name = result["image_full_name"];
	img_address = "/static/rhythm/img/generated/" + image_full_name;
	$('#image_chart3').attr('src', img_address);

	//显示参数
	var extra_information = jQuery.parseJSON(result["extra_information"]);
	console.log(extra_information);
	$('#information_entropy').text(extra_information["information_entropy"]);
	$('#varience').text(extra_information["varience"]);
	$('#standard_deviation').text(extra_information["standard_deviation"]);
	$('#mean').text(extra_information["mean"]);
	$('#max').text(extra_information["max"]);
	$('#min').text(extra_information["min"]);
	$('#skew').text(extra_information["skew"]);
	$('#kurtosis').text(extra_information["kurtosis"]);
	$('#len').text(extra_information["len"]);
}