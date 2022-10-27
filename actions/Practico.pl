materia(1,1,6111, 'Introduccion a la Programacion I').
materia(1,1,6112, 'Analisis Matematico I').
materia(1,1,6113, 'Algebra').
materia(1,1,6114, 'Quimica').

materia(1,2,6121, 'Ciencias de la Computacion I').
materia(1,2,6122, 'Introduccion a la Programacion II').
materia(1,2,6123, 'Algebra Lineal').
materia(1,2,6124, 'Fisica General').
materia(1,2,6125, 'Matematica Discreta').


materia(2,1,6211, 'Ciencias de la Computacion II').
materia(2,1,6212, 'Analisis y Dise�o de Algoritmos I').
materia(2,1,6213, 'Introduccion a la Arquitectura de Sistemas').
materia(2,1,6214, 'Analisis Matematico II').
materia(2,1,6215, 'Electricidad y Magnetismo').

materia(2,2,6221, 'Analisis y Dise�o de Algoritmos II').
materia(2,2,6222, 'Comunicacion de Datos I').
materia(2,2,6223, 'Probabilidad y Estadistica').
materia(2,2,6224, 'Electronica Digital').

materia(3,1,6311, 'Programacion Orientada a Objetos').
materia(3,1,6312, 'Estructuras de Almacenamiento de Datos').
materia(3,1,6313, 'Metodologias de Desarrollo de Software I').
materia(3,1,6314, 'Arquitectura de Computadoras I').

materia(3,2,6321, 'Programacion Exploratoria').
materia(3,2,6322, 'Base de Datos I').
materia(3,2,6323, 'Lenguajes de Programacion I').
materia(3,2,6324, 'Sistemas Operativos I').
materia(3,2,6325, 'Investigacion Operativa I').

materia(4,1,6411, 'Arquitectura de Computadoras y Tecnicas Digitales').
materia(4,1,6412, 'Teoria de la Informacion').
materia(4,1,6413, 'Comunicacion de Datos II').
materia(4,1,6414, 'Introduccion al Calculo Diferencial e Integral').

materia(4,2,6421, 'Dise�o de Sistemas de Software').
materia(4,2,6422, 'Dise�o de Compiladores I').

materia(5,1,6511, 'Ingenieria de Software').


correlativa(6122, 6111).

correlativa(6123, 6113).

correlativa(6124, 6112).

correlativa(6125, 6113).

correlativa(6211, 6121).
correlativa(6211, 6122).
correlativa(6211, 6125).

correlativa(6212, 6121).
correlativa(6212, 6122).
correlativa(6212, 6125).

correlativa(6213, 6122).
correlativa(6214, 6112).

correlativa(6215, 6124).

correlativa(6221, 6211).
correlativa(6221, 6212).

correlativa(6222, 6213).

correlativa(6223, 6214).
correlativa(6223, 6123).
correlativa(6223, 6125).

correlativa(6224, 6215).

correlativa(6311, 6221).

correlativa(6312, 6221).
correlativa(6312, 6223).

correlativa(6313, 6221).

correlativa(6314, 6213).
correlativa(6314, 6224).

correlativa(6321, 6221).

correlativa(6322, 6312).
correlativa(6322, 6313).

correlativa(6323, 6311).

correlativa(6324, 6312).
correlativa(6324, 6314).

correlativa(6325, 6214).
correlativa(6325, 6223).

correlativa(6411, 6314).

correlativa(6412, 6212).
correlativa(6412, 6222).
correlativa(6412, 6223).

correlativa(6413, 6222).
correlativa(6413, 6324).

correlativa(6414, 6214).

correlativa(6421, 6311).
correlativa(6421, 6322).
correlativa(6421, 6324).

correlativa(6422, 6323).

correlativa(6511, 6421).

listar_carrera() :- materia(A,B,_,C), write('Curso:'), write(A), write(' Cua:'), write(B), write(' Nom: '), write(C), nl, fail.


es_correlativa(A,B) :- correlativa(B, A).

devolver_nombre(X) :- materia(_,_,X,A), write(A).

materias_de(A) :- materia(A, _, _, X), write(X), nl, fail.

cantidad(X,A) :- aggregate_all(count, correlativa(X, _Y), _count), _count = A.
materias_con_correlativas(A) :- correlativa(X, _), cantidad(X, A), devolver_nombre(X), nl, fail.

curso(6321).
curso(6322).
curso(6323).
curso(6324).
curso(6325).


cursadas(Nombre) :- curso(Cod), materia(_, _, Cod, Nombre).


agenda('lunes', 0, 7, 'por dormir').
agenda('martes', 0, 7, 'por dormir').
agenda('miercoles', 0, 7, 'por dormir').
agenda('jueves', 0, 7, 'por dormir').
agenda('viernes', 0, 7, 'por dormir').


agenda('lunes', 9, 11, 'cursando').
agenda('lunes', 19, 22, 'entrenando').

agenda('martes', 9, 18, 'cursando').

agenda('miercoles', 13, 16, 'cursando').
agenda('miercoles', 19, 22, 'entrenando').

agenda('jueves', 9, 17, 'cursando').

agenda('viernes', 9, 11, 'cursando').
agenda('viernes', 19, 22, 'entrenando').


actividades('cursando').
actividades('entrenando').


consultar_agenda(Dia, Hora, Actividad) :- agenda(Dia, Desde, Hasta, Actividad), Hora >= Desde, Hora =< Hasta.
