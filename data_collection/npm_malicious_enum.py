import requests
from bs4 import BeautifulSoup
import re

req = requests.get("https://www.npmjs.com/advisories?page=0&perPage=500")

soup = BeautifulSoup(req.text, "lxml")
with open("npm_mal_pkg.csv", "w") as nmp:
	nmp.write("Package Name, Advisory, Repository\n")
	for tr in soup.find_all("tr"):
		if len(tr.find_all("td")) < 1: continue

		tds = tr.find_all("td")

		if tds[0].find_all("div")[0].find_all("a")[0].text == "Malicious Package":
			advisory =  "https://www.npmjs.com" + tds[0].find_all("div")[0].find_all("a")[0]["href"]
			pkg_name = tds[0].find_all("div")[1].text
			repository = ""

			req2 = requests.get("https://www.npmjs.com/package/"+pkg_name)
			soup2 = BeautifulSoup(req2.text, "lxml")
			for div in soup2.find_all("div"):
				if len(div.find_all("h3")) < 1 or div.find_all("h3")[0].text != "repository": continue

				repository = div.find_all("p")[0].find_all("a")[0]["href"]

			nmp.write("%s, %s, %s\n" %(pkg_name, advisory, repository))

