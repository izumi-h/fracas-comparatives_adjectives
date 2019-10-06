# -*- coding: utf-8 -*-

import argparse
from lxml import etree
from nltk.inference import Prover9, Mace
from nltk.sem.logic import Expression, NegatedExpression, ApplicationExpression
import os
import subprocess
import sys
import textwrap
import time
from multiprocessing import Queue, Process
import re

lexpr = Expression.fromstring

from axiom_prover9 import prover9_axioms
from axiom_vampire import vampire_axioms

file = open("./scripts/vampire_dir.txt")
vampire_dir = file.read().strip()

sys.path.append("./ccg2lambda")

from nltk2tptp import convert_to_tptp_proof, convert_to_tptp
from nltk2normal import get_atomic_formulas

def get_formulas_from_xml(doc):
    formulas = [s.get('sem', None) for s in doc.xpath(
        './sentences/sentence/semantics[1]/span[1]')]
    return formulas

Fpos = {'_tall':0, '_large':1, '_clever':2, '_fast':3, '_many':4, '_important':5, '_genuine':6, '_fat':8, '_successful':9, '_competent':10}
Fneg = {'_short':0, '_small':1, '_stupid':2, '_slow':3}

non_Aff = {'_former':0}
Fex = {'_tall':0, '_large':1, '_fast':2, '_fat':3, '_short':4, '_small':5}

Verbs = {'_won':0, '_lost':1, '_sold':2}
Objs = {'_computer':0, '_order':1, '_person':2, '_customer':3, '_university_student':3, '_legal_authority':4, '_law_lecturer':5}


def prove_prover9mace(premises, conclusion, predicates, lst):
    axioms = prover9_axioms(Fpos, Fneg, Verbs, Objs, Fex, predicates, lst)
    #print(axioms)
    premises = axioms + premises
    def prover_fun(queue):
        res = Prover9(timeout=3).prove(conclusion, premises)
        is_prover = True
        queue.put((is_prover, res))

    def modelbuilder_fun(queue):
        res = Mace(end_size=50).build_model(conclusion, premises)
        is_prover = False
        queue.put((is_prover, res))

    queue = Queue()
    prover_process = Process(target=prover_fun, args=(queue,))
    modelbuilder_process = Process(target=modelbuilder_fun, args=(queue,))
    processes = [prover_process, modelbuilder_process]
    for process in processes:
        process.start()

    while queue.empty():
        pass

    is_prover, result = queue.get()
    if is_prover:
        modelbuilder_process.terminate()
    else:
        prover_process.terminate()
        result = not result
    return result

