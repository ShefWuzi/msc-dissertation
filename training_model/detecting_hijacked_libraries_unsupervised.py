import random, sys
from collections import Counter
import numpy as np

if len(sys.argv) != 2:
	print("[*] Usage: %s <commit_csv>")
	sys.exit(0)


class KMeans:
	def __init__(self, dataset, K=2):
		self.centroids = []
		
		self.dataset = dataset
		self.K = K

		while len(self.centroids) != K:
			z = random.choice(self.dataset)
			if z not in self.centroids:
				self.centroids.append(z)

	def circular_dist(self, data_v, centroid_v, type):
		dow = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
		hod = [x for x in range(24)]
		moh = [x for x in range(60)]

		if type == "day":
			data_i = dow.index(data_v)
			centroid_i = dow.index(centroid_v)

			if data_i == centroid_i: return 0

			return min(abs(data_i-centroid_i), data_i+(len(dow)-centroid_i) if data_i < centroid_i else centroid_i+(len(dow) - data_i))

		elif type == "hour":
			data_i = hod.index(data_v)
			centroid_i = hod.index(centroid_v)

			if data_i == centroid_i: return 0

			return min(abs(data_i-centroid_i), data_i+(len(hod)-centroid_i) if data_i < centroid_i else centroid_i+(len(hod) - data_i))

		elif type == "minute":
			data_i = moh.index(data_v)
			centroid_i = moh.index(centroid_v)

			if data_i == centroid_i: return 0

			return min(abs(data_i-centroid_i), data_i+(len(moh)-centroid_i) if data_i < centroid_i else centroid_i+(len(moh) - data_i))


	def categorical_mean(self, data):
		data_c = Counter(data)
		data_m = np.mean(list(data_c.values()))

		#Find category with closest value to mean
		c_m = []
		for v in data_c.values():
			c_m.append(abs(data_m-v))

		return list(data_c.keys())[min(enumerate(c_m), key=lambda c:c[1])[0]]


	def compute_centroid(self, cluster):
		author_mean = self.categorical_mean([x[0] for x in cluster])
		dow_mean = self.categorical_mean([x[1] for x in cluster])
		hod_mean = self.categorical_mean([x[2] for x in cluster])
		moh_mean = self.categorical_mean([x[3] for x in cluster])

		n_rf = [int(x[4]) for x in cluster]
		n_af = [int(x[5]) for x in cluster]
		n_ef = [int(x[6]) for x in cluster]
		a_eb = [int(x[7]) for x in cluster]

		return [author_mean, dow_mean, hod_mean, moh_mean, np.mean(n_rf), np.mean(n_af), np.mean(n_ef), np.mean(a_eb)]

	def fit(self):
		temp_clusters = []
		clusters = [[] for i in range(self.K)]
		while clusters != temp_clusters:
			temp_clusters = clusters
			for data in self.dataset:
				dist_c = []
				for i,centroid in enumerate(self.centroids):
					if len(centroid) == 0 or len(data) == 0: continue	

					dist_c.append(0 if data[0] == centroid[0] else 1 + self.circular_dist(data[1], centroid[1], "day") + self.circular_dist(int(data[2]), int(centroid[2]), "hour") + self.circular_dist(int(data[3]), int(centroid[3]), "minute") + sum([abs(int(centroid[x]) - int(data[x])) for x in range(4, len(centroid))]))

				#Assign data to cluster with minimum distance
				if len(dist_c) == 0: continue
				c_id = min(enumerate(dist_c), key=lambda z:z[1])[0]
				clusters[c_id].append(data)

			#Computer new cluster means
			for i,c in enumerate(clusters):
				self.centroids[i] = self.compute_centroid(c) if len(c) > 0 else []

		return clusters



def standard_deviation(cluster):
	author_d = list(Counter([x[0] for x in cluster]).values())
	dow_d = list(Counter([x[1] for x in cluster]).values())
	hod_d = list(Counter([x[2] for x in cluster]).values())
	moh_d = list(Counter([x[3] for x in cluster]).values())

	rf_d = [int(x[4]) for x in cluster]
	af_d = [int(x[5]) for x in cluster]
	ef_d = [int(x[6]) for x in cluster]
	eb_d = [int(x[7]) for x in cluster]


	all_stds = [np.std(author_d), np.std(dow_d), np.std(hod_d), np.std(moh_d), np.std(rf_d), np.std(af_d), np.std(ef_d), np.std(eb_d)]
	return random.choice([abs((x-np.mean(all_stds))/np.std(all_stds)) for x in all_stds])
	


relevant_cols = ["Author_Name", "Commit_Date_DOW", "Commit_Date_HOD", "Commit_Date_MOH", "Number of Removed Files", "Number of Added Files", "Number of Edited Files", "Amount of edit bytes"]
dataset = []

read_header = False
with open(sys.argv[1], "r") as f:
    for line in f.readlines():
        if not read_header:
            relevant_indexes = [i for i,x in enumerate(line.split(",")) if x.strip() in relevant_cols]
            read_header = True
        else:
            dataset.append([z for j,z in enumerate(line.split(",")) if j in relevant_indexes])

f_clusters = []
c_clusters = [dataset]

while len(c_clusters) > 0:
# for i in range(5):
	c_cluster = c_clusters.pop(0)

	kmeans = KMeans(c_cluster, 5)
	k_clusters = kmeans.fit()

	for k, cluster in enumerate(k_clusters):
		if len(cluster) == 0: continue
		std_c = standard_deviation(cluster)
		print(std_c)
		if std_c <= 0.4:
			f_clusters.append(cluster)
		else:
			c_clusters.append(cluster)

# print([x for x in f_clusters], end="\n===================================\n")
# cs = KMeans(dataset, 5).fit()
# for c in cs:
# 	print(c, end="=======================================\n")
