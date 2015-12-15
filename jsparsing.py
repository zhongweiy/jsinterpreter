# TODO solve WARNING: WARNING: No ignore rule is defined for exclusive state 'comment'

# The starting non-terminal is "js" for "JavaScript program" -- which is
# just a list of "elements" (to be defined shortly). The parse tree you
# must return is simply a list containing all of the elements.
#
#       js -> element js
#       js ->
#
# An element is either a function declaration:
#
#       element -> FUNCTION IDENTIFIER ( optparams ) compoundstmt
#
# or a statement following by a semi-colon:
#
#       element -> stmt ;
#
# The parse tree for the former is the tuple ("function",name,args,body),
# the parse tree for the latter is the tuple ("stmt",stmt).
#
#       optparams ->
#       optparams -> params
#       params -> IDENTIFIER , params
#       params -> IDENTIFIER
#
# optparams is a comma-separated list of zero or more identifiers. The
# parse tree for optparams is the list of all of the identifiers.
#
#       compoundstmt -> { statements }
#       statements -> stmt ; statements
#       statements ->
#
# A compound statement is a list of zero or more statements, each of which
# is followed by a semicolon. (In real JavaScript, some statements do not
# need to be followed by a semicolon. For simplicity, we will assume that
# they all have to.) The parse tree for a compound statement is just the
# list of all of the statements.
#
# We will consider six kinds of possible statements:
#
#       stmt -> IF exp compoundstmt
#       stmt -> IF exp compoundstmt ELSE compoundstmt
#       stmt -> IDENTIFIER = exp
#       stmt -> RETURN exp
#
# The "if", "assignment" and "return" statements should be familiar. It is
# also possible to use "var" statements in JavaScript to introduce new
# local variables (this is not necessary in Python):
#
#       stmt -> VAR IDENTIFIER = exp
#
# And it is also possible to treat an expression as a statement. This is
#
#       stmt -> exp
#
# The parse trees for statements are all tuples:
#       ("if-then", conditional, then_branch)
#       ("if-then-else", conditional, then_branch, else_branch)
#       ("assign", identifier, new_value)
#       ("return", expression)
#       ("var", identifier, initial_value)
#       ("exp", expression)
# Recall the names of our tokens:
#
# 'ANDAND',       # &&          | 'LT',           # <
# 'COMMA',        # ,           | 'MINUS',        # -
# 'DIVIDE',       # /           | 'NOT',          # !
# 'ELSE',         # else        | 'NUMBER',       # 1234
# 'EQUAL',        # =           | 'OROR',         # ||
# 'EQUALEQUAL',   # ==          | 'PLUS',         # +
# 'FALSE',        # FALSE       | 'RBRACE',       # }
# 'FUNCTION',     # function    | 'RETURN',       # return
# 'GE',           # >=          | 'RPAREN',       # )
# 'GT',           # >           | 'SEMICOLON',    # ;
# 'IDENTIFIER',   # factorial   | 'STRING',       # "hello"
# 'IF',           # if          | 'TIMES',        # *
# 'LBRACE',       # {           | 'TRUE',         # TRUE
# 'LE',           # <=          | 'VAR',          # var
# 'LPAREN',       # (           |
import ply.yacc as yacc
import ply.lex as lex
import jstokens                 # use our JavaScript lexer
from jstokens import tokens     # use out JavaScript tokens

start = 'js'    # the start symbol in our grammar

def p_js(p):
    'js : element js'
    p[0] = [p[1]] + p[2]
def p_js_empty(p):
    'js : '
    p[0] = [ ]

def p_element_function(p):
    'element : FUNCTION IDENTIFIER LPAREN optparams RPAREN compoundstmt'
    p[0] = ("function", p[2], p[4], p[6])

def p_element_stmt(p):
    'element : stmt SEMICOLON'
    p[0] = ("stmt", p[1])

# TODO this rule seems introduce warning    
# def p_element_stmt_without_semi(p):
#     'element : stmt'
#     p[0] = p[1]

def p_optparams(p):
    'optparams : params'
    p[0] = p[1]

def p_optparams_empty(p):
    'optparams : '
    p[0] = []

def p_params(p):
    'params : IDENTIFIER COMMA params'
    p[0] = [p[1]] + p[3]

def p_params_last(p):
    'params : IDENTIFIER'
    p[0] = [p[1]]

def p_compoundstmt(p):
    'compoundstmt : LBRACE statements RBRACE'
    p[0] = p[2]

def p_statements(p):
    'statements : stmt SEMICOLON statements'
    p[0] = [p[1]] + p[3]

def p_statements_last(p):
    'statements : '
    p[0] = []

def p_stmt_if(p):
    'stmt : IF exp compoundstmt'
    p[0] = ("if-then", p[2], p[3])

def p_stmt_ifelse(p):
    'stmt : IF exp compoundstmt ELSE compoundstmt'
    p[0] = ("if-then-else", p[2], p[3], p[5])

def p_stmt_while(p):
    'stmt : WHILE exp compoundstmt'
    p[0] = ("while", p[2], p[3])

