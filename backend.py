

def meetsCondition(clave, texto):
    return bool(clave.startswith(texto) or clave.startswith(texto.upper()) or clave.startswith(texto.capitalize()) or clave.startswith(texto.lower()))
def meetsConditionFrec(frec,n):
    return bool(frec <= n)

class node:
    def __init__(self,parent = None):

        self.frec = 1
        self.hijos = dict()
        self.padre = parent # nodo padre

    # agrega un nodo
    def add(self,texto):
        texto = texto.strip()
        if len(texto)>0 and texto != ' ':
            if texto in self.hijos:
                self.hijos[texto].frec += 1
            else:
                nodo = node(parent = self)
                self.hijos[texto] = nodo

    # borra un nodo
    def delete(self, texto):
        if texto in self.hijos:
            if self.hijos[texto].frec == 1:
                del self.hijos[texto]
            else:
                self.hijos[texto].frec = self.hijos[texto].frec - 1

    # función que retrocede si el usuario borra una palabra que había escrito
    def goBack(self):
        return self.padre

    # para moverse un lugar
    def move(self,texto):
        if texto not in self.hijos:
            self.add(texto)
        return self.hijos[texto] # devuelve el nodo correspondiente a esa palabra (CHEQUEAR QUE ESTÉ)

    # para avanzar en el árbol varios nodos a la vez
    def jump(self,frase, agregar = True):
        r = frase.find(' ')
        if r == 0:
            frase = frase.lstrip()
            r = frase.find(' ')
        cur = self
        if r > -1:
            if agregar:
                cur.add(frase[:r])
            cur = cur.move(frase[:r])
            cur = cur.jump(frase[r+1:])
        elif len(frase)>0:
            if agregar:
                cur.add(frase)
            cur = cur.move(frase)
        return cur

    # devuelve palabras sugeridas que comiencen con determinadas letras
    def startingWith(self,texto):
        pal =[el for el in self.hijos.keys() if meetsCondition(el,texto)] # devuelve una lista ordenada (según frec) con todas las palabras que arrancan así
        if len(pal) > 0:
            pal = self.mergeSort(pal)
        return pal

    def merge(self,a, b):
        c = []
        m, n = 0, 0
        while m < len(a) and n < len(b):
            if self.hijos[a[m]].frec > self.hijos[b[n]].frec:
                c.append(a[m])
                m += 1
            else:
                c.append(b[n])
                n += 1
        if m == len(a):
            c.extend(b[n:])
        else:
            c.extend(a[m:])
        return c

    def mergeSort(self,vd): # vd es la lista de keys
        if len(vd) <= 1:
            return vd

        left, right = self.mergeSort(vd[:int(len(vd) / 2)]), self.mergeSort(vd[int(len(vd) / 2):])

        return self.merge(left, right)

    # para armar las frases sugeridas
    def treeTraversal(self, phrase, lista,k):
        if (k == 5 or len(self.hijos) == 0) and len(lista) < 5 and phrase != '':
            lista.append(phrase[1:])

        elif len(self.hijos) > 0 and len(lista) < 5:
            pal = self.startingWith('')

            if len(pal) >= 2:
                self.hijos[pal[0]].treeTraversal(phrase + ' ' + pal[0], lista, k+1)

                self.hijos[pal[1]].treeTraversal(phrase + ' ' + pal[1], lista, k + 1)

            else:
                self.hijos[pal[0]].treeTraversal(phrase + ' ' + pal[0], lista, k + 1)

    def treeCleaning(self,n = 1):
        hijos_del = [el for el in self.hijos.keys() if meetsConditionFrec(self.hijos[el].frec, n)] #nodos a borrar
        for el in hijos_del:
            for i in range(self.hijos[el].frec):
                self.delete(el)

        hijos = self.hijos.keys()  # todos los hijos de un nodo
        for el in hijos:
            self.hijos[el].treeCleaning(n)
