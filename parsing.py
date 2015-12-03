# Writing Closure

# We are currently looking at chart[i] and we see x => ab . cd from j

# Write the Python procedure, closure, that takes five parameters:

#   grammar: the grammar using the previously described structure
#   i: a number representing the chart state that we are currently looking at
#   x: a single nonterminal
#   ab and cd: lists of many things

# The closure function should return all the new parsing states that we want to
# add to chart position i
def closure (grammar, i, x, ab, cd):
    return [ (g[0], [], g[1], i) for g in grammar
             if cd != [] and g[0] == cd[0]]

# grammar = [
#     ("exp", ["exp", "+", "exp"]),
#     ("exp", ["exp", "-", "exp"]),
#     ("exp", ["(", "exp", ")"]),
#     ("exp", ["num"]),
#     ("t",["I","like","t"]),
#     ("t",[""])
# ]

# print closure(grammar,0,"exp",["exp","+"],["exp"]) == [('exp', [], ['exp', '+', 'exp'], 0), ('exp', [], ['exp', '-', 'exp'], 0), ('exp', [], ['(', 'exp', ')'], 0), ('exp', [], ['num'], 0)]
# print closure(grammar,0,"exp",[],["exp","+","exp"]) == [('exp', [], ['exp', '+', 'exp'], 0), ('exp', [], ['exp', '-', 'exp'], 0), ('exp', [], ['(', 'exp', ')'], 0), ('exp', [], ['num'], 0)]
# print closure(grammar,0,"exp",["exp"],["+","exp"]) == []

# Writing Shift

# We are currently looking at chart[i] and we see x => ab . cd from j. The input is tokens.

# Your procedure, shift, should either return None, at which point there is
# nothing to do or will return a single new parsing state that presumably
# involved shifting over the c if c matches the ith token.

def shift (tokens, i, x, ab, cd, j):
    nextstate = None
    if cd != [] and tokens[i] == cd[0]:
        nextstate = (x, ab + [cd[0]], cd[1:], j)
    return nextstate

# print shift(["exp","+","exp"],2,"exp",["exp","+"],["exp"],0) == ('exp', ['exp', '+', 'exp'], [], 0)
# print shift(["exp","+","exp"],0,"exp",[],["exp","+","exp"],0) == ('exp', ['exp'], ['+', 'exp'], 0)
# print shift(["exp","+","exp"],3,"exp",["exp","+","exp"],[],0) == None
# print shift(["exp","+","ANDY LOVES COOKIES"],2,"exp",["exp","+"],["exp"],0) == None


# Writing Reductions

# We are looking at chart[i] and we see x => ab . cd from j.
# only do reductions if cd == []

def reductions(chart, i, x, ab, cd, j):
    return [ (s[0], s[1] + [s[2][0]], s[2][1:], s[3]) for s in chart[j]
             if cd == [] and s[2] != [] and x == s[2][0] ]


# chart = {0: [('exp', ['exp'], ['+', 'exp'], 0), ('exp', [], ['num'], 0), ('exp', [], ['(', 'exp', ')'], 0), ('exp', [], ['exp', '-', 'exp'], 0), ('exp', [], ['exp', '+', 'exp'], 0)], 1: [('exp', ['exp', '+'], ['exp'], 0)], 2: [('exp', ['exp', '+', 'exp'], [], 0)]}

# print reductions(chart,2,'exp',['exp','+','exp'],[],0) == [('exp', ['exp'], ['-', 'exp'], 0), ('exp', ['exp'], ['+', 'exp'], 0)]

# chart1 = {0: [('exp', [], ['num'], 0), ('exp', [], ['exp', '-', 'exp'], 0), ('exp', [], ['exp', '+', 'exp'], 0)]}
# print reductions(chart1, 1, 'exp', ['num'], [], 0)


def addtochart(theset, index, elt):
    if not (elt in theset[index]):
        theset[index] = [elt] + theset[index]
        return True
    else:
        return False

