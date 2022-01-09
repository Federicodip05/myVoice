import sys
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QMainWindow, QHBoxLayout, QMessageBox, QGraphicsView
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QTextCursor, QFont, QCursor
from userinterface import MainWindow
from nltk import tokenize
from pynput import keyboard, mouse
import time
import smtplib
import pyttsx3
from platform import system
import pickle
from datetime import timedelta
import os
from threading import Thread
import glob
from weatherAPI import WeatherWorker, from_ts_to_time_of_day


class Aplicacion(QMainWindow):

    def __init__(self):
        super().__init__()

        self.ui = MainWindow()
        self.ui.setupUi(self)

        # self.ui.centralwidget.setStyleSheet("QMainWindow {border-image: url('pngFondoB.png');}")

        # Esto es por si los dejamos seteados con Enabled(True)
        self.ui.vMail.setVisible(False)
        self.ui.vWord.setVisible(False)
        self.ui.vConfiguracion.setVisible(False)
        self.ui.vCalendario.setVisible(False)
        self.ui.vCalculadora.setVisible(False)
        self.ui.vClima.setVisible(False)
        self.tecladoFilas()
        self.vInicioVentanasHijos()

        self.palette = QtGui.QPalette()

        # Edit text general
        self.ui.textEdit.setTextBackgroundColor(QtCore.Qt.darkGray)


        self.MouseC = mouse.Controller()
        # Título word
        self.ui.wTitulo.setTextBackgroundColor(QtCore.Qt.darkGray)
        # Mail destino y asunto
        self.ui.mDestino.setTextBackgroundColor(QtCore.Qt.darkGray)
        self.ui.mAsunto.setTextBackgroundColor(QtCore.Qt.darkGray)
        
        # Canlendario
        # self.ui.calen_event_category.setTextBackgroundColor(QtCore.Qt.darkGray)
        # self.ui.calen_event_hora.setTextBackgroundColor(QtCore.Qt.darkGray)
        # self.ui.calen_event_title.setTextBackgroundColor(QtCore.Qt.darkGray)

        # Reloj
        self.ui.reloj0.display(time.strftime("%H" + ":" + "%M"))
        self.ui.timer = QtCore.QTimer()
        self.ui.timer.timeout.connect(self.Time)
        self.ui.timer.start(1000)
        paletita = self.ui.reloj0.palette()
        paletita.setColor(QtGui.QPalette.Light, QtCore.Qt.lightGray)
        paletita.setColor(QtGui.QPalette.Dark, QtCore.Qt.white)
        self.ui.reloj0.setPalette(paletita)

        # Calendario
        self.ui.calen_titulo.setCheckable(True)
        self.ui.calen_categoria.setCheckable(True)
        self.ui.calen_hora.setCheckable(True)

        self.ui.calen_titulo.setVisible(False)
        self.ui.calen_categoria.setVisible(False)
        self.ui.calen_hora.setVisible(False)

        self.ui.calen_titulo.setChecked(False)
        self.ui.calen_categoria.setChecked(False)
        self.ui.calen_hora.setChecked(False)

        with open('eventos.pickle', 'rb') as f:
            dicEventos = pickle.load(f)

        self.events = dicEventos

        # Word
        self.ui.wNegrita.setCheckable(True)
        self.ui.wSubrayar.setCheckable(True)
        self.ui.wCursiva.setCheckable(True)
        self.ui.wButtonTitulo.setCheckable(True)
        self.ui.wNegrita.setChecked(False)
        self.ui.wSubrayar.setChecked(False)
        self.ui.wCursiva.setChecked(False)
        self.ui.wButtonTitulo.setChecked(False)
        self.ui.wButtonTitulo.setVisible(False)

        # Clima
        self.threadpool = QtCore.QThreadPool()
        self.update_weather()

        # Calcudora
        self.ui.teclaDividir.setCheckable(True)
        self.ui.teclaMutiplicar.setCheckable(True)
        self.ui.teclaMenos.setCheckable(True)
        self.ui.teclaMas.setCheckable(True)
        self.ui.teclaMas.setChecked(False)
        self.ui.teclaMenos.setChecked(False)
        self.ui.teclaMutiplicar.setChecked(False)
        self.ui.teclaDividir.setChecked(False)
        self.firstNum = None
        self.userIsTypingSecondNumber = False
        self.focusStyle = "background-color:rgb(83, 255, 255); color: black"
        self.borderStyle = " rgb(83,255,255) "  # Rosa bb
        self.focusDark()
        # " rgb(255,105,180) " # Rosa
        # " rgb(83,255,255) " #Azul
        # " rgb(56,252,72) " #Verde
        # " rgb(254,80,0) " #Naranja
        # " rgb(255,255,0) "  # Amarillo
        # " rgb(255,114,118) " #Rosa bb

        # Configuración
        self.ui.confHablaButton.setVisible(False)
        self.ui.confPaletaButton.setVisible(False)
        self.ui.confTecladoButton.setVisible(False)
        self.ui.confPredictorButton.setVisible(False)
        self.ui.confHablaButton.setCheckable(True)
        self.ui.confPaletaButton.setCheckable(True)
        self.ui.confTecladoButton.setCheckable(True)
        self.ui.confPredictorButton.setCheckable(True)
        palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(83, 255, 255))
        app.setPalette(palette)
        self.dicCambiarTeclado = dict(
            [('Á?1', self.tecladoNum), ('ABC', self.tecladoOriginal), ('#+=', self.tecladoNum2)])
        self.teclaTab = 'Z'  # QtCore.Qt.Key_Z
        self.teclaAccion = 'X'  # QtCore.Qt.Key_X
        self.ui.confTeclaAccionText.setPlainText('X')
        self.ui.confTeclaTabularText.setPlainText('Z')
        self.modoTeclas = 'DosTeclas'
        self.keysEvent = True
        self.modoInput = 'ModoTeclado'

        # Pl mail
        self.ui.mEscribirDestino.setCheckable(True)
        self.ui.mEscribirAsunto.setCheckable(True)
        self.ui.mEscribirDestino.setVisible(False)
        self.ui.mEscribirAsunto.setVisible(False)
        self.correo = ''  # Insertar Mail
        self.contrasena = ''  # Insertar Contrasena

        # Predictor
        with open('arbol.pickle', 'rb') as f:
            arbol = pickle.load(f)

        self.word = ''
        self.phrase = ''
        self.arboles = arbol

        self.currentNode = self.arboles
        self.dicCasos = dict.fromkeys('AÁBCDEÉFGHIÍJKLMNÑOÓPQRSTUÚÜVWXYZ,\"\'@0123456789_-¿¡#/{[(%$=*+^<>|°~€£Ç&',
                                      self.newChar)
        self.dicCasos.update(dict.fromkeys(' ', self.nextWord))
        self.dicCasos.update(dict.fromkeys('?!.;:)]}\n', self.newSentence))

        frases = []
        self.arboles.treeTraversal('', frases, 0)
        for i in range(len(frases)):
            frases[i] = frases[i][2:]
        self.freqPhrases = frases

        palabras = []
        letras = self.arboles.startingWith('')
        for i in range(6):
            palabras.append(self.arboles.hijos[letras[i]].startingWith('')[0])
        self.freqWords = palabras

        # central widget es el widget al que pertenecen todos los demás widgets
        # genero la conexión al evento "apretar una tecla"
        self.ui.centralwidget.keyPressEvent = self.keyPressEvent
        self.ui.centralwidget.mousePressEvent = self.mousePressEvent
        self.ui.centralwidget.mouseMoveEvent = self.mouseMoveEvent
        #self.ui.centralwidget.mouseReleaseEvent = self.mouseReleaseEvent


        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()

        # Configuro en la GUI la voz que seleccione
        self.numeroVoz = 1  # Numero de voz es igual al num de voz que elegimos +1
        # Para ver cuantas voces tienen hagan print(len(voices))
        dic = self.misVoces()
        self.ui.lineEditVoces.setText(dic[self.numeroVoz][0])

        self.dic = self.diccionarioInicio()
        self.text = self.ui.textEdit
        # self.teclado = self.ui.teclado
        self.paletaDark()
        self.show()

    # Defino la función que responde al evento "presionar una tecla"
    def keyPressEvent(self, event):

        # self.ultimaTecla = event.key()
        # Forma convencional!
        if self.keysEvent == True and self.modoInput == 'ModoTeclado':
            if self.modoTeclas == 'DosTeclas':
                if event.text().upper() == self.teclaTab.upper():  # me fijo si la tecla presionada es Z (o z)
                    if self.ui.vConfiguracion.isVisible():
                        self.tabularConf()
                    else:
                        self.tabular()
                elif event.text().upper() == self.teclaAccion.upper():  # me fijo si la tecla presionada es X (o x)
                    self.accion()

            # Con una sola tecla!
            elif self.modoTeclas == 'UnaTecla':
                if event.text().upper() == self.teclaTab.upper() and not event.isAutoRepeat():  # me fijo si la tecla presionada es Z (o z)

                    self.t = time.time()
                    with keyboard.Listener(on_release=self.callb) as listener:  # setting code for listening key-release
                        def time_out(period_sec: float):
                            time.sleep(period_sec)  # Listen to keyboard for period_sec seconds
                            listener.stop()

                        Thread(target=time_out, args=(0.2,)).start()
                        listener.join()

                    self.ti1 = time.time() - self.t
                    if float(self.ti1) < 0.2:
                        self.t = None
                        if self.ui.vConfiguracion.isVisible():
                            self.tabularConf()
                        else:
                            self.tabular()
                    else:
                        self.t = None
                        self.accion()

    def callb(self, key):  # what to do on key-release
        return False


    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove:
            if event.buttons() == QtCore.Qt.NoButton:
                pos = event.pos()
                self.edit.setText('x: %d, y: %d' % (pos.x(), pos.y()))
            else:
                pass  # do other stuff
        return QtGui.QMainWindow.eventFilter(self, source, event)


    def mousePressEvent(self, event):
        if self.modoInput == 'ModoMouse':

            if event.button() == QtCore.Qt.RightButton:
                if self.ui.vConfiguracion.isVisible():
                    self.tabularConf()
                else:
                    self.tabular()

            elif event.button() == QtCore.Qt.LeftButton:
                self.accion()
        # Con una sola tecla!
  #      elif self.modoTeclas == 'UnaTecla':
  #          if event.button() == QtCore.Qt.RightButton:
  #              self.t = time.time()
    #
     #           with keyboard.Listener(on_release=self.callb) as listener:  # setting code for listening key-release
     #               def time_out(period_sec: float):
     #                   time.sleep(period_sec)  # Listen to keyboard for period_sec seconds
     #                   listener.stop()