def p_stmt_assign(p):
    'stmt : IDENTIFIER EQUAL exp'
    p[0] = ("assign", p[1], p[3])

def p_stmt_return(p):
    'stmt : RETURN exp'
    p[0] = ("return", p[2])

def p_stmt_var(p):
    'stmt : VAR IDENTIFIER EQUAL exp'
    p[0] = ("var", p[2], p[4])

def p_stmt_exp(p):
    'stmt : exp'
    p[0] = ("exp", p[1])

## expression

# First, there are a number of "base cases" in our grammar -- simple
# expressions that are not recursive. In each case, the abstract syntax
# tree is a simple tuple.
#
#       exp -> IDENTIFIER       # ("identifier",this_identifier_value)
#       exp -> NUMBER           # ("number",this_number_value)
#       exp -> STRING           # ("string",this_string_value)
#       exp -> TRUE             # ("true","true")
#       exp -> FALSE            # ("false","false")
#
# There are also two unary expressions types -- expressions built
# recursively from a single child.
#
#       exp -> NOT exp          # ("not", child_parse_tree)
#       exp -> ( exp )          # child_parse_tree
#
# For NOT, the parse tree is a simple tuple. For parentheses, the parse
# tree is even simpler: just return the child parse tree unchanged!
#
# There are many binary expressions. To deal with ambiguity, we have to
# assign them precedence and associativity.  I will list the lowest
# predecence binary operators first, and then continue in order of
# increasing precedence:
#
#    exp ->   exp || exp        # lowest precedence, left associative
#           | exp && exp        # higher precedence, left associative
#           | exp == exp        # higher precedence, left associative
#           | exp < exp         # /---
#           | exp > exp         # | higher precedence,
#           | exp <= exp        # | left associative
#           | exp >= exp        # \---
#           | exp + exp         # /--- higher precedence,
#           | exp - exp         # \--- left associative
#           | exp * exp         # /--- higher precedence,
#           | exp / exp         # \--- left associative
#
# In each case, the parse tree is the tuple:
#
#       ("binop", left_child, operator_token, right_child)
#
# For this assignment, the unary NOT operator has the highest precedence of
# all and is right associative.
#
# Finally, it is possible to have a function call as an expression:
#
#       exp -> IDENTIFIER ( optargs )
#
# The parse tree is the tuple ("call", function_name, arguments).
#
#       optargs ->
#       optargs -> args
#       args -> exp , args
#       args -> exp
#
# It is also possible to have anonymous functions (sometimes called
# lambda expressions) in JavaScript.
#
#       exp -> function ( optparams ) compoundstmt
#
# Arguments are comma-separated expressions. The parse tree for args or
# optargs is just the list of the parse trees of the component expressions.

