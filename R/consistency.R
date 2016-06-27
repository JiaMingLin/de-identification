ConsistentMargin <- setRefClass (
  "Consistent Marginal",
  fields = list(
    N = "numeric",
    cliques = "ANY",
    domain = "ANY", #POTgrain, graphical model
    all.attrs = "vector",
    register = "ANY",
    clique.noisy.freq = "ANY",
    debug = "logical"
  ),
  methods = list(
    initialize = function(N, cliques, domain
                          , clique.noisy.freq, flag.debug = FALSE) {
      .self$N <- N
      .self$cliques <- cliques
      names(.self$cliques) <- paste('C', seq(length(.self$cliques)), sep = "")
      .self$domain <- domain
      .self$all.attrs <- domain$name
      .self$clique.noisy.freq <- clique.noisy.freq
      names(.self$clique.noisy.freq) <- names(.self$cliques)
      .self$debug <- flag.debug
    },
    ##########################################################################
    fix_negative_entry_approx = function(flag.set = TRUE) {
      curr.freq.list <- .self$clique.noisy.freq
      for (i in seq_along(curr.freq.list)) {
        if (length(which(curr.freq.list[[i]] > 0)) > 0) {
          margin.noisy <- curr.freq.list[[i]]
          margin.sorted <- sort.int(margin.noisy, index.return = TRUE
                                    , decreasing = TRUE)
          margin.sorted.pos <- margin.sorted$x[which(margin.sorted$x > 0)]
          if (length(margin.sorted.pos) > 0) {
            margin.cum <- cumsum(margin.sorted.pos)
            dist <- abs(.self$N - margin.cum)
            cut.pos <- which(dist == min(dist))
            idx <- margin.sorted$ix[1: cut.pos]       
            margin.noisy[-idx] <- 0
            curr.freq.list[[i]] <- margin.noisy        
          } else {
            #all are negative values
            expected <- .self$N / length(curr.freq.list[[i]])
            curr.freq.list[[i]] <- rep(expected, length(curr.freq.list[[i]]))
          }
          
        }
      }
      if (flag.set) {
        .self$clique.noisy.freq <- curr.freq.list
      }
      return(curr.freq.list)  
    },
    enforce_mutual_consistency = function() {
#       browser()
      #Step 1: enforce same counts in each marginal
      for (cname in .self$domain$name) {
        .self$clique.noisy.freq[[cname]] <- .self$clique.noisy.freq[[cname]] /
          sum(.self$clique.noisy.freq[[cname]]) * .self$N
      }
      #record attr-clique appearance
      register_attr_to_clique()
      #keep clique names consistent
      uni<-unique(.self$register)
      if (ncol(uni) > 1) {
        attr.group.key <- uni[do.call(order, uni),]
        consist.order <- get_consistency_order(attr.group.key)
        # print(consist.order)
        
        #Step 2: enforce mutual consistency
        for (i in seq_along(consist.order$seq)) {
          attr.intersect <- consist.order$seq[[i]]
          cq.names <- consist.order$cliques[[i]]
          single.obs <- list()
          weights <- list()
          for (cname in cq.names) {
            #         if (.self$debug) browser()
            cq.attrs <- .self$cliques[[cname]]
            freq.noisy <- .self$clique.noisy.freq[[cname]]
            clique.margin <- .self$compose_noisy_clique_margin_data_table(cname, freq.noisy)
            single.obs[[cname]] <- project_in_clique_margin_data_table(clique.margin
                                                                       , attr.intersect)
            attr.remain <- cq.attrs[! cq.attrs %in% attr.intersect]
            dsize.remain <- sapply(attr.remain, function(x) get_dsize(x))
            weights[[cname]] <- prod(unlist(dsize.remain))
          }   
          avg <- inverse_var_weighting(single.obs,weights)
          for (cname in cq.names) {
            weight <- weights[[cname]]
            cq.attrs <- .self$cliques[[cname]]
            freq.noisy <- .self$clique.noisy.freq[[cname]]
            margin.xxx <- compose_noisy_clique_margin_data_table(cname, freq.noisy)
            #plyr::join(x,y,by=) keep the order of x, and avg don't use merge, it does not keep the order    
            xxx <- plyr::join(margin.xxx,avg, by = attr.intersect)
            #merge each single obs
            curr.obs <- single.obs[[cname]]
            setnames(curr.obs, 'Freq', 'single.obs')  #rename
            xxx <- plyr::join(xxx, curr.obs, by = attr.intersect)
            consist.freq <- xxx$freq.noisy+(xxx$avg-xxx$single.obs) / weight
            .self$clique.noisy.freq[[cname]] <- consist.freq   
          }  
        }
        
        
      }
      return(.self$clique.noisy.freq)
    },
    register_attr_to_clique = function(){
      curr.register <- data.frame(setNames(replicate(length(.self$cliques)
                                                   ,logical(0), simplify = FALSE)
                                    , paste('C'
                                            , seq(length(.self$cliques))
                                            , sep = ""))
      ) 
      for (attr in .self$all.attrs) {
        row<-sapply(.self$cliques, function(x) attr %in% x)
        curr.register[nrow(curr.register)+1, ] <- row
      }
      row.names(curr.register) <- .self$all.attrs
      .self$register <- curr.register
    },
    get_consistency_order = function(attr.group.key){
      #match 
      base.seq<-list()
      consist.seq<-list()
      overlap.clq<-list()
      count<-1
      for (i in seq_len(nrow(attr.group.key))) {
        key<-attr.group.key[i, ]
        if (length(which(key == TRUE)) >= 2) {
          index.match <- which(apply(mapply(.self$register, key, FUN="==")
                                     , MARGIN=1, FUN=all))
          base.seq[[count]]<-sort(.self$all.attrs[index.match]) 
          overlap.clq[[count]]<-colnames(attr.group.key)[which(key==TRUE)]
          count<-count+1
        }
      }
      consist.seq<-base.seq
      
      
      while (length(base.seq) > 1) {
        #print(base.seq)
        subset.cands <- combn(base.seq, 2)
        #which(apply(sapply(colnames(register), function(x) {key==register[,x]}), MARGIN=2, FUN=all))
        overlap.subset <- apply(subset.cands, 2
                              , function(x){
                                index<-unique(unlist(x))
                                match<-colnames(register)[apply(register[index, ]
                                                                , 2, FUN=all)]
                                return(match)
                              })
        if (length(overlap.subset) > 0) {
          match.index<-which(sapply(overlap.subset, function(x) length(x) >= 2))
        }else{
          match.index <- character(0)
        }
          
          if (length(match.index) > 0) {
            cands <- apply(as.matrix(subset.cands[, match.index]), 2, try(as.list))
            cand.seq <- lapply(cands, function(x) sort(unique(unlist(x))))     
            base.seq <- setdiff(cand.seq, consist.seq)
            cand.overlap <- overlap.subset[match.index[match(base.seq, cand.seq)]]
            consist.seq <- append(consist.seq, base.seq) 
            overlap.clq <- append(overlap.clq, cand.overlap)
            
            
          }else{
            base.seq <- list()
          }
          
          
      
        
        
      }
      #debug check partial order
      #   for(i in 1:(length(consist.seq)-1)){
      #     curr.subset<-consist.seq[[i]]
      #     xxx=lapply(consist.seq[(i+1):length(consist.seq)], function(x) all(x %in% curr.subset))
      #     if(any(unlist(xxx))){
      #       print(i)
      #       print(curr.subset)
      #     }
      #     print(any(unlist(xxx)))
      #   }
      ans<-list()
      ans$seq <- consist.seq
      ans$cliques<-overlap.clq
      return(ans)
    },
    
    compose_noisy_clique_margin_data_table = function(cname, freq.noisy){
      cq <- .self$cliques[[cname]]
      curr_levels = lapply(cq, function(x) .self$domain$levels[[x]])
      # omit "by = .EACHI" in data.table <= 1.9.2
      #t[CJ(levels(A1), levels(A2), levels(A3), .N, allow.cartesian = T, by = .EACHI]
      index <- data.table(do.call(CJ, curr_levels))
      setnames(index, cq)
      margin.xxx <- cbind(index, freq.noisy)
      return(margin.xxx)
    },
    project_in_clique_margin_data_table = function(clique.margin, attr.subset) {
      t <- data.table(clique.margin)
      cq <- attr.subset
      setkeyv(t, cq)
      curr_levels = lapply(cq, function(x) .self$domain$levels[[x]])
      # omit "by = .EACHI" in data.table <= 1.9.2
      #t[CJ(levels(A1), levels(A2), levels(A3), .N, allow.cartesian = T, by = .EACHI]
      margin.xxx <- t[do.call(CJ, curr_levels)
                      , list(Freq=sum(freq.noisy)), allow.cartesian = T, by = .EACHI]
      return(margin.xxx)  
    },
    
    get_dsize = function(attr.name){
      return(.self$domain$dsize[which(.self$domain$name == attr.name)])
    },
    
    inverse_var_weighting = function(single.obs, weights){
      numerators <- sapply(names(single.obs), function(x) {single.obs[[x]]$Freq / weights[[x]]} )
      denominator <- sum(unlist(sapply(weights, function(x) {1 / x})))
      avg <- rowSums(numerators) / denominator
      ans <- single.obs[[1]]
      ans$Freq <- NULL
      ans[, "avg"] <- avg
      return(ans)
    },

    enforce_global_consistency = function(){
      nattempt <- 1
      ii = 1
      while (ii <= nattempt) {
        cat("enforce consistency attempt:", ii, "\n")
        fix_negative_entry_approx(flag.set = TRUE)
        enforce_mutual_consistency()
        ii <- ii + 1
      }  
      if (!is_all_positive()) {
        fix_negative_entry_approx(flag.set = TRUE)
      }
      
      return(.self$clique.noisy.freq)
    },
    
    is_all_positive = function() {
      neg.elem <- which(unlist(.self$clique.noisy.freq, use.names = FALSE) < 0)
      if (length(neg.elem) > 0) {
        return(FALSE)
      } else {
        return(TRUE)
      }
    } 
    
    )
  
  
  )
