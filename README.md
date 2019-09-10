# Inference system for comparative and adjectives of FraCaS

*The datasets and codes for my PACLIC33 paper.*

This is a program of the inference system that tries to prove FraCaS test suite of section ADJECTIVES and COMPARATIVES.

Here, there are codes for the CCG semantic parsing and the axioms of Comp.

## Requirements

* Python 3.6.5
* [Vampire](https://github.com/vprover/vampire)


## Installation

### For ccg2lambda
To use the part of ccg2lambda in our system, it is necessary to install python3, nltk, lxml, simplejson and yaml python libraries.
See [installation](https://github.com/mynlp/ccg2lambda#installation) in ccg2lambda in detail.

### For Vampire
In your home directory, run git clone of [Vampire](https://github.com/vprover/vampire).
```
git clone https://github.com/vprover/vampire.git
```
Make the file.
```
make vampire_rel
```
Rename created files (eg. vampire_rel_master_4123) `vampire`.
```
mv vampire_rel_master_XXXX vampire
```


* **ccg2lambda**  
  * CCG semantic parsing
* **fracas_plain**  
  * FraCaS test suite data (https://nlp.stanford.edu/~wcmac/downloads/fracas.xml)
* **inferences**  
  * manually constructed CCG tree data using sections ADJECTIVES and COMPARATIVES of FraCaS (`.ccg`)
  * gold answer (`.ans`)
* **scripts**  
* **tptp**  


## Usage

The process of our system:
1. CCG derivation tree (`.ccg`)
2. Convert it to Semantic representation (`.sem.xml`)
3. Convert the axioms of COMP, premises and hypothesis to tptp format (`.tptp`)
4. Run theorem proving by using Vampire

### 実験の再現方法

実行は全て`scripts`ディレクトリ下で行う。
```
cd scripts
```
評価はそこにある、`fracas.sh`で行う。  
第２引数に、section名 (adjectives -> adj, comparatives -> comp)、  
第３引数に、prover名 (vampire) を入力する。  
e.g.
```
./fracas.sh comp vampire
```
すると、指定したsectionの全ての問題に対して、gold answer, system answer, and timeが返ってくる:
```
System answer/Gold answer/Time
fra_comp_220.ccg: yes/yes/0.0492
fra_comp_221.ccg: unknown/unknown/4.2851
fra_comp_222.ccg: unknown/unknown/4.3367
fra_comp_223.ccg: no/no/2.1593
fra_comp_224.ccg: yes/yes/0.0208
fra_comp_225.ccg: unknown/unknown/4.2712
```
全ての問題の評価が終わると、最後に全体の精度とAverage timeが出力される:
```
Accuracy: 29 / 31 = .9354
Average time: 1.6729
```
実行によって作成されたファイルは、`results`ディレクトリ下に置かれる。  
各問題に対して作成されるファイルは、6つ (`.ans`/`.html`/`.sem.err`/`.sem.xml`/`.tptp`/`.xml`)。  
セクションごとに`adj_main.html`と`comp_main.html`も作成される。

