#!/bin/bash

# 使い方
# ./fracas.sh <section> <prover>
#
# <section> は adj, comp
# <prover> は prover9, vampire
#
# 例
# ./fracas.sh comp vampire

section=$1
prover=$2

results_dir="./results"
mkdir -p $results_dir

# echo "システムの答え/正解/証明にかかった時間"
echo "System answer/Gold answer/Time"

total=0
correct=0
time=0

for f in ./inferences/fra_${section}*.ccg; do
  let total++
  fname=${f##*/}
  ./scripts/prove.sh $f > $results_dir/${fname/.ccg/.ans} $prover
  sys=`cat ./results/${fname/.ccg/.ans} | awk -F',' '{print $1}'`
  gold=`cat ./inferences/${fname/.ccg/.ans}`

  ans="dammy"
  if [ "${sys}" == "${ans}" ]; then
      echo "${fname}: ${sys}/${gold}/0.0000"
  else
      prove_time=`cat ./results/${fname/.ccg/.ans} | awk -F',' '{print $2}'`
      if [ "${sys}" == "${gold}" ]; then
	  let correct++
      fi
      time=`echo "scale=3; ${time} + ${prove_time}" | bc -l`
      echo "${fname}: ${sys}/${gold}/${prove_time}"
  fi
done

accuracy=`echo "scale=4; $correct / $total" | bc -l`
average_time=`echo "scale=4; $time / $total" | bc -l`
date=`date +%Y-%m-%d_%H:%M:%S`

echo "Accuracy: "$correct" / "$total" = "$accuracy
echo "Average time: ${average_time}"

echo "<!doctype html>
<html lang='en'>
<head>
  <meta charset='UTF-8'>
  <title>Evaluation results of FraCaS</title>
  <style>
    body {
      font-size: 1.5em;
    }
  </style>
</head>
<body>
<table border='1'>
<ul>
<li>"$prover"
<li>"$date"
<li>Accuracy : "$correct" / "$total" = "$accuracy"</li>
<li>Average time: "${average_time}"</li>
</ul>
<tr>
  <td>FraCaS id</td>
  <td>FraCaS problem</td>
  <td>gold answer</td>
  <td>system answer</td>
  <td>proving time</td>
</tr>" > $results_dir/${section}_main.html

red_color="rgb(255,0,0)"
green_color="rgb(0,255,0)"
white_color="rgb(255,255,255)"
gray_color="rgb(136,136,136)"

for gold_filename in `ls -v ./inferences/fra_${section}*.ans`; do
  fname=${gold_filename##*/}
  sentences=`python ./scripts/get_sentences.py ./inferences/${fname/.ans/.ccg} | sed 's|#END#|<br>|g'`
  system_answer=`cat $results_dir/${fname/.ccg/.ans} | awk -F',' '{print $1}'`
  time=`cat $results_dir/${fname/.ccg/.ans} | awk -F',' '{print $2}'`
  gold_answer=`cat $gold_filename`
  echo '<tr>
  <td>'${fname/.ans/}'</td>
  <td>'$sentences'</td>
  <td>'${gold_answer}'</td>' >> $results_dir/${section}_main.html
  color=$white_color
  if [ "$gold_answer" == "yes" ] || [ "$gold_answer" == "no" ]; then
    if [ "$gold_answer" == "$system_answer" ]; then
      color=$green_color
    else
      color=$red_color
    fi
  elif [ "$system_answer" == "yes" ] || [ "$system_answer" == "no" ]; then
    color=$red_color
  else
    color=$white_color
  fi
  echo '<td><a style="background-color:'$color';" href="'${fname/.ans/.html}'">'$system_answer'</a></td>' >> $results_dir/${section}_main.html
  echo '<td>'${time}'</td></tr>' >> $results_dir/${section}_main.html
done
