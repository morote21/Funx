from flask import Flask, render_template, request
from jinja2 import Environment, FileSystemLoader
from FunxLexer import FunxLexer
from FunxParser import FunxParser
from antlr4 import *
from os import sys

if __name__ is not None and "." in __name__:
    from .FunxParser import FunxParser
    from .FunxVisitor import FunxVisitor
else:
    from FunxParser import FunxParser
    from FunxVisitor import FunxVisitor

# constante que se usa en caso de que dentro de una no haya nada
EMPTY_VALUE = ""


class TreeVisitor(FunxVisitor):

    def __init__(self, functions, stack):
        self.functions = functions
        self.stack = stack

    def visitRoot(self, ctx):
        l = list(ctx.getChildren())
        # aqui solo hara falta el self.visit, no la salida
        output = self.visit(l[0])
        # hacer appends de los outputs en caso de que haya mas de un input
        return self.stack, self.functions, output

    def visitOperation(self, ctx):
        l = list(ctx.getChildren())
        # cogemos el nombre del tipo de operacion en string
        operation = FunxParser.symbolicNames[l[1].getSymbol().type]
        if operation == "SUM":
            return self.visit(l[0]) + self.visit(l[2])
        elif operation == "SUB":
            return self.visit(l[0]) - self.visit(l[2])
        elif operation == "PROD":
            return self.visit(l[0]) * self.visit(l[2])
        elif operation == "DIV":
            denominator = self.visit(l[2])
            if denominator == 0:
                raise Exception("Division por 0")
            return self.visit(l[0]) / denominator
        elif operation == "POW":
            return self.visit(l[0]) ** self.visit(l[2])
        elif operation == "MOD":
            denominator = self.visit(l[2])
            if denominator == 0:
                raise Exception("Division por 0")
            return self.visit(l[0]) % denominator

    def visitComparation(self, ctx):
        l = list(ctx.getChildren())
        condition = FunxParser.symbolicNames[l[1].getSymbol().type]
        if condition == "EQ":
            return self.visit(l[0]) == self.visit(l[2])
        elif condition == "DIF":
            return self.visit(l[0]) != self.visit(l[2])
        elif condition == "GREATER":
            return self.visit(l[0]) > self.visit(l[2])
        elif condition == "GREATEREQ":
            return self.visit(l[0]) >= self.visit(l[2])
        elif condition == "LOWER":
            return self.visit(l[0]) < self.visit(l[2])
        elif condition == "LOWEREQ":
            return self.visit(l[0]) <= self.visit(l[2])

    def visitParenthesis(self, ctx):
        l = list(ctx.getChildren())
        return self.visit(l[1])

    def visitValue(self, ctx):
        l = list(ctx.getChildren())
        return float(l[0].getText())

    def visitBoolean(self, ctx):
        l = list(ctx.getChildren())
        return eval(l[0].getText())

    def visitExpression(self, ctx):
        l = list(ctx.getChildren())
        return self.visit(l[0])

    def visitVariable(self, ctx):
        l = list(ctx.getChildren())
        current_stack = self.stack.top()
        var = l[0].getText()
        if var in current_stack:
            return current_stack[var]
        else:       # en caso de que la variable aun no este definida, es decir, que no haya recibido ningun valor, debe dar 0
            return 0.0

    def visitAssignment(self, ctx):
        l = list(ctx.getChildren())
        variable = l[0].getText()
        value = self.visit(l[2])
        current_stack = self.stack.top()
        current_stack[variable] = value

    def visitIfCondition(self, ctx):
        l = list(ctx.getChildren())
        if len(l) == 4:  # en caso de que el tamaño del if sea de 4 childs, significa que no hay expresiones, por tanto devuelve EMTPY_VALUE
            return EMPTY_VALUE

        expression_result = self.visit(l[1])
        if expression_result:   # empezamos por el 3 ya que el 2 es el {

            for i in range(3, len(l)-1):  # no hay que contar la ultima ya que es }
                returned_value = self.visit(l[i])
                if returned_value is not None:
                    return returned_value

    def visitIfElseCondition(self, ctx):
        l = list(ctx.getChildren())
        # tenemos que conseguir el index del else previamente ya que no se puede
        # hacer aqui la comprobacion de symbolicnames, ya que las instrucciones
        # y expresiones de por si no tienen, por tanto dara error: debemos ver directamente el texto
        # que contienen los hijos, y ver cual contiene "else", para coger su indice
        else_index = 0
        for i in range(len(l)):
            if l[i].getText() == "else":
                else_index = i
                break

        expression_result = self.visit(l[1])
        if expression_result:
            # si la posicion en la que se encuentra el else es en la cuarta, significa que no hay ninguna expresion dentro del if
            if else_index == 4:
                return EMPTY_VALUE

            for i in range(3, else_index):
                returned_value = self.visit(l[i])
                if returned_value is not None:
                    return returned_value

        else:
            # si desde el else hasta el final solo hay 3 childs, significa que no hay ninguna expresion
            if len(l) - else_index == 3:
                return EMPTY_VALUE

            for i in range(else_index+2, len(l)-1):
                returned_value = self.visit(l[i])
                if returned_value is not None:
                    return returned_value

    def visitWhileLoop(self, ctx):
        l = list(ctx.getChildren())

        loop_condition = self.visit(l[1])
        while loop_condition:
            if len(l) == 4:  # en caso de que no haya expresiones en el while no puede acabar
                raise Exception("Bucle puede no acabar")

            for i in range(3, len(l)-1):
                return_value = self.visit(l[i])
                # en caso de que entre en un condicional no tenga expresion, y por tanto no devuelva nada, el bucle no podra acabar
                if return_value == EMPTY_VALUE:
                    raise Exception("Bucle puede no acabar")
            # cuando acabamos la iteracion, comprobamos si se sigue cumpliendo
            # la condicion del bucle o no (en caso de que sea con una i por ejemplo
            # dentro de la iteracion se habra sumado un valor a la i, y aqui se
            # comprueba la condicion con ese nuevo valor)
            loop_condition = self.visit(l[1])

    def visitFunction(self, ctx):
        l = list(ctx.getChildren())
        function_id = l[0].getText()

        if function_id in self.functions:
            raise Exception("La funcion ya ha sido definida")

        args = []
        opencurly_index = 1
        if l[opencurly_index].getText() != '{':
            while l[opencurly_index].getText() != '{':
                args.append(l[opencurly_index].getText())
                opencurly_index += 1

            # aqui comprobar que los parametros no se repiten, ya que cada parametro
            # en la definicion de una funcion debe tener diferente nombre
            args_without_repeated = set(args)
            if len(args) != len(args_without_repeated):
                raise Exception("Se repiten nombres de argumentos")

        # guardamos todas las instrucciones de la funcion
        instructions = []
        for i in range(opencurly_index+1, len(l)-1):
            instructions.append(l[i])

        # guardamos la funcion en el diccionario de funciones
        func = Function(function_id, args, instructions)
        self.functions[function_id] = func
        return None

    def visitFunctionCall(self, ctx):
        l = list(ctx.getChildren())
        function_id = l[0].getText()
        if function_id not in list(self.functions.keys()):
            raise Exception("Esta funcion no esta definida")

        function_params = self.functions[function_id].getParams()
        args = []
        if len(function_params) != 0:
            # contendra una lista con los parametros resueltos
            args = self.visit(l[1])
            if len(args) != len(function_params):
                raise Exception(
                    "El numero de parametros no coincide con el de la funcion")

        # añadimos un nuevo nivel de stack para esta funcion
        params_dict = {}
        for i in range(len(function_params)):
            # asignamos a los argumentos de la funcion su valor en orden
            # solo hace falta asignarlos, ya que se han resuelto en el visitParameters
            params_dict[function_params[i]] = args[i]

        self.stack.insert(params_dict)
        instructions = self.functions[function_id].getCtx()
        i = 0
        returned_value = None
        if len(instructions) != 0:      # en caso de que haya instrucciones dentro de la funcion
            while returned_value is None:
                # dejara de ser None cuando self.visit devuelva algun numero
                returned_value = self.visit(instructions[i])
                i += 1

        if returned_value == EMPTY_VALUE:   # returned_value sera EMPTY_VALUE cuando haya entrado en una condicion que no devuelve nada
            returned_value = None

        self.stack.delete()
        return returned_value   # este return hay que hacerlo despues del delete

    def visitParameters(self, ctx):
        l = list(ctx.getChildren())
        params = []
        for i in range(0, len(l)):
            params.append(self.visit(l[i]))
        return params


