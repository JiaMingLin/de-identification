from common.base import Base
import rpy2.robjects as ro
class Inference(Base):
	def __init__(self, data_path, edges, nodes, domain, cluster, epsilon):
	"""
	Initialize the inference class.
	TODO: 1. refactor, the data_path, edges, nodes, domain 
			are temporary to be here.
	param
		data_path: the path of data file.
	param
		edges: the edges in dependency graph.
	param
		nodes: the nodes(attributes) in data set.
	param
		domain: data information with format in dictionary
		{
			"name":"data name",
			"dsize":{
				"A": <DOMAIN SIZE OF A>,
				"B": <DOMAIN SIZE OF B>,
				...
			},
			"levels":{
				"A": [1,2,3,4,5],
				"B": [4,5,6,8,9],
				...
			}
		}
	param
		cluster: the merged cluster structure
	param
		epsilon: the privacy budget
	"""
	