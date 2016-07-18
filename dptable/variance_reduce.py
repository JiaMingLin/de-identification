from common.base import Base

import math
import random
import operator
import time
import numpy as np
import cvxpy as cvx

class VarianceReduce(Base):

	def __init__(self, domain, jtree, _lambda=0.2):
		"""
		Using linear programming method to find a less noise variance.
		param:
			domain: the domain of the given data
				(note) the order of columns in domain should be same with the original
			jtree: the structure of junction tree
			_lambda: the balance number.

		TODO:
			1. Move jt_rep to Junction Tree Module
			2. Move Different Operator to a linear algebra package
		"""
		self.LOG = Base.get_logger("CliqueMerge")
		self.domain = domain
		self.node_card = [len(vals) for vals in domain.values()]
		self._lambda = float(_lambda)
		self.max_iter = 20
		self.jtree = jtree
		self.nodes_num = len(self.node_card)
		self.cliques_num = len(jtree)
		self.cnum = range(2, len(jtree)+1) if len(jtree) >=2 else [1]
		self.jtree_in_node_index = [self.find_subset_index(clique) for clique in jtree]

	def main(self, display = True):
		"""
		1. For each specified cluster number, compute the merged junction tree. 
		2. Then compute the total variance for each merged jtree.
		3. Find the minimal total variance and the corresponding jtree.
		param:
			display: specify the returned node in clusters is 
					showed as its name or index.
		"""
		self.LOG.info("Starting to merge cliques...")
		start = time.time()
		cnum = self.cnum
		# Z: Clique-Cluster rep.
		# O: Cliques-Nodes rep.
		# m: The number of cluster
		z_and_o_for_m = [self.marginal_optimization(m) for m in cnum]
		cluster_nodes_for_m = [self.fix_negative_in_jtree_rep(z_and_o[0], z_and_o[1]) for z_and_o in z_and_o_for_m]
		variance_cluster_for_m = [(self.total_variance(cluster_nodes), cluster_nodes) for cluster_nodes in cluster_nodes_for_m]
		sorted_var_cluster = sorted(variance_cluster_for_m, key = operator.itemgetter(0))
		opt_clusters = sorted_var_cluster[0][1]
		end = time.time()
		self.LOG.info("Cliques merge job done in %d seconds." % (end-start))

		if(display == True):
			return [np.array(self.domain.keys())[cluster].tolist() for cluster in opt_clusters]
		return opt_clusters

	def construct_difference(self, m):
		"""
		The construtor of difference operator.
		"""
		M = np.zeros((m,m*(m-1)/2), dtype=int)
		count = 0
		for i in range(m):
			M[i,count:(count+m-i-1)] = 1
			M[i+1:m, count:(count+m-i-1)] = -np.eye(m-i-1)
			count=count+m-i-1;
		return M

	def jt_rep(self):
		"""
		The matrix representation of junction tree
		"""
		jtree_in_node_index = self.jtree_in_node_index
		n = self.cliques_num
		d = self.nodes_num

		O = np.zeros((d,n),dtype=int)
		for i in range(n):
			nodes_indexes = jtree_in_node_index[i]
			O[nodes_indexes, i] = 1
		return O

	def find_subset_index(self, node_subset):
		"""
		For a subset of nodes, extract the index for each node.
		"""
		node_labels = self.domain.keys()
		import collections
		node_reversed_index = collections.OrderedDict(zip(node_labels, range(len(node_labels))))
		return [int(node_reversed_index[node]) for node in node_subset]

	def log_p_func(self):
		"""
		Product of the attributes' domain size in the each clique
		"""
		node_card = self.node_card
		jtree_in_node_index = self.jtree_in_node_index
		log_p_arr = []
		for i in range(len(jtree_in_node_index)):
			# Sum of the log value of each node domain
			value = sum(np.log(list(node_card[k] for k in jtree_in_node_index[i])))
			log_p_arr.append(value)
		return np.asarray(log_p_arr).T

	def marginal_optimization(self, m):
		"""
		Do a marginal optimization
		param:
			m: The specified cluster number
		return: (z, o)
			z: the matrix rep for cliques and clusters
			o: the matrix rep for nodes and cliques
		"""
		self.LOG.debug("Starting to merge marginals")        
		node_card = self.node_card
		jtree_in_node_index = self.jtree_in_node_index
		d = self.nodes_num
		n = self.cliques_num

		# get the junction tree matrix representation: O
		O = self.jt_rep()

		# get log_p is the array of numbers of sum(log(attribute's domain))
		log_p = self.log_p_func()

		# get log_node_card: log(C1), log(C2), ..., log(Cd)
		log_node_card = np.log(node_card)

		# get value of sum_log_node_card: log(C1 * C2 *...* Cd)
		sum_log_node_card = sum(log_node_card)

		# get the difference operator M on cluster number: m
		M = self.construct_difference(m)

		prev_Z = np.random.rand(n,m)

		# run the convex optimization for max_iter times
		self.LOG.debug("Optimization starting...")
		for i in range(self.max_iter):
			self.LOG.debug("The optimization iteration: "+str(i+1))
			# sum of row of prev_Z
			tmp1 = cvx.sum_entries(prev_Z, axis=0).value

			# tmp2 = math.log(tmp1)-1+sum_log_node_card
			tmp2 = np.log(tmp1)-1+sum_log_node_card

			# tmp3: difference of pairwise columns = prev_Z * M
			tmp3 = np.dot(prev_Z,M)
			# convex optimization
			Z = cvx.Variable(n,m)
			t = cvx.Variable(1,m)
			r = cvx.Variable()

			objective = cvx.Minimize(cvx.log_sum_exp(t)-self._lambda*r)
			constraints = [
				Z >= 0,
				Z*np.ones((m,1),dtype=int) == np.ones((n,1), dtype=int),
				r*np.ones((1,m*(m-1)/2), dtype=int) - 2*np.ones((1,n), dtype=int)*(cvx.mul_elemwise(tmp3, (Z*M))) + cvx.sum_entries(tmp3 * tmp3, axis=0) <= 0,
				np.ones((1,n),dtype=int)*Z >= 1,
				log_p*Z-t-np.dot(log_node_card,O)*Z+tmp2+cvx.mul_elemwise(np.power(tmp1,-1), np.ones((1,n), dtype = int)*Z) == 0
			]
			prob = cvx.Problem(objective, constraints)
			result = prob.solve(solver='SCS',verbose=False)
			prev_Z[0:n,0:m] = Z.value

		return (prev_Z, O)

	def fix_negative_in_jtree_rep(self, Z, O):
		"""
		Using the Clique-Cluster rep. and Cliques-Nodes rep. 
		Compute the Cluster-Nodes result.
		param:
			Z: Clique-Cluster rep.
			O: Cliques-Nodes rep.
		"""
		self.LOG.debug("Generating results...")
		# find the index of max element in each row of Z
		index = map(lambda row: row.tolist().index(max(row)), Z) 
		# get the row length of Z, i.e. the number of cluster
		m = len(Z[0])

		cluster_ls = []

		for icols in range(m):
			tmp_index = [i for i, j in enumerate(index) if j == icols]
			if tmp_index is not None and len(tmp_index) != 0:
				tmp = np.sum(O[:,tmp_index],axis=1)
				cluster_ls.append([i for i, j in enumerate(tmp) if j > 0])

		return cluster_ls

	def clique_domain_size(self, given_cliques):
		node_card = self.node_card
		size_prod = dict()
		for k in range(len(given_cliques)):
			c = given_cliques[k]
			attr_domains = [node_card[i] for i in c]
			size_prod[k] = np.prod(attr_domains)
		return size_prod

	def total_variance(self, new_clusters):
		"""
		Fir the given cluster, calculate the total variance of Laplace Distribution.
		param:
			new_clusters: a junctioin tree in merged cluster.
		"""
		node_card = self.node_card
		size_prod = self.clique_domain_size(new_clusters)
		clusters_num = len(new_clusters[0])
		return 2 * (clusters_num)**2 * sum(size_prod.values())
