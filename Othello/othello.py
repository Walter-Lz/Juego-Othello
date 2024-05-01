import tkinter as tk
from tkinter import messagebox
from pyswip import Prolog
import re
# ---------------------------------------------------------->Configuración<-----------------------------------------------------------------
# Función para abrir la ventana de configuración del juego
def abrir_configuracion():
    menu.destroy()
    ventana_configuracion = tk.Tk()
    ventana_configuracion.title("Configuración del Juego")
    ventana_configuracion.geometry("400x300")
    ventana_configuracion.resizable(False, False)
    centrar_ventana(ventana_configuracion)
    # Etiqueta y opciones para el tamaño del tablero
    lbl_tamanio = tk.Label(ventana_configuracion, text="Seleccione el tamaño del tablero:")
    lbl_tamanio.pack(anchor=tk.W, padx=10, pady=(20, 0))

    tamanio_var = tk.StringVar(ventana_configuracion)
    tamanio_var.set("4x4")  # Valor predeterminado
    opciones_tam = ["4x4","6x6","8x8" ,"10x10"]
    opciones_tam = tk.OptionMenu(ventana_configuracion, tamanio_var, *opciones_tam)
    opciones_tam.pack()

    # Etiqueta y opciones para el método de obtención de movimientos de la máquina
    lbl_metodo = tk.Label(ventana_configuracion, text="Seleccione el método de la máquina:")
    lbl_metodo.pack(anchor=tk.W, padx=10)

    metodo_var = tk.StringVar(ventana_configuracion)
    metodo_var.set("mapeo de la matriz como hechos de listas de listas")  # Valor predeterminado
    opciones_metodo = ["mapeo de la matriz como hechos de listas de listas"]
    dropdown_metodo = tk.OptionMenu(ventana_configuracion, metodo_var, *opciones_metodo)
    dropdown_metodo.pack(anchor=tk.W, padx=10, pady=(0, 20))

    # Botón para confirmar la configuración y empezar el juego
    btn_confirmar = tk.Button(ventana_configuracion, text="Confirmar", command=lambda: empezar_juego(ventana_configuracion,tamanio_var.get(), metodo_var.get()))
    btn_confirmar.pack()
    
def inicializar_tablero(tamaño):
    global tablero
    mid = tamaño // 2
    tablero = [['-' for _ in range(tamaño)] for _ in range(tamaño)]
    tablero[mid - 1][mid - 1] = tablero[mid][mid] = 'negro'
    tablero[mid - 1][mid] = tablero[mid][mid - 1] = 'blanco'
    InicializarMatriz_Prolog(tamaño)
    
