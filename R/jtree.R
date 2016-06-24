library(gRain)
library(graph)
get_jtree = function(edges, nodes){
    depgraph <- ugList(edges)
    depgraph <- addNode(setdiff(nodes,nodes(depgraph)), depgraph)
    depgraph <- triangulate(depgraph)
    jtree <- jTree(depgraph)
    return(jtree$cliques)
}
