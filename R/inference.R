source('data.R')
source('consistent.R')
source('jtree.R')
Inference <- setRefClass(
	"Inference",
	
	fields = list(
		cluster = 'list',
		epsilon = 'numeric',
		data = "ANY",
		cluster.noisy.freq = "ANY",
		jtree = "ANY",
		clique.freq = "list",
		POTlist.consistent = "ANY"
	),
	
	methods = list(
		initialize <- function(cluster, edges, nodes, epsilon, data_path, domain){
			.self$cluster <- cluster
			.self$epsilon <- epsilon
			.self$data <- Data$new(data_path, domain)
			.self$jtree <- get_jtree(edges, nodes, display=FALSE)
		},
		
		inject_noise <- function(){
			t <- data.table(.self$data)
			margin.noisy.freq <- list()
			sen <- 1
			num.margins<-length(margins)
			b <- 2 * (num.margins) * sen / epsilon
			Lap <- DExp(rate = 1 / b)
			for (i in seq_len(length(margins))) {
				cq <- margins[[i]]
				setkeyv(t, cq)
				curr_levels <- lapply(cq, function(x) levels(t[, get(x)]))
        
				xxx <- t[do.call(CJ, curr_levels), list(freq = .N), allow.cartesian = T, by = .EACHI][, freq]
				noises <- r(Lap)(length(xxx))
				freq.noisy <- xxx + noises				
				margin.noisy.freq[[i]] <- freq.noisy
			}
			.self$cluster.noisy.freq <- margin.noisy.freq
		},

		consistency <- function(){
			consistency <- ConsistentMargin$new(.self$data$DB.size, .self$cluster, .self$data$domain, .self$cluster.noisy.freq)
			.self$cluster.noisy.freq <- consistency$fix_negative_entry_approx(flag.set = FALSE)
			.self$cluster.noisy.freq <- consistency$enforce_global_consistency()			
		},
		
		set_clique_margin_from_cluster = function() {
			t <- data.table(.self$data)
			domain <- .self$data$domain
			noisy.freq <- .self$cluster.noisy.freq
			cliques <- .self$jtree$cliques
			ans <- list()
			match_ids <- unlist(lapply(seq_along(cliques), function(cid) match_clique_to_cluster(cid)))
			for (i in seq_len(length(cliques))) {
				cl <- .self$cluster[[match_ids[i]]]
				cq <- cliques[[i]]
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
			clique.noisy.freq <- .self$clique.noisy.freq
			cliques<-.self$jtree$cliques
			seps<-.self$jtree$separators
			ans <- vector("list", length(cliques))
			N=.self$data$DB.size
			t <- data.table(data)
			for (ii in seq_along(cliques)){

				cq  <- cliques[[ii]]
				sp  <- seps[[ii]]
				setkeyv(t, cq)
				curr_levels <- lapply(cq, function(x) levels(t[, get(x)]))

				xxx <- t[do.call(CJ, curr_levels), list(freq = .N), allow.cartesian = T, by = .EACHI]
        
				.self$clique.freq[[ii]] <- xxx[, freq]
        
				if (length(clique.noisy.freq) > 0) {
					freq.noisy <- clique.noisy.freq[[ii]]
					xxx[, freq.noisy := freq.noisy]
					# print(xxx)
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
					t.sp      <- tableMargin(t.cq, sp)
					ans[[ii]] <- tableOp2(t.cq, t.sp, op = `/`)
				} else {
					ans[[ii]] <- t.cq / sum(t.cq)
				}   
			}
			attr(ans, "rip") <-.self$jtree
		
			.self$POTlist.consistent <- ans 
			class(.self$POTlist.consistent) <- "extractPOT"
		},
		
		message_passing = function() {
			gin.consistent <- grain(compilePOT(.self$POTlist.consistent))
			.self$POTgrain.consistent <- propagate(compile(gin.consistent))      
		},
		
		simulate = function(num.of.syn, flag.consistent=TRUE) {
			curr.grain <- .self$POTgrain.consistent
			if(is.null(curr.grain)) stop("POTgrain is not provided yet")
			data.sim <- simulate.grain(curr.grain, num.of.syn)
			return(data.sim)
		}
	)
)