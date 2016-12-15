function deIdentificationProcessManagement(){

	var endpoint = UTILITIES.endpoint;
	var dataPath = UTILITIES.data_path;
	var loadingGifPath = "";
	var currentPath = window.location.pathname;
	var doDIProc;
	var procId;
	var taskID;
	var optedCluster;
	//used for difference between dashboard path and DI path
	if(currentPath === "/privacy/"){
		//in dashboard page
		loadingGifPath = 'web/images/ajax-loading.gif';
	}else{
		loadingGifPath = 'images/ajax-loading.gif';
	}
	var loadingOption ={
		imgPath    : loadingGifPath,
		tip: '請稍後...',
		ajax: false
	}
	var loading = $.loading(loadingOption);


	this.listSensitiveTable = function(data){
		columns = data.col_names;	
		//build table head
		$("#sensitiveHead").html('');
		// for (var k = 0; k < columns.length; k++) {
		// 	var tableHead = "";
		// 	tableHead += "<th class=\"text-center\">" + columns[k] + "</th>";
		// 	$("#sensitiveHead").append(tableHead);
		// };
		showOriginData();
		
		// var rows = [];
		// rows = data.rows;
		// //build table body
		// $("#sensitiveBody").html('');
		// var rowInfo = "";
		// for (var i = 0; i < rows.length; i++) {
		// 	var rowInfo = "";
		// 	rowInfo += "<tr>";
		// 	for (var j = 0; j < rows[i].length; j++) {
		// 		rowInfo += "<td>" + rows[i][j] + "</td>";
		// 	};
		// 	rowInfo += "</tr>";
		// 	$("#sensitiveBody").append(rowInfo);
		// };

		// var rowInfo = "";
		// rowInfo +="<tr>";
		// rowInfo +="<td>身高</td><td>數值型</td><td>150</td>";
		// rowInfo +="</tr>";
		// rowInfo +="<tr>";
		// rowInfo +="<td>體重</td><td>數值型</td><td>150</td>";
		// rowInfo +="</tr>";
		// rowInfo +="<tr>";
		// rowInfo +="<td>學歷</td><td>類別型</td><td>6</td>";
		// rowInfo +="</tr>";
		//$("#sensitiveBody").append(rowInfo);
	}

	this.listColumnsetting = function(data){
		var columns = data.col_names;
		var showDefaultColumnSetting = data.default;
		var selected_attrs = {};
		var selected_names = [];
		var selected_types = [];

		// var tableHead="<th>欄位名稱</th><th>欄位型態</th><th>Domain 數量</th>";
		// $("#sensitiveHead").append(tableHead);

		//list column setting info
		$("#columnSettingBody").html('');
		console.log(data);
		if(!showDefaultColumnSetting){
			selected_attrs = data.selected_attrs;
			selected_names = selected_attrs.names;
			selected_types = selected_attrs.types;
			for (var i = 0; i < columns.length; i++) {
				var columnName = columns[i];
				var columnInfo = "";
				var index = selected_names.indexOf(columnName);	

				columnInfo += "<tr>";
				if (index >=0) {
				 	//it is a selected attribute
					columnInfo += "<td><label class=\"checkbox-inline\"><input type=\"checkbox\" value=\"" + columnName +"\" checked></label></td>";
					columnInfo += "<td>" + columnName + "</td>";
					columnInfo += "<td><div class=\"dropdown\">";
					columnInfo += "<select class=\"form-control\">";
					if(selected_types[index] == "C"){
						columnInfo += "<option value=\"C\" selected>連續型</option>";
						columnInfo += "<option value=\"D\">類別型</option>";
					}else{
						columnInfo += "<option value=\"C\">連續型</option>";
						columnInfo += "<option value=\"D\" selected>類別型</option>";
					}
					
					columnInfo += "</select></div></td>";
					// columnInfo += "<td>";
					// columnInfo += "<input type=\"text\" value=\"\" name=\"columnSet\" class=\"form-control\" data-role=\"tagsinput\" data-provide=\"typeahead\"/>";										
					// columnInfo += "</td>";
					columnInfo += "</tr>";
				}else{
				 	//it is not a selected attribute
					columnInfo += "<td><label class=\"checkbox-inline\"><input type=\"checkbox\" value=\"" + columnName +"\"></label></td>";
					columnInfo += "<td>" + columnName + "</td>";
					columnInfo += "<td><div class=\"dropdown\">";
					columnInfo += "<select class=\"form-control\">";
					columnInfo += "<option value=\"C\">連續型</option>";
					columnInfo += "<option value=\"D\">類別型</option>";
					columnInfo += "</select></div></td>";
					// columnInfo += "<td>";
					// columnInfo += "<input type=\"text\" value=\"\" name=\"columnSet\" class=\"form-control\" data-role=\"tagsinput\" data-provide=\"typeahead\"/>";								
					// columnInfo += "</td>";
					columnInfo +="</tr>";
				}
				$("#columnSettingBody").append(columnInfo);
			}
		
		}else{
			for (var i = 0; i < columns.length; i++) {
			var columnName = columns[i];
			var columnInfo = "";	

			columnInfo += "<tr>";
			columnInfo += "<td><label class=\"checkbox-inline\"><input type=\"checkbox\" value=\"" + columnName +"\"></label></td>";
			columnInfo += "<td>" + columnName + "</td>";
			columnInfo += "<td><div class=\"dropdown\">";
			columnInfo += "<select class=\"form-control\">";
			columnInfo += "<option value=\"C\">連續型</option>";
			columnInfo += "<option value=\"D\">類別型</option>";
			columnInfo += "</select></div></td>";
			//columnInfo += "<td>";
			// columnInfo += "<section style=\"border-style:inset;\">";
			// columnInfo += "<span class=\"attr_each\">" + columns[1];											
			// columnInfo += "<span class=\"glyphicon glyphicon-remove-sign\" style=\"cursor: pointer;\" title=\"移除屬性\">";													
			// columnInfo += "</span>";
			// columnInfo += "</span>";																																	
			// columnInfo += "</section>"
			// columnInfo += "<input type=\"text\" value=\"\" name=\"columnSet\" class=\"form-control\" data-role=\"tagsinput\" data-provide=\"typeahead\"/>";
			// columnInfo += "</td>";																				
			columnInfo += "</tr>";				   
			$("#columnSettingBody").append(columnInfo);

			}
			//$('.table-fixed-header').fixedHeader();
			//$(".table-fixed-header").fixedHeaderTable();
		}
	
	}
	function showBarChart(){
		var dataset=[];
  var mapdata;
  var color = d3.scale.category10();
  var margin = {top: 40, right: 20, bottom: 30, left: 40},
    width = document.getElementById("barchart").offsetWidth - margin.left - margin.right,
    height = 300 - margin.top - margin.bottom;
 	d3.json("school.json", function(error, json) { //get data
 		if (error) return console.warn(error);
    for($i=0 ; $i<json.length ; $i++){
      dataset.push({"label":json[$i].domain, "value":json[$i].count, "color": color($i)});
    }
    var formatPercent = d3.format("");

    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], .1);

    var y = d3.scale.linear()
        .range([height, 0]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
        .tickFormat(formatPercent);

    var tip = d3.tip()
      .attr('class', 'd3-tip')
      .offset([-10, 0])
      .html(function(d) {
        return "<strong>數量:</strong> <span style='color:red'>" + d.value + "</span>";
      })

    var svg2 = d3.select("#barchart").append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    svg2.call(tip);

  x.domain(dataset.map(function(d) { return d.label; }));
  y.domain([0, d3.max(dataset, function(d) { return d.value; })]);

  svg2.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis);

  svg2.append("g")
      .attr("class", "y axis")
      .call(yAxis)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("數量");

  svg2.selectAll(".bar")
      .data(dataset)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.label); })
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.value); })
      .attr("height", function(d) { return height - y(d.value); })
      .on('mouseover', tip.show)
      .on('mouseout', tip.hide);
  
  	});
	}
	function showOriginData(){
		var tableHead="<th>欄位名稱</th><th>欄位型態</th><th>Domain 數量</th>";
		$("#sensitiveHead").append(tableHead);
		var rowInfo="<tr><td>Age</td><td>Integer</td><td>74</td></tr>";
		rowInfo+="<tr><td>workclass</td><td>String</td><td>7</td></tr>";
		rowInfo+="<tr><td>fnlwgt</td><td>Integer</td><td>26741</td></tr>";
		rowInfo+="<tr><td>education</td><td>String</td><td>16</td></tr>";
		rowInfo+="<tr><td>education_num</td><td>Integer</td><td>16</td></tr>";
		rowInfo+="<tr><td>marital_status</td><td>String</td><td>7</td></tr>";
		rowInfo+="<tr><td>occupation</td><td>String</td><td>14</td></tr>";
		rowInfo+="<tr><td>relationship</td><td>String</td><td>6</td></tr>";
		rowInfo+="<tr><td>race</td><td>String</td><td>5</td></tr>";
		rowInfo+="<tr><td>sex</td><td>String</td><td>2</td></tr>";
		rowInfo+="<tr><td>capital_gain</td><td>Integer</td><td>121</td></tr>";
		rowInfo+="<tr><td>capital_loss</td><td>Integer</td><td>97</td></tr>";
		rowInfo+="<tr><td>hours_per_week</td><td>Integer</td><td>96</td></tr>";
		rowInfo+="<tr><td>native_country</td><td>String</td><td>41</td></tr>";
		rowInfo+="<tr><td>income</td><td>String</td><td>2</td></tr>";
		$("#sensitiveBody").append(rowInfo);
	}

	this.showSensitiveTableAndColumnSetting = function(inputData){
		var fileName = inputData.fileName;
		var url = endpoint + "api/data/";
		var requestBody = new Object();
		var filePath = dataPath + fileName + ".csv";
		requestBody.file_path = filePath;

		$.ajax({
			type: "Post",
			url: url,
			headers:{
				"Content-Type":"application/json;charset=utf-8"
			},
			dataType: "json",
			async: false,
			processData: false,
			data: JSON.stringify(requestBody),
			success: function(data) {
				var jsonData = JSON.parse(data);
				console.log(data);
				deIdentificationProcessManagement.listSensitiveTable(jsonData);
				inputData.col_names = jsonData.col_names;
				deIdentificationProcessManagement.listColumnsetting(inputData);
				//fake data
				$("#data_name").text("Adults");
				$("#data_rows").text("45222");
				showBarChart();
				//save columns name
				window.localStorage.setItem("columns",JSON.stringify(jsonData.col_names));
			},
			error: function() {
				console.log("file is not correct.");
				$("#information").html('資料預覽發生錯誤。');
				//$("#information").
				//clear table content
				$("#sensitiveHead").html('');
				$("#sensitiveBody").html('');
				$("#columnSettingBody").html('');
			},
			beforeSend: function(){
				loading.open();
			},
			complete: function() {
				loading.close();
			}
		});
	}

	this.getDITaskDetail=function(task_id){
		var url = endpoint + "api/de-identification/"+task_id+"/";
		$.ajax({
			type: "GET",
			url: url,
			headers:{
				"Content-Type":"application/json;charset=utf-8"
			},
			dataType: "json",
			async: false,
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data) {
				console.log(data);
				$("#task_name").val(data.task_name);
				procId=data.proc_id;
				//fake data start
				$("#data_name").text("Adults");
				$("#data_rows").text("45222");
				showBarChart();
				showOriginData();
				//fake data end

			},
			error: function() {
				console.log("get DI task detail fail.");
				$("#information").html('欄位資訊設定錯誤。');
			},
			beforeSend: function(){
				loading.open();
			},
			complete: function() {
				loading.close();
			}
		});
	}
	
	this.initDeIdentificationTask = function(requestBody) {
		var url = endpoint + "api/de-identification/";
		var response = null;
		var inputData = {};

		//console.log(requestBody);
		$.ajax({
			type: "Post",
			url: url,
			headers:{
				"Content-Type":"application/json;charset=utf-8"
			},
			dataType: "json",
			async: false,
			processData: false,
			data: JSON.stringify(requestBody),
			success: function(data) {
				//console.log(data);
				//console.log(data.proc_id);
				//deindentificationProc(data.proc_id);
				procId=data.proc_id;
				taskID=data.task_id;
				deindentificationProc(procId, taskID, "init");

				//set local storage
				inputData.task_id = data.task_id;
				window.localStorage.setItem("info",JSON.stringify(inputData));
				window.localStorage.setItem("taskID",taskID);
				doDIProc =setInterval(function(){ 
					process_status=deindentificationProc(procId, taskID, "init");
					//console.log('status:'+process_status);
				}, 3000);

				response = data;
			},
			error: function() {
				console.log("initiate DI task fail.");
				$("#information").html('欄位資訊設定錯誤。');
			},
			beforeSend: function(){
				loading.open();
			},
			complete: function() {
				loading.close();
			}
		});
		return response;
	}
	this.updateDeIdentificationTask=function(requestBody){
		taskID=window.localStorage.getItem("taskID");
		var url = endpoint + "api/de-identification/"+taskID;
		//console.log(requestBody);
		$.ajax({
			type: "Put",
			url: url,
			headers:{
				"Content-Type":"application/json;charset=utf-8"
			},
			dataType: "json",
			async: false,
			processData: false,
			data: JSON.stringify(requestBody),
			success: function(data) {

			},
			error: function() {
				console.log("initiate DI task fail.");
				$("#information").html('欄位資訊設定錯誤。');
			},
			beforeSend: function(){
				loading.open();
			},
			complete: function() {
				loading.close();
			}
		});
	}

	function deindentificationProc(proc_id, task_id, proc_type){
		url=endpoint+"api/de-identification/proc/"+proc_id;
		$.ajax({
			type: "GET",
			url: url,
			headers:{
				"Content-Type":"application/json;charset=utf-8"
			},
			//dataType: "json",
			async: false,
			//processData: false,
			//data: {'proc_id':proc_id},
			success: function(data) {
				//console.log(data);
				process_percent=data.process_percent+"%";
				process_status=data.status;
				$("#column_process .progress-bar").css("width", process_percent).text(process_percent);
				//$("#column_process .progress-bar").text(process_percent);
				
				if(process_status==3){
					clearInterval(doDIProc);
					$("#column_process .progress-bar").css("width", "100%").text("100%");
					$("#tool-tabs li").removeClass('disabled');
					if(proc_type=="init"){
						optedCluster=getOptedCluster(task_id);
					}
					if(proc_type=="exec"){ //do after exec
						getDeIdentificationJob(task_id);
					}
					setTimeout(function(){ 
						$("#column_process").fadeOut(function(){
							$("#column_process .progress-bar").css("width", "0%").text("0%");
						}); 
					}, 3000);
					//$("#column_process .progress-bar").text("100%");
					//return process_status;
				}else if(process_status==5){
					$("#systemAlertInfo").text("發生錯誤");
					$("#systemAlert").fadeIn();
					$("#column_process").fadeOut();
					clearInterval(doDIProc);
				}
			},
			error: function() {
				// console.log("initiate DI task fail.");
				// $("#information").html('欄位資訊設定錯誤。');
			},
			beforeSend: function(){
				//loading.open();
			},
			complete: function() {
				//loading.close();
			}
		});
	}

	function getOptedCluster(task_id){
		var url = endpoint + "api/de-identification/" + task_id;
		$("#defalut_cluster").empty();
		var response = null;
		$.ajax({
			type: "Get",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			async: false,
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data,textStatus) {
				response = data;
				opted_cluster=data.opted_cluster;
				dafault_cluster='';

				for(var i = 0; i < opted_cluster.length; i++) {
				    var cluster = opted_cluster[i];
				    dafault_cluster+='<li class="general_transition">';
				    for(var j = 0; j < cluster.length; j++) {
				    	dafault_cluster+='<span class="label label-info">'+cluster[j]+'</span> ';
				    }
				    dafault_cluster+='</li>';
				}
				//dafault_cluster='<li class="general_transition"></li>';
				$("#defalut_cluster").attr('data-cluster', JSON.stringify(opted_cluster));
				$("#defalut_cluster").append(dafault_cluster);
				//console.log("get the task detail success");

				// console.log(textStatus);
			},
			error: function() {
				console.log("get the task detail fail");
				$("#information").html('讀取任務內容發生錯誤。');
			},
			beforeSend: function(){
				//_showSpin();
				loading.open();
			},
			complete: function() {
				//_closeSpin();
				loading.close();
			}
		});

		//console.log(response);
		return response;
	}
	function getDeIdentificationJob(task_id){
		dp_id=window.localStorage.getItem("dp_id");
		var url=endpoint +"api/de-identification/"+task_id+"/job/"+dp_id;
		//console.log(dp_id);
		$.ajax({
			type: "Get",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			async: false,
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data,textStatus) {
				var statistics_err_attrs=[];
				console.log(data);
				$statistics_err=data.statistics_err;
				//console.log($statistics_err);
				measures=$statistics_err.measures;
				$err_thead="<td></td>";
				for(var i=0 ; i<measures.length; i++) {
					//var val = measures[key];
					$err_thead+="<td>"+measures[i]+"</td>";
					statistics_err_attrs.push(measures[i]);
				}
				$("#statisticsHead").append($err_thead);

				attrs=$statistics_err.attrs;
				//console.log(attrs);
				$err_tbody="";
				for(var i=0 ; i<attrs.length; i++){
					$err_tbody+="<tr>";
					$err_tbody+="<td>"+attrs[i]+"</td>";
					for(var j=0; j<statistics_err_attrs.length; j++){
						err_attr=statistics_err_attrs[j];
						$err_tbody+="<td>"+$statistics_err.values[err_attr][i]+"</td>";
					}
					$err_tbody+="</tr>";
				}
				$("#statisticsBody").append($err_tbody);

				if(textStatus == "success"){
					//enable the download button     
                         $("#download").prop('disabled',false);
                         $("#download").removeAttr('disabled');
                         //console.log($("#download").prop());
                         //disable the stop button     
                         $("#stopDI").prop('disabled',true);
                         //enable the start button     
                         $("#execDI").prop('disabled',false);

                         //click the button of download synthetic data
                         $("#download").click(function(e){     
                              e.preventDefault();  //stop the browser from following
                             window.location.href = download_path;
                         });
            $("#information").html('去識別化任務完成。');

				}else if(textStatus == "error"){
                         //disable the stop button     
                         $("#stopDI").prop('disabled',true);
                         //enable the start button     
                         $("#execDI").prop('disabled',false);
        }
			},
			error: function() {
				//console.log("get the task detail fail");
				$("#information").html('讀取任務內容發生錯誤。');
			},
			beforeSend: function(){
				//_showSpin();
				loading.open();
			},
			complete: function() {
				//_closeSpin();
				loading.close();
			}
		});
	}

	this.stopIDProc = function() {
		//proc_id=proc_id;
		url=endpoint+"api/de-identification/proc/"+procId;
		$.ajax({
			type: "DELETE",
			url: url,
			headers:{
				"Content-Type":"application/json;charset=utf-8"
			},
			//dataType: "json",
			async: false,
			//processData: false,
			//data: {'proc_id':proc_id},
			success: function(data) {
				//console.log(data);
				clearInterval(doDIProc);
				setTimeout(function(){ 
					$("#column_process").fadeOut(function(){
						$("#column_process .progress-bar").css("width", "0%").text("0%");
					}); 
				}, 3000);
			},
			error: function() {
				// console.log("initiate DI task fail.");
				// $("#information").html('欄位資訊設定錯誤。');
			},
			beforeSend: function(){
				//loading.open();
			},
			complete: function() {
				//loading.close();
			}
		});
	}

	this.execDeIdentificationTask = function(requestBody) {
		//console.log("execDI requestBody:");
		//console.log(requestBody);
		//var taskID = requestBody.task_id;
		var inputData = JSON.parse(window.localStorage.getItem("info"));
		var taskID = inputData.task_id;
		var url = endpoint + "api/de-identification/" + taskID + "/job/";
		var response = null;
		//console.log("taskid: "+taskID);
		$.ajax({
			// xhr: function() {
			// //for download progress bar
			// 	var xhr = new window.XMLHttpRequest();
			// 	xhr.addEventListener("progress",function(e){
			// 		if(e.lengthComputable){
			// 			var percentComplete = e.loaded / e.total;
			// 			console.log("complete: " + percentComplete);
			// 			console.log("complete(Round): " + Math.round(percentComplete * 100));
			// 			$("#dptableprogress").css({ "width": Math.round(percentComplete * 100) + "%" });
			// 			$("#dptableprogress > span").html(Math.round(percentComplete * 100)+"%");
			// 		}
			// 	},false);
			// 	return xhr;
			// },
			type: "Post",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			async: true,
			processData: false,
			data: JSON.stringify(requestBody),
			beforeSend:function(){
                    //$('#dptableprogress').show();
            },
			success: function(data,textStatus) {
				//console.log("execute DI task success.");
				 procId=data.proc_id;
				 taskID=data.task_id;
				 window.localStorage.setItem("dp_id",data.dp_id);
				// console.log(textStatus);
				deindentificationProc(procId, taskID, "exec");

				doDIProc =setInterval(function(){ 
					process_status=deindentificationProc(procId, taskID, "exec");
				}, 3000);
			},
			complete: function(xhr,textStatus,error){
				console.log(xhr);
				//console.log(textStatus);
				
			},
			error: function() {
				console.log("execute DI task fail.");
				$("#information").html('去識別化任務發生錯誤。');
			}
		
		});
	}



	this.getTaskDetail = function(task_id){
		var url = endpoint + "api/de-identification/" + task_id + "/job/";
		var response = null;
		$.ajax({
			type: "Get",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			async: false,
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data,textStatus) {
				response = data;
				//console.log("get the task detail success");
				// console.log(textStatus);

			},
			error: function() {
				console.log("get the task detail fail");
				$("#information").html('讀取任務內容發生錯誤。');
			},
			beforeSend: function(){
				//_showSpin();
				loading.open();
			},
			complete: function() {
				//_closeSpin();
				loading.close();
				//ui change

			}
		});

		//console.log(response);
		return response;
	}

	this.listStatisticsErrorRate = function(statistics_err){
		var measures = statistics_err.measures;
		var values = statistics_err.values;
		var selected_names = statistics_err.attrs;

		//build table head
		$("#statisticsHead").html('');
		for (var k = 0; k < selected_names.length; k++) {
			var tableHead = "";
			if (k==0) {
				tableHead = "<th></th>";
			}
			tableHead += "<th class=\"text-center\">" + selected_names[k] + "</th>";
			$("#statisticsHead").append(tableHead);
		};
		//$("#statisticsHead").append(tableHead);
		//build table body
		$("#statisticsBody").html('');
		for (var i = 0; i < measures.length; i++) {
			var statistics_key = measures[i];
			var statistics_value = values[measures[i]];
			
			var rowInfo = "";
			
			rowInfo += "<tr>";
			rowInfo += "<td>" + statistics_key + "</td>";
			for (var j = 0; j < statistics_value.length; j++) {
				var name = statistics_value[j];
				rowInfo += "<td class=\"text-center\">" + name + "</td>";
			};
			rowInfo += "</tr>";
			$("#statisticsBody").append(rowInfo);
		};
	}

}
