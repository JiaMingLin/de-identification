function dashboardManagement() {
	var endpoint = UTILITIES.endpoint;
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
						status = "等待中";
						break;
						case 1:
						status = "執行中";
						break;
						case 2:
						status = "錯誤發生";
						break;
						case 3:
						status = "已完成";
						break;
					}				

					jobsInfo += "<tr>";
					jobsInfo += "<td><label class=\"checkbox-inline\"><input type=\"checkbox\" value=\""+ taskId +"\"></label></td>";
					jobsInfo += "<td>" + taskName + "</td>";
					jobsInfo += "<td>開始： "+ startTime +"<br/>";
					jobsInfo += "結束： "+ endTime +"</td>";
					jobsInfo += "<td>"+ status +"</td>";
					jobsInfo += "</tr>";
					$("#dpJobListBody").append(jobsInfo);
				};
			},
			error: function() {
				
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
			},
			complete: function(xhr,textStatus,error){
				if(textStatus == "success"){
					var responseJSON = xhr.responseJSON;
					_parseInfo(responseJSON);
					window.location.href = "/privacy/web/DeIdentificationProcess.html?default=false";
				}else if(textStatus == "error"){
					location.href = "/privacy/";
				}
			}
		});


	}

	this.deleteTasks = function (requestBody) {
		var task_id = requestBody.task_id;
		var url = endpoint + "api/de-identification/" + task_id; 

		$.ajax({
			type: "Delete",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			processData: false,
			//data: JSON.stringify(requestBody),
			success: function(data) {
				
			},
			error: function() {
				
			}
		});
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
}