#
 #                   Thread(target=time_out, args=(0.5,)).start()
  #                  listener.join()


   #             self.ti1 = time.time() - self.t
    #            if float(self.ti1) < 0.5:
     #               self.t = None
     #               if self.ui.vConfiguracion.isVisible():
     #                   self.tabularConf()
     #               else:
     #                   self.tabular()
     #           else:
     #               self.t = None
     #               self.accion()



    def moverHabla(self):
        self.ui.vConfiguracionInterna.setGeometry(QtCore.QRect(0, 0, 847, 1131))

    def moverPaleta(self):
        self.ui.vConfiguracionInterna.setGeometry(QtCore.QRect(0, -190, 847, 1131))

    def moverPredictor(self):
        self.ui.vConfiguracionInterna.setGeometry(QtCore.QRect(0, -670, 847, 1131))

    def Limpiar(self):
        self.arboles.treeCleaning()

    def Entrenar(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Text files (*.txt)", options=options)
        if fileName:
            with open(fileName, 'r', encoding="utf-8") as myfile:
                data = myfile.read()

            parrafos = (data.split('\n'))

            phrases = []
            for par in parrafos:
                phrases = phrases + tokenize.sent_tokenize(par)

            for l in phrases:
                self.arboles.add(l[0].upper())
                cur = self.arboles.move(l[0].upper())
                cur.jump(l)
                if len(l) > 0:
                    palabras = l.split()
                    for k in range(1, len(palabras)):
                        self.arboles.add(palabras[k][0].upper())
                        nodo = self.arboles.hijos[palabras[k][0].upper()]
                        for j in range(k, len(palabras)):
                            nodo.add(palabras[j])
                            nodo = nodo.move(palabras[j])

    # Calculadora
    def calculator(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()
        dicType = dict([('tecla0', self.digitPress), ('tecla1', self.digitPress),
                        ('tecla2', self.digitPress), ('tecla3', self.digitPress),
                        ('tecla4', self.digitPress), ('tecla5', self.digitPress),
                        ('tecla6', self.digitPress), ('tecla7', self.digitPress),
                        ('tecla8', self.digitPress), ('tecla9', self.digitPress),
                        ('teclaMas', self.binaryOperationPress),
                        ('teclaMenos', self.binaryOperationPress),
                        ('teclaMutiplicar', self.binaryOperationPress),
                        ('teclaDividir', self.binaryOperationPress),
                        ('teclaAC', self.clearPress),
                        ('teclaComaCalcu', self.decimalPress),
                        ('teclaIgual', self.equalsPress)
                        ])

        dicType[a]()

        focus_widget.setStyleSheet("")
        self.ui.teclaSalir.setFocus()
        self.ui.teclaSalir.setStyleSheet(self.focusStyle)

    def clearPress(self):
        self.ui.teclaMas.setChecked(False)
        self.ui.teclaMenos.setChecked(False)
        self.ui.teclaMutiplicar.setChecked(False)
        self.ui.teclaDividir.setChecked(False)
        self.userIsTypingSecondNumber = False
        self.ui.resultado.setText('0')

    def digitPress(self):
        button = self.ui.centralwidget.focusWidget()
        if ((self.ui.teclaMas.isChecked() or self.ui.teclaMenos.isChecked() or
             self.ui.teclaMutiplicar.isChecked() or self.ui.teclaDividir.isChecked()) and (
                not self.userIsTypingSecondNumber)):
            newLabel = format(float(button.text()), '.15g')
            self.userIsTypingSecondNumber = True
        else:
            if (('.' in self.ui.resultado.text()) and (button.text() == '0')):  # Para que tome el 0.
                newLabel = format(self.ui.resultado.text() + button.text(), '.15g')
            else:
                newLabel = format(float(self.ui.resultado.text() + button.text()), '.15g')

        self.ui.resultado.setText(newLabel)

    def decimalPress(self):
        self.ui.resultado.setText(self.ui.resultado.text() + '.')

    def binaryOperationPress(self):
        button = self.ui.centralwidget.focusWidget()
        self.firstNum = float(self.ui.resultado.text())
        button.setChecked(True)

    def equalsPress(self):
        secondNum = float(self.ui.resultado.text())
        if self.ui.teclaMas.isChecked():
            labelNumber = self.firstNum + secondNum
            newLabel = format(labelNumber, '.15g')
            self.ui.resultado.setText(newLabel)
            self.ui.teclaMas.setChecked(False)
        elif self.ui.teclaMenos.isChecked():
            labelNumber = self.firstNum - secondNum
            newLabel = format(labelNumber, '.15g')
            self.ui.resultado.setText(newLabel)
            self.ui.teclaMenos.setChecked(False)
        elif self.ui.teclaDividir.isChecked():
            labelNumber = self.firstNum / secondNum
            newLabel = format(labelNumber, '.15g')
            self.ui.resultado.setText(newLabel)
            self.ui.teclaDividir.setChecked(False)
        elif self.ui.teclaMutiplicar.isChecked():
            labelNumber = self.firstNum * secondNum
            newLabel = format(labelNumber, '.15g')
            self.ui.resultado.setText(newLabel)
            self.ui.teclaMutiplicar.setChecked(False)
        self.userIsTypingSecondNumber = False

    # Reloj
    def Time(self):
        self.ui.reloj0.display(time.strftime("%H" + ":" + "%M"))

    # Configuracion ventana inicio
    def confInicio(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")

        self.ui.vCalculadora.setVisible(False)
        self.ui.vCalendario.setVisible(False)
        self.ui.vClima.setVisible(False)
        self.ui.vConfiguracion.setVisible(False)
        self.ui.vMail.setVisible(False)
        self.ui.vWord.setVisible(False)

        self.ui.vInicio.setVisible(True)
        self.ui.vInicio.setEnabled(True)

        self.ui.reloj0.setParent(self.ui.vInicio)
        self.ui.reloj0.setVisible(True)

        self.ui.textEdit.setParent(self.ui.vInicio)
        self.ui.textEdit.setVisible(True)
        self.ui.textEdit.setGeometry(QtCore.QRect(30, 20, 651, 251))
        self.ui.textEdit.clear()

        self.ui.textEdit.setFontItalic(False)
        self.ui.textEdit.setFontUnderline(False)
        self.ui.textEdit.setFontWeight(QFont.Normal)

        self.text = self.ui.textEdit

        self.ui.teclado.setParent(self.ui.vInicio)
        self.ui.teclado.setGeometry(QtCore.QRect(30, 290, 311, 261))
        self.ui.teclado.setVisible(True)

        self.ui.VPalabras.setParent(self.ui.vInicio)
        self.ui.VPalabras.setVisible(True)
        self.ui.VPalabras.setGeometry(QtCore.QRect(360, 290, 321, 91))

        self.ui.VFrases.setParent(self.ui.vInicio)
        self.ui.VFrases.setVisible(True)
        self.ui.VFrases.setGeometry(QtCore.QRect(360, 385, 321, 166))

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.VAplicaciones.setEnabled(False)

        self.dic = self.diccionarioInicio()
        self.dicCambiarTeclado['ABC']()
        self.vInicioVentanasHijos()

    # Configuracion ventana word
    def confWord(self):

        self.archivos = []

        for file in glob.glob("*.html"):
            a = file.rfind('.')
            self.archivos.append(file[:a])

        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.vInicio.setEnabled(False)
        self.ui.vInicio.setVisible(False)
        self.ui.vWord.setVisible(True)

        self.ui.reloj0.setParent(self.ui.vWord)
        self.ui.reloj0.setVisible(True)

        self.ui.textEdit.setParent(self.ui.vWord)
        self.ui.textEdit.setVisible(True)
        self.ui.textEdit.setGeometry(QtCore.QRect(30, 50, 641, 221))
        self.ui.textEdit.clear()

        self.ui.teclado.setParent(self.ui.vWord)
        self.ui.teclado.setVisible(True)

        self.ui.VPalabras.setParent(self.ui.vWord)
        self.ui.VPalabras.setVisible(True)
        self.ui.VPalabras.setGeometry(QtCore.QRect(350, 290, 321, 91))

        self.ui.VFrases.setParent(self.ui.vWord)
        self.ui.VFrases.setVisible(True)
        self.ui.VFrases.setGeometry(QtCore.QRect(350, 390, 321, 166))

        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()

        self.ui.wCursiva.setChecked(False)
        self.ui.wNegrita.setChecked(False)
        self.ui.wSubrayar.setChecked(False)

        self.dic = self.diccionarioWord()
        self.dicCambiarTeclado['ABC']()
        self.vWordVentanasHijos()

        if len(self.archivos) > 0:

            self.wPopulateList()
            self.ui.wCargar.setEnabled(True)
            self.ui.wArchivoAbajo.setEnabled(True)
            self.ui.wArchivoArriba.setEnabled(True)
            self.ui.wListaArchivos.setCurrentRow(0)

        else:

            self.dic['wGuardar'] = (self.ui.wGuardarCargar, self.wordGuardar)
            self.ui.wCargar.setEnabled(False)
            self.ui.wArchivoAbajo.setEnabled(False)
            self.ui.wArchivoArriba.setEnabled(False)

    # Configuracion ventana calcu
    def confCalcu(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.vInicio.setEnabled(False)
        self.ui.vCalculadora.setVisible(True)
        self.ui.reloj0.setParent(self.ui.vCalculadora)
        self.ui.reloj0.setVisible(True)
        self.ui.teclaSalir.setStyleSheet(self.focusStyle)
        self.ui.teclaSalir.setFocus()
        self.firstNum = None
        self.clearPress()
        self.dic = self.diccionarioCalcu()
        self.vCalcuVentanasHijos()
        self.ui.calcuF1.setStyleSheet('')
        self.ui.calcuF2.setStyleSheet('')
        self.ui.calcuF3.setStyleSheet('')
        self.ui.calcuF4.setStyleSheet('')
        self.ui.calcuC.setStyleSheet('')

    def confClima(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.vInicio.setEnabled(False)
        self.ui.vClima.setVisible(True)
        self.ui.climaSalir.setStyleSheet(self.focusStyle)
        self.ui.climaSalir.setFocus()
        self.dic = self.diccionarioClima()

    # Configuracion ventana calendario
    def confCalen(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.vInicio.setEnabled(False)
        self.ui.vInicio.setVisible(False)
        self.ui.vCalendario.setVisible(True)

        self.ui.reloj0.setParent(self.ui.vCalendario)
        self.ui.reloj0.setVisible(True)

        self.ui.teclado.setParent(self.ui.vCalendario)
        self.ui.teclado.setGeometry(QtCore.QRect(30, 340, 311, 261))
        self.ui.teclado.setVisible(True)

        self.ui.textEdit.setParent(self.ui.calenEventosBox)
        self.ui.textEdit.setVisible(True)
        self.ui.textEdit.setGeometry(QtCore.QRect(20, 100, 261, 141))
        self.ui.textEdit.clear()

        self.ui.calenSalir.setStyleSheet(self.focusStyle)
        self.ui.calenSalir.setFocus()
        self.vCalenVentanasHijos()
        self.dic = self.diccionarioCalen()
        self.dicCambiarTeclado['ABC']()

        date = self.ui.calendarWidget.selectedDate()

        if date in self.events.keys():
            self.dic['calenFlechasFrame'] = (self.ui.calenEventosFrame, self.ventanaHijo)
            self.dic['calenEventosFrame'] = (self.ui.calenEventosBox, self.eventosFrameEntra)
            self.dic['calenEventoAbajoButton'] = (self.ui.calenEventoArribaButton, self.recorrerListaAbajo)
            self.dic['calenEventoArribaButton'] = (self.ui.calenSeleccionarEventoButton, self.recorrerListaArriba)
            self.dic['calenSeleccionarEventoButton'] = (self.ui.calenEventosFrame, self.populate_form)
            self.dic['calen_add_button'] = (self.ui.calen_del_button, self.save_event)
            self.dic['calen_del_button'] = (self.ui.calenEventosBox, self.delete_event)
            self.populate_list()

        else:
            self.dic = self.diccionarioCalen()
            self.ui.calen_event_list.clear()
            self.clear_form()

    # Configuracion ventana Configuracion
    def confConfiguracion(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.vInicio.setEnabled(False)
        self.ui.vInicio.setVisible(False)
        self.ui.vConfiguracion.setVisible(True)
        self.ui.confSalir.setStyleSheet(self.focusStyle)
        self.ui.confSalir.setFocus()
        self.dic = self.diccionarioConfiguracion()
        self.vConfigVentanasHijos()
        self.moverHabla()
        if self.ui.radioConfUnaTecla.isChecked():
            self.modoAUnaTecla()
        if self.ui.radioConfMouseInput.isChecked():
            self.pasarAModoMouse()


    # Configuracion ventana Mail
    def confMail(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.vInicio.setEnabled(False)
        self.ui.vInicio.setVisible(False)
        self.ui.vMail.setVisible(True)
        self.mayusculas()
        self.ui.reloj0.setParent(self.ui.vMail)
        self.ui.reloj0.setVisible(True)

        self.ui.textEdit.setParent(self.ui.vMail)
        self.ui.textEdit.setVisible(True)
        self.ui.textEdit.setGeometry(QtCore.QRect(30, 100, 641, 171))
        self.ui.textEdit.clear()

        self.ui.teclado.setParent(self.ui.vMail)
        self.ui.teclado.setGeometry(QtCore.QRect(30, 290, 311, 261))
        self.ui.teclado.setVisible(True)

        self.ui.VPalabras.setParent(self.ui.vMail)
        self.ui.VPalabras.setVisible(True)
        self.ui.VPalabras.setGeometry(QtCore.QRect(350, 290, 321, 91))

        self.ui.VFrases.setParent(self.ui.vMail)
        self.ui.VFrases.setVisible(True)
        self.ui.VFrases.setGeometry(QtCore.QRect(350, 390, 321, 166))

        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()

        self.ui.mTeclaEnviar_2.setVisible(True)
        self.ui.mLabelAsunto.setText('Asunto:')
        self.ui.mLabelDestino.setText('Para:')
        self.ui.mTeclaEnviar.setVisible(True)
        self.ui.mTeclaEnter.setText('Enter')
        self.ui.mailContenedor.setGeometry(QtCore.QRect(41, 19, 641, 73))
        self.ui.mBorrarEnter.setGeometry(QtCore.QRect(31, 560, 381, 41))
        self.ui.mailSalir.setVisible(True)

        self.dic = self.diccionarioMail()
        self.dicCambiarTeclado['ABC']()
        self.vMailVentanasHijos()

    def confMailCuenta(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.textEdit.setVisible(False)
        self.ui.mTeclaEnviar_2.setVisible(False)
        self.ui.mLabelAsunto.setText('Contraseña:')
        self.ui.mLabelDestino.setText('Cuenta:')
        contra = ''
        for i in range(len(self.contrasena)):
            contra = contra + '*'
        self.ui.mAsunto.setText(contra)
        self.ui.mDestino.setText(self.correo)
        self.ui.mTeclaEnviar.setVisible(False)
        self.ui.mTeclaEnter.setText('Confirmar')
        self.ui.mailContenedor.setGeometry(QtCore.QRect(120, 150, 641, 73))
        self.ui.teclado.setGeometry(QtCore.QRect(250, 290, 311, 261))
        self.ui.mBorrarEnter.setGeometry(QtCore.QRect(250, 560, 311, 41))
        self.ui.VFrases.setVisible(False)
        self.ui.VPalabras.setVisible(False)
        self.ui.mailSalir.setVisible(False)
        self.dic = self.diccionarioMailCuenta()
        self.dicCambiarTeclado['ABC']()
        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()
        self.ui.mEscribirDestino.setChecked(False)
        self.escribirDestino()

    def escribir(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.text()
        if (a == '__'):
            a = ' '
        elif (a == '&&'):
            a = '&'
        self.text.insertPlainText(a)
        self.word = self.word + a
        # self.word = self.word.strip() #para eliminar espacios extra
        self.phrase = self.phrase + a
        # self.phrase = self.prhase.rstrip() #elimina espacios al final de la frase
        self.dicCasos[a.upper()]()
        focus_widget.setStyleSheet("")
        parent = focus_widget.parent()
        parent.setStyleSheet(self.focusStyle)
        parent.setFocus()

    def saltoLinea(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        self.text.insertPlainText("\n")
        self.dicCasos['\n']()
        focus_widget.setStyleSheet("")
        parent = focus_widget.parent()
        parent.setStyleSheet(self.focusStyle)
        parent.setFocus()

    def salirMenu(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.VAplicaciones.setEnabled(False)
        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()

    def entrarMenu(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        self.ui.VAplicaciones.setEnabled(True)
        self.ui.appCalen.setStyleSheet(self.focusStyle)
        self.ui.appCalen.setFocus()
        focus_widget.setStyleSheet("")

    def borrarLetra(self):
        if len(self.text.toPlainText()) > 0:
            b = self.text.toPlainText()[-1]
            a = self.text.toPlainText()[:-1]
            cursor = self.text.textCursor()
            cursor.movePosition(QTextCursor.End)
            cursor.deletePreviousChar()

            if len(self.text.toPlainText()) == 0:
                self.text.setTextBackgroundColor(QtCore.Qt.darkGray)

            if self.phrase == '':
                if b in '?!.;:)]}\n':
                    frase = []
                    p = max(map(a.rfind, '?!.;:)]}\n'))  # me da la última posición de cualquiera de esos
                    if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                        frase = a[p + 1:]
                    elif p == -1:
                        frase = a  # si p es -1 entonces queda una sola oración
                    if len(frase) > 0:
                        if frase[0] == ' ' and len(frase) > 1:  # recupero la última oración
                            frase = frase.lstrip()
                            # ahora hago todo el recorrido desde el pincipio del árbol hasta la última palabra escrita
                        if frase[0].upper() in self.arboles.hijos:
                            self.currentNode = self.arboles.hijos[frase[0].upper()]
                            r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                            if -1 < r < len(frase) - 1:
                                self.word = frase[r + 1:]
                                self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                                self.currentNode.delete(frase[r + 1:] + b)
                            else:
                                self.word = frase
                        self.phrase = frase

                        self.dicCasos[a[-1].upper()]()


            elif b == ' ':  # si es un espacio tengo que agarrar la última palabra escrita y eliminarla del árbol
                self.phrase = self.phrase[:-1]
                if len(self.phrase) > 0:
                    r = self.phrase.rfind(' ')  # busco último espacio
                    if -1 < r < len(a) - 1:
                        self.word = self.phrase[r + 1:]  # y me quedo con la última palabra
                    elif r == len(self.phrase) - 1:  # o sea que hay otro espacio
                        self.word = ''
                    else:  # si no hay espacios me quedo con todo
                        self.word = self.phrase
                    # ahora tengo que borrar esa palabra del árbol
                    if len(self.word) > 0:
                        if self.word[-1] != ' ':
                            self.currentNode = self.currentNode.goBack()  # retrocedo un nodo
                            if self.currentNode != self.arboles:  # si el nodo en el que estaba tenía padre, borro esa palabra (si no significa que era una letra)
                                self.currentNode.delete(self.word.strip())
                    self.dicCasos[a[-1].upper()]()  # hago como si recién se hubiese escrito el último caracter
                else:
                    self.currentNode = self.arboles
            else:
                self.phrase = self.phrase[:-1]
                # si no, simplemente cambio las sugerencias con la nueva palabra de self.word
                self.word = self.word[:-1]
                if self.phrase == '':
                    self.currentNode = self.arboles
                    self.currentNode.delete(b)  # si era la primera letra de la oración la borro

                else:
                    self.dicCasos[a[-1].upper()]()  # hago como si recién se hubiese escrito el último caracter

    def borrarTodo(self):
        self.text.clear()
        self.word = ''
        self.phrase = ''
        self.currentNode = self.arboles

    def borrarTodoWord(self):
        self.borrarTodo()
        self.ui.textEdit.clear()
        self.ui.wTitulo.clear()

    def reproducir(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        b = self.text.toPlainText()
        self.text.clear()
        engine.say(b)  # Hablar
        engine.runAndWait()  # Esperar a que terine de Hablar
        engine.stop()  # Detener motor tts
        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()
        focus_widget.setStyleSheet("")
        self.tecladoOriginal()

        # reinicio la frase
        if len(self.word) > 0:
            if self.currentNode != self.arboles:
                self.currentNode.add(self.word)
            if self.currentNode != self.arboles and self.currentNode.padre != self.arboles:
                # agrego la palabra al árbol sin el contexto de la frase
                self.arboles.hijos[self.word[0].upper()].add(self.word)

        if len(self.phrase.lstrip()) > 0:
            palabras = self.phrase.split()
            for k in range(1, len(palabras)):
                if palabras[k][0].upper() not in self.arboles.hijos.keys():
                    self.arboles.add(palabras[k][0].upper())
                nodo = self.arboles.hijos[palabras[k][0].upper()]
                for j in range(k, len(palabras)):
                    nodo.add(palabras[j])
                    nodo = nodo.move(palabras[j])

        self.currentNode = self.arboles
        self.word = ''
        self.phrase = ''

        frases = []
        self.arboles.treeTraversal('', frases, 0)
        for i in range(len(frases)):
            frases[i] = frases[i][2:]
        self.freqPhrases = frases

        palabras = []
        letras = self.arboles.startingWith('')
        for i in range(6):
            palabras.append(self.arboles.hijos[letras[i].upper()].startingWith('')[0])
        self.freqWords = palabras

    def focusColor(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()

        self.dicFocus[a][0].setChecked(True)
        self.ui.confTecladoFilasImagen.setPixmap(QtGui.QPixmap("images/tecladoF" + self.dicFocus[a][2] + ".PNG"))
        self.ui.confTecladoColumnasImagen.setPixmap(QtGui.QPixmap("images/tecladoC" + self.dicFocus[a][2] + ".PNG"))
        self.focusStyle = "background-color:" + self.dicFocus[a][1] + self.dicFocus[a][4]
        self.borderStyle = " " + self.dicFocus[a][1] + " "

        self.palette.setColor(QtGui.QPalette.Highlight, self.dicFocus[a][3])
        app.setPalette(self.palette)
        focus_widget.setStyleSheet(self.focusStyle)

    def fondoColor(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()
        dic = dict([
            ('confDark', self.paletaDark),
            ('confGris', self.paletaGris),
            ('confCeleste', self.paletaCeleste),
            ('confBeige', self.paletaBeige)
        ])
        dic[a]()
        focus_widget.setStyleSheet(self.focusStyle)

    def paletaDark(self):
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
        self.palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
        self.palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
        self.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(83, 255, 255))

        self.ui.confTecladoFilasImagen.setPixmap(QtGui.QPixmap("images/tecladoFAzulD.PNG"))
        self.ui.confTecladoColumnasImagen.setPixmap(QtGui.QPixmap("images/tecladoCAzulD.PNG"))
        self.ui.radioAzul.setChecked(True)

        self.focusDark()
        self.ui.labelAzul.setStyleSheet(
            "background-color:rgb(83,255,255); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelVerde.setStyleSheet(
            "background-color: rgb(56, 252, 72); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelNaranja.setStyleSheet(
            "background-color: rgb(254, 80, 0); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelAmarillo.setStyleSheet(
            "background-color: rgb(255, 255, 0); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosa.setStyleSheet(
            "background-color: rgb(255, 105, 180); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosaBB.setStyleSheet(
            "background-color: rgb(255, 114, 118); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")

        self.ui.confFondoNoneLabel.setStyleSheet(
            "background-color: rgb(53,53,53);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255); color: white")
        self.ui.confFondoBLabel.setStyleSheet(
            "background-color: rgb(53,53,53);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoCLabel.setStyleSheet(
            "background-color: rgb(53,53,53);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoDLabel.setStyleSheet(
            "background-color: rgb(53,53,53);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")

        self.ui.calculadora.setStyleSheet(
            "QFrame{background-color:rgb(53,53,53); border: 2px solid gray;} QLabel{background-color:rgb(0,0,0); color: rgb(255,255,255)}")

        self.ui.climaContenedor.setStyleSheet(
            "QFrame{background-color:rgb(53,53,53); } QLabel{color: white}")

        self.focusStyle = "background-color: rgb(83,255,255); color: black"
        self.borderStyle = " rgb(83,255,255) "

        app.setPalette(self.palette)

        self.ui.confPaletaLabel.setStyleSheet("color: white")
        self.ui.confHablaVolumenLabel.setStyleSheet("color: white")
        self.ui.confHablaLabel.setStyleSheet("color: white")
        self.ui.confHablaVelocidadLabel.setStyleSheet("color: white")
        self.ui.confTecladoLabel.setStyleSheet("color: white")
        self.ui.confFocusLabel.setStyleSheet("color: white")
        self.ui.confFondoLabel.setStyleSheet("color: white")
        self.ui.confTecladoColumnasLabel.setStyleSheet("background-color: rgb(53,53,53); color: white")
        self.ui.confTecladoFilasLabel.setStyleSheet("background-color: rgb(53,53,53); color: white")
        self.ui.confRecorridoLabel.setStyleSheet("color: white")
        self.ui.confOrdenTLabel.setStyleSheet("color: white")
        self.ui.mLabelDestino.setStyleSheet("color: white")
        self.ui.mLabelAsunto.setStyleSheet("color: white")
        self.ui.confDisenoLabel.setStyleSheet("color white")
        self.ui.confHablaVozLabel.setStyleSheet("color: white")
        self.ui.confAbecedarioLabel.setStyleSheet("color: white")
        self.ui.confFrecuenciaLabel.setStyleSheet("color: white")
        self.ui.confPredictorLabel.setStyleSheet("color: white")
        self.ui.wLabelTitulo.setStyleSheet("color: white")
        self.ui.calen_labelTitulo.setStyleSheet("color: white")
        self.ui.calen_labelCategoria.setStyleSheet("color: white")
        self.ui.calenEventosFechaLabel.setStyleSheet("background-color: rgb(53,53,53); color: white")
        # self.ui.confRadiosWidget.setStyleSheet("background-color: rgb(53,53,53); color: white")
        self.ui.informacionEntrenarLabel.setStyleSheet("background-color: rgb(53,53,53); color: white")
        self.ui.informacionLimpiarLabel.setStyleSheet("background-color: rgb(53,53,53); color: white")

        self.ui.confHablaVolumenWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVelocidadWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVozWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFocusWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFondoWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confDisenoWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confRecorridoWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confOrdenTWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")

        self.ui.confPaletaWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confTecladoWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confPredictorWidget.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.wWidgetTitulo.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetAsunto.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetDestino.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wtitulo.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wcategoria.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Whora.setStyleSheet(
            "background-color: rgb(53,53,53); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")

        paletita = self.ui.reloj0.palette()
        paletita.setColor(QtGui.QPalette.Light, QtCore.Qt.lightGray)
        paletita.setColor(QtGui.QPalette.Dark, QtCore.Qt.white)
        self.ui.reloj0.setPalette(paletita)

        self.ui.radioDark.setChecked(True)

    def paletaGris(self):
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(180, 180, 175))
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
        self.palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(180, 180, 175))
        self.palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(180, 180, 175))
        self.palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(3, 124, 135))

        self.ui.confTecladoFilasImagen.setPixmap(QtGui.QPixmap("images/tecladoFAzulG.PNG"))
        self.ui.confTecladoColumnasImagen.setPixmap(QtGui.QPixmap("images/tecladoCAzulG.PNG"))
        self.ui.radioAzul.setChecked(True)

        self.focusGris()
        self.ui.labelAzul.setStyleSheet(
            "background-color:rgb(3,124,135); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelVerde.setStyleSheet(
            "background-color: rgb(200, 223, 89); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelNaranja.setStyleSheet(
            "background-color: rgb(251, 193, 26); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelAmarillo.setStyleSheet(
            "background-color: rgb(208, 115, 71); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosa.setStyleSheet(
            "background-color: rgb(6, 96, 78); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosaBB.setStyleSheet(
            "background-color: rgb(204, 111, 169); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")

        self.ui.confFondoNoneLabel.setStyleSheet(
            "background-color: rgb(180, 180, 175);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255); color: black")
        self.ui.confFondoBLabel.setStyleSheet(
            "background-color: rgb(180, 180, 175);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoCLabel.setStyleSheet(
            "background-color: rgb(180, 180, 175);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoDLabel.setStyleSheet(
            "background-color: rgb(180, 180, 175);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")

        self.ui.calculadora.setStyleSheet(
            "QFrame{background-color:rgb(180,180,175); border: 2px solid gray;} QLabel{background-color:rgb(0,0,0); color: rgb(255,255,255)}")

        self.focusStyle = "background-color: rgb(3,124,135); color: black"
        self.borderStyle = " rgb(3,124,135) "

        app.setPalette(self.palette)

        self.ui.confPaletaLabel.setStyleSheet("color: black")
        self.ui.confHablaVolumenLabel.setStyleSheet("color: black")
        self.ui.confHablaLabel.setStyleSheet("color: black")
        self.ui.confHablaVelocidadLabel.setStyleSheet("color: black")
        self.ui.confTecladoLabel.setStyleSheet("color: black")
        self.ui.confFocusLabel.setStyleSheet("color: black")
        self.ui.confFondoLabel.setStyleSheet("color: black")
        self.ui.confTecladoColumnasLabel.setStyleSheet("background-color: rgb(180, 180, 175); color: black")
        self.ui.confTecladoFilasLabel.setStyleSheet("background-color: rgb(180, 180, 175); color: black")
        self.ui.confRecorridoLabel.setStyleSheet("color: black")
        self.ui.confOrdenTLabel.setStyleSheet("color: black")
        self.ui.mLabelDestino.setStyleSheet("color: black")
        self.ui.mLabelAsunto.setStyleSheet("color: black")
        self.ui.confDisenoLabel.setStyleSheet("color: black")
        self.ui.confHablaVozLabel.setStyleSheet("color: black")
        self.ui.confAbecedarioLabel.setStyleSheet("color: black")
        self.ui.confFrecuenciaLabel.setStyleSheet("color: black")
        self.ui.confPredictorLabel.setStyleSheet("color: black")
        self.ui.wLabelTitulo.setStyleSheet("color: black")
        self.ui.calen_labelTitulo.setStyleSheet("color: black")
        self.ui.calen_labelCategoria.setStyleSheet("color: black")
        self.ui.calenEventosFechaLabel.setStyleSheet("background-color: rgb(180, 180, 175); color: black")
        self.ui.informacionEntrenarLabel.setStyleSheet("background-color: rgb(180, 180, 175); color: black")
        self.ui.informacionLimpiarLabel.setStyleSheet("background-color: rgb(180, 180, 175); color: black")

        self.ui.confHablaVolumenWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVelocidadWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVozWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFocusWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFondoWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confDisenoWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confRecorridoWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confOrdenTWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(180,180,175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")

        self.ui.confPaletaWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confTecladoWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confPredictorWidget.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")

        self.ui.wWidgetTitulo.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetAsunto.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetDestino.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wtitulo.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wcategoria.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Whora.setStyleSheet(
            "background-color: rgb(180, 180, 175); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")

        paletita = self.ui.reloj0.palette()
        paletita.setColor(QtGui.QPalette.Light, QtCore.Qt.darkGray)
        paletita.setColor(QtGui.QPalette.Dark, QtGui.QColor(0, 0, 0))
        self.ui.reloj0.setPalette(paletita)

        self.ui.radioGris.setChecked(True)

    def paletaCeleste(self):
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(218, 232, 236))
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
        self.palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(218, 232, 236))
        self.palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(218, 232, 236))
        self.palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(180, 132, 100))

        self.ui.confTecladoFilasImagen.setPixmap(QtGui.QPixmap("images/tecladoFAzulC.PNG"))
        self.ui.confTecladoColumnasImagen.setPixmap(QtGui.QPixmap("images/tecladoCAzulC.PNG"))

        self.ui.radioAzul.setChecked(True)

        self.focusCeleste()
        self.ui.labelAzul.setStyleSheet(
            "background-color:rgb(180,132,100); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelVerde.setStyleSheet(
            "background-color: rgb(75, 125, 139); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelNaranja.setStyleSheet(
            "background-color: rgb(236, 203, 167); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelAmarillo.setStyleSheet(
            "background-color: rgb(253, 147, 52); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosa.setStyleSheet(
            "background-color: rgb(38, 38, 98); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosaBB.setStyleSheet(
            "background-color: rgb(217, 104, 110); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")

        self.ui.confFondoNoneLabel.setStyleSheet(
            "background-color: rgb(218, 232, 236);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255); color: black")
        self.ui.confFondoBLabel.setStyleSheet(
            "background-color: rgb(218, 232, 236);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoCLabel.setStyleSheet(
            "background-color: rgb(218, 232, 236);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoDLabel.setStyleSheet(
            "background-color: rgb(218, 232, 236);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")

        self.ui.calculadora.setStyleSheet(
            "QFrame{background-color:rgb(218,232,236); border: 2px solid gray;} QLabel{background-color:rgb(0,0,0); color: rgb(255,255,255)}")

        self.focusStyle = "background-color: rgb(180,132,100); color: black"
        self.borderStyle = " rgb(180,132,100) "

        app.setPalette(self.palette)

        self.ui.confPaletaLabel.setStyleSheet("color: black")
        self.ui.confHablaVolumenLabel.setStyleSheet("color: black")
        self.ui.confHablaLabel.setStyleSheet("color: black")
        self.ui.confHablaVelocidadLabel.setStyleSheet("color: black")
        self.ui.confTecladoLabel.setStyleSheet("color: black")
        self.ui.confFocusLabel.setStyleSheet("color: black")
        self.ui.confFondoLabel.setStyleSheet("color: black")
        self.ui.confTecladoColumnasLabel.setStyleSheet("background-color: rgb(218, 232, 236); color: black")
        self.ui.confTecladoFilasLabel.setStyleSheet("background-color: rgb(218, 232, 236); color: black")
        self.ui.confRecorridoLabel.setStyleSheet("color: black")
        self.ui.confOrdenTLabel.setStyleSheet("color: black")
        self.ui.mLabelDestino.setStyleSheet("color: black")
        self.ui.mLabelAsunto.setStyleSheet("color: black")
        self.ui.confDisenoLabel.setStyleSheet("color: black")
        self.ui.confHablaVozLabel.setStyleSheet("color: black")
        self.ui.confAbecedarioLabel.setStyleSheet("color: black")
        self.ui.confFrecuenciaLabel.setStyleSheet("color: black")
        self.ui.confPredictorLabel.setStyleSheet("color: black")
        self.ui.wLabelTitulo.setStyleSheet("color: black")
        self.ui.calen_labelTitulo.setStyleSheet("color: black")
        self.ui.calen_labelCategoria.setStyleSheet("color: black")
        self.ui.calenEventosFechaLabel.setStyleSheet("background-color: rgb(218, 232, 236); color: black")
        self.ui.informacionEntrenarLabel.setStyleSheet("background-color: rgb(218, 232, 236); color: black")
        self.ui.informacionLimpiarLabel.setStyleSheet("background-color: rgb(218, 232, 236); color: black")

        self.ui.confHablaVolumenWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVelocidadWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVozWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFocusWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFondoWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confDisenoWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confRecorridoWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confOrdenTWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(218,232,236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")

        self.ui.confPaletaWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confTecladoWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confPredictorWidget.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")

        self.ui.wWidgetTitulo.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetAsunto.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetDestino.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wtitulo.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wcategoria.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Whora.setStyleSheet(
            "background-color: rgb(218, 232, 236); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")

        paletita = self.ui.reloj0.palette()
        paletita.setColor(QtGui.QPalette.Light, QtCore.Qt.darkGray)
        paletita.setColor(QtGui.QPalette.Dark, QtGui.QColor(0, 0, 0))
        self.ui.reloj0.setPalette(paletita)

        self.ui.radioCeleste.setChecked(True)

    def paletaBeige(self):
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(236, 225, 209))  # (218, 197, 188))
        self.palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Base, QtGui.QColor(255, 255, 255))
        self.palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(236, 225, 209))  # (218, 197, 188))
        self.palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Text, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Button, QtGui.QColor(236, 225, 209))  # (218, 197, 188))
        self.palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
        self.palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
        self.palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(120, 182, 219))

        self.ui.confTecladoFilasImagen.setPixmap(QtGui.QPixmap("images/tecladoFAzulB.PNG"))
        self.ui.confTecladoColumnasImagen.setPixmap(QtGui.QPixmap("images/tecladoCAzulB.PNG"))
        self.ui.radioAzul.setChecked(True)

        self.focusBeige()
        self.ui.labelAzul.setStyleSheet(
            "background-color:rgb(120,182,219); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelVerde.setStyleSheet(
            "background-color: rgb(166, 180, 1); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelNaranja.setStyleSheet(
            "background-color: rgb(212, 74, 30); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelAmarillo.setStyleSheet(
            "background-color: rgb(253, 147, 52); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosa.setStyleSheet(
            "background-color: rgb(229, 91, 126); border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")
        self.ui.labelRosaBB.setStyleSheet(
            "background-color: #8f3c8c; border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255);")

        self.ui.confFondoNoneLabel.setStyleSheet(
            "background-color: rgb(236, 225, 209);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255); color: black")
        self.ui.confFondoBLabel.setStyleSheet(
            "background-color: rgb(236, 225, 209);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoCLabel.setStyleSheet(
            "background-color: rgb(236, 225, 209);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")
        self.ui.confFondoDLabel.setStyleSheet(
            "background-color: rgb(236, 225, 209);  border-width: 2px; border-style: solid; border-color: rgb(255, 255, 255)")

        self.ui.calculadora.setStyleSheet(
            "QFrame{background-color:rgb(236,225,209); border: 2px solid gray} QLabel{background-color:rgb(0,0,0); color: rgb(255,255,255)}")

        self.focusStyle = "background-color: rgb(120,182,219); color: black"
        self.borderStyle = " rgb(120,182,219) "

        app.setPalette(self.palette)

        self.ui.confPaletaLabel.setStyleSheet("color: black")
        self.ui.confHablaVolumenLabel.setStyleSheet("color: black")
        self.ui.confHablaLabel.setStyleSheet("color: black")
        self.ui.confHablaVelocidadLabel.setStyleSheet("color: black")
        self.ui.confTecladoLabel.setStyleSheet("color: black")
        self.ui.confFocusLabel.setStyleSheet("color: black")
        self.ui.confFondoLabel.setStyleSheet("color: black")
        self.ui.confTecladoColumnasLabel.setStyleSheet("background-color: rgb(236, 225, 209); color: black")
        self.ui.confTecladoFilasLabel.setStyleSheet("background-color: rgb(236, 225, 209); color: black")
        self.ui.confRecorridoLabel.setStyleSheet("color: black")
        self.ui.confOrdenTLabel.setStyleSheet("color: black")
        self.ui.mLabelDestino.setStyleSheet("color: black")
        self.ui.mLabelAsunto.setStyleSheet("color: black")
        self.ui.confDisenoLabel.setStyleSheet("color: black")
        self.ui.confHablaVozLabel.setStyleSheet("color: black")
        self.ui.confAbecedarioLabel.setStyleSheet("color: black")
        self.ui.confFrecuenciaLabel.setStyleSheet("color: black")
        self.ui.confPredictorLabel.setStyleSheet("color: black")
        self.ui.wLabelTitulo.setStyleSheet("color: black")
        self.ui.calen_labelTitulo.setStyleSheet("color: black")
        self.ui.calen_labelCategoria.setStyleSheet("color: black")
        self.ui.calenEventosFechaLabel.setStyleSheet("background-color: rgb(236, 225, 209); color: black")
        self.ui.informacionEntrenarLabel.setStyleSheet("background-color: rgb(236, 225, 209); color: black")
        self.ui.informacionLimpiarLabel.setStyleSheet("background-color: rgb(236, 225, 209); color: black")

        self.ui.confHablaVolumenWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVelocidadWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaVozWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFocusWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confFondoWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confDisenoWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confRecorridoWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confOrdenTWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(236,225,209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0)  gray gray rgba(255, 255, 255, 0); border-bottom-right-radius: 10px;")

        self.ui.confPaletaWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confTecladoWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confHablaWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.confPredictorWidget.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: rgba(255, 255, 255, 0) gray gray gray; border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;")
        self.ui.wWidgetTitulo.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetAsunto.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.mWidgetDestino.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wtitulo.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Wcategoria.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_Whora.setStyleSheet(
            "background-color: rgb(236, 225, 209); border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")

        paletita = self.ui.reloj0.palette()
        paletita.setColor(QtGui.QPalette.Light, QtCore.Qt.darkGray)
        paletita.setColor(QtGui.QPalette.Dark, QtGui.QColor(0, 0, 0))
        self.ui.reloj0.setPalette(paletita)

        self.ui.radioBeige.setChecked(True)

    def focusDark(self):
        self.dicFocus = dict([('confAzul', (
            self.ui.radioAzul, "rgb(83,255,255)", "AzulD", QtGui.QColor(83, 255, 255), "; color: black")),
                              ('confVerde', (self.ui.radioVerde, "rgb(56,252,72)", "VerdeD", QtGui.QColor(56, 252, 72),
                                             "; color: black")),
                              ('confNaranja', (
                                  self.ui.radioNaranja, "rgb(254,80,0)", "NaranjaD", QtGui.QColor(254, 80, 0),
                                  "; color: black")),
                              ('confAmarillo', (
                                  self.ui.radioAmarillo, "rgb(255,255,0)", "AmarilloD", QtGui.QColor(255, 255, 0),
                                  "; color: black")),
                              ('confRosa', (self.ui.radioRosa, "rgb(255,105,180)", "RosaD", QtGui.QColor(255, 105, 180),
                                            "; color: black")),
                              ('confRosaBB', (
                                  self.ui.radioRosaBB, "rgb(255,114,118)", "RosaBBD", QtGui.QColor(255, 114, 118),
                                  "; color: black"))
                              ])

    def focusGris(self):
        self.dicFocus = dict(
            [('confAzul', (self.ui.radioAzul, "rgb(3,124,135)", "AzulG", QtGui.QColor(3, 124, 135), "; color: black")),
             ('confVerde',
              (self.ui.radioVerde, "rgb(200,223,89)", "VerdeG", QtGui.QColor(200, 223, 89), "; color: black")),
             ('confNaranja',
              (self.ui.radioNaranja, "rgb(251, 193, 26)", "NaranjaG", QtGui.QColor(251, 193, 26), "; color: black")),
             ('confAmarillo',
              (self.ui.radioAmarillo, "rgb(208, 115, 71)", "AmarilloG", QtGui.QColor(208, 115, 71), "; color: black")),
             ('confRosa', (self.ui.radioRosa, "rgb(6, 96, 78)", "RosaG", QtGui.QColor(6, 96, 78), "; color: white")),
             ('confRosaBB',
              (self.ui.radioRosaBB, "rgb(204, 111, 169)", "RosaBBG", QtGui.QColor(204, 111, 169), "; color: black"))
             ])

    def focusCeleste(self):
        self.dicFocus = dict([('confAzul', (
            self.ui.radioAzul, "rgb(180,132,100)", "AzulC", QtGui.QColor(180, 132, 100), "; color: black")),
                              ('confVerde', (
                                  self.ui.radioVerde, "rgb(75,125,139)", "VerdeC", QtGui.QColor(75, 125, 139),
                                  "; color: black")),
                              ('confNaranja', (
                                  self.ui.radioNaranja, "rgb(236,203,167)", "NaranjaC", QtGui.QColor(236, 203, 167),
                                  "; color: black")),
                              ('confAmarillo', (
                                  self.ui.radioAmarillo, "rgb(253,147,52)", "AmarilloC", QtGui.QColor(253, 147, 52),
                                  "; color: black")),
                              ('confRosa', (
                                  self.ui.radioRosa, "rgb(38,38,98)", "RosaC", QtGui.QColor(38, 38, 98),
                                  "; color: white")),
                              ('confRosaBB', (
                                  self.ui.radioRosaBB, "rgb(217,104,110)", "RosaBBC", QtGui.QColor(217, 104, 110),
                                  "; color: black"))
                              ])

    def focusBeige(self):
        self.dicFocus = dict([('confAzul', (
            self.ui.radioAzul, "rgb(120,182,219)", "AzulB", QtGui.QColor(120, 182, 219), "; color: black")),
                              ('confVerde', (
                                  self.ui.radioVerde, "rgb(166, 180, 1)", "VerdeB", QtGui.QColor(166, 180, 1),
                                  "; color: black")),
                              ('confNaranja', (
                                  self.ui.radioNaranja, "rgb(212, 74, 30)", "NaranjaB", QtGui.QColor(212, 74, 30),
                                  "; color: black")),
                              ('confAmarillo', (
                                  self.ui.radioAmarillo, "rgb(253, 147, 52)", "AmarilloB", QtGui.QColor(253, 147, 52),
                                  "; color: black")),
                              ('confRosa', (self.ui.radioRosa, "rgb(229, 91, 126)", "RosaB", QtGui.QColor(229, 91, 126),
                                            "; color: black")),
                              ('confRosaBB',
                               (self.ui.radioRosaBB, "#8f3c8c", "RosaBBB", QtGui.QColor("#8f3c8c"), "; color: white"))
                              ])

    def cambiarFondo(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()
        dic = dict([('confFondoNone', ('', self.ui.radioFondoNone)),
                    ('confFondoB', ('images/pngFondoB.png', self.ui.radioFondoB)),
                    ('confFondoC', ('images/pngFondoC.png', self.ui.radioFondoC)),
                    ('confFondoD', ('images/pngFondoD.png', self.ui.radioFondoD))
                    ])
        self.ui.fondo.setPixmap(QtGui.QPixmap(dic[a][0]))
        dic[a][1].setChecked(True)

    def escribirDestino(self):
        self.ui.mEscribirAsunto.setChecked(False)
        self.ui.mWidgetAsunto.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")

        if self.ui.mEscribirDestino.isChecked():
            self.ui.mEscribirDestino.setChecked(False)
            self.ui.mLabelDestino.setStyleSheet("")
            self.ui.mWidgetDestino.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
            self.text = self.ui.textEdit
        else:
            self.ui.mEscribirDestino.setChecked(True)
            self.ui.mLabelDestino.setStyleSheet("")
            self.ui.mWidgetDestino.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)
            self.text = self.ui.mDestino

        a = self.text.toPlainText()
        if len(a) > 0:

            p = max(map(a.rfind, '?!.;:)]}\n'))  # busco último símbolo de finalización de oración

            if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                self.phrase = a[p + 1:]  # me quedo con la última oración
                frase = self.phrase
                if frase == ' ':
                    frase = ''
                else:
                    frase = frase.lstrip()
            elif p == -1:
                self.phrase = a
                frase = self.phrase
                frase = frase.lstrip()

            else:
                frase = ''
                self.phrase = ''

            if len(frase) > 0:

                if frase[0].upper() in self.arboles.hijos:
                    self.currentNode = self.arboles.hijos[frase[0].upper()]  # me paro en el nodo de la primera letra
                else:  # esto no debería suceder igual
                    self.arboles.add(frase[0].upper())
                    self.currentNode = self.arboles.hijos[frase[0].upper()]

                # ahora tengo que encontrar la última palabra
                frase = self.phrase  # por si self.phrase tiene un espacio al final
                frase = frase.rstrip()
                r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                if r > -1:
                    self.word = frase[r + 1:]
                    self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                else:
                    self.word = frase

            else:  # si la frase está vacía
                self.word = ''
                self.currentNode = self.arboles

            if p != len(a) - 1:
                self.dicCasos[a[-1].upper()]()  # hago lo que diga el último caracter


        else:  # si no hay nada en el edit text
            self.word = ''
            self.phrase = ''
            self.currentNode = self.arboles

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    def escribirAsunto(self):
        self.ui.mEscribirDestino.setChecked(False)
        self.ui.mWidgetDestino.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        if self.ui.mEscribirAsunto.isChecked():
            self.ui.mEscribirAsunto.setChecked(False)
            self.ui.mLabelAsunto.setStyleSheet("")
            self.ui.mWidgetAsunto.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
            self.text = self.ui.textEdit
        else:
            self.ui.mEscribirAsunto.setChecked(True)
            self.ui.mLabelAsunto.setStyleSheet("")
            self.ui.mWidgetAsunto.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)
            self.text = self.ui.mAsunto

        a = self.text.toPlainText()
        if len(a) > 0:

            p = max(map(a.rfind, '?!.;:)]}\n'))  # busco último símbolo de finalización de oración

            if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                self.phrase = a[p + 1:]  # me quedo con la última oración
                frase = self.phrase
                if frase == ' ':
                    frase = ''
                else:
                    frase = frase.lstrip()
            elif p == -1:
                self.phrase = a
                frase = self.phrase
                frase = frase.lstrip()

            else:
                frase = ''
                self.phrase = ''

            if len(frase) > 0:

                if frase[0].upper() in self.arboles.hijos:
                    self.currentNode = self.arboles.hijos[frase[0].upper()]  # me paro en el nodo de la primera letra
                else:  # esto no debería suceder igual
                    self.arboles.add(frase[0].upper())
                    self.currentNode = self.arboles.hijos[frase[0].upper()]

                # ahora tengo que encontrar la última palabra
                frase = self.phrase  # por si self.phrase tiene un espacio al final
                frase = frase.rstrip()
                r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                if r > -1:
                    self.word = frase[r + 1:]
                    self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                else:
                    self.word = frase

            else:  # si la frase está vacía
                self.word = ''
                self.currentNode = self.arboles

            if p != len(a) - 1:
                self.dicCasos[a[-1].upper()]()  # hago lo que diga el último caracter


        else:  # si no hay nada en el edit text
            self.word = ''
            self.phrase = ''
            self.currentNode = self.arboles

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    def enviarMail(self):
        destino = self.ui.mDestino.toPlainText()
        subject = self.ui.mAsunto.toPlainText()
        message = self.ui.textEdit.toPlainText()

        mensaje = 'Subject: {}\n\n{}'.format(subject, message)
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.correo, self.contrasena)  # Configurar correo y contraseña
            # if() #Chekear que el correo destino tenga formato valido
            server.sendmail(self.correo, destino, mensaje)
            server.quit()
            self.ui.textEdit.clear()
            self.ui.mDestino.clear()
            self.ui.mAsunto.clear()
            self.ui.teclado.setFocus()
            self.ui.teclado.setStyleSheet(self.focusStyle)
            self.ui.mTeclaEnviar.setStyleSheet("")
            # agregamos el mail del destino al árbol
            self.arboles.add(destino[0].upper())
            nodo = self.arboles.move(destino[0].upper())
            nodo.add(destino)

        except:
            self.ui.textEdit.clear()
            self.ui.mDestino.clear()
            self.ui.mAsunto.clear()
            self.ui.teclado.setFocus()
            self.ui.teclado.setStyleSheet(self.focusStyle)
            self.ui.mTeclaEnviar.setStyleSheet("")

    def escribirCuenta(self):
        #self.ui.mEscribirAsunto.setChecked(False)
        #self.ui.mWidgetAsunto.setStyleSheet(
        #    "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")

        if self.ui.mEscribirDestino.isChecked():
            self.ui.mEscribirDestino.setChecked(False)
            self.ui.mLabelDestino.setStyleSheet("")
            self.ui.mLabelAsunto.setStyleSheet("")
            self.ui.mWidgetDestino.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
            self.text = self.ui.mAsunto
            self.ui.mWidgetAsunto.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)
            self.ui.mEscribirAsunto.setChecked(True)
            self.ui.mAsunto.clear()
            self.ui.mAsunto.insertPlainText(self.contrasena)

        else:
            self.ui.mEscribirDestino.setChecked(True)
            self.ui.mEscribirAsunto.setChecked(False)
            self.ui.mLabelDestino.setStyleSheet("")
            self.ui.mLabelAsunto.setStyleSheet("")
            self.ui.mWidgetDestino.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)
            self.text = self.ui.mDestino
            self.ui.mWidgetAsunto.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
            self.contrasena= self.ui.mAsunto.toPlainText()
            self.ui.mAsunto.clear()
            contra = ''
            for i in range(len(self.contrasena)):
                contra = contra + '*'
            self.ui.mAsunto.setText(contra)


        a = self.text.toPlainText()
        if len(a) > 0:

            p = max(map(a.rfind, '?!.;:)]}\n'))  # busco último símbolo de finalización de oración

            if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                self.phrase = a[p + 1:]  # me quedo con la última oración
                frase = self.phrase
                if frase == ' ':
                    frase = ''
                else:
                    frase = frase.lstrip()
            elif p == -1:
                self.phrase = a
                frase = self.phrase
                frase = frase.lstrip()

            else:
                frase = ''
                self.phrase = ''

            if len(frase) > 0:

                if frase[0].upper() in self.arboles.hijos:
                    self.currentNode = self.arboles.hijos[frase[0].upper()]  # me paro en el nodo de la primera letra
                else:  # esto no debería suceder igual
                    self.arboles.add(frase[0].upper())
                    self.currentNode = self.arboles.hijos[frase[0].upper()]

                # ahora tengo que encontrar la última palabra
                frase = self.phrase  # por si self.phrase tiene un espacio al final
                frase = frase.rstrip()
                r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                if r > -1:
                    self.word = frase[r + 1:]
                    self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                else:
                    self.word = frase

            else:  # si la frase está vacía
                self.word = ''
                self.currentNode = self.arboles

            if p != len(a) - 1:
                self.dicCasos[a[-1].upper()]()  # hago lo que diga el último caracter


        else:  # si no hay nada en el edit text
            self.word = ''
            self.phrase = ''
            self.currentNode = self.arboles

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    def tabular(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()

        self.dic[a][0].setStyleSheet(self.focusStyle)
        self.dic[a][0].setFocus()
        focus_widget.setStyleSheet("")

    def tabularConf(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()

        self.dic[a][0].setStyleSheet(self.focusStyle)
        self.dic[a][0].setFocus()
        focus_widget.setStyleSheet("")
        if self.dic[a][2] != '':
            self.dic[a][2]()

    def accion(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()

        self.dic[a][1]()

    def diccionarioInicio(self):
        dic = dict(
            [('teclado', (self.ui.VPalabras, self.ventanaHijo)), ('VPalabras', (self.ui.VFrases, self.ventanaHijo)),
             ('VFrases', (self.ui.VBorrarEnter, self.ventanaHijo)),
             ('VBorrarEnter', (self.ui.teclado, self.ventanaHijo)),
             ('palabrasF1', (self.ui.palabrasF2, self.ventanaHijo)),
             ('palabrasF2', (self.ui.VPalabras, self.ventanaHijo)),
             ('palabraSug1', (self.ui.palabraSug2, self.autocompletar)),
             ('palabraSug2', (self.ui.palabraSug3, self.autocompletar)),
             ('palabraSug3', (self.ui.palabrasF1, self.autocompletar)),
             ('palabraSug4', (self.ui.palabraSug5, self.autocompletar)),
             ('palabraSug5', (self.ui.palabraSug6, self.autocompletar)),
             ('palabraSug6', (self.ui.palabrasF2, self.autocompletar)),
             ('fraseB1', (self.ui.fraseB2, self.autocompletar)), ('fraseB2', (self.ui.fraseB3, self.autocompletar)),
             ('fraseB3', (self.ui.fraseB4, self.autocompletar)),
             ('fraseB4', (self.ui.fraseB5, self.autocompletar)),
             ('fraseB5', (self.ui.VFrases, self.autocompletar)),
             ('teclaBorrar', (self.ui.teclaBloqMayusInicio, self.borrarLetra)),
             ('teclaBloqMayusInicio', (self.ui.teclaEnter, self.bloqMayus)),
             ('teclaEnter', (self.ui.teclaBorrarTodo, self.reproducir)),
             ('teclaBorrarTodo', (self.ui.teclaMenu, self.borrarTodo)),
             ('teclaMenu', (self.ui.VBorrarEnter, self.entrarMenu)),
             ('appCalcu', (self.ui.appExit, self.confCalcu)), ('appCalen', (self.ui.appClima, self.confCalen)),
             ('appWord', (self.ui.appConfig, self.confWord)), ('appConfig', (self.ui.appCalcu, self.confConfiguracion)),
             ('appMail', (self.ui.appWord, self.confMail)), ('appClima', (self.ui.appMail, self.confClima)),
             ('appExit', (self.ui.appCalen, self.salirMenu))
             ])
        dic.update(self.dicTeclado)
        return dic

    def diccionarioCalcu(self):
        dic = dict(
            [('teclaSalir', (self.ui.calcuF1, self.confInicio)), ('calcuF1', (self.ui.calcuF2, self.ventanaHijo)),
             ('calcuF2', (self.ui.calcuF3, self.ventanaHijo)), ('calcuF3', (self.ui.calcuF4, self.ventanaHijo)),
             ('calcuF4', (self.ui.calcuC, self.ventanaHijo)), ('calcuC', (self.ui.teclaSalir, self.ventanaHijo)),
             ('tecla7', (self.ui.tecla8, self.calculator)), ('tecla8', (self.ui.tecla9, self.calculator)),
             ('tecla9', (self.ui.calcuF1, self.calculator)), ('tecla4', (self.ui.tecla5, self.calculator)),
             ('tecla5', (self.ui.tecla6, self.calculator)), ('tecla6', (self.ui.calcuF2, self.calculator)),
             ('tecla1', (self.ui.tecla2, self.calculator)), ('tecla2', (self.ui.tecla3, self.calculator)),
             ('tecla3', (self.ui.calcuF3, self.calculator)), ('tecla0', (self.ui.teclaComaCalcu, self.calculator)),
             ('teclaComaCalcu', (self.ui.teclaIgual, self.calculator)),
             ('teclaIgual', (self.ui.calcuF4, self.calculator)),
             ('teclaAC', (self.ui.teclaMutiplicar, self.calculator)),
             ('teclaMutiplicar', (self.ui.teclaDividir, self.calculator)),
             ('teclaDividir', (self.ui.teclaMenos, self.calculator)),
             ('teclaMenos', (self.ui.teclaMas, self.calculator)),
             ('teclaMas', (self.ui.calcuC, self.calculator))
             ])
        return dic

    def diccionarioWord(self):
        dic = dict(
            [('teclado', (self.ui.VPalabras, self.ventanaHijo)), ('VPalabras', (self.ui.VFrases, self.ventanaHijo)),
             ('VFrases', (self.ui.wBorrarEnter, self.ventanaHijo)),
             ('wBorrarEnter', (self.ui.wordSalir, self.ventanaHijo)),
             ('wordSalir', (self.ui.wLabelTitulo, self.confInicio)),
             ('wLabelTitulo', (self.ui.teclado, self.escribirTitulo)),
             ('palabrasF1', (self.ui.palabrasF2, self.ventanaHijo)),
             ('palabrasF2', (self.ui.VPalabras, self.ventanaHijo)),
             ('palabraSug1', (self.ui.palabraSug2, self.autocompletar)),
             ('palabraSug2', (self.ui.palabraSug3, self.autocompletar)),
             ('palabraSug3', (self.ui.palabrasF1, self.autocompletar)),
             ('palabraSug4', (self.ui.palabraSug5, self.autocompletar)),
             ('palabraSug5', (self.ui.palabraSug6, self.autocompletar)),
             ('palabraSug6', (self.ui.palabrasF2, self.autocompletar)),
             ('fraseB1', (self.ui.fraseB2, self.autocompletar)), ('fraseB2', (self.ui.fraseB3, self.autocompletar)),
             ('fraseB3', (self.ui.fraseB4, self.autocompletar)),
             ('fraseB4', (self.ui.fraseB5, self.autocompletar)),
             ('fraseB5', (self.ui.VFrases, self.autocompletar)),
             ('wTeclaBorrar', (self.ui.wTeclaEnter, self.borrarLetra)),
             ('wTeclaEnter', (self.ui.wTeclaBloqMayus, self.saltoLinea)),
             ('wTeclaBloqMayus', (self.ui.wTeclaBorrarTodo, self.bloqMayus)),
             ('wTeclaBorrarTodo', (self.ui.wTeclaPanel, self.borrarTodoWord)),
             ('wTeclaPanel', (self.ui.wTeclaMenu, self.ventanaHijo)),
             ('wTeclaMenu', (self.ui.wBorrarEnter, self.ventanaHijo)),
             ('wWidgetNegrita', (self.ui.wWidgetCursiva, self.textNegrita)),
             ('wWidgetCursiva', (self.ui.wWidgetSubrayar, self.textCursiva)),
             ('wWidgetSubrayar', (self.ui.wLetra, self.textSubrayar)),
             ('wLetra', (self.ui.teclado, self.ventanaHijo)),
             ('wGuardar', (self.ui.wArchivoAbajo, self.wordGuardar)),
             ('wCargar', (self.ui.wGuardarCargar, self.wordCargar)),
             ('wArchivoAbajo', (self.ui.wArchivoArriba, self.moverArchivoAbajo)),
             ('wArchivoArriba', (self.ui.wCargar, self.moverArchivoArriba)),
             ('wGuardarCargar', (self.ui.teclado, self.ventanaHijo))
             ])
        dic.update(self.dicTeclado)
        return dic

    def diccionarioCalen(self):
        dic = dict([('calenSalir', (self.ui.teclado, self.confInicio)),
                    ('calenEventosBox', (self.ui.calenSalir, self.ventanaHijo)),
                    ('calenFlechasFrame', (self.ui.calenEventosBox, self.ventanaHijo)),
                    ('teclado', (self.ui.calenBorrarEnter, self.ventanaHijo)),
                    ('calenBorrarEnter', (self.ui.calenFlechasFrame, self.ventanaHijo)),
                    ('calen_dia_adelante', (self.ui.calen_sem_abajo, self.calenMover)),
                    ('calen_sem_abajo', (self.ui.calen_dia_atras, self.calenMover)),
                    ('calen_dia_atras', (self.ui.calen_sem_arriba, self.calenMover)),
                    ('calen_sem_arriba', (self.ui.calenFlechasFrame, self.calenMover)),
                    ('calen_labelTitulo', (self.ui.calen_labelCategoria, self.escribirTituloCalen)),
                    ('calen_labelCategoria', (self.ui.calen_labelHora, self.escribirCategoriaCalen)),
                    ('calen_labelHora', (self.ui.calenAllDayLabel, self.escribirHoraCalen)),
                    ('calenAllDayLabel', (self.ui.calen_add_button, self.allDayCheck)),
                    ('calen_add_button', (self.ui.calenEventosBox, self.save_event)),
                    ('calenBorrarLetra', (self.ui.calenEnter, self.borrarLetra)),
                    ('calenEnter', (self.ui.calenBloqMayus, self.saltoLinea)),
                    ('calenBloqMayus', (self.ui.calenBorrarEnter, self.bloqMayus)),
                    ])

        dic.update(self.dicTeclado)
        return dic

    def diccionarioClima(self):
        dic = dict([('climaSalir', (self.ui.pushButton, self.confInicio)),
                    ('pushButton', (self.ui.climaSalir, self.update_weather))
                    ])
        return dic

    def diccionarioConfiguracion(self):
        dic = dict([('confSalir', (self.ui.confHablaLabel, self.confInicio, self.moverHabla)),
                    ('confHablaLabel', (self.ui.confTecladoLabel, self.ventanaHijo, '')),
                    ('confTecladoLabel', (self.ui.confPaletaLabel, self.ventanaHijo, self.moverPaleta)),
                    ('confPaletaLabel', (self.ui.confPredictorLabel, self.ventanaHijo, self.moverPredictor)),
                    ('confPredictorLabel', (self.ui.confControlesLabel, self.ventanaHijo, '')),
                    ('confControlesLabel', (self.ui.confSalir, self.ventanaHijo, '')),
                    ('confRecorridoLabel', (self.ui.confOrdenTLabel, self.ventanaHijo, '')),
                    ('confOrdenTLabel', (self.ui.confTecladoLabel, self.ventanaHijo, '')),
                    ('confAbecedarioLabel', (self.ui.confFrecuenciaLabel, self.cambiarTeclado, '')),
                    ('confFrecuenciaLabel', (self.ui.confOrdenTLabel, self.cambiarTeclado, '')),
                    ('confTecladoFilas', (self.ui.confTecladoColumnas, self.setearTeclado, '')),
                    ('confTecladoColumnas', (self.ui.confRecorridoLabel, self.setearTeclado, '')),
                    ('confHablaVolumenLabel', (self.ui.confHablaVelocidadLabel, self.ventanaHijo, '')),
                    ('confHablaVelocidadLabel', (self.ui.confHablaVozLabel, self.ventanaHijo, '')),
                    ('confHablaVozLabel', (self.ui.confHablaLabel, self.ventanaHijo, '')),
                    ('hablaVozArriba', (self.ui.hablaVozAbajo, self.cambiarVozArriba, '')),
                    ('hablaVozAbajo', (self.ui.confHablaVozLabel, self.cambiarVozAbajo, '')),
                    ('hablaVolumenMenos', (self.ui.hablaVolumenMas, self.volumenMenos, '')),
                    ('hablaVolumenMas', (self.ui.confHablaVolumenLabel, self.volumenMas, '')),
                    ('hablaVelocidadMenos', (self.ui.hablaVelocidadMas, self.velocidadMenos, '')),
                    ('hablaVelocidadMas', (self.ui.confHablaVelocidadLabel, self.velocidadMas, '')),
                    ('confFocusLabel', (self.ui.confFondoLabel, self.ventanaHijo, '')),
                    ('confAzul', (self.ui.confVerde, self.focusColor, '')),
                    ('confVerde', (self.ui.confNaranja, self.focusColor, '')),
                    ('confNaranja', (self.ui.confAmarillo, self.focusColor, '')),
                    ('confAmarillo', (self.ui.confRosa, self.focusColor, '')),
                    ('confRosa', (self.ui.confRosaBB, self.focusColor, '')),
                    ('confRosaBB', (self.ui.confFocusLabel, self.focusColor, '')),
                    ('confFondoLabel', (self.ui.confDisenoLabel, self.ventanaHijo, '')),
                    ('confDark', (self.ui.confGris, self.fondoColor, '')),
                    ('confGris', (self.ui.confCeleste, self.fondoColor, '')),
                    ('confCeleste', (self.ui.confBeige, self.fondoColor, '')),
                    ('confBeige', (self.ui.confFondoLabel, self.fondoColor, '')),
                    ('confDisenoLabel', (self.ui.confPaletaLabel, self.ventanaHijo, '')),
                    ('confFondoNone', (self.ui.confFondoB, self.cambiarFondo, '')),
                    ('confFondoB', (self.ui.confFondoC, self.cambiarFondo, '')),
                    ('confFondoC', (self.ui.confFondoD, self.cambiarFondo, '')),
                    ('confFondoD', (self.ui.confDisenoLabel, self.cambiarFondo, '')),
                    ('confLimpiarButton', (self.ui.confEntrenarButton, self.Limpiar, '')),
                    ('confEntrenarButton', (self.ui.confPredictorLabel, self.Entrenar, '')),
                    ('confModoTeclasLabel', (self.ui.confElegirTeclasLabel, self.ventanaHijo, '')),
                    ('confElegirTeclasLabel', (self.ui.confControlesLabel, self.ventanaHijo, '')),
                    ('confTeclaTabularLabel', (self.ui.confTeclaAccionLabel, self.elegirTeclaTabular, '')),
                    ('confTeclaAccionLabel', (self.ui.confElegirTeclasLabel, self.elegirTeclaAccion, '')),
                    ('confDosTeclasLabel', (self.ui.confUnaTeclaLabel, self.modoADosTeclas, '')),
                    ('confUnaTeclaLabel', (self.ui.confModoTeclasLabel, self.modoAUnaTecla, '')),
                    ('confInputLabel', (self.ui.confModoTeclasLabel, self.ventanaHijo, '')),
                    ('confInputTecladoLabel', (self.ui.confInputMouseLabel, self.pasarAModoTeclado,'')),
                    ('confInputMouseLabel', (self.ui.confInputLabel, self.pasarAModoMouse, ''))
                    ])

        return dic

    def diccionarioMail(self):
        dic = dict(
            [('teclado', (self.ui.VPalabras, self.ventanaHijo)), ('VPalabras', (self.ui.VFrases, self.ventanaHijo)),
             ('VFrases', (self.ui.mBorrarEnter, self.ventanaHijo)),
             ('mBorrarEnter', (self.ui.mailSalir, self.ventanaHijo)),
             ('mailSalir', (self.ui.mLabelDestino, self.confInicio)),
             ('mLabelDestino', (self.ui.mLabelAsunto, self.escribirDestino)),
             ('mLabelAsunto', (self.ui.teclado, self.escribirAsunto)),
             ('palabrasF1', (self.ui.palabrasF2, self.ventanaHijo)),
             ('palabrasF2', (self.ui.VPalabras, self.ventanaHijo)),
             ('palabraSug1', (self.ui.palabraSug2, self.autocompletar)),
             ('palabraSug2', (self.ui.palabraSug3, self.autocompletar)),
             ('palabraSug3', (self.ui.palabrasF1, self.autocompletar)),
             ('palabraSug4', (self.ui.palabraSug5, self.autocompletar)),
             ('palabraSug5', (self.ui.palabraSug6, self.autocompletar)),
             ('palabraSug6', (self.ui.palabrasF2, self.autocompletar)),
             ('fraseB1', (self.ui.fraseB2, self.autocompletar)), ('fraseB2', (self.ui.fraseB3, self.autocompletar)),
             ('fraseB3', (self.ui.fraseB4, self.autocompletar)),
             ('fraseB4', (self.ui.fraseB5, self.autocompletar)),
             ('fraseB5', (self.ui.VFrases, self.autocompletar)),
             ('mTeclaBorrar', (self.ui.mTeclaEnter, self.borrarLetra)),
             ('mTeclaEnter', (self.ui.mBloqMayus, self.saltoLinea)),
             ('mBloqMayus', (self.ui.mTeclaEnviar, self.bloqMayus)),
             ('mTeclaEnviar', (self.ui.mTeclaEnviar_2, self.enviarMail)),
             ('mTeclaEnviar_2', (self.ui.mBorrarEnter, self.confMailCuenta))
             ])
        dic.update(self.dicTeclado)
        return dic

    def diccionarioMailCuenta(self):
        dic = dict(
            [('teclado', (self.ui.mBorrarEnter, self.ventanaHijo)),
             # ('VPalabras', (self.ui.VFrases, self.ventanaHijo)),
             # ('VFrases', (self.ui.mBorrarEnter, self.ventanaHijo)),
             ('mBorrarEnter', (self.ui.mLabelDestino, self.ventanaHijo)),
             # ('mailSalir', (self.ui.mLabelDestino, self.confInicio)),
             ('mLabelDestino', (self.ui.mLabelAsunto, self.escribirCuenta)),
             ('mLabelAsunto', (self.ui.teclado, self.escribirCuenta)),
             ('mBloqMayus', (self.ui.mBorrarEnter, self.bloqMayus)),
             ('mTeclaBorrar', (self.ui.mTeclaEnter, self.borrarLetraMailCuenta)),
             ('mTeclaEnter', (self.ui.mBloqMayus, self.confirmarCorreo)),
             # ('mTeclaEnviar', (self.ui.mBorrarEnter, self.enviarMail))
             ])
        dic.update(self.dicTeclado)
        return dic

    def confirmarCorreo(self):
        self.correo = self.ui.mDestino.toPlainText()
        # self.contrasena = self.ui.mAsunto.toPlainText()
        self.ui.mDestino.setText('')
        self.ui.mAsunto.setText('')
        self.confMail()

    def borrarLetraMailCuenta(self):
        if len(self.text.toPlainText()) > 0:
            b = self.text.toPlainText()[-1]
            a = self.text.toPlainText()[:-1]
            self.text.clear()
            self.text.insertPlainText(a)

    def bloqMayus(self):
        if self.ui.teclaT11.text() == 'A' or self.ui.teclaT11.text() == 'Á' or self.ui.teclaT11.text() == 'Ü':
            self.minusculas()
        elif self.ui.teclaT11.text() == 'a' or self.ui.teclaT11.text() == 'á' or self.ui.teclaT11.text() == 'ü':
            self.mayusculas()
        focus_widget = self.ui.centralwidget.focusWidget()
        focus_widget.setStyleSheet("")
        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    def minusculas(self):
        self.ui.teclaT11.setText(self.ui.teclaT11.text().lower())
        self.ui.teclaT12.setText(self.ui.teclaT12.text().lower())
        self.ui.teclaT13.setText(self.ui.teclaT13.text().lower())
        self.ui.teclaT14.setText(self.ui.teclaT14.text().lower())
        self.ui.teclaT15.setText(self.ui.teclaT15.text().lower())
        self.ui.teclaT16.setText(self.ui.teclaT16.text().lower())
        self.ui.teclaT17.setText(self.ui.teclaT17.text().lower())
        self.ui.teclaT21.setText(self.ui.teclaT21.text().lower())
        self.ui.teclaT22.setText(self.ui.teclaT22.text().lower())
        self.ui.teclaT23.setText(self.ui.teclaT23.text().lower())
        self.ui.teclaT24.setText(self.ui.teclaT24.text().lower())
        self.ui.teclaT25.setText(self.ui.teclaT25.text().lower())
        self.ui.teclaT26.setText(self.ui.teclaT26.text().lower())
        self.ui.teclaT27.setText(self.ui.teclaT27.text().lower())
        self.ui.teclaT31.setText(self.ui.teclaT31.text().lower())
        self.ui.teclaT32.setText(self.ui.teclaT32.text().lower())
        self.ui.teclaT33.setText(self.ui.teclaT33.text().lower())
        self.ui.teclaT34.setText(self.ui.teclaT34.text().lower())
        self.ui.teclaT35.setText(self.ui.teclaT35.text().lower())
        self.ui.teclaT36.setText(self.ui.teclaT36.text().lower())
        self.ui.teclaT37.setText(self.ui.teclaT37.text().lower())
        if self.ui.teclaT42.text() != 'Á?1':
            self.ui.teclaT42.setText(self.ui.teclaT42.text().lower())
        self.ui.teclaT43.setText(self.ui.teclaT43.text().lower())
        self.ui.teclaT44.setText(self.ui.teclaT44.text().lower())
        self.ui.teclaT45.setText(self.ui.teclaT45.text().lower())
        self.ui.teclaT46.setText(self.ui.teclaT46.text().lower())
        self.ui.teclaT47.setText(self.ui.teclaT47.text().lower())

    def mayusculas(self):
        self.ui.teclaT11.setText(self.ui.teclaT11.text().upper())
        self.ui.teclaT12.setText(self.ui.teclaT12.text().upper())
        self.ui.teclaT13.setText(self.ui.teclaT13.text().upper())
        self.ui.teclaT14.setText(self.ui.teclaT14.text().upper())
        self.ui.teclaT15.setText(self.ui.teclaT15.text().upper())
        self.ui.teclaT16.setText(self.ui.teclaT16.text().upper())
        self.ui.teclaT17.setText(self.ui.teclaT17.text().upper())
        self.ui.teclaT21.setText(self.ui.teclaT21.text().upper())
        self.ui.teclaT22.setText(self.ui.teclaT22.text().upper())
        self.ui.teclaT23.setText(self.ui.teclaT23.text().upper())
        self.ui.teclaT24.setText(self.ui.teclaT24.text().upper())
        self.ui.teclaT25.setText(self.ui.teclaT25.text().upper())
        self.ui.teclaT26.setText(self.ui.teclaT26.text().upper())
        self.ui.teclaT27.setText(self.ui.teclaT27.text().upper())
        self.ui.teclaT31.setText(self.ui.teclaT31.text().upper())
        self.ui.teclaT32.setText(self.ui.teclaT32.text().upper())
        self.ui.teclaT33.setText(self.ui.teclaT33.text().upper())
        self.ui.teclaT34.setText(self.ui.teclaT34.text().upper())
        self.ui.teclaT35.setText(self.ui.teclaT35.text().upper())
        self.ui.teclaT36.setText(self.ui.teclaT36.text().upper())
        self.ui.teclaT37.setText(self.ui.teclaT37.text().upper())
        self.ui.teclaT42.setText(self.ui.teclaT42.text().upper())
        self.ui.teclaT43.setText(self.ui.teclaT43.text().upper())
        self.ui.teclaT44.setText(self.ui.teclaT44.text().upper())
        self.ui.teclaT45.setText(self.ui.teclaT45.text().upper())
        self.ui.teclaT46.setText(self.ui.teclaT46.text().upper())
        self.ui.teclaT47.setText(self.ui.teclaT47.text().upper())

    # Funciones predicción
    def predictWord(self):
        if self.currentNode == self.arboles and self.word != '':
            if self.word.strip().upper() not in self.arboles.hijos:
                self.arboles.add(self.word.strip().upper())
            self.currentNode = self.arboles.hijos[self.word.strip().upper()]  # arranco en el nodo de dicha letra
        pal = self.currentNode.startingWith(
            self.word.strip())  # devuelve una lista ordenada por frec de los hijos del nodo
        if len(pal) > 6:
            pal = pal[0:6]  # me quedo con las seis de mayor frecuencia
        elif len(pal) < 6 and len(self.word) > 0:  # primero miro todas las palabras que arranquen así
            nodo = self.arboles.move(self.word[0].upper())
            pal2 = nodo.startingWith(self.word.strip())

            agregar = [el for el in pal2 if el not in pal]
            if len(agregar) > 0:
                for i in range(min(6 - len(pal), len(agregar) - 1)):
                    pal.append(agregar[i])

        if len(pal) < 6:  # y si no, sugiero las palabras con mayor frecuencia, sin importar la letra
            extra = [el for el in self.freqWords if el not in pal]
            for i in range(6 - len(pal)):
                pal.append(extra[i])

        return pal

    def predictSentence(self):
        if self.word == ' ':
            self.word = ''
        if self.currentNode == self.arboles and self.word != '':
            if self.word.upper() not in self.arboles.hijos:  # los caracteres especiales, por ejemplo
                self.arboles.add(self.word.upper())
            self.currentNode = self.arboles.hijos[self.word.upper()]
        frases = []
        self.currentNode.treeTraversal('', frases, 0)  # devuelve una lista con 5 frases posibles

        if len(frases) < 5:
            words = self.phrase.split()
            if len(words) > 1:
                if self.word == ' ' or self.word == '':
                    palabra = words[-1].strip()  # la última palabra escrita
                else:
                    palabra = words[-2].strip()  # la 'anteúltima'
                if palabra[0].upper() not in self.arboles.hijos.keys():
                    self.arboles.add(palabra[0].upper())
                nodo = self.arboles.hijos[palabra[0].upper()]
                if len(palabra) > 1:
                    nodo = nodo.move(palabra)
                frases2 = []
                nodo.treeTraversal('', frases2, 0)

                agregar = [el for el in frases2 if el not in frases]
                if len(agregar) > 0:
                    for i in range(min(5 - len(frases), len(agregar) - 1)):
                        frases.append(agregar[i])

        if len(frases) < 5:
            extra = [el for el in self.freqPhrases if el not in frases]
            for i in range(min(5 - len(frases), len(extra) - 1)):
                frases.append(extra[i])
        return frases

    def nextWord(self):
        if self.currentNode != self.arboles:
            if len(self.word.strip()) > 0:
                self.currentNode.add(self.word.strip())
                self.currentNode = self.currentNode.move(self.word.strip())
                if self.currentNode.padre != self.arboles:
                    # agrego la palabra al árbol sin el contexto de la frase
                    self.arboles.add(self.word[0].upper())
                    self.arboles.hijos[self.word[0].upper()].add(self.word)
            self.word = ''

            self.newChar()
        else:
            self.word = ''

    def newSentence(self):
        if len(self.word.strip()) > 0 and '@' not in self.word:
            self.currentNode.add(self.word.strip())
            if self.currentNode != self.arboles and self.currentNode.padre != self.arboles:
                # agrego la palabra al árbol sin el contexto de la frase
                self.arboles.add(self.word[0].upper())
                self.arboles.hijos[self.word[0].upper()].add(self.word)

        if len(self.phrase.lstrip()) > 0 and '@' not in self.word:
            palabras = self.phrase.split()
            for k in range(1, len(palabras)):
                self.arboles.add(palabras[k][0].upper())
                nodo = self.arboles.hijos[palabras[k][0].upper()]
                for j in range(k, len(palabras)):
                    nodo.add(palabras[j])
                    nodo = nodo.move(palabras[j])

        if '@' not in self.word:
            self.currentNode = self.arboles
            self.word = ''
            self.phrase = ''
        else:
            self.newChar()

    def newChar(self):
        palabritas = self.predictWord()
        frases = self.predictSentence()
        dic1 = dict([
            (0, self.ui.palabraSug1), (1, self.ui.palabraSug2),
            (2, self.ui.palabraSug3), (3, self.ui.palabraSug4),
            (4, self.ui.palabraSug5), (5, self.ui.palabraSug6)
        ])
        dic2 = dict([
            (0, self.ui.fraseB1), (1, self.ui.fraseB2),
            (2, self.ui.fraseB3), (3, self.ui.fraseB4),
            (4, self.ui.fraseB5)])

        for i in range(len(palabritas)):
            dic1[i].setText(palabritas[i])
        for i in range(len(frases)):
            dic2[i].setText(frases[i])

    def autocompletar(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        # Reemplazo la palabra que estaba escribiendo por la sugerida
        if self.word != '':
            b = len(self.word)
            a = self.text.toPlainText()[:-b]
            self.phrase = self.phrase[:-b]

            if self.word == focus_widget.text()[:b]:  # si la palabra empieza igual
                # agrego solo las letras que faltan para completarla
                if '@' in focus_widget.text():
                    self.phrase = self.phrase + focus_widget.text()
                    self.text.insertPlainText(focus_widget.text()[b:])
                else:
                    self.phrase = self.phrase + focus_widget.text() + ' '
                    self.text.insertPlainText(focus_widget.text()[b:] + ' ')

            else:  # si empieza distinto. Borro lo que estaba y escribo lo nuevo
                cursor = self.text.textCursor()
                cursor.movePosition(QTextCursor.End)
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, b)
                cursor.removeSelectedText()
                # cuando borro todo tengo que volver a setear el fondo gris
                if len(self.text.toPlainText()) == 0:
                    self.text.setTextBackgroundColor(QtCore.Qt.darkGray)
                if '@' in focus_widget.text():
                    self.phrase = self.phrase + focus_widget.text()
                    self.text.insertPlainText(focus_widget.text())
                else:
                    self.phrase = self.phrase + focus_widget.text() + ' '
                    self.text.insertPlainText(focus_widget.text() + ' ')

        else:
            if '@' in focus_widget.text():
                self.phrase = self.phrase + focus_widget.text()
                self.text.insertPlainText(focus_widget.text())
            else:
                self.phrase = self.phrase + focus_widget.text() + ' '
                self.text.insertPlainText(focus_widget.text() + ' ')
        if self.currentNode.padre == self.arboles:
            self.currentNode = self.arboles

        if self.currentNode == self.arboles:
            self.currentNode.add(focus_widget.text()[0].upper())
            self.currentNode = self.currentNode.move(focus_widget.text()[0].upper())
        self.currentNode = self.currentNode.jump(focus_widget.text())

        oracion = focus_widget.text()
        palabritas = oracion.split()
        for i in range(1, len(palabritas)):
            palabra = palabritas[i]
            self.arboles.add(palabra[0].upper())
            self.arboles.hijos[palabra[0].upper()].add(palabra)

        self.word = ''
        self.dicCasos[focus_widget.text()[-1].upper()]()
        focus_widget.setStyleSheet("")
        parent = focus_widget.parent()
        parent.setStyleSheet(self.focusStyle)
        parent.setFocus()

    # Funciones teclado
    def tecladoFilas(self):
        self.ui.tecladoC1.setVisible(False)

        self.ui.tecladoC2.setVisible(False)
        self.ui.tecladoC3.setVisible(False)
        self.ui.tecladoC4.setVisible(False)

        self.ui.tecladoC5.setVisible(False)
        self.ui.tecladoC6.setVisible(False)
        self.ui.tecladoC7.setVisible(False)

        self.ui.tecladoF1.setVisible(True)
        self.ui.tecladoF2.setVisible(True)
        self.ui.tecladoF3.setVisible(True)
        self.ui.tecladoF4.setVisible(True)

        # Cambio Padre
        self.ui.teclaT11.setParent(self.ui.tecladoF1)
        self.ui.teclaT12.setParent(self.ui.tecladoF1)
        self.ui.teclaT13.setParent(self.ui.tecladoF1)
        self.ui.teclaT14.setParent(self.ui.tecladoF1)
        self.ui.teclaT15.setParent(self.ui.tecladoF1)
        self.ui.teclaT16.setParent(self.ui.tecladoF1)
        self.ui.teclaT17.setParent(self.ui.tecladoF1)

        self.ui.teclaT21.setParent(self.ui.tecladoF2)
        self.ui.teclaT22.setParent(self.ui.tecladoF2)
        self.ui.teclaT23.setParent(self.ui.tecladoF2)
        self.ui.teclaT24.setParent(self.ui.tecladoF2)
        self.ui.teclaT25.setParent(self.ui.tecladoF2)
        self.ui.teclaT26.setParent(self.ui.tecladoF2)
        self.ui.teclaT27.setParent(self.ui.tecladoF2)

        self.ui.teclaT31.setParent(self.ui.tecladoF3)
        self.ui.teclaT32.setParent(self.ui.tecladoF3)
        self.ui.teclaT33.setParent(self.ui.tecladoF3)
        self.ui.teclaT34.setParent(self.ui.tecladoF3)
        self.ui.teclaT35.setParent(self.ui.tecladoF3)
        self.ui.teclaT36.setParent(self.ui.tecladoF3)
        self.ui.teclaT37.setParent(self.ui.tecladoF3)

        self.ui.teclaT41.setParent(self.ui.tecladoF4)
        self.ui.teclaT42.setParent(self.ui.tecladoF4)
        self.ui.teclaT43.setParent(self.ui.tecladoF4)
        self.ui.teclaT44.setParent(self.ui.tecladoF4)
        self.ui.teclaT45.setParent(self.ui.tecladoF4)
        self.ui.teclaT46.setParent(self.ui.tecladoF4)
        self.ui.teclaT47.setParent(self.ui.tecladoF4)

        # Cambio ubicación
        self.ui.teclaT11.setGeometry(QtCore.QRect(10, 10, 31, 31))
        self.ui.teclaT12.setGeometry(QtCore.QRect(50, 10, 31, 31))
        self.ui.teclaT13.setGeometry(QtCore.QRect(90, 10, 31, 31))
        self.ui.teclaT14.setGeometry(QtCore.QRect(130, 10, 31, 31))
        self.ui.teclaT15.setGeometry(QtCore.QRect(170, 10, 31, 31))
        self.ui.teclaT16.setGeometry(QtCore.QRect(210, 10, 31, 31))
        self.ui.teclaT17.setGeometry(QtCore.QRect(250, 10, 31, 31))

        self.ui.teclaT21.setGeometry(QtCore.QRect(10, 10, 31, 31))
        self.ui.teclaT22.setGeometry(QtCore.QRect(50, 10, 31, 31))
        self.ui.teclaT23.setGeometry(QtCore.QRect(90, 10, 31, 31))
        self.ui.teclaT24.setGeometry(QtCore.QRect(130, 10, 31, 31))
        self.ui.teclaT25.setGeometry(QtCore.QRect(170, 10, 31, 31))
        self.ui.teclaT26.setGeometry(QtCore.QRect(210, 10, 31, 31))
        self.ui.teclaT27.setGeometry(QtCore.QRect(250, 10, 31, 31))

        self.ui.teclaT31.setGeometry(QtCore.QRect(10, 10, 31, 31))
        self.ui.teclaT32.setGeometry(QtCore.QRect(50, 10, 31, 31))
        self.ui.teclaT33.setGeometry(QtCore.QRect(90, 10, 31, 31))
        self.ui.teclaT34.setGeometry(QtCore.QRect(130, 10, 31, 31))
        self.ui.teclaT35.setGeometry(QtCore.QRect(170, 10, 31, 31))
        self.ui.teclaT36.setGeometry(QtCore.QRect(210, 10, 31, 31))
        self.ui.teclaT37.setGeometry(QtCore.QRect(250, 10, 31, 31))

        self.ui.teclaT41.setGeometry(QtCore.QRect(10, 10, 31, 31))
        self.ui.teclaT42.setGeometry(QtCore.QRect(50, 10, 31, 31))
        self.ui.teclaT43.setGeometry(QtCore.QRect(90, 10, 31, 31))
        self.ui.teclaT44.setGeometry(QtCore.QRect(130, 10, 31, 31))
        self.ui.teclaT45.setGeometry(QtCore.QRect(170, 10, 31, 31))
        self.ui.teclaT46.setGeometry(QtCore.QRect(210, 10, 31, 31))
        self.ui.teclaT47.setGeometry(QtCore.QRect(250, 10, 31, 31))

        self.dicTeclado = dict([
            ('tecladoF1', (self.ui.tecladoF2, self.ventanaHijo)), ('tecladoF2', (self.ui.tecladoF3, self.ventanaHijo)),
            ('tecladoF3', (self.ui.tecladoF4, self.ventanaHijo)),
            ('tecladoF4', (self.ui.teclaEspacio, self.ventanaHijo)),
            ('teclaT11', (self.ui.teclaT12, self.escribir)),
            ('teclaT12', (self.ui.teclaT13, self.escribir)),
            ('teclaT13', (self.ui.teclaT14, self.escribir)), ('teclaT14', (self.ui.teclaT15, self.escribir)),
            ('teclaT15', (self.ui.teclaT16, self.escribir)),
            ('teclaT16', (self.ui.teclaT17, self.escribir)), ('teclaT17', (self.ui.tecladoF1, self.escribir)),
            ('teclaT21', (self.ui.teclaT22, self.escribir)),
            ('teclaT22', (self.ui.teclaT23, self.escribir)), ('teclaT23', (self.ui.teclaT24, self.escribir)),
            ('teclaT24', (self.ui.teclaT25, self.escribir)),
            ('teclaT25', (self.ui.teclaT26, self.escribir)), ('teclaT26', (self.ui.teclaT27, self.escribir)),
            ('teclaT27', (self.ui.tecladoF2, self.escribir)),
            ('teclaT31', (self.ui.teclaT32, self.escribir)), ('teclaT32', (self.ui.teclaT33, self.escribir)),
            ('teclaT33', (self.ui.teclaT34, self.escribir)),
            ('teclaT34', (self.ui.teclaT35, self.escribir)), ('teclaT35', (self.ui.teclaT36, self.escribir)),
            ('teclaT36', (self.ui.teclaT37, self.escribir)),
            ('teclaT37', (self.ui.tecladoF3, self.escribir)), ('teclaT41', (self.ui.teclaT42, self.selectTeclado)),
            ('teclaT42', (self.ui.teclaT43, self.escribir)),
            ('teclaT43', (self.ui.teclaT44, self.escribir)), ('teclaT44', (self.ui.teclaT45, self.escribir)),
            ('teclaT45', (self.ui.teclaT46, self.escribir)), ('teclaT46', (self.ui.teclaT47, self.escribir)),
            ('teclaT47', (self.ui.tecladoF4, self.escribir)), ('teclaEspacio', (self.ui.teclado, self.escribir))
        ])
        self.tecladoVentanasHijos = dict([
            ('teclado', (self.ui.tecladoF1)), ('tecladoF1', self.ui.teclaT11),
            ('tecladoF2', self.ui.teclaT21), ('tecladoF3', self.ui.teclaT31),
            ('tecladoF4', self.ui.teclaT41)
        ])

    def tecladoColumnas(self):
        self.ui.tecladoF1.setVisible(False)
        self.ui.tecladoF2.setVisible(False)
        self.ui.tecladoF3.setVisible(False)
        self.ui.tecladoF4.setVisible(False)

        self.ui.tecladoC1.setVisible(True)
        self.ui.tecladoC2.setVisible(True)
        self.ui.tecladoC3.setVisible(True)
        self.ui.tecladoC4.setVisible(True)
        self.ui.tecladoC5.setVisible(True)
        self.ui.tecladoC6.setVisible(True)
        self.ui.tecladoC7.setVisible(True)

        # Cambio Padre
        self.ui.teclaT11.setParent(self.ui.tecladoC1)
        self.ui.teclaT21.setParent(self.ui.tecladoC1)
        self.ui.teclaT31.setParent(self.ui.tecladoC1)
        self.ui.teclaT41.setParent(self.ui.tecladoC1)

        self.ui.teclaT12.setParent(self.ui.tecladoC2)
        self.ui.teclaT22.setParent(self.ui.tecladoC2)
        self.ui.teclaT32.setParent(self.ui.tecladoC2)
        self.ui.teclaT42.setParent(self.ui.tecladoC2)

        self.ui.teclaT13.setParent(self.ui.tecladoC3)
        self.ui.teclaT23.setParent(self.ui.tecladoC3)
        self.ui.teclaT33.setParent(self.ui.tecladoC3)
        self.ui.teclaT43.setParent(self.ui.tecladoC3)

        self.ui.teclaT14.setParent(self.ui.tecladoC4)
        self.ui.teclaT24.setParent(self.ui.tecladoC4)
        self.ui.teclaT34.setParent(self.ui.tecladoC4)
        self.ui.teclaT44.setParent(self.ui.tecladoC4)

        self.ui.teclaT15.setParent(self.ui.tecladoC5)
        self.ui.teclaT25.setParent(self.ui.tecladoC5)
        self.ui.teclaT35.setParent(self.ui.tecladoC5)
        self.ui.teclaT45.setParent(self.ui.tecladoC5)

        self.ui.teclaT16.setParent(self.ui.tecladoC6)
        self.ui.teclaT26.setParent(self.ui.tecladoC6)
        self.ui.teclaT36.setParent(self.ui.tecladoC6)
        self.ui.teclaT46.setParent(self.ui.tecladoC6)

        self.ui.teclaT17.setParent(self.ui.tecladoC7)
        self.ui.teclaT27.setParent(self.ui.tecladoC7)
        self.ui.teclaT37.setParent(self.ui.tecladoC7)
        self.ui.teclaT47.setParent(self.ui.tecladoC7)

        # Cambio ubicación
        self.ui.teclaT11.setGeometry(QtCore.QRect(5, 10, 31, 31))
        self.ui.teclaT21.setGeometry(QtCore.QRect(5, 60, 31, 31))
        self.ui.teclaT31.setGeometry(QtCore.QRect(5, 110, 31, 31))
        self.ui.teclaT41.setGeometry(QtCore.QRect(5, 160, 31, 31))

        self.ui.teclaT12.setGeometry(QtCore.QRect(5, 10, 31, 31))
        self.ui.teclaT22.setGeometry(QtCore.QRect(5, 60, 31, 31))
        self.ui.teclaT32.setGeometry(QtCore.QRect(5, 110, 31, 31))
        self.ui.teclaT42.setGeometry(QtCore.QRect(5, 160, 31, 31))

        self.ui.teclaT13.setGeometry(QtCore.QRect(5, 10, 31, 31))
        self.ui.teclaT23.setGeometry(QtCore.QRect(5, 60, 31, 31))
        self.ui.teclaT33.setGeometry(QtCore.QRect(5, 110, 31, 31))
        self.ui.teclaT43.setGeometry(QtCore.QRect(5, 160, 31, 31))

        self.ui.teclaT14.setGeometry(QtCore.QRect(5, 10, 31, 31))
        self.ui.teclaT24.setGeometry(QtCore.QRect(5, 60, 31, 31))
        self.ui.teclaT34.setGeometry(QtCore.QRect(5, 110, 31, 31))
        self.ui.teclaT44.setGeometry(QtCore.QRect(5, 160, 31, 31))

        self.ui.teclaT15.setGeometry(QtCore.QRect(5, 10, 31, 31))
        self.ui.teclaT25.setGeometry(QtCore.QRect(5, 60, 31, 31))
        self.ui.teclaT35.setGeometry(QtCore.QRect(5, 110, 31, 31))
        self.ui.teclaT45.setGeometry(QtCore.QRect(5, 160, 31, 31))

        self.ui.teclaT16.setGeometry(QtCore.QRect(5, 10, 31, 31))
        self.ui.teclaT26.setGeometry(QtCore.QRect(5, 60, 31, 31))
        self.ui.teclaT36.setGeometry(QtCore.QRect(5, 110, 31, 31))
        self.ui.teclaT46.setGeometry(QtCore.QRect(5, 160, 31, 31))

        self.ui.teclaT17.setGeometry(QtCore.QRect(5, 10, 31, 31))
        self.ui.teclaT27.setGeometry(QtCore.QRect(5, 60, 31, 31))
        self.ui.teclaT37.setGeometry(QtCore.QRect(5, 110, 31, 31))
        self.ui.teclaT47.setGeometry(QtCore.QRect(5, 160, 31, 31))

        self.dicTeclado = dict([
            ('tecladoC1', (self.ui.tecladoC2, self.ventanaHijo)), ('tecladoC2', (self.ui.tecladoC3, self.ventanaHijo)),
            ('tecladoC3', (self.ui.tecladoC4, self.ventanaHijo)), ('tecladoC4', (self.ui.tecladoC5, self.ventanaHijo)),
            ('tecladoC5', (self.ui.tecladoC6, self.ventanaHijo)), ('tecladoC6', (self.ui.tecladoC7, self.ventanaHijo)),
            ('tecladoC7', (self.ui.teclaEspacio, self.ventanaHijo)),
            ('teclaT11', (self.ui.teclaT21, self.escribir)),
            ('teclaT21', (self.ui.teclaT31, self.escribir)),
            ('teclaT31', (self.ui.teclaT41, self.escribir)), ('teclaT41', (self.ui.tecladoC1, self.selectTeclado)),
            ('teclaT12', (self.ui.teclaT22, self.escribir)),
            ('teclaT22', (self.ui.teclaT32, self.escribir)), ('teclaT32', (self.ui.teclaT42, self.escribir)),
            ('teclaT42', (self.ui.tecladoC2, self.escribir)),
            ('teclaT13', (self.ui.teclaT23, self.escribir)), ('teclaT23', (self.ui.teclaT33, self.escribir)),
            ('teclaT33', (self.ui.teclaT43, self.escribir)),
            ('teclaT43', (self.ui.tecladoC3, self.escribir)), ('teclaT14', (self.ui.teclaT24, self.escribir)),
            ('teclaT24', (self.ui.teclaT34, self.escribir)),
            ('teclaT34', (self.ui.teclaT44, self.escribir)), ('teclaT44', (self.ui.tecladoC4, self.escribir)),
            ('teclaT15', (self.ui.teclaT25, self.escribir)),
            ('teclaT25', (self.ui.teclaT35, self.escribir)), ('teclaT35', (self.ui.teclaT45, self.escribir)),
            ('teclaT45', (self.ui.tecladoC5, self.escribir)),
            ('teclaT16', (self.ui.teclaT26, self.escribir)), ('teclaT26', (self.ui.teclaT36, self.escribir)),
            ('teclaT36', (self.ui.teclaT46, self.escribir)),
            ('teclaT46', (self.ui.tecladoC6, self.escribir)), ('teclaT17', (self.ui.teclaT27, self.escribir)),
            ('teclaT27', (self.ui.teclaT37, self.escribir)), ('teclaT37', (self.ui.teclaT47, self.escribir)),
            ('teclaT47', (self.ui.tecladoC7, self.escribir)), ('teclaEspacio', (self.ui.teclado, self.escribir))
        ])
        self.tecladoVentanasHijos = dict([('teclado', (self.ui.tecladoC1)), ('tecladoC1', self.ui.teclaT11),
                                          ('tecladoC2', self.ui.teclaT12), ('tecladoC3', self.ui.teclaT13),
                                          ('tecladoC4', self.ui.teclaT14), ('tecladoC5', self.ui.teclaT15),
                                          ('tecladoC6', self.ui.teclaT16), ('tecladoC7', self.ui.teclaT17),
                                          ])

    def selectTeclado(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.text()
        self.dicCambiarTeclado[a]()
        if self.ui.tecladoF1.isVisible():
            self.ui.tecladoF1.setStyleSheet(self.focusStyle)
            self.ui.tecladoF1.setFocus()
        elif self.ui.tecladoC1.isVisible():
            self.ui.tecladoC1.setStyleSheet(self.focusStyle)
            self.ui.tecladoC1.setFocus()
        focus_widget.setStyleSheet("")

    def cambiarTeclado(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()
        dic = dict([
            ('confAbecedarioLabel', (self.ui.radioTAbecedario, self.tecladoOriginal)),
            ('confFrecuenciaLabel', (self.ui.radioTFrecuencia, self.tecladoFrecuencia))
        ])

        dic[a][0].setChecked(True)
        self.dicCambiarTeclado['ABC'] = dic[a][1]
        # dic[a][1]()
        focus_widget.setStyleSheet(self.focusStyle)

    def tecladoOriginal(self):
        self.ui.teclaT11.setText("A")
        self.ui.teclaT12.setText("B")
        self.ui.teclaT13.setText("C")
        self.ui.teclaT14.setText("D")
        self.ui.teclaT15.setText("E")
        self.ui.teclaT16.setText("F")
        self.ui.teclaT17.setText("G")
        self.ui.teclaT21.setText("H")
        self.ui.teclaT22.setText("I")
        self.ui.teclaT23.setText("J")
        self.ui.teclaT24.setText("K")
        self.ui.teclaT25.setText("L")
        self.ui.teclaT26.setText("M")
        self.ui.teclaT27.setText("N")
        self.ui.teclaT31.setText("Ñ")
        self.ui.teclaT32.setText("O")
        self.ui.teclaT33.setText("P")
        self.ui.teclaT34.setText("Q")
        self.ui.teclaT35.setText("R")
        self.ui.teclaT36.setText("S")
        self.ui.teclaT37.setText("T")
        self.ui.teclaT42.setText("U")
        self.ui.teclaT43.setText("V")
        self.ui.teclaT44.setText("W")
        self.ui.teclaT45.setText("X")
        self.ui.teclaT46.setText("Y")
        self.ui.teclaT47.setText("Z")
        self.ui.teclaT41.setText("Á?1")
        self.ui.teclaEspacio.setText("__")
        self.dic['teclaT42'] = (self.ui.teclaT43, self.escribir)

    def tecladoNum(self):
        self.ui.teclaT11.setText("Á")
        self.ui.teclaT12.setText("É")
        self.ui.teclaT13.setText("Í")
        self.ui.teclaT14.setText("Ó")
        self.ui.teclaT15.setText("Ú")
        self.ui.teclaT16.setText("¿")
        self.ui.teclaT17.setText("?")
        self.ui.teclaT21.setText("0")
        self.ui.teclaT22.setText("1")
        self.ui.teclaT23.setText("2")
        self.ui.teclaT24.setText("3")
        self.ui.teclaT25.setText("4")
        self.ui.teclaT26.setText("¡")
        self.ui.teclaT27.setText("!")
        self.ui.teclaT31.setText("5")
        self.ui.teclaT32.setText("6")
        self.ui.teclaT33.setText("7")
        self.ui.teclaT34.setText("8")
        self.ui.teclaT35.setText("9")
        self.ui.teclaT36.setText("(")
        self.ui.teclaT37.setText(")")
        self.ui.teclaT43.setText("@")
        self.ui.teclaT44.setText(",")
        self.ui.teclaT45.setText(".")
        self.ui.teclaT46.setText(";")
        self.ui.teclaT47.setText("-")
        self.ui.teclaT42.setText("#+=")
        self.ui.teclaT41.setText("ABC")
        self.ui.teclaEspacio.setText("__")
        self.dic['teclaT42'] = (self.ui.teclaT43, self.selectTeclado)

    def tecladoNum2(self):
        self.ui.teclaT11.setText("Ü")
        self.ui.teclaT12.setText("_")
        self.ui.teclaT13.setText("#")
        self.ui.teclaT14.setText("$")
        self.ui.teclaT15.setText("%")
        self.ui.teclaT16.setText("&&")
        self.ui.teclaT17.setText("/")
        self.ui.teclaT21.setText("[")
        self.ui.teclaT22.setText("]")
        self.ui.teclaT23.setText("{")
        self.ui.teclaT24.setText("}")
        self.ui.teclaT25.setText("'")
        self.ui.teclaT26.setText("\"")
        self.ui.teclaT27.setText("=")
        self.ui.teclaT31.setText(":")
        self.ui.teclaT32.setText("+")
        self.ui.teclaT33.setText("*")
        self.ui.teclaT34.setText("^")
        self.ui.teclaT35.setText("<")
        self.ui.teclaT36.setText(">")
        self.ui.teclaT37.setText("|")
        self.ui.teclaT43.setText("°")
        self.ui.teclaT44.setText("~")
        self.ui.teclaT45.setText("€")
        self.ui.teclaT46.setText("£")
        self.ui.teclaT47.setText("Ç")
        self.ui.teclaT42.setText("Á?1")
        self.ui.teclaT41.setText("ABC")
        self.ui.teclaEspacio.setText("__")
        self.dic['teclaT42'] = (self.ui.teclaT43, self.selectTeclado)

    def tecladoFrecuencia(self):
        self.ui.teclaT11.setText("A")
        self.ui.teclaT12.setText("E")
        self.ui.teclaT13.setText("S")
        self.ui.teclaT14.setText("I")
        self.ui.teclaT15.setText("T")
        self.ui.teclaT16.setText("B")
        self.ui.teclaT17.setText("H")
        self.ui.teclaT21.setText("O")
        self.ui.teclaT22.setText("R")
        self.ui.teclaT23.setText("L")
        self.ui.teclaT24.setText("C")
        self.ui.teclaT25.setText("Q")
        self.ui.teclaT26.setText("Y")
        self.ui.teclaT27.setText("Z")
        self.ui.teclaT31.setText("N")
        self.ui.teclaT32.setText("D")
        self.ui.teclaT33.setText("M")
        self.ui.teclaT34.setText("V")
        self.ui.teclaT35.setText("F")
        self.ui.teclaT36.setText("Ñ")
        self.ui.teclaT37.setText("K")
        self.ui.teclaT42.setText("U")
        self.ui.teclaT43.setText("P")
        self.ui.teclaT44.setText("G")
        self.ui.teclaT45.setText("J")
        self.ui.teclaT46.setText("X")
        self.ui.teclaT47.setText("W")
        self.ui.teclaT41.setText("ABC")
        self.ui.teclaEspacio.setText("__")
        self.dic['teclaT42'] = (self.ui.teclaT43, self.escribir)

    def setearTeclado(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()
        dic = dict([
            ('confTecladoFilas', (self.ui.radioTecladoFilas, self.tecladoFilas)),
            ('confTecladoColumnas', (self.ui.radioTecladoColumnas, self.tecladoColumnas))
        ])

        dic[a][0].setChecked(True)
        dic[a][1]()
        focus_widget.setStyleSheet(self.focusStyle)

    # Ventanas Hijos Optimizado
    def ventanaHijo(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()
        self.dicVentanasHijos[a].setStyleSheet(self.focusStyle)
        self.dicVentanasHijos[a].setFocus()
        focus_widget.setStyleSheet("")

    def vInicioVentanasHijos(self):
        dic = dict([
            ('VPalabras', self.ui.palabrasF1), ('palabrasF1', self.ui.palabraSug1),
            ('palabrasF2', self.ui.palabraSug4), ('VFrases', self.ui.fraseB1),
            ('VBorrarEnter', self.ui.teclaBorrar)
        ])
        dic.update(self.tecladoVentanasHijos)
        self.dicVentanasHijos = dic

    def vCalcuVentanasHijos(self):
        dic = dict([('calcuF1', self.ui.tecla7), ('calcuF2', self.ui.tecla4),
                    ('calcuF3', self.ui.tecla1), ('calcuF4', self.ui.tecla0),
                    ('calcuC', self.ui.teclaAC)
                    ])
        self.dicVentanasHijos = dic

    def vCalenVentanasHijos(self):
        dic = dict([('calenEventosBox', self.ui.calen_labelTitulo),
                    ('calenFlechasFrame', self.ui.calen_dia_adelante),
                    ('calenBorrarEnter', self.ui.calenBorrarLetra)
                    ])
        dic.update(self.tecladoVentanasHijos)
        self.dicVentanasHijos = dic

    def vWordVentanasHijos(self):
        dic = dict([
            ('VPalabras', self.ui.palabrasF1), ('palabrasF1', self.ui.palabraSug1),
            ('palabrasF2', self.ui.palabraSug4), ('VFrases', self.ui.fraseB1),
            ('wBorrarEnter', self.ui.wTeclaBorrar), ('wTeclaPanel', self.ui.wWidgetNegrita),
            ('wTeclaMenu', self.ui.wGuardar), ('wLetra', self.ui.wWidgetNegrita),
            ('wGuardarCargar', self.ui.wGuardar)
        ])
        dic.update(self.tecladoVentanasHijos)
        self.dicVentanasHijos = dic

    def vMailVentanasHijos(self):
        dic = dict([
            ('VPalabras', self.ui.palabrasF1), ('palabrasF1', self.ui.palabraSug1),
            ('palabrasF2', self.ui.palabraSug4), ('VFrases', self.ui.fraseB1),
            ('mBorrarEnter', self.ui.mTeclaBorrar)
        ])
        dic.update(self.tecladoVentanasHijos)
        self.dicVentanasHijos = dic

    def vConfigVentanasHijos(self):
        dic = dict([
            ('confTecladoLabel', self.ui.confRecorridoLabel),
            ('confHablaLabel', self.ui.confHablaVolumenLabel),
            ('confHablaVolumenLabel', self.ui.hablaVolumenMenos),
            ('confHablaVelocidadLabel', self.ui.hablaVelocidadMenos),
            ('confRecorridoLabel', self.ui.confTecladoFilas),
            ('confPaletaLabel', self.ui.confFocusLabel), ('confFocusLabel', self.ui.confAzul),
            ('confFondoLabel', self.ui.confDark),
            ('confDisenoLabel', self.ui.confFondoNone),
            ('confPredictorLabel', self.ui.confLimpiarButton),
            ('confOrdenTLabel', self.ui.confAbecedarioLabel),
            ('confHablaVozLabel', self.ui.hablaVozArriba),
            ('confControlesLabel', self.ui.confInputLabel),
            ('confModoTeclasLabel', self.ui.confDosTeclasLabel),
            ('confElegirTeclasLabel', self.ui.confTeclaTabularLabel),
            ('confInputLabel', self.ui.confInputTecladoLabel),
        ])

        self.dicVentanasHijos = dic

    # Funciones Habla
    def volumenMas(self):
        if self.ui.hablaVolumenBar.value() != 100:
            valor = self.ui.hablaVolumenBar.value() + 10
            self.ui.hablaVolumenBar.setValue(valor)
            engine.setProperty('volume', valor / 100)
        else:
            self.ui.hablaVolumenBar.setValue(100)

    def volumenMenos(self):
        if self.ui.hablaVolumenBar.value() != 0:
            valor = self.ui.hablaVolumenBar.value() - 10
            self.ui.hablaVolumenBar.setValue(valor)
            engine.setProperty('volume', valor / 100)
        else:
            self.ui.hablaVolumenBar.setValue(0)

    def velocidadMas(self):
        if self.ui.hablaVelocidadBar.value() != 100:
            valor = self.ui.hablaVelocidadBar.value() + 10
            self.ui.hablaVelocidadBar.setValue(valor)
            velocidad = valor + 100
            engine.setProperty('rate', velocidad)  # Aumentar velocidad 40%
        else:
            self.ui.hablaVelocidadBar.setValue(100)

    def velocidadMenos(self):
        if self.ui.hablaVelocidadBar.value() != 0:
            valor = self.ui.hablaVelocidadBar.value() - 10
            self.ui.hablaVelocidadBar.setValue(valor)
            velocidad = valor + 100
            engine.setProperty('rate', velocidad)  # Aumentar velocidad 40%
        else:
            self.ui.hablaVelocidadBar.setValue(0)

    def misVoces(self):
        dic = {}
        for i in range(len(voices)):
            dic.update(dict([(i + 1, ('Voz ' + str(i + 1), voices[i].id))]))
        return dic

    def cambiarVozArriba(self):
        if self.numeroVoz > 1:
            self.numeroVoz -= 1
        else:
            self.numeroVoz = len(voices)

        dic = self.misVoces()
        self.ui.lineEditVoces.setText(dic[self.numeroVoz][0])
        engine.setProperty('voice', dic[self.numeroVoz][1])
        engine.say('Hola! Esta es mi voz')
        engine.runAndWait()  # Esperar a que terine de Hablar
        engine.stop()  # Detener motor tts

    def cambiarVozAbajo(self):
        if self.numeroVoz < len(voices):
            self.numeroVoz += 1
        else:
            self.numeroVoz = 1

        dic = self.misVoces()
        self.ui.lineEditVoces.setText(dic[self.numeroVoz][0])
        engine.setProperty('voice', dic[self.numeroVoz][1])
        engine.say('Hola! Esta es mi voz')
        engine.runAndWait()  # Esperar a que terine de Hablar
        engine.stop()  # Detener motor tts

    def textNegrita(self):
        if self.ui.wNegrita.isChecked():
            self.ui.wNegrita.setChecked(False)
            self.ui.wNegrita.setStyleSheet('')
            self.ui.textEdit.setFontWeight(QFont.Normal)
        else:
            self.ui.wNegrita.setChecked(True)
            self.ui.wNegrita.setStyleSheet("border-width: 2px; border-style: solid; border-color:" + self.borderStyle)
            self.ui.textEdit.setFontWeight(QFont.Bold)

    def textCursiva(self):
        if self.ui.wCursiva.isChecked():
            self.ui.wCursiva.setChecked(False)
            self.ui.wCursiva.setStyleSheet("")
            self.ui.textEdit.setFontItalic(False)
        else:
            self.ui.wCursiva.setChecked(True)
            self.ui.wCursiva.setStyleSheet("border-width: 2px; border-style: solid; border-color:" + self.borderStyle)
            self.ui.textEdit.setFontItalic(True)

    def textSubrayar(self):
        if self.ui.wSubrayar.isChecked():
            self.ui.wSubrayar.setChecked(False)
            self.ui.wSubrayar.setStyleSheet("")
            self.ui.textEdit.setFontUnderline(False)
        else:
            self.ui.wSubrayar.setChecked(True)
            self.ui.wSubrayar.setStyleSheet("border-width: 2px; border-style: solid; border-color:" + self.borderStyle)
            self.ui.textEdit.setFontUnderline(True)

    def moverArchivoAbajo(self):
        fila = self.ui.wListaArchivos.currentRow()
        if fila == len(self.ui.wListaArchivos) - 1:
            fila = 0
        else:
            fila = fila + 1

        self.ui.wListaArchivos.setCurrentRow(fila)

    def moverArchivoArriba(self):
        fila = self.ui.wListaArchivos.currentRow()
        if fila == 0:
            fila = len(self.ui.wListaArchivos) - 1
        else:
            fila = fila - 1

        self.ui.wListaArchivos.setCurrentRow(fila)

    def wPopulateList(self):
        self.ui.wListaArchivos.clear()
        for file in self.archivos:
            self.ui.wListaArchivos.addItem(file)

    def wordGuardar(self):
        nombre = self.ui.wTitulo.toPlainText()
        texto = self.ui.textEdit.toHtml()
        if len(nombre) == 0 and len(texto) > 0:
            temporal = self.ui.textEdit.toPlainText()
            temporal = temporal.lstrip()
            p = temporal.find(' ')
            if p > 0:
                nombre = temporal[:p]  # le pongo la primera palabra del texto como nombre
            elif len(temporal) > 1:
                nombre = temporal
            else:
                nombre = 'myFile'

        if len(nombre) > 0:
            with open(nombre + '.html', 'w') as f:
                f.write(texto)
                f.close()
        if nombre not in self.archivos:
            self.archivos.append(nombre)

        self.wPopulateList()
        self.ui.wCargar.setEnabled(True)
        self.ui.wArchivoAbajo.setEnabled(True)
        self.ui.wArchivoArriba.setEnabled(True)
        self.ui.wListaArchivos.setCurrentRow(0)
        self.ui.wGuardar.setStyleSheet('')
        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()
        self.ui.wButtonTitulo.setChecked(True)
        self.escribirTitulo()
        self.dic = self.diccionarioWord()

    def wordCargar(self):
        nombre = self.ui.wListaArchivos.currentItem().text()

        if len(nombre) > 0:
            try:
                with open(nombre + '.html', 'r') as f:
                    texto = f.read()

            except FileNotFoundError:
                texto = ''
        else:
            texto = ''

        self.ui.textEdit.clear()
        self.ui.textEdit.insertHtml(texto)
        self.ui.wTitulo.clear()
        self.ui.wTitulo.insertPlainText(nombre)

        self.ui.wCargar.setStyleSheet('')
        self.ui.teclado.setStyleSheet(self.focusStyle)
        self.ui.teclado.setFocus()
        self.ui.wButtonTitulo.setChecked(True)
        self.ui.wSubrayar.setChecked(True)
        self.ui.wCursiva.setChecked(True)
        self.ui.wNegrita.setChecked(True)
        self.textCursiva()
        self.textNegrita()
        self.textSubrayar()
        self.escribirTitulo()

    def escribirTitulo(self):

        if self.ui.wButtonTitulo.isChecked():
            print('0')
            self.ui.wButtonTitulo.setChecked(False)
            self.ui.wLabelTitulo.setStyleSheet("")
            self.ui.wWidgetTitulo.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")

            self.text = self.ui.textEdit

        else:

            self.ui.wButtonTitulo.setChecked(True)
            self.ui.wLabelTitulo.setStyleSheet("")
            self.ui.wWidgetTitulo.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)

            self.text = self.ui.wTitulo
        print('1')
        a = self.text.toPlainText()
        print(a)
        if len(a) > 0:
            p = max(map(a.rfind, '?!.;:)]}\n'))  # busco último símbolo de finalización de oración
            if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                print('3')

                self.phrase = a[p + 1:]  # me quedo con la última oración
                print('4')
                frase = self.phrase
                if frase == ' ':
                    frase = ''
                else:
                    frase = frase.lstrip()
            elif p == -1:
                self.phrase = a
                frase = self.phrase
                frase = frase.lstrip()
            else:
                frase = ''
                self.phrase = ''

            if len(frase) > 0:

                if frase[0].upper() in self.arboles.hijos:

                    self.currentNode = self.arboles.hijos[frase[0].upper()]  # me paro en el nodo de la primera letra
                else:  # esto no debería suceder igual

                    self.arboles.add(frase[0].upper())
                    self.currentNode = self.arboles.hijos[frase[0].upper()]

                # ahora tengo que encontrar la última palabra
                frase = self.phrase  # por si self.phrase tiene un espacio al final
                frase = frase.rstrip()

                r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                if r > -1:

                    self.word = frase[r + 1:]
                    self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                else:
                    self.word = frase

            else:  # si la frase está vacía
                self.word = ''
                self.currentNode = self.arboles
            if p != len(a) - 1:
                self.dicCasos[a[-1].upper()]()  # hago lo que diga el último caracter


        else:  # si no hay nada en el edit text
            self.word = ''
            self.phrase = ''
            self.currentNode = self.arboles

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    # Funciones Calendario
    def escribirCategoriaCalen(self):
        self.ui.calen_titulo.setChecked(False)
        self.ui.calen_Wtitulo.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_hora.setChecked(False)
        self.ui.calen_Whora.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        if self.ui.calen_categoria.isChecked():
            self.ui.calen_categoria.setChecked(False)
            self.ui.calen_labelCategoria.setStyleSheet("")
            self.ui.calen_Wcategoria.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
            self.text = self.ui.textEdit
        else:
            self.ui.calen_categoria.setChecked(True)
            self.ui.calen_labelCategoria.setStyleSheet("")
            self.ui.calen_Wcategoria.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)
            self.text = self.ui.calen_event_category

        a = self.text.toPlainText()
        if len(a) > 0:

            p = max(map(a.rfind, '?!.;:)]}\n'))  # busco último símbolo de finalización de oración

            if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                self.phrase = a[p + 1:]  # me quedo con la última oración
                frase = self.phrase
                if frase == ' ':
                    frase = ''
                else:
                    frase = frase.lstrip()
            elif p == -1:
                self.phrase = a
                frase = self.phrase
                frase = frase.lstrip()

            else:
                frase = ''
                self.phrase = ''

            if len(frase) > 0:

                if frase[0].upper() in self.arboles.hijos:
                    self.currentNode = self.arboles.hijos[frase[0].upper()]  # me paro en el nodo de la primera letra
                else:  # esto no debería suceder igual
                    self.arboles.add(frase[0].upper())
                    self.currentNode = self.arboles.hijos[frase[0].upper()]

                # ahora tengo que encontrar la última palabra
                frase = self.phrase  # por si self.phrase tiene un espacio al final
                frase = frase.rstrip()
                r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                if r > -1:
                    self.word = frase[r + 1:]
                    self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                else:
                    self.word = frase

            else:  # si la frase está vacía
                self.word = ''
                self.currentNode = self.arboles

            if p != len(a) - 1:
                self.dicCasos[a[-1].upper()]()  # hago lo que diga el último caracter


        else:  # si no hay nada en el edit text
            self.word = ''
            self.phrase = ''
            self.currentNode = self.arboles

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    def escribirTituloCalen(self):
        self.ui.calen_categoria.setChecked(False)
        self.ui.calen_Wcategoria.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_hora.setChecked(False)
        self.ui.calen_Whora.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        if self.ui.calen_titulo.isChecked():
            self.ui.calen_titulo.setChecked(False)
            self.ui.calen_labelTitulo.setStyleSheet("")
            self.ui.calen_Wtitulo.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
            self.text = self.ui.textEdit
        else:
            self.ui.calen_titulo.setChecked(True)
            self.ui.calen_labelTitulo.setStyleSheet("")
            self.ui.calen_Wtitulo.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)
            self.text = self.ui.calen_event_title

        a = self.text.toPlainText()
        if len(a) > 0:

            p = max(map(a.rfind, '?!.;:)]}\n'))  # busco último símbolo de finalización de oración

            if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                self.phrase = a[p + 1:]  # me quedo con la última oración
                frase = self.phrase
                if frase == ' ':
                    frase = ''
                else:
                    frase = frase.lstrip()
            elif p == -1:
                self.phrase = a
                frase = self.phrase
                frase = frase.lstrip()

            else:
                frase = ''
                self.phrase = ''

            if len(frase) > 0:

                if frase[0].upper() in self.arboles.hijos:
                    self.currentNode = self.arboles.hijos[frase[0].upper()]  # me paro en el nodo de la primera letra
                else:  # esto no debería suceder igual
                    self.arboles.add(frase[0].upper())
                    self.currentNode = self.arboles.hijos[frase[0].upper()]

                # ahora tengo que encontrar la última palabra
                frase = self.phrase  # por si self.phrase tiene un espacio al final
                frase = frase.rstrip()
                r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                if r > -1:
                    self.word = frase[r + 1:]
                    self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                else:
                    self.word = frase

            else:  # si la frase está vacía
                self.word = ''
                self.currentNode = self.arboles

            if p != len(a) - 1:
                self.dicCasos[a[-1].upper()]()  # hago lo que diga el último caracter


        else:  # si no hay nada en el edit text
            self.word = ''
            self.phrase = ''
            self.currentNode = self.arboles

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    def escribirHoraCalen(self):
        self.ui.calen_categoria.setChecked(False)
        self.ui.calen_Wcategoria.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        self.ui.calen_titulo.setChecked(False)
        self.ui.calen_Wtitulo.setStyleSheet(
            "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
        if self.ui.calen_hora.isChecked():
            self.ui.calen_hora.setChecked(False)
            self.ui.calen_labelHora.setStyleSheet("")
            self.ui.calen_Whora.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color: gray rgba(255, 255, 255, 0) gray gray;")
            self.text = self.ui.textEdit
        else:
            self.ui.calen_hora.setChecked(True)
            self.ui.calen_labelHora.setStyleSheet("")
            self.ui.calen_Whora.setStyleSheet(
                "border-width: 2px; border-style: solid; border-color:" + self.borderStyle + "rgba(255, 255, 255, 0)" + self.borderStyle + self.borderStyle)
            self.text = self.ui.calen_event_hora

        a = self.text.toPlainText()
        if len(a) > 0:

            p = max(map(a.rfind, '?!.;:)]}\n'))  # busco último símbolo de finalización de oración

            if -1 < p < len(a) - 1:  # me aseguro que esa posición no sea la última
                self.phrase = a[p + 1:]  # me quedo con la última oración
                frase = self.phrase
                if frase == ' ':
                    frase = ''
                else:
                    frase = frase.lstrip()
            elif p == -1:
                self.phrase = a
                frase = self.phrase
                frase = frase.lstrip()

            if len(frase) > 0:

                if frase[0].upper() in self.arboles.hijos:
                    self.currentNode = self.arboles.hijos[frase[0].upper()]  # me paro en el nodo de la primera letra
                else:  # esto no debería suceder igual
                    self.arboles.add(frase[0].upper())
                    self.currentNode = self.arboles.hijos[frase[0].upper()]

                # ahora tengo que encontrar la última palabra
                frase = self.phrase  # por si self.phrase tiene un espacio al final
                frase = frase.rstrip()
                r = frase.rfind(' ')  # tengo que poner en self.word la última palabra
                if r > -1:
                    self.word = frase[r + 1:]
                    self.currentNode = self.currentNode.jump(frase[:r], agregar=False)
                else:
                    self.word = frase

            else:  # si la frase está vacía
                self.word = ''
                self.currentNode = self.arboles

            if p != len(a) - 1:
                self.dicCasos[a[-1].upper()]()  # hago lo que diga el último caracter


        else:  # si no hay nada en el edit text
            self.word = ''
            self.phrase = ''
            self.currentNode = self.arboles

        self.ui.teclado.setFocus()
        self.ui.teclado.setStyleSheet(self.focusStyle)

    def delete_event(self):
        date = self.ui.calendarWidget.selectedDate()
        row = self.ui.calen_event_list.currentRow()
        lista = self.events[date]
        del (self.events[date][row])
        if len(lista) == 0:
            self.ui.calen_event_list.setCurrentRow(-1)
            self.dic = self.diccionarioCalen()
            self.ui.calenEventosBox.setFocus()
            self.ui.calenEventosBox.setStyleSheet(self.focusStyle)
        else:
            self.ui.calen_event_list.setCurrentRow(0)
        self.clear_form()
        self.populate_list()
        self.ui.calen_del_button.setStyleSheet('')
        self.ui.calenEventosBox.setFocus()
        self.ui.calenEventosBox.setStyleSheet(self.focusStyle)

    def calenMover(self):
        focus_widget = self.ui.centralwidget.focusWidget()
        a = focus_widget.objectName()
        dic1 = dict([
            ('calen_dia_atras', self.move_days_down),
            ('calen_dia_adelante', self.move_days_up),
            ('calen_sem_abajo', self.move_week_up),
            ('calen_sem_arriba', self.move_week_down)
        ])
        dic1[a]()
        date = self.ui.calendarWidget.selectedDate()

        if date in self.events.keys():
            self.dic['calenFlechasFrame'] = (self.ui.calenEventosFrame, self.ventanaHijo)
            self.dic['calenEventosFrame'] = (self.ui.calenEventosBox, self.eventosFrameEntra)
            self.dic['calenEventoAbajoButton'] = (self.ui.calenEventoArribaButton, self.recorrerListaAbajo)
            self.dic['calenEventoArribaButton'] = (self.ui.calenSeleccionarEventoButton, self.recorrerListaArriba)
            self.dic['calenSeleccionarEventoButton'] = (self.ui.calenEventosFrame, self.populate_form)
            self.dic['calen_add_button'] = (self.ui.calen_del_button, self.save_event)
            self.dic['calen_del_button'] = (self.ui.calenEventosBox, self.delete_event)
            self.populate_list()

        else:
            self.dic = self.diccionarioCalen()
            self.ui.calen_event_list.clear()
            self.clear_form()

    def populate_form(self):
        self.clear_form()
        date = self.ui.calendarWidget.selectedDate()
        event_number = self.ui.calen_event_list.currentRow()
        if event_number == -1:
            return
        event_data = self.events.get(date)[event_number]
        self.ui.calen_event_category.setPlainText(event_data['Categoría'])
        if event_data['Hora'] is None:
            self.ui.calen_allday_check.setChecked(True)
        else:
            self.ui.calen_event_hora.setPlainText(event_data['Hora'])
        self.ui.calen_event_title.setPlainText(event_data['Título'])
        self.ui.textEdit.setPlainText(event_data['Detalle'])

    def allDayCheck(self):
        if self.ui.calen_allday_check.isChecked():
            self.ui.calen_allday_check.setChecked(False)
        else:
            self.ui.calen_allday_check.setChecked(True)

    def recorrerListaAbajo(self):
        fila = self.ui.calen_event_list.currentRow()
        if fila == len(self.ui.calen_event_list) - 1:
            fila = 0
        else:
            fila = fila + 1

        self.ui.calen_event_list.setCurrentRow(fila)

    def recorrerListaArriba(self):
        fila = self.ui.calen_event_list.currentRow()
        if fila == 0:
            fila = len(self.ui.calen_event_list) - 1
        else:
            fila = fila - 1

        self.ui.calen_event_list.setCurrentRow(fila)

    def move_days_up(self):
        hoy = self.ui.calendarWidget.selectedDate()
        hoy = hoy.toPyDate()
        date = str(hoy + timedelta(days=1))
        date = QtCore.QDate.fromString(date, 'yyyy-MM-dd')
        self.ui.calendarWidget.setSelectedDate(date)

    def move_days_down(self):
        hoy = self.ui.calendarWidget.selectedDate()
        hoy = hoy.toPyDate()
        date = str(hoy - timedelta(days=1))
        date = QtCore.QDate.fromString(date, 'yyyy-MM-dd')
        self.ui.calendarWidget.setSelectedDate(date)

    def move_week_up(self):
        hoy = self.ui.calendarWidget.selectedDate()
        hoy = hoy.toPyDate()
        date = str(hoy + timedelta(days=7))
        date = QtCore.QDate.fromString(date, 'yyyy-MM-dd')
        self.ui.calendarWidget.setSelectedDate(date)

    def move_week_down(self):
        hoy = self.ui.calendarWidget.selectedDate()
        hoy = hoy.toPyDate()
        date = str(hoy - timedelta(days=7))
        date = QtCore.QDate.fromString(date, 'yyyy-MM-dd')
        self.ui.calendarWidget.setSelectedDate(date)

    # def escribirHora(self): #Cuidado, es con un timeEdit, tiene para escribir la hora, minutos, y después para moverse con flechas
    #   self.ui.calen_event_time.setTime()

    def todoElDia(self):
        if self.ui.calen_allday_check.isChecked():
            self.ui.calen_allday_check.setChecked(False)
        else:
            self.ui.calen_allday_check.setChecked(False)

    def clear_form(self):
        self.ui.calen_event_title.setPlainText("")
        self.ui.calen_event_category.setPlainText("")
        self.ui.calen_event_hora.setPlainText("")
        self.ui.calen_allday_check.setChecked(False)
        self.ui.textEdit.setPlainText("")

    def populate_list(self):
        self.ui.calen_event_list.clear()
        self.clear_form()
        date = self.ui.calendarWidget.selectedDate()
        for event in self.events.get(date, []):
            time = (
                event["Hora"]
                if event["Hora"]
                else "Todo el día"
            )
            self.ui.calen_event_list.addItem(f"{time}: {event['Título']}")

    def isTimeFormat(self, input):
        try:
            time.strptime(input, '%H:%M')
            return True
        except ValueError:
            return False

    def save_event(self):
        hora = self.ui.calen_event_hora.toPlainText()

        if not self.isTimeFormat(hora):
            self.ui.calen_event_hora.clear()
            self.ui.calen_event_hora.insertPlainText('12:00')

        event = {
            'Categoría': self.ui.calen_event_category.toPlainText(),
            'Hora': (
                None
                if self.ui.calen_allday_check.isChecked()
                else self.ui.calen_event_hora.toPlainText()
            ),
            'Título': self.ui.calen_event_title.toPlainText(),
            'Detalle': self.ui.textEdit.toPlainText()
        }

        date = self.ui.calendarWidget.selectedDate()
        event_list = self.events.get(date, [])
        event_number = self.ui.calen_event_list.currentRow()
        if event_number == -1:
            event_list.append(event)
        else:
            event_list[event_number] = event
        event_list.sort(key=lambda x: x['Hora'] or QtCore.QTime(0, 0))
        # Los que no tengan hora de inicio, van a ser el día completo, entonces va de 0 a 0
        self.events[date] = event_list
        self.dic['calenFlechasFrame'] = (self.ui.calenEventosFrame, self.ventanaHijo)
        self.dic['calenEventosFrame'] = (self.ui.calenEventosBox, self.eventosFrameEntra)
        self.dic['calenEventoAbajoButton'] = (self.ui.calenEventoArribaButton, self.recorrerListaAbajo)
        self.dic['calenEventoArribaButton'] = (self.ui.calenSeleccionarEventoButton, self.recorrerListaArriba)
        self.dic['calenSeleccionarEventoButton'] = (self.ui.calenEventosFrame, self.populate_form)
        self.dic['calen_add_button'] = (self.ui.calen_del_button, self.save_event)
        self.dic['calen_del_button'] = (self.ui.calenEventosBox, self.delete_event)
        self.populate_list()

    def eventosFrameEntra(self):
        self.ui.calenEventoAbajoButton.setFocus()
        self.ui.calenEventoAbajoButton.setStyleSheet(self.focusStyle)
        self.ui.calenEventosFrame.setStyleSheet('')
        self.ui.calen_event_list.setCurrentRow(0)

    # Funciones Clima
    def alert(self, message):
        alert = QMessageBox.warning(self, "Warning", message)

    def update_weather(self):
        worker = WeatherWorker(self.ui.lineEdit.text())
        worker.signals.result.connect(self.weather_result)
        worker.signals.error.connect(self.alert)
        self.threadpool.start(worker)

    def weather_result(self, weather, forecasts):
        self.ui.latitudeLabel.setText("%.2f °" % weather['coord']['lat'])
        self.ui.longitudeLabel.setText("%.2f °" % weather['coord']['lon'])

        self.ui.windLabel.setText("%.2f m/s" % weather['wind']['speed'])

        self.ui.temperatureLabel.setText("%.1f °C" % weather['main']['temp'])
        self.ui.pressureLabel.setText("%d" % weather['main']['pressure'])
        self.ui.humidityLabel.setText("%d" % weather['main']['humidity'])

        self.ui.sunriseLabel.setText(from_ts_to_time_of_day(weather['sys']['sunrise']))

        self.ui.weatherLabel.setText("%s (%s)" % (
            weather['weather'][0]['main'],
            weather['weather'][0]['description']))

        self.set_weather_icon(self.ui.weatherIcon, weather['weather'])

        for n, forecast in enumerate(forecasts['list'][:5], 1):
            getattr(self.ui, 'forecastTime%d' % n).setText(from_ts_to_time_of_day(forecast['dt']))
            self.set_weather_icon(getattr(self.ui, 'forecastIcon%d' % n), forecast['weather'])
            getattr(self.ui, 'forecastTemp%d' % n).setText("%.1f °C" % forecast['main']['temp'])

    def set_weather_icon(self, label, weather):
        label.setPixmap(
            QtGui.QPixmap(os.path.join('images', "%s.png" %
                                       weather[0]['icon'])))

    def elegirTeclaTabular(self):

        self.keysEvent = False
        self.anteriorTeclaTexto = self.teclaTab #self.ui.confTeclaTabularText.toPlainText().upper()
        self.ui.confTeclaTabularText.clear()

        with keyboard.Listener(on_press=self.on_press) as listener:  # setting code for listening key-release
            listener.join()
        if self.ui.radioConfDosTeclas.isChecked():
            if self.ultimaTeclaT.upper() != self.teclaAccion.upper():
                self.teclaTab = self.ultimaTeclaT.upper()
                self.ui.confTeclaTabularText.setPlainText(self.ultimaTeclaT.upper())
            else:
#            self.teclaTab = self.anteriorTeclaTexto.upper()
                self.ui.confTeclaTabularText.setPlainText(self.anteriorTeclaTexto.upper())
        else:
            self.teclaTab = self.ultimaTeclaT.upper()
            self.ui.confTeclaTabularText.setPlainText(self.ultimaTeclaT.upper())
        self.funcionAyuda()
        self.tabular()

    def on_press(self, key):
        try:
            self.ultimaTeclaT = str(key.char).upper()  # single-char keys

        except:
            self.ultimaTeclaT = self.anteriorTeclaTexto.upper()
            # other keys

        return False

    def elegirTeclaAccion(self):

        self.keysEvent = False

        self.ui.confTeclasMensajeLabel.setVisible(True)
        self.ui.logoInformacionElegirTeclas.setVisible(True)

        self.anteriorTeclaTexto = self.teclaAccion.upper()#self.ui.confTeclaAccionText.toPlainText().upper()
        self.ui.confTeclaAccionText.clear()
        with keyboard.Listener(on_press=self.on_press) as listener:  # setting code for listening key-release
            listener.join()
        if self.ultimaTeclaT.upper() != self.teclaTab.upper():
            self.teclaAccion = self.ultimaTeclaT.upper()
            self.ui.confTeclaAccionText.setPlainText(self.ultimaTeclaT.upper())
        else:
            self.ui.confTeclaAccionText.setPlainText(self.anteriorTeclaTexto.upper())
        self.funcionAyuda()


    def modoADosTeclas(self):
        self.ui.radioConfDosTeclas.setChecked(True)
        self.modoTeclas = 'DosTeclas'
        self.dic = self.diccionarioConfiguracion()
        self.ui.confTeclaAccionText.setVisible(True)
        self.ui.confTeclaAccionLabel.setVisible(True)
        self.ui.confTeclaTabularLabel.setText('Tecla tabular:')
        if self.teclaTab == self.teclaAccion:
            if self.teclaAccion == 'X':
                self.teclaAccion = 'Z'
                self.ui.confTeclaAccionText.clear()
                self.ui.confTeclaAccionText.setPlainText(self.teclaAccion.upper())
            else:
                self.teclaAccion = 'X'
                self.ui.confTeclaAccionText.clear()
                self.ui.confTeclaAccionText.setPlainText(self.teclaAccion.upper())




    def modoAUnaTecla(self):
        self.ui.radioConfUnaTecla.setChecked(True)
        self.modoTeclas = 'UnaTecla'
        # self.dic = self.diccionarioConfiguracion()
        self.ui.confTeclaAccionText.setVisible(False)
        self.ui.confTeclaAccionLabel.setVisible(False)
        self.ui.confTeclaTabularLabel.setText('Tecla única:')
        self.dic['confTeclaTabularLabel'] = (self.ui.confElegirTeclasLabel, self.elegirTeclaTabular, '')

    def funcionAyuda(self):
        self.keysEvent = True


    def pasarAModoTeclado(self):
        self.modoInput = 'ModoTeclado'
        self.dic = self.diccionarioConfiguracion()
        self.ui.radioConfTecladoInput.setChecked(True)

    def pasarAModoMouse(self):
        self.modoInput = 'ModoMouse'
        self.ui.radioConfMouseInput.setChecked(True)
        self.modoADosTeclas()
        self.dic['confInputLabel'] = (self.ui.confControlesLabel, self.ventanaHijo, '')




if __name__ == "__main__":
    ThisOS = system()  # consultar Sistema operativo actual
    engine = pyttsx3.init()  # inicializar motor de voz
    voices = engine.getProperty('voices')
    if ThisOS == 'Windows':
        engine.setProperty('voice', voices[0].id)
    #          'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_ES-ES_PABLO_11.0')
    engine.setProperty('rate', 140)  # Aumentar velocidad 40%
    engine.setProperty('volume', 1.0)  # Poner el volumen al 100%: Minimo:0, Maximo: 1

    app = QApplication(sys.argv)
    app.setStyle('fusion')
    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 15, 15))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(142, 45, 197).lighter())
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtCore.Qt.darkGray)
    palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtCore.Qt.darkGray)
    app.setPalette(palette)
    ventana = Aplicacion()
    ventana.show
    ret = app.exec_()
    with open('arbol.pickle', 'wb') as f:  # se guarda el árbol
        pickle.dump(ventana.arboles, f)
    with open('eventos.pickle', 'wb') as f:  # se guardan los eventos del calendario
        pickle.dump(ventana.events, f)
    sys.exit(ret)