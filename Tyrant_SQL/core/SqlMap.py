# *-* coding: utf-8 *-*

from PySide import QtGui
from PySide import QtCore
from threading import Thread

from core.Resources import Resources
from core.RawAnalyzer import RawAnalyzer


class SqlMap(object):

    def __init__(self, parent=None):
        print('Created SQLMap manipulator')
        self.SQLFile = QtCore.QFile('SQL_Map/sqlmap.py')
        self.Wdg = parent
        self.RawAnalyzer = RawAnalyzer(self.Wdg)
        self.SqlMapExist()
        self.Resources = Resources()
        self.Python = self.Resources.getPref('Python')
        self.Proc = QtCore.QProcess()
        self.Target = ''
        self.CurrentDB = None
        self.isRunning = False
        self.TBName = ''

    def SqlMapExist(self):
        if not self.SQLFile.exists():
            Info = QtGui.QMessageBox()
            Info.information(self.Wdg, 'SQLMap ERROR',
                'Tyrant SQL cannot find sqlmap.py file')

    def IdentifyDB(self):
        if self.isRunning:
            self.Wdg.Info.appendPlainText('[WARINING]There is a process' +
                ' running. Please, wait.')
            return
        else:
            self.isRunning = True
        self.Target = self.Wdg.edtTarget.text()
        self.Wdg.Info.setPlainText('')
        self.Wdg.RawData.setPlainText('')
        self.Wdg.tabData.Clear()
        self.Wdg.Info.appendPlainText('[INFO]Starting the analyze.')
        argIdentify = ['SQL_Map/sqlmap.py', '-u', str(self.Target), '--dbs',
            '--answers=skip test=N, include all tests=N' +
            ', keep testing the=Y', '--batch']
        self.Run(argIdentify)
        self.Proc.finished.connect(self.getDBInfo)

    def Run(self, Arg):
        self.Th = Thread(self._Run(Arg))
        self.Th.start()

    #run the sqlmap
    def _Run(self, Arg):
        self.Proc.readyReadStandardOutput.connect(self.Output)
        self.Proc.start(self.Python, Arg,
                                    mode=QtCore.QIODevice.ReadWrite)

    #read the output and find the DBMS version and the databases
    def getDBInfo(self, Exit=None):
        self.isRunning = False
        self.Proc.finished.disconnect()
        if (Exit is None):
            Info = QtGui.QMessageBox()
            Info.information(self.Wdg, 'DB Analyzer', 'The databases was not \n'
             + 'analyzed. Please, restart the analyze.')
        elif Exit == 0:
            self.RawAnalyzer.getDBInfo()

    def Output(self):
        Out = (str(self.Proc.readAllStandardOutput()))
        if len(Out) > 1:
            self.Wdg.RawData.appendPlainText(Out)

    def getTables(self, DB, CurrentDB):
        if self.isRunning:
            self.Wdg.Info.appendPlainText('[WARNING]There is a process ' +
                'running. Please, wait.')
            return
        else:
            self.isRunning = True
        self.CurrentDB = CurrentDB
        self.Wdg.Info.appendPlainText('[INFO]Getting %s tables.Please, wait'
             % DB)
        self.DB = DB
        argTables = ['SQL_Map/sqlmap.py', '-u', str(self.Target), '-D', DB,
            '--tables', '--answers=do you want to use common table existence=N']
        self.Run(argTables)
        self.Proc.finished.connect(self.AnalyzeTables)

    def AnalyzeTables(self, Exit=None):
        self.isRunning = False
        self.Proc.finished.disconnect()
        if (Exit is None) | (Exit != 0):
            self.Wdg.Info.appendPlainText('[ERROR] The scanning stopped' +
                'incorretly. Restart the analyze')
        elif Exit == 0:
            self.RawAnalyzer.AnalyzeTables(self.DB, self.CurrentDB)

    def getTableContent(self, TB):
        self.TBName = str(TB.text(0))
        DB = str(TB.parent().text(0))
        if self.isRunning:
            self.Wdg.Info.appendPlainText('[WARNING]There is a process ' +
                'running.Please, wait.')
            return
        else:
            self.isRunning = True
        self.Wdg.Info.appendPlainText('[INFO]Getting table content, wait')
        argTBContent = ['SQL_Map/sqlmap.py', '-u', str(self.Target), '-D', DB,
            '-T', self.TBName, '--dump', '--answers=hashes to a temporary file=N' +
            ',dictionary-based attack=N']
        self.Run(argTBContent)
        self.Proc.finished.connect(self.AnalyzeTableContent)

    def AnalyzeTableContent(self, Exit=None):
        self.isRunning = False
        self.Proc.finished.disconnect()
        if (Exit is None) | (Exit != 0):
            self.Wdg.Info.appendPlainText('[ERROR] The scanning stopped' +
                'incorretly. Restart the analyze')
        elif Exit == 0:
            self.RawAnalyzer.getTBContent(self.TBName)
