function dataSettingManagement(){
	utilities = new utilities();
	var endpoint = utilities.endpoint;

	this.showSensitiveTable = function(filePath){
		var url = endpoint + "api/data/";
		var requestBody = new Object();
		requestBody.file_path = filePath;

		$.ajax({
			type: "Post",
			url: url,
			headers:{
				"Content-Type":"application/json"
			},
			dataType: "json",
			processData: false,
			data: JSON.stringify(requestBody),
			success: function(data) {
				var jsonData = JSON.parse(data);
				var columns = [];
				columns = jsonData.col_names;
				
				//build table head
				$("#sensitiveHead").html('');
				for (var k = 0; k < columns.length; k++) {
					var tableHead = "";
					tableHead += "<th class=\"text-center\">" + columns[k] + "</th>";
					$("#sensitiveHead").append(tableHead);
				};
				
				var rows = [];
				rows = jsonData.rows;
				//build table body
				$("#sensitiveBody").html('');
				for (var i = 0; i < rows.length; i++) {
					var rowInfo = "";
					rowInfo += "<tr>";
					for (var j = 0; j < rows[i].length; j++) {
						rowInfo += "<td>" + rows[i][j] + "</td>";
					};
					rowInfo += "</tr>";
					$("#sensitiveBody").append(rowInfo);
				};
			},
			error: function() {
				console.log("file is not correct.");
				//clear table content
				$("#sensitiveHead").html('');
				$("#sensitiveBody").html('');
			}
		});
	}

	this.columnSetting = function (columns) {
		$("#columnSettingBody").html('');
		for (var i = 0; i < columns.length; i++) {
			var columnName = columns[i];
			var columnInfo = "";

			columnInfo += "<tr>";
			columnInfo += "<td><label class=\"checkbox-inline\"><input type=\"checkbox\" value=\"\"></label></td>";
			columnInfo += "<td>" + columnName + "</td>";
			columnInfo += "<td><div class=\"dropdown\">";
			columnInfo += "<select class=\"form-control\">";
			columnInfo += "<option>連續型</option>";
			columnInfo += "<option>類別型</option>";
			columnInfo += "</select></div></td>";
			columnInfo += "<td>";
			columnInfo += "<section style=\"border-style:inset;\">";
			columnInfo += "<span class=\"attr_each\">" + columns[1];											
			columnInfo += "<span class=\"glyphicon glyphicon-remove-sign\" style=\"cursor: pointer;\" title=\"移除屬性\">";													
			columnInfo += "</span>";												
			columnInfo += "</span>";											
			columnInfo += "<span class=\"attr_each\">" + columns[2];											
			columnInfo += "<span class=\"glyphicon glyphicon-remove-sign\" style=\"cursor: pointer;\">";										
			columnInfo += "</span>";											
			columnInfo += "</span></section></td></tr>";																				
											   
			
			$("#columnSettingBody").append(columnInfo);
		};
	}
	
}
