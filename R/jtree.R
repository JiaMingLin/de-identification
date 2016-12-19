get_jtree <- function(edges, nodes, jtree_path, display=TRUE){
	depgraph <- ugList(edges)
	depgraph <- addNode(setdiff(nodes,nodes(depgraph)), depgraph)
	depgraph <- triangulate(depgraph)
	jtree <- jTree(depgraph)

	if(nchar(jtree_path)>1){
		saveRDS(jtree, file=jtree_path)	
	}
	# convert to python readable format
	jtreepy <- list()
	jtreepy$cliques <- jtree$cliques
	jtreepy$separators <- jtree$separators
	jtreepy$parents <- jtree$parents
	return(jtreepy)
}
