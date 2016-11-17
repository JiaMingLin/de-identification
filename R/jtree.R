get_jtree <- function(edges, nodes, jtree_path, display=TRUE){
	jtreepy <- list()
	if(length(edges) == 0){
		jtreepy <- gen_psudo_tree(nodes)
		save_jtree(jtreepy, jtree_path)
		return(jtreepy)
	}

	depgraph <- ugList(edges)
	depgraph <- addNode(setdiff(nodes,nodes(depgraph)), depgraph)
	depgraph <- triangulate(depgraph)
	jtree <- jTree(depgraph)
	save_jtree(jtree, jtree_path)
	
	# convert to python readable format
	jtreepy$cliques <- jtree$cliques
	jtreepy$separators <- jtree$separators
	jtreepy$parents <- jtree$parents
	return(jtreepy)
}

save_jtree <- function(jtree, path){
	if(nchar(path)>1){
		saveRDS(jtree, file=path)	
	}
}

gen_psudo_tree <- function(nodes){
	tree <- list()
	tree$cliques <- nodes
	tree$separators <- lapply(1:length(nodes), function(x) character(0))
	tree$parents <- sapply(1:length(nodes), function(x) 0)
	return(tree)
}
