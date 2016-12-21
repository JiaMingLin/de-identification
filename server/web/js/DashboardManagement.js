function dashboardManagement() {
	var endpoint = UTILITIES.endpoint;
	var loadingOption ={
		imgPath    : 'web/images/ajax-loading.gif',
		tip: '請稍後...',
		ajax: false
	}
	var loading = $.loading(loadingOption);
	deIdentificationProcessManagement = new deIdentificationProcessManagement();

	this.listTasks = function (size,page) {
		var url = endpoint + "api/de-identification?page=" + page + "&size=" + size; 

		$.ajax({
			type: "Get",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data) {
				$("#dpJobListBody").html("");
				for (var i = 0; i < data.length; i++) {
					var jobsInfo = "";
					var taskId = data[i].task_id;
					var taskName = data[i].task_name;
					var startTime = data[i].start_time;
					var endTime = data[i].end_time;
					var status = data[i].status;
					var procId = data[i].proc_id;

					if (startTime == null) {
						startTime = "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp—";
					}else{
						startTime = startTime.replace(/[TZ\.]/g," ");
					}
					if (endTime == null) {
						endTime = "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp—";
					}else{
						endTime = endTime.replace(/[TZ\.]/g," ");
					}

					switch(status){
						case 0:
						statusName = "等待中";
						break;
						case 1:
						statusName = "進入排程，等待執行";
						break;
						case 2:
						statusName = "執行中";
						break;
						case 3:
						statusName = "已完成";
						break;
						case 4:
						statusName = "執行中斷";
						break;
						case 5:
						statusName = "執行錯誤";
						break;
					}				

					jobsInfo += "<tr id=\"task"+taskId+"\" data-procid=\""+procId+"\" data-status=\""+status+"\">";
					jobsInfo += "<td><label class=\"checkbox-inline\"><input type=\"checkbox\" data-taskid=\""+taskId+"\" value=\""+ taskId +"\"></label></td>";
					jobsInfo += "<td>" + taskName + "</td>";
					jobsInfo += "<td>開始： "+ startTime +"<br/>";
					jobsInfo += "結束： "+ endTime +"</td>";
					jobsInfo += "<td class='job_status'>"+ statusName +"</td>";
					jobsInfo += "</tr>";
					$("#dpJobListBody").append(jobsInfo);
				};
			},
			error: function() {
				$("#systemAlertInfo").text("讀取發生錯誤。");
				$("#systemAlert").removeClass('alert-info').addClass('alert-danger').fadeIn();
			},
			beforeSend: function(){
				loading.open();
			},
			complete: function() {
				loading.close();
			}
		});
	}

	this.editTask = function (task_id) {
		var url = endpoint + "api/de-identification/" + task_id +"/"; 

		$.ajax({
			type: "Get",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data) {
				console.log("get record back success");
			},
			error: function() {
				console.log("get record back fail");
				$("#systemAlertInfo").text("讀取任務內容發生錯誤。");
				$("#systemAlert").removeClass('alert-info').addClass('alert-danger').fadeIn();
			},
			complete: function(xhr,textStatus,error){
				if(textStatus == "success"){
					var responseJSON = xhr.responseJSON;
					_parseInfo(responseJSON);
					window.location.href = "/privacy/web/DeIdentificationProcess.html?default=false";
				}else if(textStatus == "error"){
					location.href = "/privacy/";
				}
				loading.close();
			},
			beforeSend: function(){
				loading.open();
			}
		});


	}

	this.deleteTasks = function (requestBody) {
		var task_id = requestBody.task_id;
		var url = endpoint + "api/de-identification/" + task_id; 

		$.ajax({
			type: "DELETE",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data) {
				var trId=$("#task"+task_id);
				trId.remove();
			},
			error: function() {
				$("#systemAlertInfo").text("刪除任務發生錯誤。");
				$("#systemAlert").removeClass('alert-info').addClass('alert-danger').fadeIn();
			},
			beforeSend: function(){
				loading.open();
			},
			complete: function() {
				loading.close();
			}
		});
	}
	this.deleteAnalysis = function (requestBody) {
		var analysis_id = requestBody.ana_id;
		var url = endpoint + "api/de-identification/utility/" + analysis_id; 

		$.ajax({
			type: "DELETE",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data) {
				var trId=$("#ana"+analysis_id);
				trId.remove();
			},
			error: function() {
				$("#systemAlertInfo").text("刪除合成資料分析發生錯誤。");
				$("#systemAlert").removeClass('alert-info').addClass('alert-danger').fadeIn();
			},
			beforeSend: function(){
				loading.open();
			},
			complete: function() {
				loading.close();
			}
		});
	}
	this.stopProc = function (requestBody) {
		var trId=$("#"+requestBody.list_type+requestBody.task_id)
		var procId=trId.attr("data-procid");
		var status=trId.attr("data-status");
		//console.log(procId+", "+status)
		if(status==1){
			url=endpoint+"api/de-identification/proc/"+procId;
			$.ajax({
				type: "DELETE",
				url: url,
				headers:{
					"Content-Type":"application/json;charset=utf-8"
				},
				async: false,
				success: function(data) {
					trId.find(".job_status").text("等待中");
				},
				error: function() {

				},
				beforeSend: function(){
					loading.open();
				},
				complete: function() {
					loading.close();
				}
			});
		}
		
	}

	var _parseInfo = function(jsonData){
		var data_path = jsonData.data_path;
		var selected_attrs = jsonData.selected_attrs;
		var task_id = jsonData.task_id;
		var words = data_path.split("/");
		var file_name = words[words.length-1].replace(".csv","");
		var inputData = {};

		inputData.default = false;
		inputData.fileName = file_name;
		inputData.selected_attrs = selected_attrs;
		inputData.task_id = task_id;

		console.log("Edit task input data: ");
		console.log(inputData);
		window.localStorage.setItem("info",JSON.stringify(inputData));
	}

	//get data synthesis list
	this.listDataSynthesis=function(){
		var dataSynthesisList="";
		var url = endpoint + "api/de-identification/utility/";
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
				console.log(data);
				//var DataSynthesisList = "";
				$("#dataSynthesisBody").html("");
				for (var i = 0; i < data.length; i++) {
					
					var analysisId = data[i].analysis_id;
					var analysisName = data[i].analysis_name;
					var startTime = data[i].start_time;
					var endTime = data[i].end_time;
					var status = data[i].status;
					var procId = data[i].proc_id;

					if (startTime == null) {
						startTime = "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp—";
					}else{
						startTime = startTime.replace(/[TZ\.]/g," ");
					}
					if (endTime == null) {
						endTime = "&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp—";
					}else{
						endTime = endTime.replace(/[TZ\.]/g," ");
					}

					switch(status){
						case 0:
						statusName = "等待中";
						break;
						case 1:
						statusName = "進入排程，等待執行";
						break;
						case 2:
						statusName = "執行中";
						break;
						case 3:
						statusName = "已完成";
						break;
						case 4:
						statusName = "執行中斷";
						break;
						case 5:
						statusName = "執行錯誤";
						break;
					}				

					dataSynthesisList += "<tr id=\"ana"+analysisId+"\" data-procid=\""+procId+"\" data-status=\""+status+"\">";
					dataSynthesisList += "<td><label class=\"checkbox-inline\"><input data-anaid=\""+analysisId+"\" type=\"checkbox\" value=\""+ analysisId +"\"></label></td>";
					dataSynthesisList += "<td>" + analysisName + "</td>";
					dataSynthesisList += "<td>開始： "+ startTime +"<br/>";
					dataSynthesisList += "結束： "+ endTime +"</td>";
					dataSynthesisList += "<td class='job_status'>"+ statusName +"</td>";
					dataSynthesisList += "</tr>";					
				};
				$("#dataSynthesisBody").append(dataSynthesisList);
				//$("#dataSynthesisBody").append();
			},
			error: function() {
				$("#systemAlertInfo").text("讀取發生錯誤。");
				$("#systemAlert").removeClass('alert-info').addClass('alert-danger').fadeIn();
			},
			beforeSend: function(){
				//loading.open();
			},
			complete: function() {
				//loading.close();
			}
		});
	}
	
}