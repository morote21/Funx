grammar Funx ;

root : code EOF ;

code : inputs*
    ;

inputs : instructions  
    | functions 
    ;

functions : NAME VAR* OPENCURLY instructions* CLOSECURLY    # Function
    ;

instructions : VAR ASSIG expr                                                               # Assignment
    | IF expr OPENCURLY instructions* CLOSECURLY                                            # IfCondition 
    | IF expr OPENCURLY instructions* CLOSECURLY ELSE OPENCURLY instructions* CLOSECURLY    # IfElseCondition
    | WHILE expr OPENCURLY instructions* CLOSECURLY                                         # WhileLoop
    | expr                                                                                  # Expression
    ;

expr : NAME args                                                        # FunctionCall
    | expr (EQ | DIF | GREATER | GREATEREQ | LOWER | LOWEREQ) expr      # Comparation
    | <assoc=right> expr POW expr                                       # Operation
    | expr (PROD | DIV | MOD) expr                                      # Operation
    | expr (SUM | SUB) expr                                             # Operation
    | OPENPARENTHESIS expr CLOSEPARENTHESIS                             # Parenthesis
    | BOOL                                                              # Boolean
    | NUM                                                               # Value
    | VAR                                                               # Variable
    ;

args : expr*     # Parameters
    ;  

SUM : '+' ;
SUB : '-' ;
PROD : '*' ;
DIV : '/' ;
POW : '^' ;
MOD : '%' ;
ASSIG : '<-' ;
OPENPARENTHESIS : '(' ;
CLOSEPARENTHESIS : ')' ;
OPENCURLY : '{' ;
CLOSECURLY : '}' ;
IF : 'if' ;
THEN : 'then' ;
ELSE : 'else' ;
END : 'end' ;
WHILE : 'while' ;
EQ : '=' ;
GREATER : '>' ;
GREATEREQ : '>=' ;
DIF : '!=' ;
LOWER : '<' ;
LOWEREQ : '<=' ;


BOOL : 'True' | 'False' ;

NUM : (FLOAT | INTEGER) ; 
FLOAT : DIGIT+ '.' DIGIT* 
    | '.' DIGIT+
    ;
INTEGER : DIGIT+ ;
DIGIT : [0-9] ;

NAME : [A-Z] [a-zA-Z\u0080-\u00FF_0-9]* ; // con el [A-Z] al principio forzamos que empiece por mayus
VAR : [a-zA-Z\u0080-\u00FF]+ ; 

COMMENT : ( '#' ~[\r\n]* ) -> skip;
WS : [ \n\r\t]+ -> skip ;