def parse(tokens,grammar):
    global work_count
    work_count = 0
    tokens = tokens + [ "end_of_input_marker" ]
    chart = {}
    start_rule = grammar[0]
    for i in range(len(tokens)+1):
        chart[i] = [ ]
    start_state = (start_rule[0], [], start_rule[1], 0)
    chart[0] = [ start_state ]
    for i in range(len(tokens)):
        while True:
            changes = False
            for state in chart[i]:
                # State ===   x -> a b . c d , j
                x = state[0]
                ab = state[1]
                cd = state[2]
                j = state[3]

                # Current State ==   x -> a b . c d , j
                # Option 1: For each grammar rule c -> p q r
                # (where the c's match)
                # make a next state               c -> . p q r , i
                # English: We're about to start parsing a "c", but
                #  "c" may be something like "exp" with its own
                #  production rules. We'll bring those production rules in.
                next_states = closure(grammar, i, x, ab, cd)
                for next_state in next_states:
                    changes = addtochart(chart,i,next_state) or changes
                work_count = work_count + len(grammar)

                # Current State ==   x -> a b . c d , j
                # Option 2: If tokens[i] == c,
                # make a next state               x -> a b c . d , j
                # in chart[i+1]
                # English: We're looking for to parse token c next
                #  and the current token is exactly c! Aren't we lucky!
                #  So we can parse over it and move to j+1.
                next_state = shift(tokens, i, x, ab, cd, j)
                if next_state != None:
                    changes = addtochart(chart,i+1,next_state) or changes
                work_count = work_count + len(grammar)

                # Current State ==   x -> a b . c d , j
                # Option 3: If cd is [], the state is just x -> a b . , j
                # for each p -> q . x r , l in chart[j]
                # make a new state                p -> q x . r , l
                # in chart[i]
                # English: We just finished parsing an "x" with this token,
                #  but that may have been a sub-step (like matching "exp -> 2"
                #  in "2+3"). We should update the higher-level rules as well.
                next_states = reductions(chart, i, x, ab, cd, j)
                work_count = work_count + len(chart[j])
                for next_state in next_states:
                    changes = addtochart(chart,i,next_state) or changes

                # We're done if nothing changed!
            if not changes:
                break

## Uncomment this block if you'd like to see the chart printed.
    for i in range(len(tokens)):
        print "== chart " + str(i)
        for state in chart[i]:
            x = state[0]
            ab = state[1]
            cd = state[2]
            j = state[3]
            print "    " + x + " ->",
            for sym in ab:
                print " " + sym,
            print " .",
            for sym in cd:
                print " " + sym,
            print "  from " + str(j)

# Uncomment this block if you'd like to see the chart printed
# in cases where it's important to see quotes in the grammar
    # for i in range(len(tokens)):
    #     print "== chart " + str(i)
    #     for state in chart[i]:
    #         x = state[0]
    #         ab = state[1]
    #         cd = state[2]
    #         j = state[3]
    #         print "    " + x.__repr__() + " ->",
    #         for sym in ab:
    #             print " " + sym.__repr__(),
    #         print " .",
    #         for sym in cd:
    #             print " " + sym.__repr__(),
    #         print "  from " + str(j)

    accepting_state = (start_rule[0], start_rule[1], [], 0)
    return accepting_state in chart[len(tokens)-1]

# grammar = [
#     ("S", ["P" ]) ,
#     ("P", ["P", "P"]),
#     ("P", ["(" , "P", ")" ]),
#     ("P", [ ]) ,
# ]
# tokens = [ "(", "(", ")", ")", "(", ")"]
# result=parse(tokens, grammar)
# print result

# grammar = [
#     ("S", ["id", "(", "OPTARGS", ")"]),
#     ("OPTARGS", []),
#     ("OPTARGS", ["ARGS"]),
#     ("ARGS", ["exp", ",", "ARGS"]),
#     ("ARGS", ["exp"]),
#     ]

# grammar = [
#     ("S", ["E"]),
#     ("E", ["E", "+", "E"]),
#     ("E", ["E", "-", "E"]),
#     ("E", ["num"]),
#     ("E", ["string"]),
#     ("t", ["hi"])
#     ]
# tokens = ["num", "+", "num"]

grammar = [
    ("S", ["P"]),
    ("P", ["x"]),
    ("P", ["P", "P"]),
    ("P", [""]),
    ]
tokens = ["x", "x"]
print parse(tokens, grammar)
