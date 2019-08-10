#Based on research with DOI - 10.1145/2597073.2597112

from similarity.jarowinkler import JaroWinkler #https://github.com/luozhouyang/python-string-similarity
import re, collections
import sys

if len(sys.argv) != 2:
	print("[x] Usage: python %s <text_data_file>" %sys.argv[0])
	sys.exit(0)

class Heuristics:

	def __init__(self, similarity_threshold=0.75, line_threshold=0.75):
		self.similarity_threshold = similarity_threshold
		self.line_threshold = line_threshold

	#check keywords from different programming languages
	def keyword_detection(self, line):
		keywords = ['asm', 'typeof', 'auto', 'def', 'volatile', 'var', 'include_one', 'cin', 'cout', 'instanceof', 'typeid', 'enum', 'int', 'unsigned', 'xor', 'True', 'elif', 'null', 'False', 'die', 'readonly', 'del', 'assert', 'goto', 'package', 'float', 'synchronized', 'String', 'typedef', 'class', 'false', 'throw', 'true', 'async', 'clone', 'string', 'static']
		return " ".join([v+"_T" if v in keywords else v+"_N" for v in line.split(" ")])


	#Check if line is technical using fuzzy logic
	def fuzzy_line_equality_detection(self, lines):
		new_lines = []

		jarowinkler = JaroWinkler()
		#Compare all lines against each other
		for k in range(len(lines.split("\n"))):
			max_sim = 0
			for l in range(len(lines.split("\n"))):
				if k == l: continue
				jaro_sim = jarowinkler.similarity(lines.split("\n")[k].lower(), lines.split("\n")[l].lower())

				#Get maximum similarity
				if jaro_sim > max_sim:
					max_sim = jaro_sim

			#If maximum similarity >= similarity threshold: make all tokens technical(T)
			if max_sim >= self.similarity_threshold and lines.split("\n")[k].replace(" ", ""):
				new_lines.append(" ".join([w+"_T" for w in lines.split("\n")[k].split(" ")]))
			else:
				new_lines.append(" ".join([w+"_N" for w in lines.split("\n")[k].split(" ")]))

		return "\n".join(new_lines)


	#Detecting patches 
	def fuzzy_patch_detection(self, line):
		patch_signature = ["+++ ", "--- ", "diff ", "@@ ", "+", "-"]
		if len([ps for ps in patch_signature if line.startswith(ps)]) > 0:
			return " ".join([w+"_T" for w in line.split(" ")])
		else:
			return " ".join([w+"_N" for w in line.split(" ")])


	#Regular Expression detections
	def regular_expression_detection(self, line):
		if len(line.replace(" ", "")) == 0: return " ".join([z+"_N" for z in line.split(" ")])
		
		programming_regexes = ["[\w]+\([\w\W]*\)", "^\s+(for|if|elif|else if)\s?.*\)\s*[:{]?", "<(/)?[\w]+.*>", "}$", "\s+{$", "<<|>>", "^[A-Z][a-z0-9]+(?:[a-z0-9]+|[A-Z]+)+|^[a-z]+[A-Z][a-z0-9]+(?:[a-z0-9]+|[A-Z]+)+", "\"?[\w-]+\"?\s?:\s?(\"|\w+|{|\[(?={?))"]
		logfile_regexes = ["\d{1,2}:\d{1,2}:\d{1,2}", "[a-zA-Z0-9\-]+_\w+[\s:]", "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "(\d{4}-\d{2}-\d{2}|\d{2}-\d{2}-\d{4}).*\[.*\]"]
		for z in programming_regexes+logfile_regexes:
			k = re.findall(z, line)
			if (len("".join(k)))/len(line.replace(" ", "")) > self.line_threshold:
				return " ".join([w+"_T" for w in line.split(" ")])
			else:
				for m in k:
					line = line.replace(m, m+"_T")
				return " ".join([w+"_N" if not w.endswith("_T") else w for w in line.split(" ")])
		

	#Run heuristics
	def run_heuristics(self, raw_data):
		kwd_results = "\n".join([self.keyword_detection(kd) for kd in raw_data.split("\n")]).split(" ")
		fled_results = self.fuzzy_line_equality_detection(raw_data).split(" ")
		fpd_results = "\n".join([self.fuzzy_patch_detection(fp) for fp in raw_data.split("\n")]).split(" ")
		red_results = "\n".join([self.regular_expression_detection(rd) for rd in raw_data.split("\n")]).split(" ")

		results = []
		for i in range(len(kwd_results)):
			c_r = list(zip([kwd_results[i]], [fled_results[i]], [fpd_results[i]], [red_results[i]]))[0]
			if len(set(c_r)) == 1:
				results.append(c_r[0])
				continue
			results.append(kwd_results[i].replace("_N", "_T"))
		return " ".join(results)


		

class Clustering:

	def __init__(self, sim_min=0.9):
		self.sim_min = sim_min

	#class function
	def class_fn(self, c):
		return True if len([i for i in c if i.endswith("_T")])/len(c) > 0.7 else False

	#Similarity function
	def similarity(self, c_1, c_2, l_C):
		if c_1[:-2] == c_2[:-2]:
			return 1

		elif self.class_fn(c_1) == self.class_fn(c_2):
			return 1 - (len(list(set(c_1) & set(c_2)))/l_C)
		else:
			return 0

	
	#Bottom-up clustering
	def bottom_up(self, pre_classified_data):
		clusters = []
		for c_i in pre_classified_data.split(" "):
			clusters.append([c_i])

		l_C = len(pre_classified_data.split(" "))
		while len(clusters) > 1:
			sim_max = 0
			sim_cs = []
			for c_n1 in clusters:
				for c_n2 in clusters:
					if c_n1 == c_n2: continue

					sim_c = self.similarity(c_n1, c_n2, l_C)
					if sim_c > sim_max:
						sim_max = sim_c
						sim_cs = [c_n1, c_n2]

			if sim_max < self.sim_min:
				break

			n_c = sim_cs[0] + sim_cs[1]
			clusters.remove(sim_cs[0])
			clusters.remove(sim_cs[1])

			clusters.append(n_c)
		return clusters

	def run_clustering(self, preprocessed_data):
		return self.bottom_up(preprocessed_data)


def get_natural_words(clusters):
	#Identify cluster for natural text
	c_id = max(enumerate([len([w for w in c if w.endswith("_N")]) for c in clusters]), key=lambda x:x[1])[0]
	
	return ' '.join([w[:-2].replace("_N", " ") for w in clusters[c_id]]).split(' ')

with open(sys.argv[1], "r") as f:
	issues = f.read()
heuristics = Heuristics()
pp_d = heuristics.run_heuristics(issues)
clustering = Clustering()
c_d = clustering.run_clustering(pp_d)


natural_words = get_natural_words(c_d)
print(' '.join([word for word in issues.split(" ") if word in natural_words]))
