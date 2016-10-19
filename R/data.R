Data <- setRefClass(
	"Data",
	
	fields = list(
		domain = "ANY",
		DB.size = "numeric"
	),
	
	methods = list(
		initialize = function(domain){
			.self$domain <- list()
			.self$domain$name <- unlist(domain['name'])
			.self$domain$dsize <- domain['dsize']$dsize
			.self$domain$levels <- domain['levels']$levels
			.self$DB.size <- domain['nrows']$nrows
		}
	)
)