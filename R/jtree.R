get_jtree <- function(edges, nodes, display=TRUE){
	library(gRain)
	library(graph)

    depgraph <- ugList(edges)
    depgraph <- addNode(setdiff(nodes,nodes(depgraph)), depgraph)
    depgraph <- triangulate(depgraph)
    jtree <- jTree(depgraph)
    if(display){
	  return(jtree$cliques)
    }
    return(jtree)
}