# clase function para poder almacenar las funciones en un diccionario
# con sus parametros, nombre, y las instrucciones que contiene
class Function:
    def __init__(self, name, params, context):
        self.name = name
        self.params = params
        self.ctx = context  # array de instrucciones

    def getName(self):
        return self.name

    def getParams(self):
        return self.params

    def getCtx(self):
        return self.ctx

# stack del programa, que contendra una lista de diccionarios con variables locales
# y sus valores, inicializado con un diccionario vacio en el primer nivel de stack


class Stack:
    def __init__(self, first_dict):
        self.elements = [first_dict]

    def insert(self, x):
        self.elements.append(x)

    def delete(self):
        self.elements.pop()

    def top(self):
        return self.elements[len(self.elements)-1]

    def size(self):
        return len(self.elements)


# -----------------------------------
# FLASK
# -----------------------------------

def showError(e):
    error = str(e)
    if error == "Se repiten nombres de argumentos":
        return "Error: " + error
    elif error == "Esta funcion no esta definida":
        return "Error: " + error
    elif error == "El numero de parametros no coincide con el de la funcion":
        return "Error: " + error
    elif error == "La funcion ya ha sido definida":
        return "Error: " + error
    elif error == "Division por 0":
        return "Error: " + error
    elif error == "La funcion o expresion no se ha escrito correctamente":
        return "Error: " + error
    elif error == "Bucle puede no acabar":
        return "Error: " + error
    else:
        return "Error desconocido"


i = 0
functions = {}
results = []

app = Flask(__name__)


@app.route('/', methods=['POST', 'GET'])
def index():
    stack = Stack({})
    if request.method == 'POST':
        global i, results, functions
        i += 1
        try:
            input = request.form.get("input")
            input_stream = InputStream(str(input))
            lexer = FunxLexer(input_stream)
            token_stream = CommonTokenStream(lexer)
            parser = FunxParser(token_stream)
            tree = parser.root()
            n_syntax_errors = parser.getNumberOfSyntaxErrors()
            if (n_syntax_errors > 0):
                raise Exception(
                    "La funcion o expresion no se ha escrito correctamente")

            visitor = TreeVisitor(functions=functions, stack=stack)
            stack, functions, output = visitor.visit(tree)
        except Exception as e:
            output = showError(e)

        results.append({'it': i, 'input': input, 'output': output})

        functions_list = []
        for f in list(functions.values()):
            function_string = str(f.getName())
            function_params = f.getParams()
            for parameter in function_params:
                function_string = function_string + " " + str(parameter)
            functions_list.append(function_string)

        return render_template("base.html", title="Funx", functions=functions_list, results=reversed(results[-5:]))

    return render_template("base.html", title="Funx")


if __name__ == '__main__':
    app.run(debug=True)
