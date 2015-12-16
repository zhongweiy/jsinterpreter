import unittest
import ply.lex as lex
import ply.yacc as yacc
import jsparsing, jstokens, jsinterpretast

def interpret(program_str):
    jslexer = lex.lex(module=jstokens)
    jsparser = yacc.yacc(module=jsparsing)
    jslexer.input(program_str)
    ast = jsparser.parse(program_str, lexer=jslexer)
    jsinterpretast.interpret_ast(ast)

class TestFunc(unittest.TestCase):
    def test_func(self):
        program_str = """
        function sqrt(x) {
          return x * x;
        }
        return sqrt(3);
        """
        try:
            interpret(program_str)
        except Exception as ret:
            self.assertEqual(9, ret.args[0])

if __name__ == '__main__':
    unittest.main()

