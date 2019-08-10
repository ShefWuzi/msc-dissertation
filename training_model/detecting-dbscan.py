import random, sys
from collections import Counter
import numpy as np

if len(sys.argv) != 2:
	print("[x] Usage: %s <data_file>" %sys.argv[0])
	sys.exit(0)


def regionQuery(P, eps):
	global D

	eps_neighborhood = [P]
	for P_ in D:
		if P == P_:continue

		P_d = P["data"]
		P__d = P_["data"]
		eps_check = [P_d[0] == P__d[0], P_d[1] == P__d[1], P__d[2] in [x if x < 24 else x-24 for x in range(P_d[2], P_d[2]+eps[0])], P__d[3] in [x if x < 60 else x-60 for x in range(P_d[3], P_d[3]+eps[1])], abs(P_d[4]-P__d[4]) < (2*eps[2]), abs(P__d[5]-P_d[5]) < (2*eps[3]), abs(P__d[6] - P_d[6]) < (2*eps[4]), abs(P__d[7]-P_d[7]) < (2*eps[5])]

		if Counter(eps_check[1:])[True] > 6:
			eps_neighborhood.append(P_)

	return eps_neighborhood

def expandCluster(P, NeighborPts, cluster, eps, MinPts):
	global D
	global clusters

	cluster.append(P)
	D[P["id"]]["cluster"] = len(clusters)

	for P_ in NeighborPts:
		if not P_["visited"]:
			D[P_["id"]]["visited"], P_["visited"] = True, True
			NeighborPts_ = regionQuery(P_, eps)
			if len(NeighborPts_) >= MinPts:
				NeighborPts.extend(NeighborPts_)

		if P_["cluster"] is None:
			D[P_["id"]]["cluster"], P_["cluster"] = len(clusters), len(clusters)
			cluster.append(P_)
	clusters.append(cluster)

#eps[hod+2, moh+10, n_r_std, n_a_std, n_e_std, n_e_l_std]
def DBSCAN(eps, MinPts=3):
	global D
	global clusters

	for P in D:
		if P["visited"]: continue

		D[P["id"]]["visited"] = True
		NeighborPts = regionQuery(P, eps)
		if len(NeighborPts) < MinPts:
			D[P["id"]]["type"] = "N"
		else:
			expandCluster(P, NeighborPts, [], eps, MinPts)

			



#[author_name, dow, hod, moh, n_removed, n_added, n_edit, n_edit_l]
D, n_r, n_a, n_e, n_e_l, clusters = [], [], [], [], [], []
with open(sys.argv[1], "r") as data_file:
	data_file.readline()
	p_id = 0
	for line in data_file:
		ls = line.split(",")

		n_r.append(int(ls[18]))
		n_a.append(int(ls[19]))
		n_e.append(int(ls[20]))
		n_e_l.append(int(ls[21]))

		D.append({"id": p_id, "visited": False, "cluster": None, "type": None, "data": [x if i < 15 else int(x) for i,x in enumerate(ls) if i in [6, 14, 15, 16, 18, 19, 20, 21]]})
		p_id += 1

# print(D[0], regionQuery(D[0], [2, 10, np.std(n_r), np.std(n_a), np.std(n_e), np.std(n_e_l)]))
DBSCAN([3, 20, np.std(n_r), np.std(n_a), np.std(n_e), np.std(n_e_l)], 4)

for P in D:
	if P["cluster"] is None: 
		print(P)
print("\n\n\n")
print(len(clusters))
