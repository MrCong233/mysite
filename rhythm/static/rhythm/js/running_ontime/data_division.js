/**
 * Created by 30947 on 2018/7/20.
 */
//var myChart = echarts.init(document.getElementById("chart1"));
var submitted = false; //submitted变量用于保证加载过程中不能重复提交
var method_choice; //提交的方法
var file_submitted = false;//判断是否已经提交了文件
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
	};
	//如果正在加载则不能重复提交
	if (submitted == true) {
		alert("正在加载请耐心等待！");
		return;
	}
	//判断是否选择了方法和数据集
	var flags = true;
//	alert(file_submitted);
	if (formData["method"] == undefined && file_submitted == false) {
		alert("请选择方法并上传数据集！");
		flags = false;
	} else if (formData["method"] == undefined) {
		alert("请选择想要运行的方法!");
		flags = false;
	} else if (file_submitted == false) {
		alert("请上传数据集！");
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
		data: formData,
		success: function (result) {
			//有返回值
			submitted = false;
			console.log(result)
			handle(result,formData);
		},
		error: function () {
			alert("异常！");
			submitted = false;
			$('#final_image').attr('src', '/static/rhythm/img/instruction.png');
		}
	});

}


function handle(result,formData) {
	var turl = getImageUrl(formData);
//	console.log(result); //打印服务端返回的数据(调试用)
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
	img_address = "/static/rhythm/img/generated/" + turl;
	$('#final_image').attr('src', img_address);

	//显示参数
	var extra_information = result["extra_information"]
//	var extra_information = jQuery.parseJSON(result["extra_information"]);
//	console.log(extra_information);
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
function getImageUrl(formData){
	var methodname ;
	var url;
	var turl
	if(formData["method"] == "method1"){
		methodname = "2d_equal_grid";
		turl = methodname +"-"+ formData["method1"];
	}else if(formData["method"] == "method2"){
		methodname = "2d_kdtree";
		turl = methodname +'-'+ formData["method2"];
	}else if(formData["method"] == "method3"){
		methodname = "3d_equal_grid";
		turl = methodname + "-" + formData["method3"];
	}else if(formData["method"] == "method4"){
		methodname = "3d_kdtree";
		turl = methodname + "-" + formData["method4"];
	}else if(formData["method"] == "method5"){
		methodname = "3d_slice_merge";
		turl = methodname + "-" +formData["method5"];
	}else if(formData["method"] == "method6"){
		methodname = "time_space";
		turl = methodname + "-" + formData["method6_1"] + "-" + formData["method6_2"]; 
	}else if(formData["method"] == "method7"){
		methodname = "space_time";
		turl = methodname + "-" + formData["method7_1"] + "-" + formData["method7_2"];
	}
	url = "upload_processed-" + turl + ".png";
	return url;
}

var wb;//读取完成的数据
var rABS = false; //是否将文件读取为二进制字符串

function importf(obj) {//导入
	var flag = check_file();
	if(flag == false){
		return;
	}
	
	
	if(!obj.files) {
		return;
	}
	
	var f = obj.files[0];
	var reader = new FileReader();
	reader.onload = function(e) {
		// console.log(e.target.result);
		if(rABS) {
			wb = XLSX.read(btoa(fixdata(e.target.result)), {//手动转化
				type: 'base64'
			});
		} else {
			wb = XLSX.read(e.target.result, {
				type: 'binary'
			});
		}
		
		//wb.SheetNames[0]是获取Sheets中第一个Sheet的名字
		//wb.Sheets[Sheet名]获取第一个Sheet的数据
		var data = XLSX.utils.sheet_to_json(wb.Sheets[wb.SheetNames[0]]);
		console.log(data);
		var keyAry = [];
		// 遍历json对象，获取每一列的键名,即表头
		for(var key in data[1]){
			keyAry.push(key);
		}
//		console.log("keyAry=",keyAry);
		// 清除上次渲染的表格
		$("#demo").empty();
		// 设置表格头
//		var thead = $("<thead><tr></tr></thead>");
//		for (var i=0;i<3;i++){
//			thead.append("<td>"+keyAry[0]+"</td>");
//			thead.append("<td>"+keyAry[1]+"</td>");
//			thead.append("<td>"+keyAry[2]+"</td>");
//		}
//		thead.appendTo($("#demo"))
//		$(`<thead><tr><th colspan=${keyAry.length}>${keyAry[0]}</th></tr></thead>`).appendTo($("#demo"));
		for (var i=0;i<data.length;i++ ){
			if(i+2>=data.length ){
				break;
			}
			var tr = $("<tr></tr>");
			for(var j = i;j<i+3;j++ ){
				tr.append("<td>"+ data[i+j][keyAry[0]] + "</td>");
				tr.append("<td>"+ data[i+j][keyAry[1]] + "</td>");
				tr.append("<td>"+ data[i+j][keyAry[2]] + "</td>");
			}
			tr.appendTo($("#demo"));
		}
		
		
//		for(var d of data){
//			// 通过循环,每有一条数据添加一行表格
//			var tr = $("<tr></tr>");
//			for(var n = 0;n< keyAry.length;n++){
//				// 根据keyAry数组的长度,创建每一行表格中的td
//				$("<td></td>").html("<input>").addClass(keyAry[n]).appendTo(tr);
//			}
//			// 遍历对象,根据键名找到是哪一列的数据,给对应的td添加内容
//			for(k in d){
//				// (tr[0].children[keyAry.indexOf(k)])
//				$(tr[0].children[keyAry.indexOf(k)]).html(d[k]);
//			}
//			tr.appendTo($("#demo"));
//		}
	}	
	
	if(rABS) {
		reader.readAsArrayBuffer(f);
	} else {
		reader.readAsBinaryString(f);
	}
	submit_file(obj)
}
function check_file() {
	var obj = $("input[name='csv_file']").val();
	// 判断文件是否为空 
	if (obj == "") {
		alert("请选择上传的目标文件");
		return false;
	}
	
	//判断文件类型,要求是csv文件
	var fileName1 = obj.substring(obj.lastIndexOf(".") + 1).toLowerCase();
	if (fileName1 != "csv") {
		alert("请选择csv文件!");
		return false;
	}
	//判断文件大小
	var size1 = $("input[name='csv_file']")[0].files[0].size;
	if(size1 > 41943040){
		alert("上传文件不能大于40M!");
		return false;
	}
}
function submit_file(){	
	var csrftoken = getCookie('csrftoken');
	$.ajaxSetup({
		beforeSend: function (xhr, settings) {
			if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
				xhr.setRequestHeader("X-CSRFToken", csrftoken);
			}
		}
	});
	//访问服务器。

	var type = "csv_file";
	var formData = new FormData(); //这里需要实例化一个FormData来进行文件上传
	formData.append(type, $("#csv_input")[0].files[0]);
	$.ajax({
		type: "post",
		url: "upload_csv",
		data: formData,
		processData: false,
		contentType: false,
		success: function (result) {
			var res = result["error"];
			if( res == null){
				alert("数据上传成功")
				file_submitted = true;
			}else{
				alert("上传失败",res);
			}
			
			console.log(result)
		},
		error: function (result) {
			console.log('here',result);
			alert("异常！");
		}
	});

}
function fixdata(data) { //文件流转BinaryStrings
	var o = "",
		l = 0,
		w = 10240;
	jsArry=[];
	for(; l < data.byteLength / w; ++l) 
		jsArry.push(String.fromCharCode.apply(null, new Uint8Array(data.slice(l * w, l * w + w))));
	return jsArry;
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