simulate <- function(curr.grain, size) {
	library(gRain)
	data.sim <- simulate.grain(curr.grain, size)
	return(data.sim)
}