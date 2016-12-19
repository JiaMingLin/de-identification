Simulate <- setRefClass(
	"Simulate",
	method = list(
		simulate = function(curr.grain, size){
			data.sim <- simulate.grain(curr.grain, size)
			return(data.sim)
		}
	)
)

simulate <- function(curr.grain, size) {
	library(gRain)
	data.sim <- simulate.grain(curr.grain, size)
	return(data.sim)
}
