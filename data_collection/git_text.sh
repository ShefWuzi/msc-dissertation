#!/bin/bash

if [ $# -ne 1 ];then
	echo "[*] Usage: $0 <github url>"
	exit;
fi

if [[ $1 == "https://github.com/*" ]]; then
	echo "[X] Can't extract data for non-github website"
	exit;
fi


issue_data() {
	issue_resp=$(echo "$1")
	for issue in $(echo $issue_resp | jq -r '.[] | @base64'); do
		title=$(echo "$issue" | base64 -d | jq -r '.title' | sed 's/,//g' )
		state=$(echo "$issue" | base64 -d | jq -r '.state')
		id=$(echo "$issue" | base64 -d | jq -r '.number')
		created_time=$(echo "$issue" | base64 -d | jq -r '.created_at')
		updated_time=$(echo "$issue" | base64 -d | jq -r '.updated_at')
		closed_time=$(echo "$issue" | base64 -d | jq -r '.closed_at')
		body=$(python ../data_preparation/extract_natural_text.py <(echo "$issue" | base64 -d | jq -r '.body' | perl -p -e 's/\r/<\\r>/' | perl -p -e 's/\n/<\\n>/' | sed 's/,/<c>/g'))
		user_name=$(echo "$issue" | base64 -d | jq -r '.user.login')
		user_id=$(echo "$issue" | base64 -d | jq -r '.user.id')
		author_assoc=$(echo "$issue" | base64 -d | jq -r '.author_association')

		if [[ $is_pull == "" ]]; then 
			is_pull="0";
		else
			is_pull="1";
		fi
			
		echo "$id,$state,$created_time,$updated_time,$closed_time,$user_name,$user_id,$author_assoc,$title,$body" 
	done
}

check_github_api=$(curl -s https://api.github.com/users/ShefWuzi | jq 'select (.message != null) | .message' | grep "API rate limit")
while true; 
do
	if [[ $check_github_api != "" ]]; then
		sleep 5m;
		check_github_api=$(curl -s https://api.github.com/users/ShefWuzi | jq 'select (.message != null) | .message')
	else
		break
	fi
done

echo "ID,State,Time Created,Time Updated,Time Closed,Username,User ID,Author Association,Title,Body"
user=$(echo $1 | rev | cut -d / -f 2 | rev)
repo=$(echo $1 | rev | cut -d / -f 1 | rev)

issue_resp=$(curl -s https://api.github.com/repos/$user/$repo/issues?state=closed&filter=all&direction=asc)
if [[ $issue_resp == "" ]]; then
	exit;
fi
issue_data "$issue_resp"


pull_resp=$(curl -s https://api.github.com/repos/$user/$repo/pulls?state=closed&filter=all&direction=asc)
if [[ $issue_resp == "" ]]; then
	exit;
fi
issue_data "$pull_resp"
