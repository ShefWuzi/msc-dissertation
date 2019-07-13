import requests
from bs4 import BeautifulSoup

for i in range(1, 1348):
	req = requests.get("https://snyk.io/vuln/page/"+str(i)+"?type=any")

	soup = BeautifulSoup(req.text, 'lxml')

	for tr in soup.find_all("tr"):
		if len(tr.find_all("td")) < 1 : continue

		tds = tr.find_all("td")
		if tds[0].find_all("span")[1].find_all("a")[0].find_all("strong")[0].text == "Malicious Package":
			print("%s => %s" %(tds[1].find_all("strong")[0].find_all("a")[0].text.strip(), tds[2].text.strip()))