#Inicializar las casillas según el tamaño elegido por el usuario para crear el tablero
def calcular_tamaño_casilla(ancho_ventana, alto_ventana):
    global tamaño_casilla_ancho, tamaño_casilla_alto
    tamaño_minimo_casilla = 60
    tamaño_casilla_ancho = max(ancho_ventana // tamaño, tamaño_minimo_casilla)
    tamaño_casilla_alto = max(alto_ventana // tamaño, tamaño_minimo_casilla)
    
#------------------------------------------------------------->Juego Othelo<------------------------------------------------------------
# Función para empezar el juego con las opciones seleccionadas
def empezar_juego(ventanaconfig, tamaño_tablero, metodo_maquina):
    global ventana_juego, tamaño
    ventanaconfig.destroy()  # Cerrar la ventana de configuración
    print("Tamaño del tablero elegido:",tamaño_tablero)
    print("Método elegido para la máquina:",metodo_maquina)
    # Crear la ventana del juego
    ventana_juego = tk.Tk()
    ventana_juego.title("Othello")
    ventana_juego.resizable(False, False)
    ventana_juego.update_idletasks()
    # Crear un menú "Opciones"
    menu = tk.Menu(ventana_juego)
    ventana_juego.config(menu=menu)
    menu.add_cascade(label="Saltar Turno", command=saltar_turno )#menu=menu_opciones
    tamaño = int(tamaño_tablero.split("x")[0])  
    inicializar_tablero(tamaño)
    calcular_tamaño_casilla(ventana_juego.winfo_width(), ventana_juego.winfo_height())
    crear_tablero()
    centrar_ventana(ventana_juego)
    
def saltar_turno():
    global Mov_Cpu,Mov_Jugador
    if Juego_Fin != True and Mov_Jugador==True:
        Mov_Jugador, Mov_Cpu = Mov_Cpu, Mov_Jugador 
        print("Se ha saltado el turno....")  
        movimientoProlog()
        
def crear_tablero():
    global ventana_juego,tamaño,tablero,tamaño_casilla_ancho,tamaño_casilla_alto,Juego_Fin 
    conteo=contar_fichas()  
    if conteo['blanco'] + conteo['negro'] == tamaño*tamaño: 
        print("Se ha completado el tablero. Fin del Juego.")
        Juego_Fin= True 
    for i in range(tamaño):
        for j in range(tamaño):
            # Crear la casilla
            casilla = tk.Canvas(ventana_juego, width=tamaño_casilla_ancho, height=tamaño_casilla_alto, bd=1, highlightthickness=0)
            casilla.grid(row=i, column=j, padx=1, pady=1, ipadx=0, ipady=0)
            # Dibujar el fondo verde de la casilla
            casilla.create_rectangle(2, 4, tamaño_casilla_ancho, tamaño_casilla_alto, fill="green", outline="black")
            # Calcular el radio para el círculo (ficha)
            radio = min(tamaño_casilla_ancho, tamaño_casilla_alto) * 0.4
            # Si la casilla no está vacía, dibujar la ficha correspondiente
            if tablero[i][j] != '-':
                # Obtener el color de la ficha en esta posición del tablero y pintar en el canvas
               if tablero[i][j] == 'negro': color_ficha = 'black' 
               if tablero[i][j] == 'blanco': color_ficha='white'      
               casilla.create_oval(tamaño_casilla_ancho/2 - radio, tamaño_casilla_alto/2 - radio,
                                    tamaño_casilla_ancho/2 + radio, tamaño_casilla_alto/2 + radio, fill=color_ficha)
               continue #se salta esa iteracion ya que no hace uso de evento con el click izq
            # Asociar la función on_click_izquierdo a la casilla
            casilla.bind("<Button-1>", lambda  event,fila=i, columna=j, casilla=casilla: on_click_izquierdo(event, fila, columna,casilla))
    if Juego_Fin == True:
        final_Juego()
    else:
        Movimiento_AplicableCualquierFicha =punto_muerto() # devuelve false si existe almenos un movimiento
        if Movimiento_AplicableCualquierFicha == True :
            print("No hay movimientos para ninguna ficha posible..")
            Juego_Fin=True
            final_Juego()
        saltar_turno_automaticamente() # si el jugador actual no tiene movimientos posibles, automaticamente se pasa el turno 
    
def on_click_izquierdo(event,fila, columna,_):
    global tablero, Mov_Jugador,Mov_Cpu
    if Mov_Jugador== True:
        if tablero[fila][columna]== '-' and movimiento_valido(fila, columna, 'blanco'):
            Mov_Jugador= False
            Mov_Cpu =True
            voltear_fichas(fila, columna, 'blanco')
            tablero[fila][columna] = 'blanco'
            actualizar_valor_Prolog(fila+1,columna+1,'blanco')
            crear_tablero()
            movimientoProlog()
            
    elif Mov_Jugador== False and Juego_Fin!=True:
        print("Es el turno de la CPU. Juega con ficha negra")
         
def Jugador_IA(fila, columna,ficha):
    global tablero, Mov_Jugador,Mov_Cpu,Juego_Fin
    if Mov_Cpu== True:
        if tablero[fila][columna] == '-' and movimiento_valido(fila, columna,ficha):
            Mov_Jugador= True
            Mov_Cpu =False
            voltear_fichas(fila, columna,ficha)
            tablero[fila][columna] = ficha
            crear_tablero()         
    else:
        print("Es el turno del Jugador. Juega con ficha blanca")
         
#------------------------------------------------------------->Validar Movimiento<------------------------------------------------------------
def movimiento_valido(x, y, ficha):
    direcciones = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in direcciones:
        if direccion_valida(x, y, dx, dy, ficha):
            return True
    return False

def voltear_fichas(x, y, ficha):
    direcciones = [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]
    for dx, dy in direcciones:
        if direccion_valida(x, y, dx, dy, ficha):
            cambiar_direccion(x, y, dx, dy, ficha)
           
def direccion_valida(x, y, dx, dy, ficha):
    global tablero
    x += dx
    y += dy
    if not (0 <= x < len(tablero) and 0 <= y < len(tablero)) or tablero[x][y] == '-' or tablero[x][y] == ficha:
        return False
    while 0 <= x < len(tablero) and 0 <= y < len(tablero):
        if tablero[x][y] == ficha:
            return True
        elif tablero[x][y] == '-':
            return False
        x += dx
        y += dy
    return False

def cambiar_direccion(x, y, dx, dy, ficha):
    global tablero
    x += dx
    y += dy
    while 0 <= x < len(tablero) and 0 <= y < len(tablero) and tablero[x][y] != '-' and tablero[x][y] != ficha:
        tablero[x][y] = ficha
        actualizar_valor_Prolog(x+1,y+1,ficha) # se tiene que sumar 1 porque en Prolog las posiciones empiezan en (1,1) en lugar de (0,0)
        x += dx
        y += dy

def punto_muerto_Jugador():
    global tablero, Mov_Cpu, Mov_Jugador
    if Mov_Jugador:
        jugador_actual = 'blanco'
    elif Mov_Cpu:
        jugador_actual = 'negro'
    for i in range(tamaño):
        for j in range(tamaño):
            if tablero[i][j] == '-' and movimiento_valido(i, j, jugador_actual):
                return False
    return True
#Validar los posibles movimientos que tiene el jugador en curso, si no tiene automaticamente se salta el turno 
def saltar_turno_automaticamente():
    global Mov_Cpu, Mov_Jugador
    if punto_muerto_Jugador() and Juego_Fin!=True:  # Verifica si el jugador actual no tiene movimientos válidos
        if Mov_Jugador:
            print("El jugador con fichas blancas no tiene movimientos validos. Saltando turno...")
            Mov_Jugador, Mov_Cpu = Mov_Cpu, Mov_Jugador
            movimientoProlog()
        elif Mov_Cpu:
            print("El jugador con fichas negras no tiene movimientos validos. Saltando turno...")
            Mov_Jugador, Mov_Cpu = Mov_Cpu, Mov_Jugador

#Función para validar que no se haya llegado a un punto en la partida en la que ningun jugador pueda realizar un movimiento
def punto_muerto():
    global tablero
    for i in range(tamaño):
        for j in range(tamaño):
            if tablero[i][j] == '-' and (movimiento_valido(i, j, 'blanco') or movimiento_valido(i, j, 'negro')):
                return False # existen movimientos posibles
    return True  # ninguna ficha es valida para moverse

def contar_fichas():
    global tamaño,Juego_Fin,tablero
    conteo = {'blanco': 0, 'negro': 0}
    for fila in tablero:
        for celda in fila:
            if celda == 'blanco':
                conteo['blanco'] += 1
            elif celda == 'negro':
                conteo['negro'] += 1
    return conteo

def final_Juego():
    global tablero
    recuento = contar_fichas()
    recuento_blancas = recuento['blanco']
    recuento_negras = recuento['negro']
    resultado = ""
    if recuento_blancas > recuento_negras:
        resultado = "Fichas blancas ganan"
    elif recuento_negras > recuento_blancas:
        resultado = "Fichas negras ganan"
    else:
        resultado = "Empate"
    imprimir_matriz_Prolog()
    ventana_final = tk.Toplevel()
    ventana_final.title("Resultados")
    ventana_final.geometry("300x300")
    ventana_final.resizable(False, False)
    
    lbl_blancas = tk.Label(ventana_final, text=f"Fichas Blancas: {recuento_blancas}")
    lbl_blancas.pack(pady=20)

    lbl_negras = tk.Label(ventana_final, text=f"Fichas Negras: {recuento_negras}")
    lbl_negras.pack(pady=20)

    lbl_resultado = tk.Label(ventana_final, text=f"Resultado: {resultado}")
    lbl_resultado.pack(pady=20)

    btn_salir = tk.Button(ventana_final, text="Salir", command=ventana_final.destroy)
    btn_salir.pack(pady=5)
    centrar_ventana(ventana_final) 
    
def imprimir_tablero(tablero):
    print("[")
    for fila in tablero:
        print(" "+ str(fila))
    print("]")
        
# Función para salir del juego
def salir_juego():
    if messagebox.askokcancel("Salir", "¿Estás seguro que quieres salir?"):
        menu.destroy()
        
def centrar_ventana(ventana):
    ventana.update_idletasks()
    ancho_ventana = ventana.winfo_width()
    alto_ventana = ventana.winfo_height()
    x_ventana = (ventana.winfo_screenwidth() // 2) - (ancho_ventana // 2)
    y_ventana = (ventana.winfo_screenheight() // 2) - (alto_ventana // 2)
    ventana.geometry('{}x{}+{}+{}'.format(ancho_ventana, alto_ventana, x_ventana, y_ventana))  
    
#------------------------------------------------------------->Consultas a Prolog<------------------------------------------------------------
def InicializarMatriz_Prolog(Tam):
    consulta = f"iniciar_tablero({Tam})."
    list(prolog.query(consulta))
    posicion = Tam // 2
    # +1 porque el tablero empieza en (1,1)
    actualizar_valor_Prolog(posicion + 1, posicion + 1, 'negro')
    actualizar_valor_Prolog(posicion, posicion, 'negro')
    actualizar_valor_Prolog(posicion+1 , posicion, 'blanco')
    actualizar_valor_Prolog(posicion, posicion+1 , 'blanco')
    imprimir_matriz_Prolog()

# Función para actualizar un valor en la matriz
def actualizar_valor_Prolog(fila, columna, valor):
    consulta = f"movimiento({fila}, {columna}, {valor})."
    list(prolog.query(consulta))

def movimientoProlog():
    # Consulta Prolog
    global Mov_Cpu, Mov_Jugador, Juego_Fin
   
    consulta = "mejor_movimiento('negro', Movimiento)"
    # Realizar la consulta
    resultados = list(prolog.query(consulta))
    if Juego_Fin!=True and Mov_Cpu ==True: # El juego sigue en curso
        print("Buscando mejor movimiento")
        if resultados:
            result = resultados[0]['Movimiento']
            # Buscar los números en la cadena usando una expresión regular
            numeros = re.findall(r'\d+', result)
            # Los números encontrados estarán en forma de cadena, así que se convierte a int
            numeros_enteros = [int(num) for num in numeros] 
            # Asignar cada valor a una variable separada
            fila = numeros_enteros[0]
            columna = numeros_enteros[1]
            print("Movimiento a hacer:",(fila-1,columna-1)) # los indices en prolog empiezan en 1 por eso se resta 1
            actualizar_valor_Prolog(fila,columna,'negro')
            Jugador_IA(fila-1,columna-1,'negro') # los indices en prolog empiezan en 1 por eso se resta 1
            imprimir_matriz_Prolog()
        else:
            print("No hay movimientos válidos disponibles para el jugador con fichas negras.")
            Mov_Jugador, Mov_Cpu = Mov_Cpu, Mov_Jugador
# Función para imprimir la matriz
def imprimir_matriz_Prolog():
    print("Tablero desde Prolog.")
    for solucion in prolog.query("imprimir_matriz."):
        if solucion != {}:
            print(solucion)

if __name__== '__main__':    
    menu = tk.Tk()
    menu.title("Menú Principal")
    menu.geometry("400x200")
    menu.resizable(False, False)
    btn_jugar = tk.Button(menu, text="Jugar", command=abrir_configuracion)
    btn_jugar.pack(pady=20)
    btn_salir = tk.Button(menu, text="Salir", command=salir_juego)
    btn_salir.pack()
    # Variables globales para el tamaño de las casillas
    tamaño_casilla_ancho = None
    tamaño_casilla_alto = None
    Mov_Jugador= True
    Mov_Cpu = False
    Juego_Fin= False
    prolog = Prolog()
    # Cargar el archivo de Prolog que contiene los hechos y reglas definidas
    prolog.consult("metodoLista.pl")
    centrar_ventana(menu)
    menu.mainloop()