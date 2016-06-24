from common.base import Base
import math
import random
import operator
import time
import numpy as np
import cvxpy as cvx

class VarianceReduce(Base):
    def __init__(self, domain, jtree, cnum, _lambda):
		"""
		Using linear programming method to find a less noise variance.
		param:
			domain: the domain of the given data
				(note) the order of columns in domain should be same with the original
			jtree: the structure of junction tree
			cnum: the list of cluster numbers will merge to.
			_lambda: the balance number.
		"""
    	self.domain = domain
    	self.node_card = [len(vals) for vals in domain.values()]
		self._lambda = float(_lambda)
		self.output_file = output_file
		self.max_iter = 20

		self.nodes_num = len(self.node_card)
		self.cliques_num = len(self.cliques)
		self.cnum = cnum
		
	def main(self):
		"""
		1. For each specified cluster number, compute the merged junction tree.
		2. Then compute the total variance for each merged jtree.
		3. Find the minimal total variance and the corresponding jtree.
		"""
		cnum = self.cnum
		merged_jtrees = [ marginal_optimization(m) for m in cnum]
	
	def compute_best(self):
		"""
		For all the merged junction tree, 
		select the one with minimal variance.
		"""
		pass
		
		
	
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
		cliques = self.cliques
		n = self.cliques_num
		d = self.nodes_num

		O = np.zeros((d,n),dtype=int)
		for i in range(n):
			O[cliques[i], i] = 1

		return O

    def log_p_func(self):
		"""
		Product of the attributes' domain size in the each clique
		"""
        node_card = self.node_card
        cliques = self.cliques
        log_p_arr = []
        for i in range(len(cliques)):
            value = sum(np.log(list(node_card[k] for k in cliques[i])))
            log_p_arr.append(value)
        return np.asarray(log_p_arr).T
	
	def marginal_optimization(self, m):
		"""
		Do a marginal optimization
		param:
			m: The specified cluster number
		"""
		logging.debug("Starting to merge marginals")        
		node_card = self.node_card
		cliques = self.cliques
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
        M = self.construct_difference()
        # initial a seed Z
		prev_Z = seed
		if prev_Z is None:
			prev_Z = np.random.rand(n,m)        
    
		# run the convex optimization for max_iter times
		logging.debug("Optimization starting...")
		for i in range(self.max_iter):
			logging.debug("The optimization iteration: "+str(i+1))
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
