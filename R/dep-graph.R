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
	nodes_name = "ANY",
	pairs = "ANY",
	flag.all.binary = "logical",
	pairwise.table = "data.frame",
	thresh = "numeric",
	noise.flag = "logical",
	debug = "logical"
	),

	methods = list(
	initialize = function(data, domain, noise.flag = TRUE, thresh.CV = 0.2, epsilon.1 = 700){
		.self$domain <- domain
		.self$N <- nrow(data)
		.self$noise.flag <- noise.flag
		.self$thresh <- thresh.CV
		.self$epsilon.1 <- epsilon.1
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
		.self$nodes_name <- names(.self$domain)
		.self$pairs <- combn(as.vector(.self$nodes_name), 2)
		.self$beta <- .compute_best_sampling_rate_with_Gtest(nrow(data), epsilon.1, domain)

		mi_scale <- .computemi_scale()
		if(noise.flag){
			.construct_dep_graph_with_noise(data, mi_scale)
		}else{
			.construct_dep_graph(data)
		}
		
	},

	.construct_dep_graph_with_noise = function(data, mi_scale){
		
		Lap.CV2 <- DExp(rate = 1 / mi_scale)
		noise.thresh.CV2 <- r(Lap.CV2)(1)

		for (i in seq_len(ncol(.self$pairs))) {
			pair <- .self$pairs[,i]
			dk.name <- pair[1]
			dl.name <- pair[2]
			curr_xtab <- xtabs(formula = ~ get(dk.name) + get(dl.name), data = data)
			dk <- length(.self$domain[[dk.name]])
			dl <- length(.self$domain[[dl.name]])

			expected_sum <- .get_xtable_expected_sum(curr_xtab)
			chi2 <- sum((curr_xtab - expected_sum) ** 2 / expected_sum, na.rm = TRUE)

			mi <- mi.empirical(curr_xtab, unit = 'log')
			CV <- sqrt(chi2 / (.self$N * (min(dk, dl) - 1)))

			CV2.LH <- mi + r(Lap.CV2)(1)
			CV2.RH <- (.self$thresh ^ 2) * (min(dk, dl) - 1) / 2 + noise.thresh.CV2
			.filter_association_edges(pair, CV2.LH, CV2.RH)

			.append_pairwise_association_table(
				dk.name, dl.name,
				dk, dl, mi,
				CV, CV2.LH, CV2.RH)
		}
	},

	.construct_dep_graph = function(data){
		for (i in seq_len(ncol(.self$pairs))) {
			pair <- .self$pairs[,i]
			dk.name <- pair[1]
			dl.name <- pair[2]
			curr_xtab <- xtabs(formula = ~ get(dk.name) + get(dl.name), data = data)
			expected_sum <- .get_xtable_expected_sum(curr_xtab)
			chi2 <- sum((curr_xtab - expected_sum) ** 2 / expected_sum, na.rm = TRUE)
			
			dk <- length(.self$domain[[dk.name]])
			dl <- length(.self$domain[[dl.name]])

			#mi <- mi.empirical(curr_xtab, unit = 'log')
			CV <- sqrt(chi2 / (.self$N * (min(dk, dl) - 1)))
			.filter_association_edges(pair, CV, .self$thresh)
			
			#CV2.LH <- mi
			#CV2.RH <- (.self$thresh^ 2) * (min(dk, dl) - 1) / 2
			
			#.append_pairwise_association_table(
			#	dk.name, dl.name,
			#	dk, dl, mi,
			#	CV, CV2.LH, CV2.RH
			#)
			
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
	},

	.computemi_scale = function(){
		epsilon.alpha.1 <- .amplify_epsilon_under_sampling(.self$epsilon.1, .self$beta)
		sensitivity.scale.mi <- .compute_mi_sensitivity_scale(.self$N, FALSE)
		b.scale.mi <- 2 * sensitivity.scale.mi / epsilon.alpha.1
		return(b.scale.mi)
	},
	.compute_mi_sensitivity_scale = function(N, flag.all.binary) {
		if(flag.all.binary){
			sensitivity.scale <- (1 / N) * log(N) + ((N - 1) / N) * log(N / (N - 1))
		}else{
			sensitivity.scale <- (2 / N) * log((N + 1) / 2) + ((N - 1) / N) * log((N + 1) / (N - 1))
		} 
		return(sensitivity.scale)
	},
	.amplify_epsilon_under_sampling = function(epsilon, sample.rate) {
		epsilon.alpha <- log(exp(1) ** (epsilon) - 1 + sample.rate) - log(sample.rate)
		return(epsilon.alpha)
	},
	.compute_best_sampling_rate_with_Gtest = function(DB.size, epsilon.1, domain) {
		#e.g. e=0.05, N=300000, \beta=0.25
		init.array <- seq(0, 1, by = 0.001)
		beta.array <- init.array[2: length(init.array)]
		flag.all.binary <- (length(which(domain$dsize != 2)) == 0)
		get_noise_scale <- function(size, eps, x) {
			N = size * x
			epsilon.alpha <- .amplify_epsilon_under_sampling(eps, x)
			sensitivity.scale <- .compute_Gtest_sensitivity_scale(N, flag.all.binary)
			b <- 2 * sensitivity.scale / epsilon.alpha
			return(b)
		}
		b.array <- lapply(beta.array, function(x) get_noise_scale(DB.size, epsilon.1, x))
		b.min <- min(unlist(b.array))
		beta <- beta.array[which(b.array == b.min)]
		return(beta)
	},
	.compute_Gtest_sensitivity_scale = function(N, flag.all.binary) {                    #Gtest.scale????
		mi.sen <- .compute_mi_sensitivity_scale(N, flag.all.binary)
		Gtest.scale <- 2 * mi.sen
		return(Gtest.scale)
	}
	)
)

get_dep_edges <- function(data, domain, noise.flag, epsilon.1){
	dep_graph <- DependenceGraph$new(data, domain, noise.flag = noise.flag, epsilon.1 = epsilon.1)
	return(dep_graph$edges)
}
