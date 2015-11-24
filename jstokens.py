# JavaScript: Numbers & Strings
#
# handling Numbers, Identifiers and Strings in a simpler version.
#
# a JavaScript IDENTIFIER must start with an upper- or
# lower-case character. It can then contain any number of upper- or
# lower-case characters or underscores. Its token.value is the textual
# string of the identifier.
#       Yes:    my_age
#       Yes:    cRaZy
#       No:     _starts_with_underscore
#
# a JavaScript NUMBER is one or more digits. A NUMBER
# can start with an optional negative sign. A NUMBER can contain a decimal
# point, which can then be followed by zero or more additional digits. Do
# not worry about hexadecimal (only base 10 is allowed in this problem).
# The token.value of a NUMBER is its floating point value (NOT a string).
#       Yes:    123
#       Yes:    -456
#       Yes:    78.9
#       Yes:    10.
#       No:     +5
#       No:     1.2.3
#
# a JavaScript STRING is zero or more characters
# contained in double quotes. A STRING may contain escaped characters.
# Notably, \" does not end a string. The token.value of a STRING is
# its contents (not including the outer double quotes).
#       Yes:    "hello world"
#       Yes:    "this has \"escaped quotes\""
#       No:     "no"t one string"
#
# Hint: float("2.3") = 2.3

import ply.lex as lex

tokens = (
    'ANDAND',       # &&
    'COMMA',        # ,
    'DIVIDE',       # /
    'ELSE',         # else
    'EQUAL',        # =
    'EQUALEQUAL',   # ==
    'FALSE',        # false
    'FUNCTION',     # function
    'GE',           # >=
    'GT',           # >
    'IDENTIFIER',   # identifier
    'IF',           # if
    'LBRACE',       # {
    'LE',           # <=
    'LPAREN',       # (
    'LT',           # <
    'MINUS',        # -
    'MOD',          # %
    'NOT',          # !
    'NUMBER',       # number
    'OROR',         # ||
    'PLUS',         # +
    'RBRACE',       # }
    'RETURN',       # return
    'RPAREN',       # )
    'SEMICOLON',    # ;
    'STRING',       # string
    'TIMES',        # *
    'TRUE',         # true
    'VAR',          # var
)

t_ignore = ' \t\v\r' # whitespace

def t_newline(t):
    r'\n'
    t.lexer.lineno += 1
    
states = (
    ('comment', 'exclusive'),
)

t_ANDAND = r'&&'
t_COMMA = r','
t_DIVIDE = r'/'
t_EQUALEQUAL = r'=='
t_EQUAL = r'='
t_GE = r'>='
t_GT = r'>'
t_LBRACE = r'{'
t_LE = r'<='
t_LPAREN = r'\('
t_LT = r'<'
t_MINUS = r'\-'
t_MOD = r'%'
t_NOT = r'!'
t_OROR = r'\|\|'
t_PLUS = r'\+'
t_RBRACE = r'}'
t_RPAREN = r'\)'
t_SEMICOLON = r';'
t_TIMES = r'\*'
t_IDENTIFIER = r'[a-zA-Z][_a-zA-Z]*'

def t_VAR(t):
    r'var'
    return t
    
def t_TRUE(t):
    r'true'
    return t

def t_RETURN(t):
    r'return'
    return t

def t_IF(t):
    r'if'
    return t

def t_FUNCTION(t):
    r'function'
    return t

def t_FALSE(t):
    r'false'
    return t

def t_ELSE(t):
    r'else'
    return t

def t_NUMBER(t):
    r'-?[0-9]+(?:\.[0-9]*)?'
    t.value = float(t.value)
    return t

def t_STRING(t):
    r'"((\\.)|[^"])*"'
    t.value = t.value[1:-1]
    return t

def t_comment(t):
    r'\/\*'
    t.lexer.begin('comment')
    
def t_comment_end(t):
    r'\*\/'
    t.lexer.lineno += t.value.count('\n')
    t.lexer.begin('INITIAL')
    pass
    
def t_comment_error(t):
    t.lexer.skip(1)

def t_eolcomment(t):
    r'//.*'
    pass

def t_error(t):
    print "JavaScript Lexer: Illegal character " + t.value[0]
    t.lexer.skip(1)

# This handle // end of line comments as well as /* delimited comments */.
#
# We will assume that JavaScript is case sensitive and that keywords like
# 'if' and 'true' must be written in lowercase. There are 26 possible
# tokens that you must handle. The 'tokens' variable below has been
# initialized below, listing each token's formal name (i.e., the value of
# token.type). In addition, each token has its associated textual string
# listed in a comment. For example, your lexer must convert && to a token
# with token.type 'ANDAND' (unless the && is found inside a comment).
#
# Hint 1: Use an exclusive state for /* comments */. You may want to define
# t_comment_ignore and t_comment_error as well.

if __name__ == '__main__':
    lexer = lex.lex()
    def test_lexer1(input_string):
        lexer.input(input_string)
        result = [ ]
        while True:
            tok = lexer.token()
            if not tok: break
            result = result + [tok.type,tok.value]
        return result

    input1 = 'some_identifier -12.34 "a \\"escape\\" b"'
    output1 = ['IDENTIFIER', 'some_identifier', 'NUMBER', -12.34, 'STRING',
               'a \\"escape\\" b']
    print test_lexer1(input1) == output1

    input2 = '-12x34'
    output2 = ['NUMBER', -12.0, 'IDENTIFIER', 'x', 'NUMBER', 34.0]
    print test_lexer1(input2) == output2
    
    def test_lexer2(input_string):
        lexer.input(input_string)
        result = [ ]
        while True:
            tok = lexer.token()
            if not tok: break
            result = result + [tok.type]
        return result
    
    input3 = """ - !  && () * , / ; { || } + < <= = == > >= else false function
    if return true var """
    
    output3 = ['MINUS', 'NOT', 'ANDAND', 'LPAREN', 'RPAREN', 'TIMES', 'COMMA',
               'DIVIDE', 'SEMICOLON', 'LBRACE', 'OROR', 'RBRACE', 'PLUS', 'LT', 'LE',
               'EQUAL', 'EQUALEQUAL', 'GT', 'GE', 'ELSE', 'FALSE', 'FUNCTION', 'IF',
               'RETURN', 'TRUE', 'VAR']
    
    test_output3 = test_lexer2(input3)
    
    print test_lexer2(input3) == output3
    
    input4 = """
    if // else mystery  
    =/*=*/= 
    true /* false 
    */ return"""
    
    output4 = ['IF', 'EQUAL', 'EQUAL', 'TRUE', 'RETURN']
    
    print test_lexer2(input4) == output4
