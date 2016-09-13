Data <- setRefClass(
	"Data",
	
	fields = list(
		origin = "ANY",
		data = "ANY",
		domain = "ANY",
		DB.size = "numeric"
	),
	
	methods = list(
		initialize = function(data, domain){
			.self$domain <- list()
			.self$data <- data
			.self$domain$name <- unlist(domain['name'])
			.self$domain$dsize <- domain['dsize']$dsize
			.self$domain$levels <- domain['levels']$levels
			load_coarse_data()
		},

		load_coarse_data = function() {
			.self$origin <- list()

			rows <- .self$data
			for (col.name in colnames(rows)) {
				rows[col.name]<-lapply(rows[col.name], factor
					, levels = .self$domain$levels[[col.name]])
			}

			.self$origin <- rows
			.self$DB.size = as.integer(nrow(rows))
		}
	)
)