#!/bin/bash

if [ $# -ne 1 ];then
	echo "[*] Usage: $0 <github url>"
	exit;
fi

if [[ $1 == "https://github.com/*" ]]; then
	echo "[X] Can't extract data for non-github website"
	exit;
fi

user=$(echo $1 | rev | cut -d / -f 2 | rev)
repo=$(echo $1 | rev | cut -d / -f 1 | rev)

issue_resp=$(curl -s https://api.github.com/repos/$user/$repo/issues?state=all&filter=all&direction=asc)

if [[ $issue_resp == "" ]]; then
	echo "[X] No issues returned"
	exit;
fi

echo "ID,State,Time Created,Time Updated,Pull Request?,Username,User ID,Author Association,Number of Comments,Title,Body"
for issue in $(echo $issue_resp | jq -r '.[] | @base64'); do
	title=$(echo "$issue" | base64 -d | jq -r '.title' | sed 's/,//g' )
	state=$(echo "$issue" | base64 -d | jq -r '.state')
	id=$(echo "$issue" | base64 -d | jq -r '.id')
	n_comments=$(echo "$issue" | base64 -d | jq -r '.comments')
	created_time=$(echo "$issue" | base64 -d | jq -r '.created_at')
	updated_time=$(echo "$issue" | base64 -d | jq -r '.updated_at')
	body=$(echo "$issue" | base64 -d | jq -r '.body' | perl -p -e 's/\r/<\\r>/' | perl -p -e 's/\n/<\\n>/' | sed 's/,/<c>/g')
	user_name=$(echo "$issue" | base64 -d | jq -r '.user.login')
	user_id=$(echo "$issue" | base64 -d | jq -r '.user.id')
	author_assoc=$(echo "$issue" | base64 -d | jq -r '.author_association')
	is_pull=$(echo "$issue" | base64 -d | jq -r '. | select(.pull_request)')

	if [[ $is_pull == "" ]]; then 
		is_pull="F";
	else
		is_pull="T";
	fi
		
	echo "$id,$state,$created_time,$updated_time,$is_pull,$user_name,$user_id,$author_assoc,$n_comments,$title,$body" 
done
