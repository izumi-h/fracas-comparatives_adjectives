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

def prover9_axioms(Fpos, Fneg, Verbs, Objs, Fex, predicates):
    axiom = []
    Fp = Fm = ''

    foFla = ''

    for pred in predicates:

        # Adjectives
        if ((pred[0] in Fpos) or (pred[0] in Fneg)):

            if (pred[1][1] == '_np(_u,_th(_u))'):
                defcom = lexpr('all x. (' + pred[0] + '(x,_np(_u,_th(_u))) <-> ' + pred[0] + '(x,_np(_person,_th(_person))))')
                axiom.extend([defcom])
                
            # Number
            if ('10' in (pred[1])[1]):
                num10 = lexpr('10 = ' + 'S('*10 + 'O' + ')'*10)
                axiom.extend([num10])
            elif ('11' in (pred[1])[1]):
                num11 = lexpr('11 = ' + 'S('*11 + 'O' + ')'*11)
                axiom.extend([num11])
            elif ('20' in (pred[1])[1]):
                num20 = lexpr('20 = ' + 'S('*20 + 'O' + ')'*20)
                axiom.extend([num20])
            elif ('500' in (pred[1])[1]):
                num500 = lexpr('500 = ' + 'S('*500 + 'O' + ')'*500)
                axiom.extend([num500])
            elif ('3000' in (pred[1])[1]):
                num3000 = lexpr('3000 = ' + 'S('*3000 + 'O' + ')'*3000)
                axiom.extend([num3000])
            elif ('2500' in (pred[1])[1]):
                num2500 = lexpr('2500 = ' + 'S('*2500 + 'O' + ')'*2500)
                axiom.extend([num2500])
            elif ('5500' in (pred[1])[1]):
                num5500 = lexpr('5500 = ' + 'S('*5500 + 'O' + ')'*5500)
                axiom.extend([num5500])
            else:
                pass
            
            if ('$sum' in (pred[1])[1]):

                # Robinson arithmetic
                q1 = lexpr('all x. (-(O = S(x)))')
                q2 = lexpr('all x. all y. ((S(x) = S(y)) -> (x = y))')
                q3 = lexpr('all x. ((-(x = O)) -> exists y. (x = S(y)))')
                q4 = lexpr('all x. (($sum(x,O)) = x)')
                q5 = lexpr('all x. all y. (($sum(x,S(y))) = S($sum(x,y)))')
                q6 = lexpr('all x. all y. (($lesseq(x,y)) <-> (exists z. (($sum(x,z)) = y)))')
                axiom.extend([q1, q2, q3, q4, q5, q6])

            # Positive adjectives
            if (pred[0] in Fpos):
            
                Fp = pred[0]

                cp1 = lexpr('all x. all y. ((exists d1. (' + Fp + '(x,d1) & -' + Fp + '(y,d1))) -> all d2. (' + Fp + '(y,d2) -> ' + Fp + '(x,d2)))')
                ax2 = lexpr('all d1. all x. (' + Fp + '(x,d1) <-> all d2. ($lesseq(d2,d1) -> ' + Fp + '(x,d2)))')
                axiom.extend([cp1, ax2])

                if ('_th(_u)' in ((pred[1])[1])):
                    thp = lexpr('all x. (' + Fp + '(x,_th(_u)) <-> exists d. (' + Fp + '(x,d) & ($less(_th(_u),d))))')
                    axiom.extend([thp])


            # Negative adjectives
            elif (pred[0] in Fneg):

                Fm = pred[0]

                cp2 = lexpr('all x. all y. ((exists d1. (' + Fm + '(x,d1) & -' + Fm + '(y,d1))) -> all d2. (' + Fm + '(y,d2) -> ' + Fm + '(x,d2)))')
                ax1 = lexpr('all d1. all x. (' + Fm + '(x,d1) <-> all d2. ($lesseq(d1,d2) -> ' + Fm + '(x,d2)))')
                axiom.extend([cp2, ax1])

                if ('_th(_u)' in ((pred[1])[1])):
                    thm = lexpr('all x. (' + Fm + '(x,_th(_u)) <-> exists d. (' + Fm + '(x,d) & ($less(d,_th(_u)))))')
                    axiom.extend([thm])
                
        elif (pred[0] == '$less'):
                
            # less than ($less)
            lt_trans = lexpr('all x y z. (($less(x,y) & $less(y,z)) -> $less(x,z))')
            lt_asym = lexpr('all x y. (($less(x,y) & $less(y,x)) -> (x = y))') 
            lt_irrefl = lexpr('all x. -$less(x,x)') 
            axiom.extend([lt_trans, lt_asym, lt_irrefl])
                
        elif (pred[0] == '$lesseq'):

            # less or equal ($lesseq) 
            le_trans = lexpr('all x y z. (($lesseq(x,y) & $lesseq(y,z)) -> $lesseq(x,z))')
            le_asym = lexpr('all x y. (($lesseq(x,y) & $lesseq(y,x)) -> (x = y))')
            le_irrefl = lexpr('all x. $lesseq(x,x)')
            axiom.extend([le_trans, le_asym, le_irrefl])

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
        ax = lexpr('all x. all y. (($less(x,y)) <-> ($lesseq(x,y) & -(x = y)))')
        axiom.extend([ax])
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
