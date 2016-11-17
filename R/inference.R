Inference <- setRefClass(
	"Inference",
	
	fields = list(
		cluster = 'list',
		epsilon = 'numeric',
		data = "ANY",
		histograms = "ANY", 
		cluster.noisy.freq = "ANY",
		jtree = "ANY",
		clique.freq = "list",
		POTlist.consistent = "ANY",
		POTgrain.consistent = 'ANY',
		POTlist = "ANY",
		POTgrain = "ANY",
		noise.flag = "logical"
	),

	methods = list(
		initialize = function(cluster, jtree_file, histograms, domain, noise.flag=TRUE, epsilon=0.0){
			.self$cluster.noisy.freq <- list()
			.self$cluster <- cluster
			.self$epsilon <- epsilon
			.self$data <- Data$new(domain)
			.self$histograms <- histograms
			.self$jtree <- readRDS(jtree_file)
			.self$noise.flag <- noise.flag
		},

		inject_noise = function(){

			margins <- .self$cluster
			#t <- data.table(.self$data$origin)
			margin.noisy.freq <- list()
			sen <- 1
			num.margins<-length(margins)
			b <- 2 * (num.margins) * sen / epsilon
			Lap <- DExp(rate = 1 / b)
			for (i in seq_len(length(margins))) {
				cq <- margins[[i]]

				#setkeyv(t, cq)
				#curr_levels <- lapply(cq, function(x) levels(t[, get(x)]))
				#xxx <- t[do.call(CJ, curr_levels), list(freq = .N), allow.cartesian = T, by = .EACHI][, freq]
				xxx <- get_freq(cq)
				noises <- r(Lap)(length(xxx))
				freq.noisy <- xxx + noises				
				margin.noisy.freq[[i]] <- freq.noisy
			}
			.self$cluster.noisy.freq <- margin.noisy.freq
		},

		consistency = function(){
			consistency <- ConsistentMargin$new(.self$data$DB.size, .self$cluster, .self$data$domain, .self$cluster.noisy.freq)
			.self$cluster.noisy.freq <- consistency$fix_negative_entry_approx(flag.set = FALSE)
			.self$cluster.noisy.freq <- consistency$enforce_global_consistency()			
		},
		
		set_clique_margin_from_cluster = function() {

			domain <- .self$data$domain
			noisy.freq <- .self$cluster.noisy.freq
			cliques <- .self$jtree$cliques
			ans <- list()
			# the each element in "match_ids" is the index of "cluster" which contains the clique.
			match_ids <- unlist(lapply(seq_along(cliques), function(cid) match_clique_to_cluster(cid)))
			for (i in seq_len(length(cliques))) {
				cl <- .self$cluster[[match_ids[i]]]
				cq <- cliques[[i]]
				# find the domain for each nodes in cluster.
				curr_cl_levels <- lapply(cl, function(x) domain$levels[[x]])
				index <- data.table(do.call(CJ, curr_cl_levels))
				setnames(index, cl)
				cluster.freq.noisy <- noisy.freq[[match_ids[i]]]
				margin.cluster <- cbind(index, cluster.freq.noisy)   

				curr_cq_levels <- lapply(cq, function(x) domain$levels[[x]])

				margin.cluster <- data.table(margin.cluster)
				setkeyv(margin.cluster, cq)
				freq.noisy <- margin.cluster[do.call(CJ, curr_cq_levels)
						, list(Freq=sum(cluster.freq.noisy))
						, allow.cartesian = T, by = .EACHI][, Freq]
				ans[[i]] <- freq.noisy
			}
			.self$cluster.noisy.freq <- ans
		},
		
		match_clique_to_cluster = function(cid) {
			clique <- .self$jtree$cliques[[cid]]
			for (ii in seq_len(length(.self$cluster))) {
				if (all(clique %in% .self$cluster[[ii]])) {
					return(ii)
				}
			}
			return(NULL)
		},
		
		init_potential_data_table = function() {
			cliques.noisy.freq <- .self$cluster.noisy.freq
			cliques<-.self$jtree$cliques
			seps<-.self$jtree$separators
			ans <- vector("list", length(cliques))
			N=.self$data$DB.size
			#t <- data.table(.self$data$origin)
			for (ii in seq_along(cliques)){

				cq  <- cliques[[ii]]
				sp  <- seps[[ii]]
				#setkeyv(t, cq)
				#curr_levels <- lapply(cq, function(x) levels(t[, get(x)]))

				#xxx <- t[do.call(CJ, curr_levels), list(freq = .N), allow.cartesian = T, by = .EACHI]
				xxx <- get_xtab(cq)
				setDT(xxx)
				.self$clique.freq[[ii]] <- get_freq(cq)
		
				if (length(cliques.noisy.freq) > 0) {
					freq.noisy <- cliques.noisy.freq[[ii]]
					xxx[, freq.noisy := freq.noisy]
					f <- as.formula(paste("freq.noisy~", paste(cq, collapse = "+")))
					xxx <- xtabs(formula = f, data = xxx)
				} else {
					f <- as.formula(paste("freq~", paste(cq, collapse = "+")))
					xxx <- xtabs(formula = f, data = xxx)		   
				}
				#ftable(t.cq)
				t.cq <- tableMargin(xxx, cq)
				names(dimnames(t.cq)) <- cq

				if (!is.null(seps) && length(sp) > 0) {
					t.sp	  <- tableMargin(t.cq, sp)
					ans[[ii]] <- tableOp2(t.cq, t.sp, op = `/`)
				} else {
					ans[[ii]] <- t.cq / sum(t.cq)
				}   
			}
			attr(ans, "rip") <-.self$jtree

			if(.self$noise.flag){
				.self$POTlist.consistent <- ans
				class(.self$POTlist.consistent) <- "extractPOT"
			}else{
				.self$POTlist <- ans
				class(.self$POTlist) <- "extractPOT"
			}
		},

		get_model = function() {
			if (.self$noise.flag) {
				curr.grain <- .self$POTgrain.consistent
			}else {
				curr.grain <- .self$POTgrain
			}
			return(curr.grain)
		},
		
		message_passing = function() {
			if(.self$noise.flag == TRUE){
				gin.consistent <- grain(compilePOT(.self$POTlist.consistent))
				.self$POTgrain.consistent <- propagate(compile(gin.consistent))
			}else{
				gin <- grain(compilePOT(.self$POTlist))
				.self$POTgrain <- propagate(compile(gin))
			}
		},
		
		simulate = function(flag.consistent=TRUE) {
			if (.self$noise.flag) {
				curr.grain <- .self$POTgrain.consistent
			}else {
				curr.grain <- .self$POTgrain
			}
			num.of.syn <- .self$data$DB.size
			if(is.null(curr.grain)) stop("POTgrain is not provided yet")
			data.sim <- simulate.grain(curr.grain, num.of.syn)
			return(data.sim)
		},

		get_xtab = function(clique){
			keyname <- convert2keyname(clique)
			hist <- .self$histograms[[keyname]]
			return(hist)
		},

		get_freq = function(clique){
			hist <- get_xtab(clique)
			freq <- as.vector(hist$freq)
			return(freq)
		},

		convert2keyname = function(clique){
			clique = sort(clique)
			return(paste(clique, collapse='_'))
		}
	)
)