def prove_vampire(premises, conclusion, predicates, lst):
    # add axioms
    axioms = vampire_axioms(Fpos, Fneg, Verbs, Objs, Fex, predicates, lst)
    #print(axioms)
    tptp_axioms = [convert_to_tptp(axiom) for axiom in axioms]
    
    premises = tptp_axioms + premises
    premises.append(conclusion)
    fols = convert_to_tptp_proof(premises)

    F = list(Fpos.keys())
    F.extend(list(Fneg.keys()))
    
    type_f = []

    for pred in predicates:
        for adj in F:
            if pred[0] == adj:
                adj = adj.strip('_')
                adj_type = 'tff(' + adj + '_type, type , ' + adj + ' : $i * $int > $o).'
                type_f.append(adj_type)
        for naf in non_Aff.keys():
            if pred[0] == naf:
                naf = naf.strip('_')
                naf_type = 'tff(' + naf + '_type, type , ' + naf + ' : $o > $o).'
                type_f.append(naf_type)

        for obj in Objs.keys():
            if (pred[0] == obj) or (obj in pred[1][0]):
                obj = obj.strip('_')
                obj_type = 'tff(' + obj + '_type, type , ' + obj + ' : $i > $o).'
                type_f.append(obj_type)
                
        if (len(pred[1]) == 2) and ('_th' in (pred[1])[1]):
            type_f.append('tff(th_type, type , th : $i > $int).')
        if (len(pred[1]) == 2) and ('_np' in (pred[1])[1]):
            type_f.append('tff(np_type, type , np : $i * $int > $int).')
            
    type_f = set(type_f)
    type_f = list(type_f)
        
    fols = type_f + fols
    
    
    if ('many' in fols[0]):
        f = lexpr('all d1.-exists d2.($less(d1,d2) & $less(d2,$sum(d1,1)))')
        lemma = convert_to_tptp(f)
        fols.insert(-1, 'tff(p1,lemma,{0}).'.format(lemma))

    # arg = ARGS.sem.strip("./results")
    # arg = arg.strip(".sem.xml")
    arg = ARGS.sem.strip(".sem.xml")
    # with open("tptp/" + arg + ".tptp", "w", encoding="utf-8") as z:
    with open(arg + ".tptp", "w", encoding="utf-8") as z:
        for f in fols:
            z.write(f + "\n")
    tptp_script = ' '.join(fols)
    ps = subprocess.Popen(('echo', tptp_script), stdout=subprocess.PIPE)
    try:
        output = subprocess.check_output(
              (vampire_dir + '/vampire', '-t', '15', '--mode', 'casc'),
              stdin=ps.stdout,
              stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        return False
    ps.wait()
    output_lines = [
        str(line).strip() for line in output.decode('utf-8').split('\n')]
    res = is_theorem_in_vampire(output_lines)
    return res

def is_theorem_in_vampire(output_lines):
    if output_lines:
        proof_message = '% Refutation found. Thanks to Tanya!'
        if (proof_message in output_lines):
        #proof_message = output_lines[0]
        #if proof_message == '% Refutation found. Thanks to Tanya!':
            return True
        else:
            #print(output_lines)
            return False
    else:
        #print(output_lines)
        return False

def theorem_proving(prove_fun, premises, conclusion, predicates, lst):
    res = prove_fun(premises, conclusion, predicates, lst)
    if res:
        prediction = 'yes'
    else:
        negated_conclusion = NegatedExpression(conclusion)
        res = prove_fun(premises, negated_conclusion, predicates, lst)
        if res:
            prediction = 'no'
        else:
            prediction = 'unknown'
    return prediction

def multi_theorem_proving(prove_fun, premises, conclusion, predicates, lst):
    def prove_positive(queue):
        res = prove_fun(premises, conclusion, predicates, lst)
        is_prover = True
        queue.put((is_prover, res))

    def prove_negative(queue):
        negated_conclusion = NegatedExpression(conclusion)
        res = prove_fun(premises, negated_conclusion, predicates)
        is_prover = False
        queue.put((is_prover, res))

    queue = Queue()
    prove_pos_process = Process(target=prove_positive, args=(queue,))
    prove_neg_process = Process(target=prove_negative, args=(queue,))
    processes = [prove_pos_process, prove_neg_process]
    for process in processes:
        process.start()

    while queue.empty():
        pass

    is_prover, is_theorem = queue.get()
    if is_prover and is_theorem:
        prove_neg_process.terminate()
        prediction = 'yes'
    else:
        prove_pos_process.terminate()
        if is_theorem:
            prediction = 'no'
        else:
            prediction = 'unknown'
    return prediction

def get_predicate(formula):
    predlst = []
    preds = get_atomic_formulas(lexpr(formula))
    for pred in preds:
        if isinstance(pred, ApplicationExpression):
            predicate, args = pred.uncurry()
            pred_str = str(predicate)
            args_str = [str(arg) for arg in args]
            item = [pred_str, args_str]
            if not item in predlst:
                predlst.append(item)
    return predlst

def main(args = None):
    global ARGS
    global DOCS
    DESCRIPTION=textwrap.dedent("""\
            The input file sem should contain the parsed sentences. All CCG trees correspond
            to the premises, except the last one, which is the hypothesis.
      """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION)
    parser.add_argument("sem", help="XML input filename with semantics")

    parser.add_argument("--prover", nargs='?', type=str, default="prover9",
        choices=["prover9", "vampire"],
        help="Prover (default: prover9).")
     
    ARGS = parser.parse_args()

    if not os.path.exists(ARGS.sem):
        print('File does not exist: {0}'.format(ARGS.sem), file=sys.stderr)
        parser.print_help(file=sys.stderr)
        sys.exit(1)
    
    parser = etree.XMLParser(remove_blank_text=True)
    root = etree.parse(ARGS.sem, parser)

    DOCS = root.findall('.//document')
    doc = DOCS[0]

    formulas = get_formulas_from_xml(doc)
    if (formulas == ['\\O.O']):
        print('dammy')

    else:
        lst = []
        predicates = []
        for formula in formulas:
            if ('all' in formula) and ('->' in formula):
                lst.append(formula)    
            preds = get_predicate(formula)
            for pred in preds:
                if not pred in predicates:
                    predicates.append(pred)
        
        #print(predicates)
        
        if ARGS.prover == "prover9":
            formulas = [lexpr(formula) for formula in formulas]
            conclusion = formulas[-1]
            premises = formulas[:-1]
            start = time.time()
            prediction = theorem_proving(prove_prover9mace, premises, conclusion, predicates, lst)
            end = time.time() - start
            print('{0},{1:.4f}'.format(prediction, end))

        if ARGS.prover == "vampire":
            formulas = [lexpr(formula) for formula in formulas]
            premises = formulas[:-1]
            conclusion = formulas[-1]
            start = time.time()
            #prediction = multi_theorem_proving(prove_vampire, premises, conclusion, predicates)
            prediction = theorem_proving(prove_vampire, premises, conclusion, predicates, lst)
            end = time.time() - start
            print('{0},{1:.4f}'.format(prediction, end))
        
if __name__ == '__main__':
    main()


## Test formulas
f1 = lexpr('exists x. (boy(x) & tall(x))')
f2 = lexpr('exists x. (boy(x))')
f3 = lexpr('forall x. (boy(x) -> -tall(x))')
f4 = lexpr('tall(john)')
f5 = lexpr('-boy(john)')
inf1 = [f1,f2]
inf2 = [f2,f1]
inf3 = [f3,f4,f5]
