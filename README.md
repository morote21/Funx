# Funx

## Descripción 

Práctica de Lenguajes de Programación (edición 2022-2023 Q1) sobre un intérprete para un lenguaje de programación basado en expresiones y funciones. 

## Contenido de la práctica

Archivo `Funx.g4` con la gramática del intérprete, `Funx.py` con el cual se 
ejecuta el programa, y una carpeta *templates* con el archivo `base.html`
con los templates de la página del intérprete. 

## Instalación
Para la instalación de Antlr4 Python Runtime:
```bash
pip3 install antlr4-python3-runtime==4.10
```
Para la instalación de Flask:
```bash
pip3 install flask
```
Para la instalación de Jinja2:
```bash
pip3 install Jinja2
```

Y en el mismo archivo donde se encuentra la gramática:
```bash
curl -O https://www.antlr.org/download/antlr-4.10.1-complete.jar
```
O en caso de no tener instalado "curl", se puede encontrar este archivo en las 
diapositivas de "compiladors" en este link: 
https://gebakx.github.io/Python3/compiladors.html#2
haciendo click en "jar file" y moviendo el archivo a la carpeta donde se encuentra Funx.g4

## Compilación de la gramática 

Para compilar la gramática, hay que ejecutar el siguiente comando:
```bash
java -jar antlr-4.10.1-complete.jar -Dlanguage=Python3 -no-listener -visitor Funx.g4
```

## Ejecución del intérprete

Ejecutar intérprete con el siguiente comando:
```bash
python3 Funx.py
```
O también con los siguientes comandos:
```bash
export FLASK_APP=Funx
flask run
```

A continuación, abrir navegador y entrar a la siguiente página:
http://127.0.0.1:5000


## Uso del intérprete

Nada más ejecutar el intérprete y entrar a la página indicada, se podrá ver una
interfaz con tres partes principales:

- *Funcions*: Donde se encuentran las cabeceras de las funciones declaradas
- *Resultats*: Donde se encuentran los inputs y sus outputs correspondientes
- *Consola*: Donde se puede ingresar una expresión o declarar una función

Solo se puede hacer un submit de una expresión o una función a la vez.
Una vez se haya escrito en la consola el input que se desee, hay que presionar 
el botón "submit" para ejecutar el input. 

Si se quiere solo evaluar una expresión, hay que escribirla simplemente
(por ejemplo `3 + 4`, o en el caso de querer evaluar una función, como por ejemplo
calcular el Fibonacci de 4, simplemente escribir `Fibonacci 4`, siempre y cuando 
en el apartado de funciones se encuentre presente esta función).

Si se quiere declarar una función, primero hay que escribir su nombre empezando por 
letra mayúscula obligatóriamente, seguido de sus parámetros separados por espacios,
y por último escribir el contexto (todas las instrucciones) de la función entre `{ }`.
Todo contexto de una función acaba en una expresión, de manera que simula el típico
`return`.

## Valores de los números y variables

Un número puede ser tanto un *integer* como un *float*, y los resultados siempre se mostrarán en tipo *float*.
Si a una variable no se le ha asignado un número, su valor sera *0*.

## Ejemplos de ejecución

### Suma 

Si se escribe en la consola `Suma x y { x + y }`, aparecerá en el apartado de *Funcions*
la cabecera *Suma x y*, y en el apartado de *Resultats* se encontrará como input
*Suma x y { x + y }*, y como output *None*, ya que la declaración de una función no
devuelve nada.
Si a continuación se escribe en la consola `Suma 2 3`, aparecerá en el apartado
*Resultats* el resultado de evaluar esta expresión, siendo el input *Suma 2 3*, y el
output *5*.

### Fibonacci

Si se escribe en la consola:
```
Fibo n
{
    if n < 2 { n }
    (Fibo n-1) + (Fibo n-2)
}
```
Aparecerá en el apartado *Funcions* la cabecera *Fibo n*, y en el apartado *Resultats*
se encontrará como input `Fibo n { if n < 2 { n } (Fibo n-1) + (Fibo n-2) }`, y como
output `None`.
Si a continuación se escribe en la consola `Fibo 4`, aparecerá en el apartado
*Resultats* como input lo mismo que se ha escrito, y como output el resultado de la 
expresión, en este caso `3`.

## Operadores lógicos

Se ha incluido como pequeña extensión los operadores lógicos `True` y `False`.
Si se escribe en la consola la siguiente función:
```
Either x y b
{
    if b { x }
    else { y }
}
```
Se puede observar como dependiendo de si el parámetro `b` es *True* o *False*, devuelve el primer 
parámetro o el segundo:

## Excepciones

El intérprete considera los siguientes errores:
- *Se repiten nombres de argumentos*: En la definición de una función se ha repetido el nombre de algun argumento.
- *Esta funcion no esta definida*: Se ha intentado llamar a una función que no está definida.
- *El numero de parametros no coincide con el de la funcion*: El número de parámetros insertado en la llamada a una función no coincide con su número de parámetros real.
- *La funcion ya ha sido definida*: Se ha intentado definir una función ya existente.
- *Division por 0*: Se ha intentado dividir un valor por 0.
- *La funcion o expresion no se ha escrito correctamente*: Ha habido un error de sintaxis a la hora de definir una función o una expresión.
- *Bucle no puede acabar*: El bucle está vacío o se ha entrado en una condición vacía dentro del bucle, que puede provocar que no acabe.
- *Error desconocido*: Ha surgido un error no conocido.

`Either 1 2 True` tendrá como output `1`.
`Either 1 2 False` tendrá como output `2`.

## Autor

José Morote García.
Estudiante de GEI en la Facultad de Informática de Barcelona.