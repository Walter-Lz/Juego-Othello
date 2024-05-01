:- dynamic matriz/1.
oponente('negro', 'blanco').
% Predicado para inicializar el tablero con tamaño NxN
iniciar_tablero(N) :-
    retractall(matriz(_)),
    generar_matriz(N, Matriz),
    assertz(matriz(Matriz)).
generar_matriz(N, Matriz) :-
    length(Matriz, N),
    maplist(generar_fila(N), Matriz).
% Predicado auxiliar para generar la matriz NxN con valores '-'
generar_fila(N, Fila) :-
    length(Fila, N),
    maplist(=(('-')), Fila).
% Predicado para actualizar un valor en la matriz
movimiento(Fila, Columna, NuevoValor) :-
    matriz(MatrizActual),
    actualizar_valor_en_posicion(Fila, Columna, NuevoValor, MatrizActual, NuevaMatriz),
    retractall(matriz(_)),
    assertz(matriz(NuevaMatriz)).
% Predicado auxiliar para actualizar el valor en una posición específica de la matriz
actualizar_valor_en_posicion(1, Columna, NuevoValor, [Fila|Resto], [NuevaFila|Resto]) :-
    actualizar_valor_en_posicion_en_fila(Columna, NuevoValor, Fila, NuevaFila).
actualizar_valor_en_posicion(Fila, Columna, NuevoValor, [FilaActual|Resto], [FilaActual|NuevaResto]) :-
    Fila > 1,
    FilaNueva is Fila - 1,
    actualizar_valor_en_posicion(FilaNueva, Columna, NuevoValor, Resto, NuevaResto).
% Predicado auxiliar para actualizar el valor en una posición específica de una fila
actualizar_valor_en_posicion_en_fila(1, NuevoValor, [_|Resto], [NuevoValor|Resto]).
actualizar_valor_en_posicion_en_fila(Columna, NuevoValor, [Elemento|Resto], [Elemento|NuevaResto]) :-
    Columna > 1,
    ColumnaNueva is Columna - 1,
    actualizar_valor_en_posicion_en_fila(ColumnaNueva, NuevoValor, Resto, NuevaResto).
% Predicado para imprimir la matriz
imprimir_matriz :-
    matriz(Matriz),
    writeln('['),
    imprimir_lista_de_listas(Matriz),
    writeln(']').
% Predicado para imprimir una lista de listas
imprimir_lista_de_listas([]).
imprimir_lista_de_listas([Lista|Resto]) :-
    write(' '), % Espacio para alinear 
    writeln(Lista),
    imprimir_lista_de_listas(Resto).
% Predicado para obtener todas las jugadas válidas para un jugador en el tablero
mejor_movimiento(Jugador, MejorJugada) :-
    matriz(MatrizActual),
    findall((Fila, Columna, _, Puntuacion), (
        nth1(Fila, MatrizActual, FilaTablero),       % Obtener la fila del tablero
        nth1(Columna, FilaTablero, '-'),          % Verificar si la casilla está vacía ('-')
        buscar_jugada(Jugador, Fila, Columna, MatrizActual),  % Verificar si es una jugada válida
        evaluar_jugada(Jugador, Fila, Columna, Puntuacion)  % Evaluar la jugada
    ), ListaJugadas),
    % Encontrar la jugada con la puntuación más alta
    max_member((_, _, _, MaxPuntuacion), ListaJugadas),
    member((MejorFila, MejorColumna, MaxFichasCapturadas, MaxPuntuacion), ListaJugadas),
    MejorJugada = (MejorFila, MejorColumna, MaxFichasCapturadas, MaxPuntuacion).
% Predicado para evaluar una jugada
evaluar_jugada(_, Fila, Columna, Puntuacion) :-
    % Asigna valores a los factores relevantes
    valor_posicion(Fila, Columna, ValorPosicion),
    % Calcula la puntuación total
    Puntuacion is ValorPosicion.
% Ejemplo de asignación de valores (ajusta estos valores según tu estrategia)
valor_posicion(Fila, Columna, Valor) :-
    matriz(Tablero),
    dimensiones_tablero(Tablero, NumFilas, NumColumnas),
    DistanciaCentroFila is min(Fila, NumFilas - Fila + 1),
    DistanciaCentroColumna is min(Columna, NumColumnas - Columna + 1),
    DistanciaCentro is min(DistanciaCentroFila, DistanciaCentroColumna),
    Valor is 5 - DistanciaCentro.
% Predicado para verificar si una jugada es válida para un jugador en una posición dada
buscar_jugada(Jugador, Fila, Columna, Tablero) :-
    oponente(Jugador, Oponente),
    member((DirF, DirC), [(1,0), (-1,0), (0,1), (0,-1), (1,1), (-1,-1), (1,-1), (-1,1)]),  % Direcciones posibles
    validar_jugada(Jugador, Fila, Columna, DirF, DirC, Oponente, Tablero).
% Predicado para validar una jugada en una dirección específica
validar_jugada(Jugador, Fila, Columna, DirF, DirC, Oponente, Tablero) :-
    Fila2 is Fila + DirF,               % Calcular la fila siguiente
    Columna2 is Columna + DirC,         % Calcular la columna siguiente
    dentro_tablero(Fila2, Columna2, Tablero),  % Verificar si está dentro del tablero
    validar_jugada_aux(Fila2, Columna2, Oponente, Tablero),    % Verificar si la casilla contiene al oponente
    % Probar si se pueden voltear fichas en esta dirección
    verificar_direccion(Jugador, Fila2, Columna2, DirF, DirC, Oponente, Tablero).
% Predicado para seguir una línea en una dirección específica y validar si se pueden voltear fichas
verificar_direccion(Jugador, Fila, Columna, _, _, _, Tablero) :-
    validar_jugada_aux(Fila, Columna, Jugador, Tablero).  % se halla una ficha del jugador
verificar_direccion(Jugador, Fila, Columna, DirF, DirC, Oponente, Tablero) :-
    validar_jugada_aux(Fila, Columna, Oponente, Tablero),  % se halla una ficha del oponente
    Fila2 is Fila + DirF,
    Columna2 is Columna + DirC,
    dentro_tablero(Fila2, Columna2, Tablero),
    verificar_direccion(Jugador, Fila2, Columna2, DirF, DirC, Oponente, Tablero).
% Predicado para verificar si una casilla contiene un cierto valor en el tablero
validar_jugada_aux(Fila, Columna, Contenido, Tablero) :-
    nth1(Fila, Tablero, FilaTablero),   % Obtener la fila del tablero
    nth1(Columna, FilaTablero, Contenido).  % Verificar el contenido de la casilla
% Predicado para obtener las dimensiones del tablero (filas y columnas)
dimensiones_tablero(Tablero, NumFilas, NumColumnas) :-
    length(Tablero, NumFilas),  % Obtener el número de filas del tablero
    (   NumFilas > 0 ->
        nth1(1, Tablero, Fila),
        length(Fila, NumColumnas)  % Obtener el número de columnas de la primera fila
    ;   NumColumnas = 0  % Si el tablero está vacío, el número de columnas es 0
    ).
% Predicado para verificar si una posición está dentro del tablero
dentro_tablero(Fila, Columna, Tablero) :-
    dimensiones_tablero(Tablero, NumFilas, NumColumnas),
    Fila >= 1,
    Fila =< NumFilas,
    Columna >= 1,
    Columna =< NumColumnas.