function dashboardManagement() {
	var endpoint = "http://140.92.25.109:8080/privacy/";

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

	this.deleteTasks = function (requestBody) {
		var url = endpoint + "api/de-identification?page=" + page + "&size=" + size; 

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

	
}