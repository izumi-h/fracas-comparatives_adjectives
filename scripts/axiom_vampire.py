from nltk import *
# from nltk.sem.drt import DrtParser
# from nltk.sem import logic
# logic._counter._value = 0

from nltk.sem import Expression
from nltk.sem.logic import *
lexpr = Expression.fromstring

import time

## Logical formulas ##

# Negation: -A
# Conjunction: A & B
# Disjunction: A | B
# Conditional mood: A -> B
# Universal quantifier: all x. A
# Existential quantifier: exists x. A
# Equal: x = y
# Lambda formula: \x. A

class Inference:
    def __init__(self, number, gold, premises, conclusion):
        self.number = number
        self.gold = gold
        self.premises = premises
        self.conclusion = conclusion
    def show(self, system_answer, time):
        print('{0}: {1}/{2}  time:{3:.2f}'.format(self.number, self.gold, system_answer, time))

def prove_neg(premises, conclusion):
    negconclusion = NegatedExpression(conclusion)
    try:
        if Prover9(timeout=3).prove(negconclusion, axioms + premises):
            answer = 'no'
        else:
            if Mace(end_size=50).build_model(conclusion, axioms + premises):
                answer = 'unknown'
            else:
                answer = 'timeout'
    except:
        answer = 'unknown1'
    return answer

def prove(premises, conclusion):
    try:
        if Prover9(timeout=3).prove(conclusion, axioms + premises):
           answer = 'yes'
        else:
           answer = prove_neg(premises, conclusion)
        return answer
    except:
        answer = prove_neg(premises, conclusion)
        return answer

def vampire_axioms(Fpos, Fneg, Verbs, Objs, Fex, predicates):
    axiom = []
    Fp = Fm = ''

    foFla = ''

    for pred in predicates:

        # Adjectives
        if ((pred[0] in Fpos) or (pred[0] in Fneg)):

            if (pred[1][1] == '_np(_u,_th(_u))'):
                defcom = lexpr('all x. (' + pred[0] + '(x,_np(_u,_th(_u))) <-> ' + pred[0] + '(x,_np(_person,_th(_person))))')
                axiom.extend([defcom])

            # Positive adjectives
            if (pred[0] in Fpos):
            
                Fp = pred[0]

                cp1 = lexpr('all x. all y. ((exists d1. (' + Fp + '(x,d1) & -' + Fp + '(y,d1))) -> all d2. (' + Fp + '(y,d2) -> ' + Fp + '(x,d2)))')
                ax2 = lexpr('all d1. all x. (' + Fp + '(x,d1) <-> all d2. ($lesseq(d2,d1) -> ' + Fp + '(x,d2)))')
                axiom.extend([cp1, ax2])

                if '_th(_u)' in ((pred[1])[1]):
                    thp = lexpr('all x. (' + Fp + '(x,_th(_u)) <-> exists d. (' + Fp + '(x,d) & ($less(_th(_u),d))))')
                    axiom.extend([thp])


            # Negative adjectives
            elif (pred[0] in Fneg):

                Fm = pred[0]

                cp2 = lexpr('all x. all y. ((exists d1. (' + Fm + '(x,d1) & -' + Fm + '(y,d1))) -> all d2. (' + Fm + '(y,d2) -> ' + Fm + '(x,d2)))')
                ax1 = lexpr('all d1. all x. (' + Fm + '(x,d1) <-> all d2. ($lesseq(d1,d2) -> ' + Fm + '(x,d2)))')
                axiom.extend([cp2, ax1])

                if '_th(_u)' in ((pred[1])[1]):
                    thm = lexpr('all x. (' + Fm + '(x,_th(_u)) <-> exists d. (' + Fm + '(x,d) & ($less(d,_th(_u)))))')
                    axiom.extend([thm])

        # Verbs
        elif (pred[0] in Verbs):
            V = pred[0]

        # Objectives
        elif (pred[0] in Objs):
            obj = pred[0]

        # former
        elif ((pred[0] in '_former') and (type(pred[1][0]) is str)):
            aff = lexpr('all x. (_former(' + pred[1][0] + ') -> -' + pred[1][0] + ')')
            axiom.extend([aff])

        else:
            pass
        
            
    if ((Fp != '') and (Fm != '')):
        ax3 = lexpr('all d1. all x. (' + Fm + '(x,d1) <-> all d2. ($less(d1,d2) -> -' + Fp + '(x,d2)))')
        ax4 = lexpr('all d1. all x. (' + Fp + '(x,d1) <-> all d2. ($less(d2,d1) -> -' + Fm + '(x,d2)))')
        ax5 = lexpr('all d1. all x. (-' + Fm + '(x,d1) <-> all d2. ($lesseq(d2,d1) -> ' + Fp + '(x,d2)))')
        ax6  = lexpr('all d1. all x. (-' + Fp + '(x,d1) <-> all d2. ($lesseq(d1,d2) -> ' + Fm + '(x,d2)))')
        axiom.extend([ax3, ax4, ax5, ax6])
            

    axiom = set(axiom)
    axiom = list(axiom)
    #print(axiom)
    return axiom

def main():
    print('Gold answer/System answer')
    total_problem = 0
    correct_answer = 0

    for ex in examples:
        start = time.time()
        answer = prove(ex.premises, ex.conclusion)
        end = time.time() - start
        if answer == ex.gold:
            correct_answer += 1
            total_problem += 1
        else:
            total_problem += 1
        ex.show(answer, end)

    accuracy = correct_answer / total_problem
    print('Accuracy: {0:.4f}'.format(accuracy))

if __name__ == "__main__":
    main()
