#!/bin/bash

echo "[*] Detecting malicious commits in event-stream"
##################################
echo "[*] Stats"
echo "========================================"
echo -n "Number of commits: "
nc=$(echo "$(cat data_collection/event-stream.csv | wc -l) - 1" | bc)
echo "$nc"
echo -n "Number of malicious commits: "
nm=$(cat data_collection/event-stream.csv | cut -d ',' -f 27 | grep T | wc -l)
echo "$nm"
echo -n "Percentage of malicious commits: "
echo "scale=3;($nm / $nc) * 100" | bc
echo "========================================"
####################################


echo "[*] Evaluation with DBSCAN"
event_stream=$(python training_model/detecting-dbscan.py data_collection/event-stream.csv)
echo "$event_stream" | tail -n 4

echo ""
echo "[*] Evaluation with DBSCAN+NLP tactics"
python training_model/elimination-nlp.py $(echo "$event_stream" | head -n 1) data_collection/event-text.csv data_collection/event-stream.csv


echo "========================================================"
echo "[*] Detecting malicious commits in eslint-scope"
##################################
echo "[*] Stats"
echo "========================================"
echo -n "Number of commits: "
nc=$(echo "$(cat data_collection/eslint-scope.csv | wc -l) - 1" | bc)
echo "$nc"
echo -n "Number of malicious commits: "
nm=$(cat data_collection/eslint-scope.csv | cut -d ',' -f 27 | grep T | wc -l)
echo "$nm"
echo -n "Percentage of malicious commits: "
echo "scale=3;($nm / $nc) * 100" | bc
echo "========================================"
####################################
echo "[*] Evaluation with DBSCAN"
eslint_scope=$(python training_model/detecting-dbscan.py data_collection/eslint-scope.csv)
echo "$eslint_scope" | tail -n 4

echo ""
echo "[*] Evaluation with DBSCAN+NLP tactics"
python training_model/elimination-nlp.py $(echo "$eslint_scope" | head -n 1) data_collection/eslint-text.csv data_collection/eslint-scope.csv