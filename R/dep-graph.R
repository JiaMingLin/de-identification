library(distr)
library(entropy)
# TODO: Add the noise method.
# TODO: Check the attributes are binerary or not.
# TODO: Add a data structure of dep-graph for displaying.
DependenceGraph <- setRefClass(
    "DependenceGraph",

  fields = list(
  	beta = "numeric",
	epsilon.1 = "numeric",
	N = "numeric",
	edges = "list",
	domain = "list",
	flag.all.binary = "logical",
	pairwise.table = "data.frame",
	thresh = "numeric",
	debug = "logical"
    ),

  methods = list(
  	initialize = function(data, domain, thresh.CV = 0.2){
  		.self$domain = domain
  		.self$N = nrow(data)
  		.self$thresh = thresh.CV
  		.self$pairwise.table <-data.frame(
  			dk.name = character()
			, dl.name = character()
			, dk = integer()
			, dl = integer()
			, mi = numeric()
			, CV = numeric()
			, CV2.LH = numeric()
			, CV2.RH = numeric()
      )
  		.construct_dep_graph(data)	
	},

	.construct_dep_graph = function(data){
		nodes_name = names(.self$domain)
		pairs <- combn(as.vector(nodes_name), 2)

		for (i in seq_len(ncol(pairs))) {
			pair <- pairs[,i]
			dk.name <- pair[1]
			dl.name <- pair[2]
			curr_xtab <- xtabs(formula = ~ get(dk.name) + get(dl.name), data = data)
			dk <- length(.self$domain[[dk.name]])
			dl <- length(.self$domain[[dl.name]])

			expected_sum <- .get_xtable_expected_sum(curr_xtab)
			chi2 <- sum((curr_xtab - expected_sum) ** 2 / expected_sum, na.rm = TRUE)
			mi <- mi.empirical(curr_xtab, unit = 'log')
			CV <- sqrt(chi2 / (.self$N * (min(dk, dl) - 1)))

			.filter_association_edges(pair, CV, .self$thresh)
			CV2.LH <- mi
			CV2.RH <- (.self$thresh ^ 2) * (min(dk, dl) - 1) / 2

			.append_pairwise_association_table(
				dk.name, dl.name,
				dk, dl, mi,
				CV, CV2.LH, CV2.RH)
		}
	},

	.append_pairwise_association_table = function(dk.name, dl.name, 
													dk, dl, mi,
													CV, CV2.LH, CV2.RH){
		newrow<-data.frame(dk.name = dk.name
						, dl.name = dl.name
						, dk = dk
						, dl = dl
						, mi = mi
						, CV = CV
						, CV2.LH = CV2.LH
						, CV2.RH = CV2.RH
      )
		.self$pairwise.table<-rbind(.self$pairwise.table,newrow)

	},

	.get_xtable_expected_sum = function(xtable) {
		rsums <- rowSums(xtable)
		rsums <- matrix(rsums, nrow = length(rsums), ncol = 1)
		csums <- colSums(xtable)
		csums <- matrix(csums, nrow = 1, ncol = length(csums))
		table.sum <- sum(rsums)
		expected_sum <- rsums %*% csums / table.sum
		return(expected_sum) 
    },

    .filter_association_edges = function(pair, measure, bar) {
      if(measure >= bar){
        curr_length <- length(.self$edges)
        .self$edges[[curr_length + 1]]<- pair
      }      
    }
	)
)

get_dep_edges <- function(data, domain){
    dep_graph <- DependenceGraph$new(data, domain)
    return(dep_graph$edges)
}
