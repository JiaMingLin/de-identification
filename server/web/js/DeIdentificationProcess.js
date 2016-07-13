$(function() {

	var dataPath = UTILITIES.data_path;
	var initDI_response = {};
	var execDI_response = {};
	var loadingOption ={
		imgPath    : 'images/ajax-loading.gif',
		tip: '請稍後...'
	}
	var loading = $.loading(loadingOption);
	loading.ajax(true);
	var isDefault = true;
	deIdentificationProcessManagement = new deIdentificationProcessManagement();

	var _checkRender = function(){
		isDefault = location.href.split("?default=")[1];
		if((isDefault == false || isDefault == "false") && isDefault != undefined){
			var inputData = JSON.parse(window.localStorage.getItem("info"));
			deIdentificationProcessManagement.showSensitiveTableAndColumnSetting(inputData);
			var input_fileName = inputData.fileName;
			$("#filenameinput").val(input_fileName);
			$("#filenameinput").prop('disabled',true);
			//disabled the column setting panel
			_columnSettingPanelControl(true);
			window.localStorage.setItem("columnSetting",JSON.stringify(inputData.selected_attrs));
		}
	}

	var _initDI = function(){
		var initDI_requestBody = {};
		var filename = "";
		var selected_attrs = {};
		var selected_names = [];
		var selected_types = [];
		var response;

		if($("#filenameinput").prop('disabled') && $("#filenameinput").val() != undefined && localStorage.getItem("columns") != undefined){
			filename = $("#filenameinput").val();
		}
		initDI_requestBody.data_path = dataPath + filename + ".csv";
		initDI_requestBody.task_name = "task_of_" + filename + ".csv";

		//check column setting panel
		$("#columnSettingBody input[type=checkbox]:checked").each(function(){
			var jsonObject = {};
			var selected_name = $(this).val();
			var selected_type = $(this).parent().parent().parent().find("select").val();
			selected_names.push(selected_name);
			selected_types.push(selected_type);
		});

		selected_attrs.names = selected_names;
		selected_attrs.types = selected_types;
		initDI_requestBody.selected_attrs = selected_attrs;
		//store the columns setting info
		window.localStorage.setItem("columnSetting",JSON.stringify(initDI_requestBody));
		response = deIdentificationProcessManagement.initDeIdentificationTask(initDI_requestBody);

		return response;
	}

	var _execDI = function(response){
		var execDI_requestBody = {};	
		var task_id = -1;
		var privacy_level = -1;
		var epsilon = -1.0;
		
		//the DI task is waitting
		if(response.status == 0){
			task_id = response.task_id;
			execDI_requestBody.task_id = task_id;
			privacy_level = $("#PL-options").val();

			//privacy level translation
			switch(privacy_level){
				case "1":
				epsilon = 0.01;
				break;
				case "2":
				epsilon = 0.1;
				break;
				case "3":
				epsilon = 1.0;
				break;
				case "4":
				epsilon = 10.0;
				break;
				case "5":
				epsilon = 100.0;
				break;
			}

			console.log("taskID: "+task_id+" privacy_level: " + privacy_level + " epsilon: "+ epsilon);
			execDI_requestBody.privacy_level = privacy_level;
			execDI_requestBody.epsilon = epsilon;

			//execute the DI task
			deIdentificationProcessManagement.execDeIdentificationTask(execDI_requestBody);
		}
	}

	var _execButtonReady = function(){
		// console.log("changed button status");
		//disable the download button	
		$("#download").prop('disabled',true);
		//enable the stop button	
		$("#stopDI").prop('disabled',true);
		//disable the start button	
		$("#execDI").prop('disabled',false);
	}

	var _columnSettingPanelControl = function(disabled){
		//disable or enable the column setting panel	
		$("#columnSettingBody").find("input,select,section").prop('disabled',disabled);
	}
	
	//To check wether display record or not
	_checkRender();

	//click confirm button
	$("#fileconfirm").click(function(){
		$("#filenameinput").prop('disabled',true);
		var fileName = $("#filenameinput").val();
		var data = {};
		data.fileName = fileName;
		//for list default column setting
		data.default = true;		
		deIdentificationProcessManagement.showSensitiveTableAndColumnSetting(data);
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
			//clear columns setting content
			$("#columnSettingBody").html('');

			//clear the local storage
			localStorage.removeItem("columns");
			localStorage.removeItem("columnSetting");
			localStorage.removeItem("info");
		}
	});

	//check all box
	$("#dataSelectedCheckAll").bind("click",function (e) {	
		var checkboxes = $("input:checkbox");
		checkboxes.prop('checked', $(this).prop("checked"));
	});

	//click column setting confirm button
	$("#columnconfirm").click(function(){
		//loading.open();
		var jsonArray = [];
		_columnSettingPanelControl(true);
		// $('#columnSettingBody tr').each(function() {
		// 	var jsonObject = {};
		//     var checkbox  = $(this).find("input:checkbox").prop('checked');
		//     var select = $(this).find("select").val();
		//     var columnName = $(this)
		//     jsonObject.checkbox = checkbox;
		//     jsonObject.select = select; 
		//     jsonArray.push(jsonObject); 
		//  });

		//begin to initiate the DI task
		initDI_response = _initDI();
		_execButtonReady();
		//loading.close();
	});

	//click column setting cancel button
	$("#columncancel").click(function(){
		_columnSettingPanelControl(false);
	});

	//click column setting reset button
	$("#columnreset").click(function(){
		if($("#columnSettingBody").find("input,select,section").prop('disabled') == false){
			var columns = [];
			columns = JSON.parse(window.localStorage.getItem("columns"));
			var data = {};
			data.col_names = columns;
			//for list default column setting
			data.default = true;
			deIdentificationProcessManagement.listColumnsetting(data);
			localStorage.removeItem("columnSetting");
			localStorage.removeItem("info");
		}
	});

	//execute the De-Identification task
	$("#execDI").click(function(){
		
		if($("#filenameinput").prop('disabled') == false && $("#filenameinput").val() == ""){
			$("#information").html('請輸入檔案。');
			return;
		}
		if($("#columnSettingBody").find("input,select,section").prop('disabled') == false){
			$("#information").html('請確認欄位資訊設定。');
			return;
		}else{
			if($("#columnSettingBody input[type=checkbox]:checked").length == 0){
				$("#information").html('請選擇欲去識別化之欄位。');
				return;
			}
		}

		if($.isEmptyObject(initDI_response) == true){
			if(isDefault){
				//conflict happened
				$("#information").html('去識別化任務發生錯誤。');
				return;
			}
			//old record is exist
			var inputData = JSON.parse(window.localStorage.getItem("info"));
			var task_id = inputData.task_id;
			var records = deIdentificationProcessManagement.getTaskDetail(task_id);
			var lastRecord = records[records.length-1];
			initDI_response.task_id = task_id;
			initDI_response.privacy_level = lastRecord.privacy_level;
			initDI_response.epsilon = lastRecord.epsilon;
			//set waitting status
			initDI_response.status = 0;		
		}

		if(!$("#download").prop('disabled')){
			$("#download").prop('disabled',true);
		}
		if($("#stopDI").prop('disabled')){
			$("#stopDI").prop('disabled',false);
		}
		if(!$("#execDI").prop('disabled')){
			$("#execDI").prop('disabled',true);
		}

		_execDI(initDI_response);
	});

	//detect the privacy level options changed
	$("#PL-options").on('change',function(){	
		_execButtonReady();
	});

	

	$(window).on('keydown',function(e){
		var keycode = e.keyCode;
		//console.log("keycode: " + keycode);
		if(keycode == 13){
			//press enter
			$("#fileconfirm").click();
		}else if(keycode == 116){
			//press F5
			e.preventDefault();
			$("#filenameinput").prop('disabled',false);
			$("#fileclear").click();
			window.localStorage.removeItem("info");
			window.location.href = "/privacy/web/DeIdentificationProcess.html?default=true";
		}
	});

	


});
