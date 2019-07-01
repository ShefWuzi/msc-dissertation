#!/bin/bash

if [ $# -ne 1 ]; then
	echo "[*] Usage $0 <git url>"
	exit;
fi

folder=$(echo "$1" | cut -d / -f 5)
git clone $1 /tmp/$folder

cd /tmp/$folder
echo "ID, Commit Author, Commit Date, Commit Message, Number of Removed File, Number of Added Files, Number of Edited Files, Amount of edit bytes, Added content, Removed content"
for id in $(git log | grep -E "^commit" | cut -d ' ' -f 2); do

	commit_details=$(git show $id | cat)

	commit_author=$(echo "$commit_details" | grep -E '^Author:\s' | sed -e 's/^Author:\s//g')
	commit_msg=$(git show $id --stat | grep -E '^\s{4}' | sed -e "s/'//g" | sed -e "s/,//g" | xargs)
	commit_date=$(echo "$commit_details" | grep -E '^Date:\s{3}' | sed -e 's/^Date:\s\{3\}//g')

	n_removed_files=$(echo "$commit_details" | grep -E '^\+{3}\s/dev/null' | wc -l)
	n_added_files=$(echo "$commit_details" | grep -E '^-{3}\s/dev/null' | wc -l)
	n_edit_files=$(echo "$commit_details" | grep -E '^-{3}|^\+{3}' | grep -v /dev/null | grep -oE '^-{3}|^\+{3}' | sort |  uniq -c | sort -n | head -n 1 | awk '{print $1}')

	n_edit_size=$(echo "$commit_details" | grep -E '^\+[^\+{2}]|^-[^-{2}]' | wc -c)
	added_lines=$(echo "$commit_details" | grep -E '^\+[^\+{2}]' | perl -p -e 's/\n/<\\n>/' | sed -e 's/,/<c>/g')
	removed_lines=$(echo "$commit_details" | grep -E '^-[^-{2}]' | perl -p -e 's/\n/<\\n>/' | sed -e 's/,/<c>/g')

	if [ -z "$n_edit_files" ]; then
		n_edit_files=0
	fi
	echo "$id,$commit_author,$commit_date,$commit_msg,$n_removed_files,$n_added_files,$n_edit_files,$n_edit_size,$added_lines,$removed_lines"

done

rm -rf /tmp/$folder