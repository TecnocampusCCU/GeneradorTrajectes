# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeneradorTrajectes
                                 A QGIS plugin
 GeneradorTrajectes
                              -------------------
        begin                : 2018-06-01
        git sha              : $Format:%H$
        copyright            : (C) 2018 by CCU
        email                : jlopez@tecnocampus.cat
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import sys
import os
import processing
from os.path import expanduser
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QAction,QMessageBox,QTableWidgetItem, QApplication
from qgis.core import QgsMapLayer
from qgis.core import QgsDataSourceUri
from qgis.core import QgsVectorLayer
from qgis.core import QgsPointXY
from qgis.core import QgsReferencedPointXY
from qgis.core import QgsCoordinateReferenceSystem
from qgis.core import QgsField
from qgis.core import QgsWkbTypes 
from qgis.core import QgsFeatureRequest
from qgis.core import QgsFeature
from qgis.core import QgsFields
from qgis.core import QgsVectorFileWriter
from qgis.core import QgsVectorLayerExporter
from qgis.core import QgsGraduatedSymbolRenderer
from qgis.core import QgsCategorizedSymbolRenderer
from qgis.core import QgsGradientColorRamp
from qgis.core import QgsProject
from qgis.core import QgsRendererRange
from qgis.core import QgsSymbol
from qgis.core import QgsFillSymbol
from qgis.core import QgsLineSymbol
from qgis.core import QgsSymbolLayerRegistry
from qgis.core import QgsRandomColorRamp
from qgis.core import QgsRendererRangeLabelFormat
from qgis.core import QgsProject
from qgis.core import QgsLayerTreeLayer
from qgis.core import QgsRenderContext
from qgis.core import QgsPalLayerSettings
from qgis.core import QgsTextFormat
from qgis.core import QgsTextBufferSettings
from qgis.core import QgsVectorLayerSimpleLabeling
import psycopg2
import unicodedata
import datetime
import time
from qgis.utils import iface
from PyQt5.QtSql import *
import datetime
import time

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .GeneradorTrajectes_dialog import GeneradorTrajectesDialog
import os.path
from itertools import dropwhile
from _operator import itemgetter
"""
Variables globals per a la connexio
i per guardar el color dels botons
"""
Versio_modul="V_Q3.191128"
micolorArea = None
micolor = None
nomBD1=""
contra1=""
host1=""
port1=""
usuari1=""
schema=""
entitat_poi=""
Fitxer=""
Path_Inicial=expanduser("~")
cur=None
conn=None
progress=None
aux=False
lbl_Cost = ''

