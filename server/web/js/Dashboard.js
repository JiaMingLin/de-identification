$(function() {
	
	dashboardManagement = new dashboardManagement();

	dashboardManagement.listTasks(0,0);
	dashboardManagement.listDataSynthesis();
	//click create button
	// $("#cDPTableTask").click(function(){
	// 	location.href = "/privacy/web/DeIdentificationProcess.html?default=true";
	// });

	//click edit button
	$("#eDPTableTask").click(function(){
		var selected_task_id = $("#dpJobListBody input[type=checkbox]:checked").val();
		// console.log(selected_task_id);
		window.location.href="/privacy/web/DeIdentificationProcess.html?task_id="+selected_task_id;
		//dashboardManagement.editTask(selected_task_id);
	});

	//click delete task button
	$("#dDPTableTask").click(function(){
		$("#dpJobListBody input[type=checkbox]:checked").each(function(){
			var task_id = $(this).attr("data-taskid");
			var requestBody = {};
			requestBody.task_id = task_id;
			dashboardManagement.deleteTasks(requestBody);

		});
	});
	//click delete analysis button
	$("#dAnalysisTask").click(function(){
		$("#dataSynthesisBody input[type=checkbox]:checked").each(function(){
			var ana_id = $(this).attr("data-anaid");
			var requestBody = {};
			requestBody.ana_id = ana_id;
			dashboardManagement.deleteAnalysis(requestBody);
		});
	});
	//click stop button
	$("#sDPTableTask").click(function(){
		$("#dpJobListBody input[type=checkbox]:checked").each(function(){
			var task_id = $(this).attr("data-taskid");
			var requestBody = {};
			requestBody.task_id = task_id;
			requestBody.list_type="task";
			dashboardManagement.stopProc(requestBody);
		});
	});
	$("#sAnalysisTask").click(function(){
		$("#dataSynthesisBody input[type=checkbox]:checked").each(function(){
			var task_id = $(this).attr("data-anaid");
			var requestBody = {};
			requestBody.task_id = task_id;
			requestBody.list_type="ana";
			dashboardManagement.stopProc(requestBody);
		});
	});
	$('[data-toggle="popover"]').popover()
	$("#eAnalysisTask").click(function(){
		var selected_ana_id = $("#dataSynthesisBody input[type=checkbox]:checked").val();
		// console.log(selected_task_id);
		window.location.href="/privacy/web/DataSynthesis.html?id="+selected_ana_id;
	});
	//check all box
	$("#DPTableCheckAll").bind("click",function (e) {	
		var checkboxes = $("#dpJobListBody input:checkbox");
		checkboxes.prop('checked', $(this).prop("checked"));
		if($(this).prop("checked")){
			$("#eDPTableTask").attr("disabled","disabled");
			$("#dDPTableTask").removeAttr("disabled");
			$("#sDPTableTask").removeAttr("disabled");
		}else{
			$("#eDPTableTask").attr("disabled","disabled");
			$("#dDPTableTask").attr("disabled","disabled");
			$("#sDPTableTask").attr("disabled","disabled");
		}
	});
	$("#ANTableCheckAll").bind("click",function (e) {	
		var checkboxes = $("#dataSynthesisBody input:checkbox");
		checkboxes.prop('checked', $(this).prop("checked"));
		if($(this).prop("checked")){
			$("#eAnalysisTask").attr("disabled","disabled");
			$("#dAnalysisTask").removeAttr("disabled");
			$("#sAnalysisTask").removeAttr("disabled");
		}else{
			$("#eAnalysisTask").attr("disabled","disabled");
			$("#dAnalysisTask").attr("disabled","disabled");
			$("#sAnalysisTask").attr("disabled","disabled");
		}
	});
	//multi select enable
	$("#dpJobListBody").on("click","input[type=checkbox]", function(){
		$totalCheck=$("#dpJobListBody").find("input:checked").length;
		if($totalCheck==0){
			$("#eDPTableTask").attr("disabled","disabled");
			$("#dDPTableTask").attr("disabled","disabled");
			$("#sDPTableTask").attr("disabled","disabled");
		}else if($totalCheck==1){
			$("#eDPTableTask").removeAttr("disabled");
			$("#dDPTableTask").removeAttr("disabled");
			$("#sDPTableTask").removeAttr("disabled");
		}else{
			$("#eDPTableTask").attr("disabled","disabled");
		}
	});
	$("#dataSynthesisBody").on("click","input[type=checkbox]", function(){
		$totalCheck=$("#dataSynthesisBody").find("input:checked").length;
		if($totalCheck==0){
			$("#eAnalysisTask").attr("disabled","disabled");
			$("#dAnalysisTask").attr("disabled","disabled");
			$("#sAnalysisTask").attr("disabled","disabled");
		}else if($totalCheck==1){
			$("#eAnalysisTask").removeAttr("disabled");
			$("#dAnalysisTask").removeAttr("disabled");
			$("#sAnalysisTask").removeAttr("disabled");
		}else{
			$("#eAnalysisTask").attr("disabled","disabled");
		}
	});


});