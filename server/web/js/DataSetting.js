$(function() {
	
	dataSettingManagement = new dataSettingManagement();


	//click confirm button
	$("#fileconfirm").click(function(){
		$("#filenameinput").prop('disabled',true);
		var filepath = "static/test/" + $("#filenameinput").val() + ".csv";
		var columns = dataSettingManagement.showSensitiveTable(filepath);
		//list columns setting
		dataSettingManagement.columnSetting(columns);
	});

	$("#filecancel").click(function(){		
		$("#filenameinput").prop('disabled',false);
	});

	$("#fileclear").click(function(){
		if($("#filenameinput").prop('disabled') == false){
			$("#filenameinput").val("");
			//clear table content
			$("#sensitiveHead").html('');
			$("#sensitiveBody").html('');
		}
	});

	//check all box
	$("#dataSelectedCheckAll").bind("click",function (e) {	
		var checkboxes = $("input:checkbox");
		checkboxes.prop('checked', $(this).prop("checked"));
	});

});
