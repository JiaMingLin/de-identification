library(gRain)
library(graph)
get_jtree = function(edges, nodes, display=TRUE){
    depgraph <- ugList(edges)
    depgraph <- addNode(setdiff(nodes,nodes(depgraph)), depgraph)
    depgraph <- triangulate(depgraph)
    jtree <- jTree(depgraph)
    if(display){
	  return(jtree$cliques)
    }
    return(jtree)
}
