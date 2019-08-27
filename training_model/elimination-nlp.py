import sys, re
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

if len(sys.argv) != 4:
	print("[x] Usage: %s <commit_data_ids_csv> <issues_file> <commit_file>" %sys.argv[0])
	sys.exit(0)


def find_similar_issues(issues_tfidf, commit_tfidf, top_n=5):
	cosine_similarities = linear_kernel(commit_tfidf, issues_tfidf).flatten()
	issues_indices = [i for i in cosine_similarities.argsort()[::-1]]

	return [(index, cosine_similarities[index]) for index in issues_indices][:top_n]

def fix_commits_heuristics(commit_date, commit_text, issues):
	
	heuristics_word = ["fix", "bug", "issue", "resolve", "merge", "pull", "request"]
	for word in heuristics_word:
		if word in commit_text:
			issue_nums = re.findall("#[0-9]+", commit_text)
			if len(issue_nums) > 0:
				return True
				# for issue_num in issue_nums:
				# 	if issue_num.replace("#", "") in issues:
				# 		issue_num = issue_num.replace("#", "")
				# 		issue = issues[issue_num]
				# 		if type(commit_date) == str:
				# 			commit_date = datetime.strptime(commit_date, "%d %b %Y")
				# 		if (commit_date >= datetime.strptime(issue[0][0].split("T")[0], "%Y-%m-%d") and commit_date <= datetime.strptime(issue[0][2].split("T")[0], "%Y-%m-%d")) or (commit_date >= datetime.strptime(issue[-1][0].split("T")[0], "%Y-%m-%d") and commit_date <= datetime.strptime(issue[-1][2].split("T")[0], "%Y-%m-%d")): 
				# 			return True

	return False


def closest_issues_nlp(commit_date, commit_text, tfidf, issues_tfidf, issues, score_threshold=0.4):
	commit_tfidf = tfidf.transform([commit_text])
	for issue_index, score in find_similar_issues(issues_tfidf, commit_tfidf):
		if score < score_threshold: continue

		issue = issues[list(issues.keys())[issue_index]]
		if type(commit_date) == str:
			commit_date = datetime.strptime(commit_date, "%d %b %Y")
		if (commit_date >= datetime.strptime(issue[0][0].split("T")[0], "%Y-%m-%d") and commit_date <= datetime.strptime(issue[0][2].split("T")[0], "%Y-%m-%d")) or (commit_date >= datetime.strptime(issue[-1][0].split("T")[0], "%Y-%m-%d") and commit_date <= datetime.strptime(issue[-1][2].split("T")[0], "%Y-%m-%d")):
			return True
	return False



ids = list(map(int, sys.argv[1][:-1].split(",")))
issues, commits = {}, {}

#[created_time, updated_time, closed_time, title, body]
with open(sys.argv[2], "r") as issue_file:
	issue_file.readline()
	for line in issue_file:
		ls = line.split(",")

		issues[ls[0]] = issues.get(ls[0], []) + [[x for i, x in enumerate(ls) if i in [2, 3, 4, 8, 9]]]


no_malicious = 0
#{commit_date hod:moh : commit message}
with open(sys.argv[3], "r") as commit_file:
	commit_file.readline()
	p_id = 0
	for line in commit_file:
		ls = line.split(",")
		if ls[26].strip() == "T": no_malicious+=1

		if p_id not in ids: 
			p_id += 1
			continue

		ckey = "%s %s:%s" %(ls[17], ls[15], ls[16])
		commits[ckey] = {"message": commits.get(ckey, {}).get("message", "") + " " + ls[18].replace("<c>", ",").replace("<\n>", " ").lower().strip(), "ids": commits.get(ckey, {}).get("ids", []) + [p_id], "malicious": commits.get(ckey, {}).get("malicious", []) + [ls[26].strip()]}
		p_id += 1

#Create TFIDF of all issues
tfidf = TfidfVectorizer(analyzer="word", ngram_range=(1,3), min_df=0, stop_words="english")
issues_tfidf = tfidf.fit_transform([" ".join(v[0][3:5]).lower()+" "+" ".join(v[-1][3:5]).lower() for v in issues.values()])


no_suspicious = 0
tp = 0
for ckey, cvalue in commits.items():
	if not fix_commits_heuristics(' '.join(ckey.split(" ")[:-1]), cvalue["message"], issues):
		if not closest_issues_nlp(' '.join(ckey.split(" ")[:-1]), cvalue["message"], tfidf, issues_tfidf, issues, 0.005):
			no_suspicious += len(cvalue["ids"])
			tp += len([x for x in cvalue["malicious"] if x == "T"])
			

print("Number of suspicious commits: %d" %(no_suspicious))
print("Number of discovered malicious commits: %d" %tp)
print("Precision: %.3f" %(tp/no_suspicious))
print("Recall: %.3f" %(tp/no_malicious))
