#Equipo
#Luis Sebastián Chavarría Cerda 
#Eduardo Iván Quintanilla Elizondo 
#Dante Osmar Limas Lopez 
#César Eduardo Leos Molina 

from scipy.optimize import linprog
import math
import csv

#Como linprog minimiza hay que multiplicar por -1 la funcion objetivo al maximizar
c = [] #Funcion objetivo
A_ub = [] #Restricciones con desigualdades
b_ub = [] #Lados derechos de restricciones con desigualdades
A_eq = [] #Restricciones con igualdades
b_eq = [] #Lados derechos de restricciones con igualdades

greatestLeaf = {"value": [-99999]} #Creamos una hoja con un valor de z muy pequeño para ayudar a encontrar la hoja mayor

def readcsv(archivo):   #Función para la lectura del archivo csv, conteniendo los coeficientes de la Func Objetivo y las restricciones
    input = open(archivo, "r")  #Se abre el archivo
    reader = csv.reader(input, delimiter=",")   #La coma delimita la separación de los valores
    rownum = 0
    a = []  #Declaramos la variable que contendrá todos los valores que leerá del archivo
    for row in reader:
        a.append(row)   #Añade la fila de valores al arreglo a
        rownum += 1     #Incrementa en 1 el numero de fila
    input.close()   #Cierra el archivo
    return a    #Regresa arreglo con todos los valores

def es_entero(x): #Funcion para saber si los numeros son enteros
    return x - int(x) == 0 #Regresa True si es entero y False si es decimal

def negativo(arr): #Convierte las restricciones de <= a >=
    arr[-1] = [i * -1 for i in arr[-1]]
    return arr

def createTree(c, A_ub, b_ub, A_eq, b_eq, z = -99999): #Crea el arbol
    Tree = { #Creamos un diccionario 
        "value" : None, #Valores de z y x
        "left" : None, #Hijo izquierdo
        "right" : None, #Hijo derecho
        "status": None #Status que nos indica si tiene soluciond
    }

    nueva_restriccion = []
    indice = None

    res = linprog(c, A_ub, b_ub, A_eq, b_eq, bounds=(0, None), method='simplex') #Llamamos al metodo simplex
    res_fun = res.fun * -1 #Como linprog es para minimizar multiplicamos por -1
    Tree["value"] = [res_fun, res.x]
    Tree["status"] = res.status

    if res.status != 0: #Si no tiene solucion retorna el arbol
        return Tree
    
    for i, x in enumerate(res.x): #Verifica si las variables son enteras
        if not es_entero(x):
            indice = i
            break

    if indice == None and res_fun > z: #Si todos son enteros y el nuevo valor de z es mayor al guardado guardamos el nuevo valor de z
        z = res_fun

    if indice != None and res_fun > z: #Si se encontro un valor que no es entero ramificamos
        for i in range(len(res.x)): #Ciclo para agregar los coeficientes de la nueva restriccion
            if indice != i:
                nueva_restriccion.append(0)
            else:
                nueva_restriccion.append(1)
        try: #Se agrega la nueva restriccion y su lado derecho
            A_ub_nuevo = A_ub.copy()
            A_ub_nuevo.append(nueva_restriccion) #Agregamos la nueva restriccion
            b_ub_izquierdo = b_ub.copy()
            b_ub_izquierdo.append(math.floor(res.x[indice])) #Agregamos el piso de la variable no entera para el hijo izqueirdo
            b_ub_derecho = b_ub.copy()
            b_ub_derecho.append(math.ceil(res.x[indice]) * -1) #Agregamos el techo de la variable no entera para el hijo derecho para cambiar de <= a >=
        except:
            A_ub_nuevo = [nueva_restriccion]
            b_ub_izquierdo = [math.floor(res.x[indice])]
            b_ub_derecho = [math.ceil(res.x[indice])]
        Tree["left"] = createTree(c, A_ub_nuevo, b_ub_izquierdo, A_eq, b_eq, z) #Creamos el hijo izquierdo
        Tree["right"] = createTree(c, negativo(A_ub_nuevo), b_ub_derecho, A_eq, b_eq, z) #Creamos el hijo derecho

    return Tree

def getGreatestLeafs(Tree): #Funcion para encontrar el hijo mas grande
    global greatestLeaf #Tomamos el valor de la hoja mas grande
    enteros = True
    if Tree["left"] == None and Tree["right"] == None: #Verifica si la rama no tiene hijos
        print("Hoja:")
        print("\tz* = ", Tree["value"][0])
        print("\tx* = ", Tree["value"][1])
        if Tree["value"][0] > greatestLeaf["value"][0] and Tree["status"] == 0: #Verfica si la funcion objetivo de la hoja es mayor que la guardada y tiene solucion factible
            for i in Tree["value"][1]: #Comprobamos que los valores de x sean enteros
                if not es_entero(i):
                    enteros = False
            if enteros: #Si todos son enteros guardamos la nueva hoja mas grande
                greatestLeaf = Tree
    else: #Si tiene hijos pasamos a los hijos
        getGreatestLeafs(Tree["left"])
        getGreatestLeafs(Tree["right"])

def BnB(c, A_ub, b_ub, A_eq, b_eq): #Branch and Bound
    global greatestLeaf
    Tree = createTree(c, A_ub, b_ub, A_eq, b_eq) #Creamos el arbol
    getGreatestLeafs(Tree) #Obtenemos la hoja mas grande
    z, x = greatestLeaf["value"] #Desempaquedar funcion objetivo y valores de x
    return z, x

datos = readcsv(r'Equipo2_datos.csv') #Llama a la función "readcsv" para leer el archivo csv
c = datos[1][1:] #Lee los beneficios de los objetos
A_ub.append(datos[2][1:])    #Lee los pesos de los objetos
b_ub.append(datos[3][1])      #Lee el peso maximo de la mochila
print(c,A_ub, b_ub)
c = negativo([[float(i) for i in c]]) #Convierte los valores a tipo flotante (anteriormente eran tipo caracter y la librería scipy trabaja con flotantes o enteros) y Convierte la función objetivo a maximizar, multiplicando sus valores por -1
b_ub = [float(i) for i in b_ub]         #Convierte los valores a tipo flotante (anteriormente eran tipo caracter y la librería scipy trabaja con flotantes o enteros)
b_eq = [float(i) for i in b_eq]
A_ub = [[float(i) for i in A_ub[j]] for j in range(len(A_ub))]
A_eq = [[float(i) for i in A_eq[j]] for j in range(len(A_eq))]

if len(A_eq) == 0:  #Si no existen restricciones con "=", las variables A_eq y b_eq se igual a "None", ya que no pueden quedarse como arreglo vacío
    A_eq = None
    b_eq = None

z, x = BnB(c, A_ub, b_ub, A_eq, b_eq) #Invocamos el metodo Branch and Bound

print("\nValor Optimo Funcion Objetivo:")   
print("\tz* = ", z)
print("Solicion Optima:")
print("\tx* = ", x)