precedence = (
    # Fill in the precedence and associativity. List the operators
    # in order of _increasing_ precedence (start low, go to high).
    ('left', 'OROR'),
    ('left', 'ANDAND'),
    ('left', 'EQUALEQUAL'),
    ('left', 'LT', 'GT', 'LE', 'GE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('right', 'NOT'),
)

# Here's the rules for simple expressions.
def p_exp_identifier(p):
    'exp : IDENTIFIER'
    p[0] = ("identifier",p[1])

def p_exp_number(p):
    'exp : NUMBER'
    p[0] = ('number',p[1])

def p_exp_string(p):
    'exp : STRING'
    p[0] = ('string',p[1])
    
def p_exp_true(p):
    'exp : TRUE'
    p[0] = ('true','true')
    
def p_exp_false(p):
    'exp : FALSE'
    p[0] = ('false','false')
    
def p_exp_not(p):
    'exp : NOT exp'
    p[0] = ('not', p[2])

def p_exp_parens(p):
    'exp : LPAREN exp RPAREN'
    p[0] = p[2]

# This is what the rule for anonymous functions
def p_exp_lambda(p):
    'exp : FUNCTION LPAREN optparams RPAREN compoundstmt'
    p[0] = ("function",p[3],p[5])

def p_exp_bin_opt(p):
    """exp : exp OROR exp
           | exp ANDAND exp
           | exp EQUALEQUAL exp
           | exp MOD exp
           | exp LT exp
           | exp GT exp
           | exp LE exp
           | exp GE exp
           | exp PLUS exp
           | exp MINUS exp
           | exp TIMES exp
           | exp DIVIDE exp"""
    p[0] = ("binop", p[1], p[2], p[3])
    
def p_exp_call(p):
    'exp : IDENTIFIER LPAREN optargs RPAREN'
    p[0] = ("call", p[1], p[3])

# TODO add anonymous functions call exp

def p_exp_optargs_last(p):
    'optargs : '
    p[0] = []

def p_exp_optargs(p):
    'optargs : args'
    p[0] = p[1]

def p_exp_args(p):
    'args : exp COMMA args'
    p[0] = [p[1]] + p[3]

def p_exp_args_last(p):
    'args : exp'
    p[0] = [p[1]]

if __name__ == '__main__':
    jslexer = lex.lex(module=jstokens)
    jsparser = yacc.yacc(debug=True)

    # test
    def test_parser(input_string):
        jslexer.input(input_string)
        parse_tree = jsparser.parse(input_string,lexer=jslexer)
        return parse_tree

    # Simple binary expression.
    jstext1_exp = "x + 1;"
    jstree1_exp = [('stmt', ('exp', ('binop', ('identifier', 'x'), '+', ('number', 1.0))))]
    print test_parser(jstext1_exp) == jstree1_exp

    # Simple associativity.
    jstext2_exp = "1 - 2 - 3;"   # means (1-2)-3
    jstree2_exp = [('stmt', ('exp', ('binop', ('binop', ('number', 1.0), '-', ('number', 2.0)), '-',
                   ('number', 3.0))))]
    print test_parser(jstext2_exp) == jstree2_exp
    
    # Precedence and associativity.
    jstext3_exp = "1 + 2 * 3 - 4 / 5 * (6 + 2);"
    jstree3_exp = [('stmt', ('exp', ('binop', ('binop', ('number', 1.0), '+', ('binop', ('number', 2.0), '*', ('number', 3.0))), '-', ('binop', ('binop', ('number', 4.0), '/', ('number', 5.0)), '*', ('binop', ('number', 6.0), '+', ('number', 2.0))))))]
    print test_parser(jstext3_exp) == jstree3_exp

    # String and boolean constants, comparisons.
    jstext4_exp = ' "hello" == "goodbye" || true && false ;'
    jstree4_exp = [('stmt', ('exp', ('binop', ('binop', ('string', 'hello'), '==', ('string', 'goodbye')), '||', ('binop', ('true', 'true'), '&&', ('false', 'false')))))]
    print test_parser(jstext4_exp) == jstree4_exp

    # Not, precedence, associativity.
    jstext5_exp = "! ! tricky || 3 < 5;"
    jstree5_exp = [('stmt', ('exp', ('binop', ('not', ('not', ('identifier', 'tricky'))), '||', ('binop', ('number', 3.0), '<', ('number', 5.0)))))]
    print test_parser(jstext5_exp) == jstree5_exp

    # nested function calls!
    jstext6_exp = "apply(1, 2 + eval(recursion), sqrt(2));"
    jstree6_exp = [('stmt', ('exp', ('call', 'apply', [('number', 1.0), ('binop', ('number', 2.0), '+', ('call', 'eval', [('identifier', 'recursion')])), ('call', 'sqrt', [('number', 2.0)])])))]
    print test_parser(jstext6_exp) == jstree6_exp

    # Simple function with no arguments and a one-statement body.
    jstext1_stm = "function myfun() { return nothing ; }"
    jstree1_stm = [('function', 'myfun', [], [('return', ('identifier', 'nothing'))])]

    print test_parser(jstext1_stm) == jstree1_stm

    # Function with multiple arguments.
    jstext2_stm = "function nobletruths(dukkha,samudaya,nirodha,gamini) { return buddhism ; }"
    jstree2_stm = [('function', 'nobletruths', ['dukkha', 'samudaya', 'nirodha', 'gamini'], [('return', ('identifier', 'buddhism'))])]
    print test_parser(jstext2_stm) == jstree2_stm

    # Multiple top-level elemeents, each of which is a var, assignment or
    # expression statement.
    jstext3_stm = """var view = right;
    var intention = right;
    var speech = right;
    action = right;
    livelihood = right;
    effort_right;
    mindfulness_right;
    concentration_right;"""
    jstree3_stm = [('stmt', ('var', 'view', ('identifier', 'right'))), ('stmt', ('var', 'intention', ('identifier', 'right'))), ('stmt', ('var', 'speech', ('identifier', 'right'))), ('stmt', ('assign', 'action', ('identifier', 'right'))), ('stmt', ('assign', 'livelihood', ('identifier', 'right'))), ('stmt', ('exp', ('identifier', 'effort_right'))), ('stmt', ('exp', ('identifier', 'mindfulness_right'))), ('stmt', ('exp', ('identifier', 'concentration_right')))]
    print test_parser(jstext3_stm) == jstree3_stm

    # if-then and if-then-else and compound statements.
    jstext4_stm = """
    if cherry {
    orchard;
    if uncle_vanya {
    anton ;
    chekov ;
    } else { 
    } ;
    nineteen_oh_four ;
    } ;
    """
    jstree4_stm = [('stmt', ('if-then', ('identifier', 'cherry'), [('exp', ('identifier', 'orchard')), ('if-then-else', ('identifier', 'uncle_vanya'), [('exp', ('identifier', 'anton')), ('exp', ('identifier', 'chekov'))], []), ('exp', ('identifier', 'nineteen_oh_four'))]))]
    print test_parser(jstext4_stm) == jstree4_stm

    # BUG
    jstext5_stm = """
    function add_func() {
      function count_func() {
      };
    }

    add_func();
    """
    print test_parser(jstext5_stm)

    jstext6_stm = """
    function add_func() {
      var counter = 0;
      var add = function() {
        counter = counter + 1;
        return counter;
      };
      return add;
    }
    
    var add = add_func();
    add();
    write(add());
    """
    print test_parser(jstext6_stm)
