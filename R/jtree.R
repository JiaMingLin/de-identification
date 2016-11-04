get_jtree <- function(edges, nodes, jtree_path, display=TRUE){
	
	jtreepy <- list()
	if(length(edges) == 0){
		jtreepy$cliques <- nodes
		jtreepy$separators <- list()
		jtreepy$parents <- list()

		save_jtree(jtreepy)
		return(jtreepy, jtree_path)
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
