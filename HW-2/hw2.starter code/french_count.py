import sys
from fst import FST
from fsmutils import composewords, trace

kFRENCH_TRANS = {0: "zero", 1: "un", 2: "deux", 3: "trois", 4:
                 "quatre", 5: "cinq", 6: "six", 7: "sept", 8: "huit",
                 9: "neuf", 10: "dix", 11: "onze", 12: "douze", 13:
                 "treize", 14: "quatorze", 15: "quinze", 16: "seize",
                 20: "vingt", 30: "trente", 40: "quarante", 50:
                 "cinquante", 60: "soixante", 100: "cent"}

kFRENCH_AND = 'et'

def prepare_input(integer):
    assert isinstance(integer, int) and integer < 1000 and integer >= 0, \
      "Integer out of bounds"
    return list("%03i" % integer)

def french_count():
    f = FST('french')

    f.add_state('start')
    f.initial_state = 'start'
    f.add_state('h')
    f.add_state('zh')
    f.add_state('t')
    f.add_state('zt')
    f.add_state('special')
    f.add_state('10')
    f.add_state('70')
    f.add_state('80')
    f.add_state('u')

    f.set_final('u')

    for ii in range(2,10):
        f.add_arc('start','h',str(ii),[kFRENCH_TRANS[ii] + " " + kFRENCH_TRANS[100]])

    f.add_arc('start','h','1',[kFRENCH_TRANS[100]])
    f.add_arc('start','zh','0',[])

    f.add_arc('zh','zt','0',[])
    f.add_arc('zh','10','1',[])
    for ii in range(2,7):
        f.add_arc('zh','t',str(ii),[kFRENCH_TRANS[ii*10]])

    f.add_arc('zh','70','7',[kFRENCH_TRANS[60]])
    f.add_arc('zh','80','8',[kFRENCH_TRANS[4] + " " + kFRENCH_TRANS[20]])
    f.add_arc('zh','10','9',[kFRENCH_TRANS[4] + " " + kFRENCH_TRANS[20]])


    for ii in range(2,7):
        f.add_arc('h','t',str(ii),[kFRENCH_TRANS[ii*10]])

    f.add_arc('h','10','1',[])
    f.add_arc('h','special','0',[])
    f.add_arc('special','u','0',[])
    for ii in range(1,10):
        f.add_arc('special','u',str(ii),[kFRENCH_TRANS[ii]])

    f.add_arc('h','70','7',[kFRENCH_TRANS[60]])
    f.add_arc('h','80','8',[kFRENCH_TRANS[4] + " " + kFRENCH_TRANS[20]])
    f.add_arc('h','10','9',[kFRENCH_TRANS[4] + " " + kFRENCH_TRANS[20]])

    for ii in range(2,10):
        f.add_arc('t','u',str(ii),[kFRENCH_TRANS[ii]])

    f.add_arc('t','u', '1', [kFRENCH_AND + " " + kFRENCH_TRANS[1]])
    f.add_arc('t','u', '0', [])

    for ii in range(0,7):
        f.add_arc('10','u',str(ii),[kFRENCH_TRANS[10+ii]])

    for ii in range(7,10):
        f.add_arc('10','u',str(ii),[kFRENCH_TRANS[10] + " " + kFRENCH_TRANS[ii]])

    f.add_arc('70','u','1',[kFRENCH_AND + " " + kFRENCH_TRANS[11]])
    for ii in [0,2,3,4,5,6]:
        f.add_arc('70','u',str(ii),[kFRENCH_TRANS[10+ii]])

    for ii in range(7,10):
        f.add_arc('70','u',str(ii),[kFRENCH_TRANS[10] + " " + kFRENCH_TRANS[ii]])

    for ii in range(1,10):
        f.add_arc('80','u',str(ii),[kFRENCH_TRANS[ii]])
    f.add_arc('80','u', '0', [])

    for ii in range(1,10):
        f.add_arc('zt','u',str(ii),[kFRENCH_TRANS[ii]])

    f.add_arc('zt','u','0',[kFRENCH_TRANS[0]])

    return f


if __name__ == '__main__':
    string_input = raw_input()
    user_input = int(string_input)
    f = french_count()
    if string_input:
        print user_input, '-->',
        print " ".join(f.transduce(prepare_input(user_input)))