class GeneradorTrajectes:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'GeneradorTrajectes_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
                
        self.dlg = GeneradorTrajectesDialog()
        self.dlg.bt_sortir.clicked.connect(self.on_click_Sortir)
        self.dlg.bt_inici.clicked.connect(self.on_click_Inici)
        self.dlg.comboConnexio.currentIndexChanged.connect(self.on_Change_ComboConn)
        self.dlg.comboCost.currentIndexChanged.connect(self.changeComboCost)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&CCU')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'CCU')
        self.toolbar.setObjectName(u'Generador de Trajectes')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('GeneradorTrajectes', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/GeneradorTrajectes/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Generador Trajectes'),
            callback=self.run,
            parent=self.iface.mainWindow())
    
    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Generador de trajectes'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def on_click_Sortir(self):
        '''
        Tanca la finestra del plugin 
        '''
        self.estatInicial()
        self.dlg.close()

    def getConnections(self):
        """Aquesta funcio retorna les connexions que estan guardades en el projecte."""
        s = QSettings() 
        s.beginGroup("PostgreSQL/connections")
        currentConnections = s.childGroups()
        s.endGroup()
        return currentConnections
    
    def populateComboBox(self,combo,list,predef,sort):
        """Procediment per omplir el combo especificat amb la llista suministrada"""
        combo.blockSignals (True)
        combo.clear()
        model=QStandardItemModel(combo)
        predefInList = None
        for elem in list:
            try:
                item = QStandardItem(unicode(elem))
            except TypeError:
                item = QStandardItem(str(elem))
            model.appendRow(item)
            if elem == predef:
                predefInList = elem
        if sort:
            model.sort(0)
        combo.setModel(model)
        if predef != "":
            if predefInList:
                combo.setCurrentIndex(combo.findText(predefInList))
            else:
                combo.insertItem(0,predef)
                combo.setCurrentIndex(0)
        combo.blockSignals (False)

    def ompleCombos(self, combo, llista, predef, sort):
        """Aquesta funció omple els combos que li passem per paràmetres"""
        combo.blockSignals (True)
        combo.clear()
        model=QStandardItemModel(combo)
        predefInList = None
        for elem in llista:
            try:
                item = QStandardItem(unicode(elem[0]))
            except TypeError:
                item = QStandardItem(str(elem[0]))
            model.appendRow(item)
            if elem == predef:
                predefInList = elem
        combo.setModel(model)
        if predef != "":
            if predefInList:
                combo.setCurrentIndex(combo.findText(predefInList))
            else:
                combo.insertItem(0,predef)
                combo.setCurrentIndex(0)
        combo.blockSignals (False)
        
    def estatInicial(self):
        '''
        @param self:
        Resteja tots els valors per defecte del plugin: estat inicial.
        '''
        global aux
        global Versio_modul
        aux = False
        self.barraEstat_noConnectat()
        self.dlg.versio.setText(Versio_modul)
        self.dlg.comboCost.setCurrentIndex(0)
        self.dlg.chk_CostNusos.setEnabled(False)
        self.dlg.chk_CostNusos.setChecked(False)
        self.dlg.SB_camins.setValue(3)
        self.dlg.comboCapaDesti.clear()
        self.dlg.comboCapaOrigen.clear()
        self.dlg.txt_nomTaula.clear()
        self.dlg.txt_nomProximitat.clear()
        self.dlg.comboGraf.clear()
        self.dlg.text_info.setText('')
        self.dlg.progressBar.setValue(0)
        self.dlg.chk_Local.setChecked(True)
        self.dlg.chk_Local.setEnabled(False)

        
    
    def changeComboCost(self):
        """Aquesta funció controla el canvi d'opció del comboBox del mètode treball."""
        dist = u'Distancia'
        nom_metode=self.dlg.comboCost.currentText()
        if dist == nom_metode:
            self.dlg.chk_CostNusos.setEnabled(False)
            self.dlg.chk_CostNusos.setChecked(False)
            self.dlg.chk_Local.setChecked(True)
        else:
            self.dlg.chk_CostNusos.setEnabled(True)
            self.dlg.chk_Local.setChecked(False)
            
    def getLimit(self):
        '''
        Aquesta funció s'encarrega de obtenir el límit de camins que s'han de crear,
        ja que es pot donar el cas que N-camins si sigui major que nombre d'entitats de desti
        '''
        global cur
        global conn
        limitUsuari = self.dlg.SB_camins.value()
        count = 'select count(*) from "public".\"' + self.dlg.comboCapaDesti.currentText() + '\";'
        
        cur.execute(count)
        vect = cur.fetchall()
        
        if (limitUsuari > vect[0][0]):
            return vect[0][0]
        else:
            return limitUsuari
    
    def on_Change_ComboGraf(self, state):
        """
        En el moment en que es modifica la opcio escollida 
        del combo o desplegable de la capa de punts,
        automÃ ticament comprova els camps de la taula escollida.
        """
        try:
            capa=self.dlg.comboGraf.currentText()
            if capa != "":
                if capa != 'Selecciona una entitat':
                    if (self.grafValid(capa)):
                        pass
                    else:
                        QMessageBox.information(None, "Error", 'El graf seleccionat no té la capa de nusos corresponent.\nEscolliu un altre.')
        except Exception as ex:
            print ("Error Graf seleccionat")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            QMessageBox.information(None, "Error", "Error Graf seleccionat")
            conn.rollback()
            self.bar.clearWidgets()
            self.dlg.lblEstatConn.setText('Connectat')
            self.dlg.lblEstatConn.setStyleSheet('border:1px solid #000000; background-color: #7fff7f')
            return "ERROR"
    
    def controlErrorsInput(self):
        '''
        Aquesta funció s'encarrega de controlar que quan comenci el càlcul
        totes les entrades de dades estiguin omplertes i siguin correctes
        '''
        errors = []
        if self.dlg.comboConnexio.currentText() == u'Selecciona connexió':
            errors.append(u"No hi ha connexió")
        if self.dlg.comboCapaOrigen.currentText() == u'':
            errors.append(u'No hi ha cap capa d\'origen disponible')
        if self.dlg.comboCapaOrigen.currentText() == u'Selecciona una entitat':
            errors.append(u'No hi ha cap capa d\'origen seleccionada')
        if self.dlg.comboCapaDesti.currentText() == u'':
            errors.append(u'No hi ha cap capa de destí disponible')
        if self.dlg.comboCapaDesti.currentText() == u'Selecciona una entitat':
            errors.append(u'No hi ha cap capa de destí seleccionada')
        if self.dlg.txt_nomTaula.text() == u'':
            errors.append(u'No hi ha nom per la taula de destí')
        if self.dlg.txt_nomProximitat.text() == u'':
            errors.append(u'No hi ha nom per la taula de proximitat')
        if self.dlg.comboGraf.currentText() == 'Selecciona una entitat':
            errors.append("No hi ha seleccionada cap capa de xarxa")
        return errors
    
    
    def calculo_Local(self,network_lyr,uri2,start_point,end_lyr):
        #processing.algorithmHelp("native:shortestpathpointtolayer")
        parameters= {'INPUT':network_lyr,
                     'STRATEGY':0, 
                     'DIRECTION_FIELD': '',
                     'VALUE_FORWARD': '',
                     'VALUE_BACKWARD': '',
                     'VALUE_BOTH': '',
                     'DEFAULT_DIRECTION':2,
                     'SPEED_FIELD': '',
                     'DEFAULT_SPEED':1,
                     'TOLERANCE':0,
                     'START_POINT':start_point,
                     'END_POINTS':end_lyr,
                     'OUTPUT':'memory:'}
        
        resultado = processing.run('native:shortestpathpointtolayer',parameters)
    
        return resultado['OUTPUT']
    
    def getIndexNom(self,vlayer):
        fields = vlayer.fields()
        for x in range(len(fields)):
            if('Nom' in fields[x].displayName()):
                return x
        return -1
    
    def compararFeatures(self,featureA,featureB):
        if featureA["Carrer_Num_Bis"] > featureB["Carrer_Num_Bis"]:
            return 1
        elif featureA["Carrer_Num_Bis"] < featureB["Carrer_Num_Bis"]:
            return -1
        
        if featureA["cost"] > featureB["cost"]:
            return 1
        elif  featureA["cost"] < featureB["cost"]:
            return -1
        
        return 0
    
    '''
    # El mergeSort ha demostrado una mayor eficiencia que el quickSort.
    # A continuación queda planteada la función de quickSort por si hiciera falta recuperarla.    
    def quickSort(self,list):
        less = []
        equal = []
        greater = []
    
        if len(list) > 1:
            pivot = list[0]
            for feature in list:
                cmp = self.compararFeatures(feature,pivot)
                if (cmp==-1):
                    less.append(feature)
                elif (cmp==1):
                    greater.append(feature)
                else:
                    equal.append(feature)
            return self.quickSort(less)+equal+self.quickSort(greater)
        else:
            return list
    '''
    
    def mergeSort(self,list):
        if len(list)>1:
            mid = len(list)//2
            lefthalf = list[:mid]
            righthalf = list[mid:]
    
            self.mergeSort(lefthalf)
            self.mergeSort(righthalf)
    
            i=0
            j=0
            k=0
            while i < len(lefthalf) and j < len(righthalf):                
                if (self.compararFeatures(lefthalf[i],righthalf[j])==-1):
                    list[k]=lefthalf[i]
                    i=i+1
                else:
                    list[k]=righthalf[j]
                    j=j+1
                k=k+1
    
            while i < len(lefthalf):
                list[k]=lefthalf[i]
                i=i+1
                k=k+1
    
            while j < len(righthalf):
                list[k]=righthalf[j]
                j=j+1
                k=k+1
        return list  
                
    
    def on_click_Inici(self):
        #Inici de l'execució
        self.barraEstat_processant()
        self.dlg.text_info.clear()
        a=time.time()
        
        '''Control d'errors'''
        llistaErrors = self.controlErrorsInput()
        if len(llistaErrors) > 0:
            llista = u"Llista d'errors:\n\n"
            for i in range (0,len(llistaErrors)):
                llista += (u"- "+llistaErrors[i] + u'\n')
            QMessageBox.information(None, "Error", llista)
            self.barraEstat_connectat()
            return
        
        Fitxer=datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
        textBox = u'INICI DE LA CERCA DE CAMINS:\n'
        self.dlg.text_info.setText(textBox)
        self.MouText()
        QApplication.processEvents()      
        create = 'drop table if exists "GTT"."'+self.dlg.txt_nomTaula.text()+'";\n'
        create += 'CREATE TABLE "GTT"."'+self.dlg.txt_nomTaula.text()+'" (\n'
        create += "\t\"idInici\" int8,\n"
        create += "\tid int8,\n"
        create += "\tentitatid int8,\n"
        create += "\t\"NomEntitat\" varchar,\n"
        create += "\t\"the_geom\" geometry, \n"
        create += "\tagg_cost FLOAT);"
        try:
            cur.execute(create)
            conn.commit()
        except Exception as ex:
            print ("Error CREATE Taula de camins")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            QMessageBox.information(None, "Error", "Error CREATE Taula de camins")
            conn.rollback()
            self.eliminaTaulesCalcul(Fitxer)
            return
            
        sql_xarxa = 'drop table IF EXISTS "Xarxa_Prova";\n'
        sql_xarxa += 'create local temp table "Xarxa_Prova" as  (select * from "public"."'+self.dlg.comboGraf.currentText()+'");\n'
        if self.dlg.comboCost.currentText() == 'Distancia':
            sql_xarxa += 'update "Xarxa_Prova" set "cost"="LONGITUD_SEGMENT", "reverse_cost"="LONGITUD_SEGMENT";'
        else:
            if (self.dlg.chk_CostNusos.isChecked()):
                """Es suma al camp 'cost' i a 'reverse_cost' el valor dels semafors sempre i quan estigui la opció marcada"""
                sql_xarxa +='UPDATE "Xarxa_Prova" set "cost"="cost"+(\"Cost_Total_Semafor_Tram\"), \"reverse_cost\"=\"reverse_cost\"+(\"Cost_Total_Semafor_Tram\");\n'
        
        try:
            cur.execute(sql_xarxa)
            conn.commit()
        except Exception as ex:
            print ("Error CREATE Xarxa_Prova")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            QMessageBox.information(None, "Error", "Error CREATE Xarxa_Prova")
            conn.rollback()
            self.eliminaTaulesCalcul(Fitxer)
            return
            
        if self.dlg.comboCapaOrigen.currentText() != 'dintreilla':
            select = 'select "id" as "idInici" from "public"."'+self.dlg.comboCapaOrigen.currentText()+'" order by 1;'
        else:
            select = 'select "Carrer_Num_Bis" as "idInici" from "public"."'+self.dlg.comboCapaOrigen.currentText()+'" order by 1;'
            
        try:
            cur.execute(select)
            resultat = cur.fetchall()
        except Exception as ex:
            print ("Error SELECT inici")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            QMessageBox.information(None, "Error", "Error SELECT inici")
            conn.rollback()
            self.eliminaTaulesCalcul(Fitxer)
            return
            
            
            
        '''Cálculo local'''
        if(self.dlg.chk_Local.isChecked()):
            uri = QgsDataSourceUri()
            try:
                uri.setConnection(host1,port1,nomBD1,usuari1,contra1)
            except:
                print ("Error a la connexio")
                
            QApplication.processEvents()
            sql_origen = 'SELECT * FROM "public".\"' + self.dlg.comboCapaDesti.currentText() + '\"'
            QApplication.processEvents()
            uri.setDataSource("","("+sql_origen+")","geom","","id")
            QApplication.processEvents()
            start_lyr = QgsVectorLayer(uri.uri(False), "origen", "postgres")
            QApplication.processEvents()
            
            sql_desti = 'SELECT * FROM "public".\"' + self.dlg.comboCapaOrigen.currentText() + '\"'
            QApplication.processEvents()
            uri.setDataSource("","("+sql_desti+")","geom","","id")
            QApplication.processEvents()
            end_lyr = QgsVectorLayer(uri.uri(False), "desti", "postgres")
            QApplication.processEvents()
            
            sql_xarxa='SELECT * FROM "public".\"'+self.dlg.comboGraf.currentText()+'\"'
            QApplication.processEvents()
            uri.setDataSource("","("+sql_xarxa+")","the_geom","","id")
            QApplication.processEvents()
            network_lyr = QgsVectorLayer(uri.uri(False), "xarxa", "postgres")
            QApplication.processEvents()
            
            
            
            crs=start_lyr.sourceCrs()
            if(crs.authid() != self.iface.mapCanvas().mapSettings().destinationCrs().authid()):
                QMessageBox.information(None, "Error", "\nEls CRS no coincideixen:\n-CRS del projecte: "+self.iface.mapCanvas().mapSettings().destinationCrs().authid()+"\n-CRS de la capa dels punts d'origen: "+crs.authid())
                self.barraEstat_connectat()
                conn.rollback()
                self.eliminaTaulesCalcul(Fitxer)
                self.dlg.text_info.setText('')
                return
            #print(self.iface.mapCanvas().mapSettings().destinationCrs().authid())# == EPSG:25831
            valorProgreso = 0
            self.dlg.progressBar.setValue(valorProgreso)
            QApplication.processEvents()
            
            features = start_lyr.getFeatures()            
            listVlayers = []

            incremento = 45/start_lyr.featureCount()
            x=0
            for feature in features:
                Hora=datetime.datetime.now().strftime("%H:%M:%S:%f")
                textBox += u'CAMÍ Nº ' + str(x+1) + u': ' + Hora + u'\n'
                self.dlg.text_info.setText(textBox)
                self.MouText()
                
                valorProgreso+=incremento
                self.dlg.progressBar.setValue(round(valorProgreso))
                QApplication.processEvents()
                x=x+1
                
                
                QApplication.processEvents()
                point = feature.geometry().asPoint()
                referencedPoint = QgsReferencedPointXY(point,crs)
                #coordenadas = str(point.x())+','+str(point.y())+" ["+str(crs.authid())+"]"
                #coordenadas = str(point.x())+','+str(point.y())+" [EPSG:25831]"
                #print("Point: "+coordenadas)
                QApplication.processEvents()

                listVlayers.append(self.calculo_Local(network_lyr, uri, referencedPoint, end_lyr))
                
                ultimoIndex = len(listVlayers)-1
                
                listVlayers[ultimoIndex].startEditing()
                listVlayers[ultimoIndex].addAttribute(QgsField('Nom', QVariant.Int))
                
                itfeature = listVlayers[ultimoIndex].getFeatures()
                for f in itfeature:
                    listVlayers[ultimoIndex].changeAttributeValue(f.id(),self.getIndexNom(listVlayers[ultimoIndex]),feature[self.getIndexNom(start_lyr)])
                listVlayers[ultimoIndex].commitChanges()
            
                

            
            '''Unificación de todos los resultados en una única lista'''
            listFeaturesAllVlayers = []
            for x in range(len(listVlayers)):
                features = listVlayers[x].getFeatures()
                for feature in features:
                    listFeaturesAllVlayers.append(feature)
            
            
            
            '''Ordenación del resultado en función de su nombre y coste'''
            textBox += u'Ordenant resultat...\n'
            self.dlg.text_info.setText(textBox)
            self.MouText()
            QApplication.processEvents()
            valorProgreso = 50
            self.dlg.progressBar.setValue(valorProgreso)
            QApplication.processEvents()
            
            try: # Ordenación rápida pero con riesgo de excepción
                def takeCost(feature):
                    return feature["cost"]
                
                def takeCarrer_Num_Bis(feature):
                    return feature["Carrer_Num_Bis"]
                
                QApplication.processEvents()
                listFeaturesAllVlayers.sort(key=takeCost)
                QApplication.processEvents()
                listFeaturesAllVlayers.sort(key=takeCarrer_Num_Bis)
                
            except: # Ordenación lenta pero segura
                print("Error ordenación: "+str(listFeaturesAllVlayers[0]["Carrer_Num_Bis"])+', '+str(listFeaturesAllVlayers[0]["cost"]))
                try:
                    listFeaturesAllVlayers = self.mergeSort(listFeaturesAllVlayers)
                except Exception as ex:
                    print ("Error ordenació")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error ordenació.\n Reinicia el mòdul i probablement s'hagi solucionat quan ho tornis a executar.")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
               
            
            '''Añadir a una lista el número de features indicadas por el usuario con "limit"'''
            try:    
                limit = self.getLimit()
            except Exception as ex:
                print ("Error getLimit")
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                QMessageBox.information(None, "Error", "Error getLimit")
                conn.rollback()
                self.eliminaTaulesCalcul(Fitxer)
                return
            listResultadoFinal = []
            nomAux = None
            for x in range(len(listFeaturesAllVlayers)):
                if(nomAux != listFeaturesAllVlayers[x]["Carrer_Num_Bis"]):
                    nomAux = listFeaturesAllVlayers[x]["Carrer_Num_Bis"]
                    for i in range(limit):
                        listResultadoFinal.append(listFeaturesAllVlayers[x+i])
                
           
            '''Creación de Taula de camins'''  
            textBox += u'Generant taula de camins...\n'
            self.dlg.text_info.setText(textBox)
            self.MouText()            
            
            try:                
                incremento = 30/len(listResultadoFinal)
                LayerCamins=QgsVectorLayer("LineString?crs="+listVlayers[1].crs().authid(), "temp", "memory");
                pr = LayerCamins.dataProvider()
                camps=[]
                fields = QgsFields()
                fields.append(QgsField("id",QVariant.Int))
                fields.append(QgsField("FromStop", QVariant.String))
                fields.append(QgsField("ToStop", QVariant.String))
                fields.append(QgsField("CAMI", QVariant.Double))
                #fields.append(QgsField("ID1", QVariant.Int))
                for camp in fields:
                    camps.append(camp)
                pr.addAttributes(camps)
                LayerCamins.updateFields()
                list_feat=[]

                for x in range (len(listResultadoFinal)):
                    feat = QgsFeature()
                    feat.setFields(fields)
                    feat.setGeometry(listResultadoFinal[x].geometry())
                    feat.setAttributes([(x+1),str(listResultadoFinal[x]["Carrer_Num_Bis"]),str(listResultadoFinal[x]["Nom"]),round(listResultadoFinal[x]["cost"]),(x+1)])
                    list_feat.append(feat)
                    valorProgreso+=incremento
                    self.dlg.progressBar.setValue(round(valorProgreso))
                    QApplication.processEvents()
                pr.addFeatures(list_feat)
                LayerCamins.commitChanges()
                drop = 'DROP TABLE IF EXISTS "GTT".\"'+self.dlg.txt_nomTaula.text()+'\";'
                try:
                    cur.execute(drop)
                    conn.commit()
                except Exception as ex:
                    print ("Error DROP Taula de camins")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error DROP Taula de camins")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
            
                error = QgsVectorLayerExporter.exportLayer(LayerCamins, 'table="GTT"."'+self.dlg.txt_nomTaula.text()+'" (geom) '+uri.connectionInfo(), "postgres", listVlayers[1].crs(), False)
                if error[0] != 0:
                    iface.messageBar().pushMessage(u'Error', error[1])
                

            except:
                print ("Creació de taula "+self.dlg.txt_nomTaula.text()+" ERROR")
                
                
            '''Creación de Taula de proximitat'''                
            textBox += u'Generant taula de proximitat...\n'
            self.dlg.text_info.setText(textBox)
            self.MouText()
            valorProgreso = 90
            self.dlg.progressBar.setValue(valorProgreso)
            QApplication.processEvents()
            
            
            drop = 'DROP TABLE IF EXISTS "GTT".\"'+self.dlg.txt_nomProximitat.text()+'\";'
            try:
                cur.execute(drop)
                conn.commit()
            except Exception as ex:
                print ("Error CREATE Taula de proximitat")
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                QMessageBox.information(None, "Error", "Error CREATE Taula de proximitat")
                conn.rollback()
                self.eliminaTaulesCalcul(Fitxer)
                return
            
            create = 'CREATE TABLE "GTT".\"'+self.dlg.txt_nomProximitat.text()+'\" (\n'
            create += "\t\"Carrer_Num_Bis\" varchar,\n"

            for x in range (limit):
                create += "\t\"nEB"+str(x+1)+"\" varchar,\n"
                if(x==limit-1):
                    create += "\t\"dm"+str(x+1)+"\" int8);"
                else:
                    create += "\t\"dm"+str(x+1)+"\" int8, \n"                
            
            try:
                cur.execute(create)
                conn.commit()  
            except Exception as ex:
                print ("Error CREATE Taula de proximitat")
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                QMessageBox.information(None, "Error", "Error CREATE Taula de proximitat")
                conn.rollback()
                self.eliminaTaulesCalcul(Fitxer)
                return
            '''Inserción de los datos en Taula de proximitat'''             
            try:
                x=0
                while (x<len(listResultadoFinal)):
                    insert = 'INSERT INTO "GTT".\"'+self.dlg.txt_nomProximitat.text()+'\" (\"Carrer_Num_Bis\"'
                    for y in range (limit):
                        insert += ', \"nEB'+str(y+1)+'\"'
                        insert += ', \"dm'+str(y+1)+'\"'
                    insert += ') VALUES (\''+str(listResultadoFinal[x]["Carrer_Num_Bis"])+'\''
                    
                    y=0
                    while(x<len(listResultadoFinal) and y<limit):
                        nomString = str(listResultadoFinal[x]["Nom"])
                        nomString = nomString.replace("'", "''")
                        insert += ', \''+nomString+'\', '+str(round(listResultadoFinal[x]["cost"]))                        
                        x+=1
                        y+=1
                    insert += ');\n'
                    QApplication.processEvents()                    
                    cur.execute(insert)
            except Exception as ex:
                print ("Error INSERT Taula de proximitat")
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                QMessageBox.information(None, "Error", "Error INSERT Taula de proximitat")
                conn.rollback()
                self.eliminaTaulesCalcul(Fitxer)
                return
            self.dlg.progressBar.setValue(100)
            QApplication.processEvents()      
            
        else:    
            #Cálculo en el servidor pendiente de implementar
            for i in range(0,len(resultat)):
                idInici = resultat[i][0]
                Hora=datetime.datetime.now().strftime("%H:%M:%S:%f")
                textBox += u'CAMÍ Nº ' + str(i+1) + u': ' + Hora + u'\n'
                self.dlg.text_info.setText(textBox)
                self.MouText()
                QApplication.processEvents()
                
                
                drop = 'DROP TABLE IF EXISTS NPoints_'+Fitxer+';'
                try:
                    cur.execute(drop)
                    conn.commit()
                except Exception as ex:
                    print ("Error DROP NPoints")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error DROP NPoints")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                
                create = 'CREATE TABLE NPoints_'+Fitxer+' (\n'
                create += "\tpid    serial primary key,\n"
                create += "\tthe_geom geometry,\n"
                create += "\tentitatID int8,\n"
                create += "\tedge_id BIGINT,\n"
                create += "\tfraction FLOAT,\n"
                create += "\tnewPoint geometry);"
                try:
                    cur.execute(create)
                    conn.commit()
                except Exception as ex:
                    print ("Error CREATE NPoints")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error CREATE NPoints")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                    
                '''
                #    4.2 S'afegeixen els punts necessaris a la taula
                '''
                if self.dlg.comboCapaOrigen.currentText() != 'dinterilla':             
                    insert = 'INSERT INTO NPoints_'+Fitxer+' (entitatID,the_geom) (SELECT 0, ST_Centroid("geom") the_geom from "'+self.dlg.comboCapaOrigen.currentText()+'" where "id" = \''+str(idInici)+'\');\n'
                else:
                    insert = 'INSERT INTO NPoints_'+Fitxer+' (entitatID,the_geom) (SELECT 0, ST_Centroid("geom") the_geom from "'+self.dlg.comboCapaOrigen.currentText()+'" where "Carrer_Num_Bis" = \''+str(idInici)+'\');\n'
                insert += 'INSERT INTO NPoints_'+Fitxer+' (entitatID, the_geom) (SELECT "id", ST_Centroid("geom") the_geom from "' + self.dlg.comboCapaDesti.currentText() + '" order by "id");'
                try:
                    cur.execute(insert)
                    conn.commit()
                except Exception as ex:
                    print ("Error INSERT NPoints")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error INSERT NPoints")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                
                '''
                #    4.3 S'afegeix el id del tram al que estan més próxims els punts, els punts projectats sobre el graf 
                #    i la fracció de segment a on estant 
                '''
                update = 'UPDATE NPoints_'+Fitxer+' set "edge_id"=tram_proper."tram_id" from (SELECT distinct on(Poi."pid") Poi."pid" As Punt_id,Sg."id" as Tram_id, ST_Distance(Sg."the_geom",Poi."the_geom")  as dist FROM "Xarxa_Prova" as Sg,NPoints_'+Fitxer+' AS Poi ORDER BY  Poi."pid",ST_Distance(Sg."the_geom",Poi."the_geom"),Sg."id") tram_proper where NPoints_'+Fitxer+'."pid"=tram_proper."punt_id";\n'
                update += 'UPDATE NPoints_'+Fitxer+' SET fraction = ST_LineLocatePoint(e.the_geom, NPoints_'+Fitxer+'.the_geom),newPoint = ST_LineInterpolatePoint(e."the_geom", ST_LineLocatePoint(e."the_geom", NPoints_'+Fitxer+'."the_geom")) FROM "Xarxa_Prova" AS e WHERE NPoints_'+Fitxer+'."edge_id" = e."id";\n'
                try:
                    cur.execute(update)
                    conn.commit()
                except Exception as ex:
                    print ("Error UPDATE NPoints")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error UPDATE NPoints")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                    
                '''
                #    4.4 Es fa una consulta per poder generar una sentencia SQL que faci la cerca de
                #    tots els camins més curts a tots el punts necessaris
                '''
                select = 'select * from NPoints_'+Fitxer+' order by pid'
                try:
                    cur.execute(select)
                    vec = cur.fetchall()
                except Exception as ex:
                    print ("Error SELECT NPoints")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error SELECT NPoints")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return 
                create = 'create local temp table "Resultat" as SELECT * FROM (\n'
                for x in range (0,len(vec)):
                    if x < len(vec) and x >= 2:
                        create += 'UNION\n'
                    if x != 0:
                        if vec[x][4] == 1.0 or vec[x][4] == 0.0:
                            create += 'select '+ str(x) +' as routeID,'+ str(vec[x][2]) +' as entitatID, * from pgr_withPointsKSP(\'SELECT id, source, target, cost, reverse_cost FROM "Xarxa_Prova" ORDER BY id\',\'SELECT pid, edge_id, fraction from NPoints_'+Fitxer+'\',-1,' + str(vec[x][2])+',1)\n'
                        else:
                            create += 'select '+ str(x) +' as routeID,'+ str(vec[x][2]) +' as entitatID, * from pgr_withPointsKSP(\'SELECT id, source, target, cost, reverse_cost FROM "Xarxa_Prova" ORDER BY id\',\'SELECT pid, edge_id, fraction from NPoints_'+Fitxer+'\',-1,-' + str(vec[x][0]) +',1)\n'
                create += ')QW ORDER BY routeID, seq;'
                
                '''
                #    4.5 Selecció del nom del camp on figura el Nom de l'entitat de destí
                '''
                try:
                    select="SELECT column_name FROM information_schema.columns WHERE table_schema = 'public' and table_name = '"+ self.dlg.comboCapaDesti.currentText() +"'and column_name like 'Nom%';"
                    cur.execute(select)
                    nomCamp = cur.fetchall()
                except Exception as ex:
                    print ("Error SELECT camp nom")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error SELECT camp nom")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
    
                '''
                #    5. Destrucció i creació de la taula on figuren tots els camins possibles
                '''
                drop = 'DROP TABLE IF EXISTS "Resultat";'
                try:
                    cur.execute(drop)
                    conn.commit()
                except Exception as ex:
                    print ("Error DROP Resultat")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error DROP Resultat")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                
                try:
                    cur.execute(create)
                    conn.commit()
                except Exception as ex:
                    print ("Error CREATE Resultat")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error CREATE Resultat")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                
                '''
                #    6. Destrucció i creació de la taula "Segments finals" on figuren tots els camins possibles que són prinicipi i/o final
                '''
        
                drop = "DROP TABLE IF EXISTS \"SegmentsFinals\";"
                try:
                    cur.execute(drop)
                    conn.commit()
                except Exception as ex:
                    print ("Error DROP SegmentsFinals")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error DROP SegmentsFinals")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                
                create = "CREATE local temp TABLE \"SegmentsFinals\" (\n"
                create += "\trouteid int8,\n"
                create += "\tedge int8,\n"
                create += "\t\"edgeAnt\" int8,\n"
                create += "\tfraction FLOAT,\n"
                create += "\t\"ordreTram\" int8,\n"
                create += "\t\"cutEdge\" geometry);"
                try:
                    cur.execute(create)
                    conn.commit()
                except Exception as ex:
                    print ("Error CREATE SegmentsFinals")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error CREATE SegmentsFinals")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                '''
                #    6.1 Query per seleccionar els segments que són inici i final
                '''
                select = 'select routeid, node, edge from "Resultat" order by routeid, path_seq;'
                try:
                    cur.execute(select)
                    vec = cur.fetchall()
                    conn.commit()
                except Exception as ex:
                    print ("Error SELECT Resultat")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error SELECT Resultat")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                insert = ''
                for x in range (len(vec)):
                    if vec[x][1] < 0:
                        if vec[x][1] != -1:
                            insert += 'INSERT INTO "SegmentsFinals" (routeid, edge, "edgeAnt", "ordreTram") VALUES (' + str(vec[x][0]) + ', ' + str(vec[x-1][2]) + ', ' + str(vec[x-2][2]) + ', ' + str(2) +');\n'
                        else:
                            insert += 'INSERT INTO "SegmentsFinals" (routeid, edge, "edgeAnt", "ordreTram") VALUES (' + str(vec[x][0]) + ', ' + str(vec[x][2]) + ', ' + str(vec[x+1][2]) + ', ' + str(1) + ');\n'
                try:
                    cur.execute(insert)
                    conn.commit()
                except Exception as ex:
                    print ("Error INSERT SegmentsFinals")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error INSERT SegmentsFinals")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                    
                '''
                #    6.2 UPDATE per poder afegir la fracció en què es troba el punt sobre el segment
                '''
                select = 'select routeid, edge, "ordreTram" from "SegmentsFinals" order by routeid, "ordreTram";'
                try:
                    cur.execute(select)
                    vec = cur.fetchall()
                    conn.commit()
                except Exception as ex:
                    print ("Error SELECT Resultat 2")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error SELECT Resultat 2")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
        
                update = ''
                for x in range(len(vec)):
                    ruta = vec[x][0]
                    edge = vec[x][1]
                    ordre = vec[x][2]
                    if ordre == 1:
                        update += 'update "SegmentsFinals" s set fraction = n.fraction from NPoints_'+Fitxer+' n where n.edge_id = '+str(edge)+' and s.edge ='+str(edge)+' and s."ordreTram" = 1 and s.routeid = '+str(ruta)+' and n.entitatid = 0;\n'
                    else:
                        update += 'update "SegmentsFinals" s set fraction = n.fraction from NPoints_'+Fitxer+' n where n.edge_id = '+str(edge)+' and s.edge ='+str(edge)+' and s."ordreTram" = 2 and s.routeid = '+str(ruta)+' and n.pid = '+str(ruta+1)+';\n'
        
                try:
                    cur.execute(update)
                    conn.commit()
                except Exception as ex:
                    print ("Error UPDATE SegmentsFinals")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error UPDATE SegmentsFinals")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                    
                '''
                #    6.3 Query per escollir i afegir el tros de tram que correspon a cada inici i final 
                #    Posteriorment es fa un UPDATE del camp de geometria de la taula 'SegmentsFinals' amb els trams ja retallats
                '''
                select = 'select * from "SegmentsFinals" order by routeid;'
                try:
                    cur.execute(select)
                    vec = cur.fetchall()
                    conn.commit()
                except Exception as ex:
                    print ("Error SELECT SegmentsFinals")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error SELECT SegmentsFinals")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                updateSegment = ''
                for x in range(len(vec)):
                    ordre = vec[x][4]
                    fraction = vec[x][3]
                    edgeAnt = vec[x][2]
                    edge = vec[x][1]
                    selectTouch = 'SELECT ST_Touches((select ST_Line_Substring("Xarxa_Prova"."the_geom",0,'+str(fraction)+') as geom from "Xarxa_Prova" where "id"='+str(edge)+'),(select the_geom as  geom from "Xarxa_Prova" where "id"='+str(edgeAnt)+'));'
                    try:
                        cur.execute(selectTouch)
                        resposta = cur.fetchall()
                        conn.commit()
                    except Exception as ex:
                        print ("Error SELECT Touch")
                        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                        message = template.format(type(ex).__name__, ex.args)
                        print (message)
                        QMessageBox.information(None, "Error", "Error SELECT Touch")
                        conn.rollback()
                        self.eliminaTaulesCalcul(Fitxer)
                        return
                    if edgeAnt != -1:   
                        if resposta[0][0]:
                            updateSegment += 'update "SegmentsFinals" sf set "cutEdge" = ST_Line_Substring(s."the_geom",0,'+str(fraction)+') from "Xarxa_Prova" s where sf."edge"='+str(edge)+' and s."id"='+str(edge)+' and sf."routeid" = '+str(vec[x][0])+';\n'
                        else:
                            updateSegment += 'update "SegmentsFinals" sf set "cutEdge" = ST_Line_Substring(s."the_geom",'+str(fraction)+',1) from "Xarxa_Prova" s where sf."edge"='+str(edge)+' and s."id"='+str(edge)+' and sf."routeid" = '+str(vec[x][0])+';\n'
                    else:
                        if ordre == 1:
                            fractForward = vec[x+1][3]
                        else:
                            fractForward = vec[x-1][3]
                        if fraction >= fractForward:
                            updateSegment += 'update "SegmentsFinals" sf set "cutEdge" = ST_Line_Substring(s."the_geom",'+str(fractForward)+','+str(fraction)+') from "Xarxa_Prova" s where sf."ordreTram" = '+ str(ordre)+' and sf."edge"='+str(edge)+' and s."id"='+str(edge)+' and sf."routeid" = '+str(vec[x][0])+';\n'
                        else:
                            updateSegment += 'update "SegmentsFinals" sf set "cutEdge" = ST_Line_Substring(s."the_geom",'+str(fraction)+','+str(fractForward)+') from "Xarxa_Prova" s where sf."ordreTram" = '+ str(ordre)+' and sf."edge"='+str(edge)+' and s."id"='+str(edge)+' and sf."routeid" = '+str(vec[x][0])+';\n'
                                
        
                try:
                    cur.execute(updateSegment)
                    conn.commit()
                except Exception as ex:
                    print ("Error UPDATE SegmentsFinals Geometries")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error UPDATE SegmentsFinals Geometries")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                
                '''
                #    7. S'afegeix i s'actualitza el camp de geometria a la taula resultat
                '''
                alter = 'ALTER TABLE "Resultat" ADD COLUMN newEdge geometry;\n'
                alter += 'update "Resultat" r set newedge = s.the_geom from "Xarxa_Prova" s where s.id = r.edge;'
        
                try:
                    cur.execute(alter)
                    conn.commit()
                except Exception as ex:
                    print ("Error ALTER UPDATE Resultat")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error ALTER UPDATE Resultat")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
        
                '''
                #    8. UPDATE per actualitzar els trams retallats a la taula 'Resultat'
                '''
                update = 'update "Resultat" r set newedge = s."cutEdge" from "SegmentsFinals" s where s."routeid" = r.routeid and s.edge = r.edge;'
                try:
                    cur.execute(update)
                    conn.commit()
                except Exception as ex:
                    print ("Error UPDATE Resultat")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error UPDATE Resultat")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                
                '''
                #    9. Seleccio dels N-camins més proxims al domicili indicat per tal de presentar els resultats
                #    en el quadre de la interficie del modul
                '''
                try:
                    limit = self.getLimit()
                except Exception as ex:
                    print ("Error getLimit")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error getLimit")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                select = 'select e."'+ nomCamp[0][0] +'" as NomEntitat, r.agg_cost as Cost, r.entitatID from "Resultat" r  join "' + self.dlg.comboCapaDesti.currentText() + '" e on r.entitatID = e.id where  r.edge = -1 order by 2 asc limit ' + str(limit) + ';'
                try:
                    cur.execute(select)
                    vec = cur.fetchall()
                    conn.commit()
                except Exception as ex:
                    print ("Error SELECT Resultat")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error SELECT Resultat")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                    
                '''
                #    10. Drop i Create d'una sentencia SQL per obtenir els trams junts per a cada camí optim escollit
                #     i al mateix temps, s'afegeix la informació obtinguda en el select anterior.
                '''
                createTrams = 'drop table if exists "NousTrams_'+Fitxer+'";\n'
                createTrams += 'create table "NousTrams_'+Fitxer+'" as select * from (\n' 
    
                for x in range (0,len(vec)):
    
                    if x < len(vec) and x >= 1:
                        createTrams += 'UNION\n'
                        
                    createTrams += 'select entitatid, \'' + unicode(vec[x][0].replace("'","''")) +'\' as "NomEntitatDesti" ,'+str(round(vec[x][1]))+' as agg_cost, ST_Union(newedge) as the_geom from "Resultat" where entitatid = '+str(vec[x][2])+' group by entitatid\n'
                
                createTrams += ")total order by agg_cost asc;"
                QApplication.processEvents()
                
                '''
                #    10.1 Execució de la sentencia SQL per crear la taula amb els trams
                '''
                try:
                    cur.execute(createTrams)
                    conn.commit()
                except Exception as ex:
                    print ("Error CREATE NousTrams")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error CREATE NousTrams")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
                    
    
                insert = 'INSERT INTO "ResultatFinal" ("idInici", id, entitatid, "NomEntitat",agg_cost, the_geom) (select \''+ str(idInici) +'\' as "idInici", row_number() OVER() AS "id", * from "NousTrams_'+Fitxer+'");'
                
                try:
                    cur.execute(insert)
                    conn.commit()
                except Exception as ex:
                    print ("Error INSERT ResultatFinal")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print (message)
                    QMessageBox.information(None, "Error", "Error INSERT ResultatFinal")
                    conn.rollback()
                    self.eliminaTaulesCalcul(Fitxer)
                    return
        
        
        self.eliminaTaulesCalcul(Fitxer)
            
        textBox += u'FINAL DE LA CERCA\n'
        textBox += u'Durada: '+str(int(time.time()-a))+' s.\n'
        self.dlg.text_info.setText(textBox)
        self.MouText()
        
        QApplication.processEvents()
        self.barraEstat_connectat()
                
                
    def eliminaTaulesCalcul(self,Fitxer):
        global cur
        global conn
        try:
            cur.execute('DROP TABLE IF EXISTS "Resultat";\n') 
            cur.execute('DROP TABLE IF EXISTS "NousTrams_'+Fitxer+'";\n')
            cur.execute('DROP TABLE IF EXISTS NPoints_'+Fitxer+';\n')
            cur.execute('DROP TABLE IF EXISTS "SegmentsFinals";\n')
            cur.execute('DROP TABLE IF EXISTS "Xarxa_Prova";\n')
            
            conn.commit()
        except Exception as ex:
            print("Error DROP final")
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(ex).__name__, ex.args)
            print (message)
            QMessageBox.information(None, "Error", "Error DROP final")
            conn.rollback()
            self.bar.clearWidgets()
            self.dlg.Progres.setValue(0)
            self.dlg.Progres.setVisible(False)
            self.dlg.lblEstatConn.setText('Connectat')
            self.dlg.lblEstatConn.setStyleSheet('border:1px solid #000000; background-color: #7fff7f')
            
                        
    
    def MouText(self):
        newCursor=QTextCursor(self.dlg.text_info.document())
        newCursor.movePosition(QTextCursor.End)
        self.dlg.text_info.setTextCursor(newCursor)
        
        
    def on_Change_ComboConn(self):
        """
        En el moment en que es modifica la opcio escollida 
        del combo o desplegable de les connexions,
        automàticament comprova si es pot establir
        connexió amb la bbdd seleccionada.
        """
        global aux
        global nomBD1
        global contra1
        global host1
        global port1
        global usuari1
        global schema
        global cur
        global conn
        s = QSettings()
        select = 'Selecciona connexió'
        self.dlg.comboCapaDesti.clear()
        self.dlg.comboCapaOrigen.clear()
        self.dlg.comboGraf.clear()
        nom_conn=self.dlg.comboConnexio.currentText()
        if nom_conn != select:
            aux = True
            s.beginGroup("PostgreSQL/connections/"+nom_conn)
            currentKeys = s.childKeys()
            
            nomBD1 = s.value("database", "" )
            contra1 = s.value("password", "" )
            host1 = s.value("host", "" )
            port1 = s.value("port", "" )
            usuari1 = s.value("username", "" )
            schema= 'public'
            
            self.barraEstat_connectant()
            self.dlg.lblEstatConn.setAutoFillBackground(True)
            QApplication.processEvents()

            #Connexio
            nomBD = nomBD1.encode('ascii','ignore')
            usuari = usuari1.encode('ascii','ignore')
            servidor = host1.encode('ascii','ignore')     
            contrasenya = contra1.encode('ascii','ignore')
            try:
                estructura = "dbname='"+ nomBD.decode("utf-8") + "' user='" + usuari.decode("utf-8") +"' host='" + servidor.decode("utf-8") +"' password='" + contrasenya.decode("utf-8") + "'"# schema='"+schema+"'"
                conn = psycopg2.connect(estructura)
                self.barraEstat_connectat()
                cur = conn.cursor()
                
                sql = "select distinct(g.f_table_name) from geometry_columns g join information_schema.columns c on g.f_table_name = c.table_name where g.type = 'POINT' and g.f_table_schema ='public' order by 1"
                cur.execute(sql)
                llista = cur.fetchall()
                self.ompleCombos(self.dlg.comboCapaOrigen, llista, u'Selecciona una entitat', True)
                
                sql = "select g.f_table_name from geometry_columns g join information_schema.columns c on g.f_table_name = c.table_name where g.type = 'POINT' and g.f_table_schema ='public' and c.table_schema ='public' and c.column_name like 'Nom%'order by 1"
                cur.execute(sql)
                llista = cur.fetchall()
                self.ompleCombos(self.dlg.comboCapaDesti, llista, u'Selecciona una entitat', True)
                
                sql2 = "select f_table_name from geometry_columns where ((type = 'MULTILINESTRING' or type = 'LINESTRING') and f_table_schema ='public') order by 1"
                cur.execute(sql2)
                llista2 = cur.fetchall()
                self.ompleCombos(self.dlg.comboGraf, llista2, 'Selecciona una entitat', True)
                
            except Exception as ex:
                self.dlg.lblEstatConn.setStyleSheet('border:1px solid #000000; background-color: #ff7f7f')
                self.dlg.lblEstatConn.setText(u'Error: Hi ha algun camp erroni.')
                print ("I am unable to connect to the database")
                template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                message = template.format(type(ex).__name__, ex.args)
                print (message)
                QMessageBox.information(None, "Error", "Error connexio")
                return
           
        else:
            aux = False
            self.barraEstat_noConnectat()
    
    def barraEstat_processant(self):
        '''Aquesta funció canvia l'aparença de la barra inferior a "Processant"'''
        self.dlg.lblEstatConn.setStyleSheet('border:1px solid #000000; background-color: rgb(255, 125, 155)')
        self.dlg.lblEstatConn.setText(u"Processant...")
        QApplication.processEvents()
        
    def barraEstat_noConnectat(self):
        '''Aquesta funció canvia l'aparença de la barra inferior a "No connectat"'''
        self.dlg.lblEstatConn.setStyleSheet('border:1px solid #000000; background-color: #FFFFFF')
        self.dlg.lblEstatConn.setText(u'No connectat')
        QApplication.processEvents()
        
    def barraEstat_connectat(self):
        '''Aquesta funció canvia l'aparença de la barra inferior a "Connectat"'''
        self.dlg.lblEstatConn.setStyleSheet('border:1px solid #000000; background-color: #7fff7f')
        self.dlg.lblEstatConn.setText(u'Connectat')
        QApplication.processEvents()
        
    def barraEstat_connectant(self):
        '''Aquesta funció canvia l'aparença de la barra inferior a "Connectant"'''
        self.dlg.lblEstatConn.setStyleSheet('border:1px solid #000000; background-color: #ffff7f')
        self.dlg.lblEstatConn.setText(u'Connectant...')
        QApplication.processEvents()


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.estatInicial()
        self.dlg.show()
        conn=self.getConnections()
        self.populateComboBox(self.dlg.comboConnexio ,conn,u'Selecciona connexió',True)

        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
