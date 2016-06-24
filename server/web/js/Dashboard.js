$(function() {
	var endpoint = "http://140.92.25.109:8080/privacy/";

	var listJobs = function (size,page) {
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

					jobsInfo += "<tr>";
					jobsInfo += "<td><label class=\"checkbox-inline\"><input type=\"checkbox\" value=\""+ taskId +"\"></label></td>";
					jobsInfo += "<td>" + taskName + "</td>";
					jobsInfo += "<td>開始： "+ start_time +"<br/>";
					jobsInfo += "結束： "+ end_time +"</td>";
					jobsInfo += "<td>"+ status +"</td>";
					jobsInfo += "</tr>";
					$("#dpJobListBody").append(jobsInfo);
				};
			},
			error: function() {
				
			}
		});
	}

	listJobs(0,0);
});