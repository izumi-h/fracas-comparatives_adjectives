# Compositional Semantics and Inference System for Comparatives

This repository contains code for our paper [A CCG-based Compositional Semantics and Inference System for Comparatives](https://arxiv.org/abs/1910.00930).

  - Izumi Haruta, Koji Mineshima and Daisuke Bekki. A CCG-based Compositional Semantics and Inference System for Comparatives. The 33rd Pacific Asia Conference on Language, Information and Computation (PACLIC 33).

## Requirements

* Python 3.6.5+
* [Vampire](https://github.com/vprover/vampire) 4.3.0+


## Setup

The system uses scripts available from [ccg2lambda](https://github.com/mynlp/ccg2lambda). It is necessary to install python3 (3.6.5 or later), nltk, lxml, simplejson and pyyaml python libraries.
If python3 and pip are already installed, you can install these packages with pip:

```
pip install lxml simplejson pyyaml nltk
```

See also [installation](https://github.com/mynlp/ccg2lambda#installation) of ccg2lambda.

To run the system, first clone our repository:

```
git clone https://github.com/izumi-h/fracas-comparatives_adjectives.git
```

To install Vampire, change your directory to where you cloned the repository and run the following:

```
cd fracas-comparatives_adjectives
./install_vampire.sh
```

This command downloads Vampire (version 4.4.0) to `fracas-comparatives_adjectives/vampire-4.4`. 
You can change the location of Vampire by editing `scripts/vampire_dir.txt`.

## Running the system on the FraCaS test suite

Run experiments on [the FraCaS test suite](https://nlp.stanford.edu/~wcmac/downloads/fracas.xml):

```
./scripts/fracas.sh comp vampire
```

This command runs evaluation on the COMPARATIVE section of FraCaS. If you change `comp` to `adj`, it runs evaluation on the ADJECTIVE section.

```
./scripts/fracas.sh adj vampire
```

The outputs are shown as:

```
System answer/Gold answer/Time
fra_comp_220.ccg: yes/yes/0.0492
fra_comp_221.ccg: unknown/unknown/4.2851
fra_comp_222.ccg: unknown/unknown/4.3367
fra_comp_223.ccg: no/no/2.1593
fra_comp_224.ccg: yes/yes/0.0208
fra_comp_225.ccg: unknown/unknown/4.2712
...
Accuracy: 29 / 31 = .9354
Average time: 1.6729
```

Here, system answer, gold answer, and proving time are indicated for each problem. The overall accuracy and average proving time are also shown.

By default, created files are to be stored in the `results` directory.

- `results/*.ans` -- system prediction (yes, no, unknown) 
- `results/*.html` -- visualized CCG derivation tree with semantic representation: the CCG tree for each FraCaS problem is accessible from
`results/main.html` and `results/comp_main.html`. 
- `results/*.sem.xml` -- CCG derivation tress in XML format
- `results/*.tptp` -- semantic representation in [tptp format](http://www.tptp.org/)

You can also run the system on each inference in FraCaS.
For example, the following tried to prove the inference with ID FraCaS-243:

```
./scripts/prove.sh inferences/fra_comp_243.ccg vampire
```

## Code Structure

The code is divided into the following:

1.  `./ccg2lambda` -- scripts from [ccg2lambda](https://github.com/mynlp/ccg2lambda)
2.  `./fracas\_plain` -- inference problems from [FraCaS](https://nlp.stanford.edu/~wcmac/downloads/fracas.xml). In each `fracas_plain/*.txt` file, a set of premises and a hypothesis are shown line by line. For example, for ID fracas\_220, the first two lines are premises and the final line "The PC_6082 is fast" is a hypothesis.
```
$ cat fracas_plain/fracas_220_comparatives.txt
The PC_6082 is faster than the ITEL_XZ.
The ITEL_XZ is fast.
The PC_6082 is fast.
```
The gold answer label is in `fracas_plain/*.txt`.
```  
$ cat fracas_plain/fracas_220_comparatives.answer
yes
```
3. `./inferences` -- gold CCG derivations trees manually constructed
```
$ cat inferences/fra_comp_220.ccg
(S (S/<S\NP> (NP (NP/N the) (N PC_6082))) (S\NP (<S\NP>/<S\NP> is) (S\NP (<S\NP>/<S/<S\NP>> (<S\NP>\D fast) (<<S\NP>/<S/<S\NP>>>\<<S\NP>\D> er)) (S/<S\NP> (S/S than) (S/<S\NP> (NP (NP/N the) (N ITEL_XZ)))))))
(S (S/<S\NP> (NP (NP/N the) (N ITEL_XZ))) (S\NP (<S\NP>/<S\NP> is) (S\NP (<S\NP>/<<S\NP>\D> pos) (<S\NP>\D fast))))
(S (S/<S\NP> (NP (NP/N the) (N PC_6082))) (S\NP (<S\NP>/<S\NP> is) (S\NP (<S\NP>/<<S\NP>\D> pos) (<S\NP>\D fast))))
```
4. `./scripts` - main scripts including semantic templates (`scripts/templates_comparatives.yaml`) and the COMP axioms.

## Citation

```
@InProceedings{haruta2019:paclic,
  author    = {Haruta, Izumi and Mineshima, Koji and Bekki, Daisuke},
  title     = {A CCG-based Compositional Semantics and Inference System for Comparatives},
  booktitle = {Proceedings of 33rd Pacific Asia Conference on Language, Information and Computation (PACLIC 33)},
  month     = {September},
  year      = {2019},
  address   = {Hakodate, Japan},
  pages     = {67--76}
}
```

## Results
You can see [the html files](https://drive.google.com/drive/folders/1F0iZEp9p4KWf28fYhrZ1WCC2shSCGe9O) as the results that maps CCG derivation trees to semantic representaions.