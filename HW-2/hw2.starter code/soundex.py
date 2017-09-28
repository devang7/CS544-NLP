from fst import FST
import string, sys
from fsmutils import composechars, trace

def letters_to_numbers():
    """
    Returns an FST that converts letters to numbers as specified by
    the soundex algorithm
    """

    # Let's define our first FST
    f1 = FST('soundex-generate')

    # Indicate that '1' is the initial state
    f1.add_state('start')
    f1.add_state('vowel')
    f1.add_state('state1')
    f1.add_state('state2')
    f1.add_state('state3')
    f1.add_state('state4')
    f1.add_state('state5')
    f1.add_state('state6')
    f1.initial_state = 'start'

    # Set all the final states
    f1.set_final('vowel')
    f1.set_final('state1')
    f1.set_final('state2')
    f1.set_final('state3')
    f1.set_final('state4')
    f1.set_final('state5')
    f1.set_final('state6')

    # Add the rest of the arcs

    for letter in ['a','A','e','E','h','H','i','I','o','O','u','U','w','W','y','Y']:
        f1.add_arc('start','vowel', (letter), (letter))
        f1.add_arc('vowel','vowel', (letter), ())
        f1.add_arc('state1','vowel', (letter), ())
        f1.add_arc('state2','vowel', (letter), ())
        f1.add_arc('state3','vowel', (letter), ())
        f1.add_arc('state4','vowel', (letter), ())
        f1.add_arc('state5','vowel', (letter), ())
        f1.add_arc('state6','vowel', (letter), ())

    for letter in ['b','B','f','F','p','P','v','V']:
        f1.add_arc('start','state1', (letter), (letter))
        f1.add_arc('vowel','state1', (letter), ('1'))
        f1.add_arc('state1','state1', (letter), ())
        f1.add_arc('state2','state1', (letter), ('1'))
        f1.add_arc('state3','state1', (letter), ('1'))
        f1.add_arc('state4','state1', (letter), ('1'))
        f1.add_arc('state5','state1', (letter), ('1'))
        f1.add_arc('state6','state1', (letter), ('1'))

    for letter in ['c','C','g','G','j','J','k','K','q','Q','s','S','x','X','z','Z']:
        f1.add_arc('start','state2', (letter), (letter))
        f1.add_arc('vowel','state2', (letter), ('2'))
        f1.add_arc('state2','state2', (letter), ())
        f1.add_arc('state1','state2', (letter), ('2'))
        f1.add_arc('state3','state2', (letter), ('2'))
        f1.add_arc('state4','state2', (letter), ('2'))
        f1.add_arc('state5','state2', (letter), ('2'))
        f1.add_arc('state6','state2', (letter), ('2'))

    for letter in ['d','D','t','T']:
        f1.add_arc('start','state3', (letter), (letter))
        f1.add_arc('vowel','state3', (letter), ('3'))
        f1.add_arc('state3','state3', (letter), ())
        f1.add_arc('state1','state3', (letter), ('3'))
        f1.add_arc('state2','state3', (letter), ('3'))
        f1.add_arc('state4','state3', (letter), ('3'))
        f1.add_arc('state5','state3', (letter), ('3'))
        f1.add_arc('state6','state3', (letter), ('3'))

    for letter in ['l','L']:
        f1.add_arc('start','state4', (letter), (letter))
        f1.add_arc('vowel','state4', (letter), ('4'))
        f1.add_arc('state4','state4', (letter), ())
        f1.add_arc('state1','state4', (letter), ('4'))
        f1.add_arc('state2','state4', (letter), ('4'))
        f1.add_arc('state3','state4', (letter), ('4'))
        f1.add_arc('state5','state4', (letter), ('4'))
        f1.add_arc('state6','state4', (letter), ('4'))

    for letter in ['m','M','n','N']:
        f1.add_arc('start','state5', (letter), (letter))
        f1.add_arc('vowel','state5', (letter), ('5'))
        f1.add_arc('state5','state5', (letter), ())
        f1.add_arc('state1','state5', (letter), ('5'))
        f1.add_arc('state2','state5', (letter), ('5'))
        f1.add_arc('state3','state5', (letter), ('5'))
        f1.add_arc('state4','state5', (letter), ('5'))
        f1.add_arc('state6','state5', (letter), ('5'))

    for letter in ['r','R']:
        f1.add_arc('start','state6', (letter), (letter))
        f1.add_arc('vowel','state6', (letter), ('6'))
        f1.add_arc('state6','state6', (letter), ())
        f1.add_arc('state1','state6', (letter), ('6'))
        f1.add_arc('state2','state6', (letter), ('6'))
        f1.add_arc('state3','state6', (letter), ('6'))
        f1.add_arc('state4','state6', (letter), ('6'))
        f1.add_arc('state5','state6', (letter), ('6'))

    """trace(f1, ['m','n','e','m','o','n','i','c'])"""
    return f1

    # The stub code above converts all letters except the first into '0'.
    # How can you change it to do the right conversion?

def truncate_to_three_digits():
    """
    Create an FST that will truncate a soundex string to three digits
    """

    # Ok so now let's do the second FST, the one that will truncate
    # the number of digits to 3
    f2 = FST('soundex-truncate')

    # Indicate initial and final states
    f2.add_state('start')
    f2.initial_state = 'start'
    f2.add_state('dig1')
    f2.add_state('dig2')
    f2.add_state('dig3')
    f2.set_final('start')
    f2.set_final('dig1')
    f2.set_final('dig2')
    f2.set_final('dig3')
    # Add the arcs
    for letter in string.ascii_letters:
        f2.add_arc('start','start', (letter), (letter))

    for letter in ['1','2','3','4','5','6']:
        f2.add_arc('start','dig1', (letter), (letter))
        f2.add_arc('dig1','dig2', (letter), (letter))
        f2.add_arc('dig2','dig3', (letter), (letter))
        f2.add_arc('dig3','dig3', (letter), ())

    return f2

    # The above stub code doesn't do any truncating at all -- it passes letter and number input through
    # what changes would make it truncate digits to 3?

def add_zero_padding():
    # Now, the third fst - the zero-padding fst
    f3 = FST('soundex-padzero')

    f3.add_state('start')
    f3.add_state('dig1')
    f3.add_state('dig2')
    f3.add_state('dig3')

    f3.initial_state = 'start'
    f3.set_final('dig3')

    f3.add_arc('start','dig1',(),('0'))
    f3.add_arc('dig1', 'dig2', (), ('0'))
    f3.add_arc('dig2', 'dig3', (), ('0'))

    for letter in string.letters:
        f3.add_arc('start', 'start', (letter), (letter))

    for letter in ['1','2','3','4','5','6']:
        f3.add_arc('start','dig1',(letter),(letter))
        f3.add_arc('dig1','dig2',(letter),(letter))
        f3.add_arc('dig2','dig3',(letter),(letter))

    return f3

letters_to_numbers()
    # The above code adds zeroes but doesn't have any padding logic. Add some!
if __name__ == '__main__':
    user_input = raw_input().strip()
    f1 = letters_to_numbers()
    f2 = truncate_to_three_digits()
    f3 = add_zero_padding()

    if user_input:
        print("%s -> %s" % (user_input, composechars(tuple(user_input), f1, f2, f3)))
