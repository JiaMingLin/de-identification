Data <- setRefClass(
	"Data",
	
	fields = list(
		origin = "ANY",
		data_path = "character",
		domain = "ANY",
		DB.size = "numeric"
	),
	
	methods = list(
		initialize = function(data_path, domain){
			.self$domain <- list()
			.self$data_path <- data_path
			.self$domain$name <- unlist(domain['name'])
			.self$domain$dsize <- domain['dsize']$dsize
			.self$domain$levels <- domain['levels']$levels
			load_coarse_data()
		},

		load_coarse_data = function() {
			.self$origin <- list()
			
			rows <- read.csv(file = .self$data_path, 
				header = FALSE, 
				col.names = .self$domain$name, 
				colClasses = rep('factor', length(.self$domain$name)), 
				check.names = FALSE
			)

			rows <- as.data.frame(rows)
			for (col.name in colnames(rows)) {
				rows[col.name]<-lapply(rows[col.name], factor
					, levels = .self$domain$levels[[col.name]])
			}

			.self$origin <- rows
			.self$DB.size = as.integer(nrow(rows))
			print(paste("Dataset size:", .self$DB.size))
		}
	)
)