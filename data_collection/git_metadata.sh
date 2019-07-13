#!/bin/bash

if [ $# -ne 1 ]; then
	echo "[*] Usage $0 <git url>"
	exit;
fi

check_github_api=$(curl -s https://api.github.com/users/ShefWuzi | jq 'select (.message != null) | .message' | grep "API rate limit")
while true; 
do
	if [[ $check_github_api != "" ]]; then
		sleep 10m;
		check_github_api=$(curl -s https://api.github.com/users/ShefWuzi | jq 'select (.message != null) | .message')
	else
		break
	fi
done


user=$(echo $1 | rev | cut -d / -f 2 | rev)
repo=$(echo $1 | rev | cut -d / -f 1 | rev)

contrib_res=$(curl -s https://api.github.com/repos/$user/$repo/contributors)

if [[ $contrib_res == "" ]]; then
	echo "[X] No issues returned"
	exit;
fi

for contrib in $(echo $contrib_res | jq -r '.[] | @base64'); do
	login=$(echo "$contrib" | base64 -d | jq -r '.login')

	user_profile=$(curl -s https://api.github.com/users/$login)
	
	name=$(echo "$user_profile" | jq '.name')
	public_repos=$(echo "$user_profile" | jq '.public_repos')
	public_gists=$(echo "$user_profile" | jq '.public_gists')
	followers=$(echo "$user_profile" | jq '.followers')
	following=$(echo "$user_profile" | jq '.following')
	u_type=$(echo "$user_profile" | jq '.type')
	is_company=$(echo "$user_profile" | jq 'select (.company != null) | .company')
	if [[ $is_company == "" ]]; then
		is_company="0"
	else
		is_company="1"
	fi

	created_at=$(echo "$user_profile" | jq 'select (.created_at != null) | .created_at')
	updated_at=$(echo "$user_profile" | jq 'select (.updated_at != null) | .updated_at')

	if [[ $created_at != "" && $updated_at != "" ]];then
		created_at=$(date -d $(echo "$user_profile" | jq '.created_at' | cut -d T -f 1 | tr -d \") '+%s')
		updated_at=$(date -d $(echo "$user_profile" | jq '.updated_at' | cut -d T -f 1 | tr -d \") '+%s')

		n_days=$(printf "%.0f" $(echo "scale=2; ( $updated_at - $created_at )/(60*60*24)" | bc))
	else
		n_days=$(echo "-1")
	fi

	contrib_arr=$(echo -e "$contrib_arr\n$name,$public_repos,$public_gists,$followers,$following,$u_type,$is_company,$n_days")
done


author_details(){
	author_name=$(awk 'NF{NF--};1' < <(echo "$1"))

	while read -r contrib;
	do
		author=$(echo "$contrib" | grep "$author_name")
		
		if [[ $author != "" ]]; then
			commit_author=$(echo "$contrib" | cut -d , -f 2-)
			return 1
		fi
	done <<< "$contrib_arr"

	commit_author=$(echo "-1,-1,-1,-1,-1,-1,-1")
}

get_date(){
	dow=$(echo "$1" | cut -d ' ' -f 1)
	hod=$(echo "$1" | cut -d ' ' -f 4 | cut -d ':' -f 1)
	moh=$(echo "$1" | cut -d ' ' -f 4 | cut -d ':' -f 2)

	commit_date=$(echo "$dow,$hod,$moh")
}

repo_deets=""
repo_details(){
	repo_deets=$(curl -s https://api.github.com/repos/$user/$repo)

	forks_count=$(echo "$repo_deets" | jq '.forks_count')
	stargazers_count=$(echo "$repo_deets" | jq '.stargazers_count')
	watchers_count=$(echo "$repo_deets" | jq '.watchers_count')
	size=$(echo "$repo_deets" | jq '.size')
	open_issues_count=$(echo "$repo_deets" | jq '.open_issues_count')
	subscribers_count=$(echo "$repo_deets" | jq '.subscribers_count')

	repo_deets=$(echo "$forks_count,$stargazers_count,$watchers_count,$size,$open_issues_count,$subscribers_count")
}

folder=$(echo "$1" | cut -d / -f 5)
git clone $1 /tmp/$folder

cd /tmp/$folder
echo "Repo_Forks, Repo_Stars, Repo_Watchers, Repo_Size, Repo_Issues, Repo_Subscribers, Author_Repos, Author_Gists, Author_Followers, Author_Following, Author_Type, Author_Company, Author_Days, Commit_Date_DOW, Commit_Date_HOD, Commit_Date_MOH, Commit Message, Number of Removed File, Number of Added Files, Number of Edited Files, Amount of edit bytes, Added content, Removed content"
for id in $(git log | grep -E "^commit" | cut -d ' ' -f 2); do

	commit_details=$(git show $id | cat)

	author_details "$(echo "$commit_details" | grep -E '^Author:\s' | sed -e 's/^Author:\s//g')"

	commit_msg=$(git show $id --stat | grep -E '^\s{4}' | sed -e "s/'//g" | sed -e "s/,//g" | xargs)

	get_date "$(echo "$commit_details" | grep -E '^Date:\s{3}' | sed -e 's/^Date:\s\{3\}//g')"


	n_removed_files=$(echo "$commit_details" | grep -E '^\+{3}\s/dev/null' | wc -l)
	n_added_files=$(echo "$commit_details" | grep -E '^-{3}\s/dev/null' | wc -l)
	n_edit_files=$(echo "$commit_details" | grep -E '^-{3}|^\+{3}' | grep -v /dev/null | grep -oE '^-{3}|^\+{3}' | sort |  uniq -c | sort -n | head -n 1 | awk '{print $1}')

	n_edit_size=$(echo "$commit_details" | grep -E '^\+[^\+{2}]|^-[^-{2}]' | wc -c)
	added_lines=$(echo "$commit_details" | grep -E '^\+[^\+{2}]' | perl -p -e 's/\n/<\\n>/' | sed -e 's/,/<c>/g')
	removed_lines=$(echo "$commit_details" | grep -E '^-[^-{2}]' | perl -p -e 's/\n/<\\n>/' | sed -e 's/,/<c>/g')

	if [ -z "$n_edit_files" ]; then
		n_edit_files=0
	fi

	repo_details

	echo "$repo_deets,$commit_author,$commit_date,$commit_msg,$n_removed_files,$n_added_files,$n_edit_files,$n_edit_size,$added_lines,$removed_lines"

done

rm -rf /tmp/$folder


# for repo in "https://github.com/ShefWuzi/msc-dissertation" "https://github.com/dominictarr/event-stream" "https://github.com/eslint/eslint-scope" "https://github.com/vasilevich/nginxbeautifier" "https://github.com/Neil-UWA/simple-alipay" "https://github.com/andrewjstone/s3asy" "https://github.com/OpusCapita/react-dates" "https://github.com/react-component/calendar" "https://github.com/anbi/mydatepicker"; do repo_name=$(echo $repo | rev | cut -d / -f 1 | rev); ./git_metadata.sh $repo > $repo_name.csv ; echo "Done with $repo_name....Sleeping"; sleep 15m;  done