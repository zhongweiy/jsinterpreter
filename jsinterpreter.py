'''
Global data structure definition
 - environment:
   global-environment: (None, {key-values})
   environment: (global-environment, {key-values})
   environment: (environment, {key-values})
'''

import unittest,copy

# Return will throw an excception
# Function Calls: new environments, catch return values
def eval_stmt(tree,environment):
    stmttype = tree[0]
    if stmttype == "function":
        # ("function", identifier, optparams, compoundstmt)
        fname = tree[1]
        fparams = tree[2]
        fbody = tree[3]
        # TODO Is it correct to define function's enclosing environment?
        fenv = environment
        value = ("function", fparams, fbody, fenv)
        env_add(fname, value, environment)
    elif stmttype == "return":
        retval = eval_exp(tree[1],environment)
        raise Exception(retval)
    elif stmttype == "exp":
        eval_exp(tree[1],environment)
    elif stmttype == "while":
        # TODO assign tree to a named valuable.
        eval_while(tree, environment)
    elif stmttype == "var":
        eval_var(tree, environment)
    elif stmttype == "assign":
        fname = tree[1]
        exp = tree[2]
        fvalue = eval_exp(exp, environment)
        env_update(fname, fvalue, environment)
    else:
        print "ERROR: {} statement type is not supported.".format(stmttype)

def eval_var(var_stmt, env):
    exp = var_stmt[2]
    value = eval_exp(exp, env)
    vname = var_stmt[1]
    # var statement doesn't raise error when variable is defined,
    # it just overwrite it.
    (env[1])[vname] = value

def eval_while(while_stmt, env):
    exp = while_stmt[1]
    stmts = while_stmt[2]
    # we could also use recursive one to interpreter while
    # if eval_exp(exp, env):
    #     eval_stmts(stmts, env)
    #     eval_while(while_stmt, env)
    while eval_exp(exp, env):
        eval_stmts(stmts, env)

def env_lookup(vname,env):
    if vname in env[1]:
        return (env[1])[vname]
    elif env[0] == None:
        return None
    else:
        return env_lookup(vname,env[0])

def env_update(vname,value,env):
    if vname in env[1]:
        (env[1])[vname] = value
    elif not (env[0] == None):
        env_update(vname,value,env[0])

def env_add(vname, value, env):
    (env[1])[vname] = value

def eval_exp(exp,env):
    etype = exp[0]
    if etype == "number":
        return float(exp[1])
    elif etype == "binop":
        a = eval_exp(exp[1],env)
        op = exp[2]
        b = eval_exp(exp[3],env)
        if op == "*":
            return a*b
        elif op == "+":
            return a+b
        elif op == "-":
            return a-b
        elif op == "/":
            return a/b
        else:
            print "ERROR: \"{}\" binop has not supportted yet.".format(op)
    elif etype == "identifier":
        vname = exp[1]
        value = env_lookup(vname,env)
        if value == None:
            print "ERROR: unbound variable " + vname
        else:
            return value
    elif etype == "call":
        fname = exp[1]
        args = exp[2]
        fvalue = env_lookup(fname, env)
        if fvalue[0] == "function":
            fparams = fvalue[1]
            fbody = fvalue[2]
            fenv = fvalue[3]
            if len(fparams) != len(args):
                print "ERROR: function argument and formal params does not match."
            else:
                #Make a new environment frame
                new_cur_env = {}
                for i in range(len(fparams)):
                    new_cur_env[fparams[i]] = eval_exp(args[i], env)
                    # new environment's parent is fenv. This is lexical binding.
                new_env = (fenv, new_cur_env)
                try:
                    eval_stmts(fbody, new_env)
                except Exception as return_value:
                    print return_value.args[0]
                    return return_value.args[0]
        else:
            print "ERROR: call to non-function"
            print "ERROR-details: exp: {}, env: {}".format(exp, env)
    elif etype == "function":
        # anonymous function
        args = exp[1]
        fbody = exp[2]
        fenv = env
        return ("function", args, fbody, fenv)
    else:
        print "ERROR: \"{}\" exp type has not supportted yet.".format(etype)

def eval_stmts(stmts,env):
    for stmt in stmts:
        # TODO how can we return "the return value"?
        eval_stmt(stmt,env)

class TestFunc(unittest.TestCase):
    # def test_func(self):
    #     sqrt = ("function",("x"),(("return",("binop",("identifier","x"),"*",("identifier","x"))),),{})
    #     environment = (None,{"sqrt":sqrt})

    #     try:
    #         eval_exp(("call","sqrt",[("number","2")]),environment)
    #     except Exception as return_value:
    #         self.assertEqual(str(return_value), "4.0")

    def test_closure(self):
        tree = [('function', 'add_func', [], [('var', 'counter', ('number', 0.0)), ('var', 'add', ('function', [], [('assign', 'counter', ('binop', ('identifier', 'counter'), '+', ('number', 1.0))), ('return', ('identifier', 'counter'))])), ('return', ('identifier', 'add'))]), ('var', 'add', ('call', 'add_func', [])), ('exp', ('call', 'add', [])), ('exp', ('call', 'add', [])),]
        environment = (None, {})
        print eval_stmts(tree, environment)
        #self.assertEqual(str(return_value), "2.0")

# class TestVar(unittest.TestCase):
#     def test_var(self):
#         var_func = ("function",
#                     (),
#                     (("var", "foo", ("number", 2)),
#                      ("return", ("identifier", "foo")),),
#                     {})
#         environment = (None, {"var_func":var_func})
#         try:
#             eval_exp(("call", "var_func", []), environment)
#         except Exception as return_value:
#             self.assertEqual(str(return_value), "2.0")

#     def test_refvar(self):
#         var_func = ("function",
#                     (),
#                     (("var", "foo", ("number", 2)),
#                       ("var", "bar", ("identifier", "foo")),
#                      ("return", ("identifier", "bar")),),
#                     {})
#         environment = (None, {"var_func":var_func})
#         try:
#             eval_exp(("call", "var_func", []), environment)
#         except Exception as return_value:
#             self.assertEqual(str(return_value), "2.0")

if __name__ == '__main__':
    unittest.main()