do_inference <- function(r_script_dir, cluster, jtree_path, epsilon, histograms, domain){

	source(paste(r_script_dir, 'data.R', sep='/'))
	source(paste(r_script_dir, 'consistency.R', sep='/'))
	source(paste(r_script_dir, 'time_measure.R', sep='/'))
	
	inference <- Inference$new(
		cluster, 
		jtree_path, 
		histograms,
		domain, 
		epsilon = epsilon, 
		noise.flag = TRUE
	)
	tm <- TimeMeasure$new("Inference")

	tm$start("Noises Injection")
	inference$inject_noise()
	tm$check()
	
	tm$start("Marginals Consistency")
	inference$consistency()
	inference$set_clique_margin_from_cluster()
	tm$check()

	tm$start("Data Model Initialize")
	inference$init_potential_data_table()
	inference$message_passing()
	tm$check()
	
	return(inference$get_model())
	
}

do_inference_without_noise <- function(r_script_dir, cluster, jtree_path, histograms, domain){

	source(paste(r_script_dir, 'data.R', sep='/'))
	source(paste(r_script_dir, 'consistency.R', sep='/'))
	source(paste(r_script_dir, 'time_measure.R', sep='/'))
	
	inference <- Inference$new(
		cluster, 
		jtree_path, 
		histograms, 
		domain, 
		noise.flag = FALSE
	)
	inference$init_potential_data_table()
	inference$message_passing()
	return(inference$get_model())
	
}
