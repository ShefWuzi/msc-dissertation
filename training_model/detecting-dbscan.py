import sys
from collections import Counter
import numpy as np

if len(sys.argv) != 2:
	print("[x] Usage: %s <data_file>" %sys.argv[0])
	sys.exit(0)



class DBSCAN:
	def __init__(self, D, eps, MinPts=3):
		self.D = D
		self.eps = eps
		self.MinPts = MinPts
		self.clusters = []

	def regionQuery(self, P, eps):
		eps_neighborhood = [P]
		for P_ in self.D:
			if P == P_:continue

			P_d = P["data"]
			P__d = P_["data"]
			eps_check = [P_d[0] == P__d[0], P_d[1] == P__d[1], P__d[2] in [x if x < 24 else x-24 for x in range(P_d[2], P_d[2]+eps[0])], P__d[3] in [x if x < 60 else x-60 for x in range(P_d[3], P_d[3]+eps[1])], abs(P_d[4]-P__d[4]) < (10*eps[2]), abs(P__d[5]-P_d[5]) < (10*eps[3]), abs(P__d[6] - P_d[6]) < (10*eps[4]), abs(P__d[7]-P_d[7]) < (10*eps[5])]

			if Counter(eps_check[1:])[True] > 6:
				eps_neighborhood.append(P_)

		return eps_neighborhood

	def expandCluster(self, P, NeighborPts, cluster, eps, MinPts):
		cluster.append(P)
		D[P["id"]]["cluster"] = len(self.clusters)

		for P_ in NeighborPts:
			if not P_["visited"]:
				self.D[P_["id"]]["visited"], P_["visited"] = True, True
				NeighborPts_ = self.regionQuery(P_, eps)
				if len(NeighborPts_) >= MinPts:
					NeighborPts.extend(NeighborPts_)

			if P_["cluster"] is None:
				self.D[P_["id"]]["cluster"], P_["cluster"] = len(self.clusters), len(self.clusters)
				cluster.append(P_)
		self.clusters.append(cluster)

	#eps[hod+2, moh+10, n_r_std, n_a_std, n_e_std, n_e_l_std]
	def fit_transform(self):
		for P in self.D:
			if P["visited"]: continue

			self.D[P["id"]]["visited"] = True
			NeighborPts = self.regionQuery(P, self.eps)
			if len(NeighborPts) < self.MinPts:
				self.D[P["id"]]["type"] = "N"
			else:
				self.expandCluster(P, NeighborPts, [], self.eps, self.MinPts)


#[author_name, dow, hod, moh, n_removed, n_added, n_edit, n_edit_l, malicious]
D, n_r, n_a, n_e, n_e_l, no_malicious = [], [], [], [], [], 0
with open(sys.argv[1], "r") as data_file:
	data_file.readline()
	p_id = 0
	for line in data_file:
		ls = line.split(",")

		if ls[26].strip() == "T": no_malicious += 1

		n_r.append(int(ls[19]))
		n_a.append(int(ls[20]))
		n_e.append(int(ls[21]))
		n_e_l.append(int(ls[22]))

		D.append({"id": p_id, "visited": False, "malicious": True if ls[26].strip() == "T" else False,"cluster": None, "type": None, "data": [x if i < 15 else int(x) for i,x in enumerate(ls) if i in [6, 14, 15, 16, 19, 20, 21, 22]]})
		p_id += 1


# print(D[0], regionQuery(D[0], [2, 10, np.std(n_r), np.std(n_a), np.std(n_e), np.std(n_e_l)]))
dbscan = DBSCAN(D, [3, 20, np.std(n_r), np.std(n_a), np.std(n_e), np.std(n_e_l)], 4)
dbscan.fit_transform()
D = dbscan.D

tp = 0
no_suspicious = 0

for P in D:	
	if P["cluster"] is None: 
		no_suspicious += 1
		if P["malicious"]: tp+=1
		print(P["id"], end=",")

print("\nNumber of suspicious commits: %d" %(no_suspicious))
print("Number of discovered malicious commits: %d" %tp)
print("Precision: %.3f" %(tp/no_suspicious))
print("Recall: %.3f" %(tp/no_malicious))
