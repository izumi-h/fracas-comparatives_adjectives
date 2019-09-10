#!/bin/bash

# Usage:
# ./prove.sh <ccg file> <prover>

# prover ::= prover9 | vampire

ccg=$1
prover=$2

home=$HOME
c2l_dir="./ccg2lambda"
semantics="./scripts/templates_comparatives.yaml"
file=${ccg##*/}
jigg=${file/.ccg/.xml}

res_dir="./results"
mkdir -p $res_dir

python ./ccg2lambda/ccg2jiggxml.py -i $ccg > $res_dir/$jigg

python ${c2l_dir}/semparse.py $res_dir/$jigg $semantics $res_dir/${jigg/.xml/.sem.xml} \
    2> $res_dir/${jigg/.xml/.sem.err}

python ${c2l_dir}/visualize.py $res_dir/${jigg/.xml/.sem.xml} \
    > $res_dir/${jigg/.xml/.html}

python ./scripts/eval.py $res_dir/${jigg/.xml/.sem.xml} --prover $prover

# python callprover9.py $res_dir/${jigg/.xml/.sem.xml}


