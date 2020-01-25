import os
import argparse
import logging
import csv as cs
import hashlib
import time

log = logging.getLogger('main._pfish')

#
#Nombre:
#           ParseoArgumentos
#
#Descripcion:
#           Procesa y valida los argumentos de terminal usando una libreria estandar
#
#Acciones:
#           Implementa la libreria estandar para establecer los argumentos y sus reglas
#           Utiliza variables globales (gl_args) para almacenar los argumentos
#
def ParseoArgumentos():
    parser = argparse.ArgumentParser("Obtencion de Hash\'s de archivos de sistema")
    parser.add_argument('-v', '--verbose', help='Despliega mensajes mas mensajes de error e informativos', action='store_true')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--md5', help='Utilizar un hash md5', action='store_true')
    group.add_argument('--sha256', help='Utilizar un hash sha 256', action='store_true')
    group.add_argument('--sha512', help='Utilizar un hash sha 512', action='store_true')
    parser.add_argument('-d', '--rootPath', type=ValidarDirectorio, required=True, help='Establecer el directorio raiz para hash')
    parser.add_argument('-r', '--reportPath', type=ValidarPermisos, required=True, help='Establece el directorio para reportes y logs')
    global gl_tipoHash
    global gl_args
    gl_args = parser.parse_args()
    if gl_args.md5:
        gl_tipoHash = 'MD5'
    elif gl_args.sha256:
        gl_tipoHash = 'SHA256'
    elif gl_args.sha512:
        gl_tipoHash = 'SHA512'
    else:
        gl_tipoHash = 'Desconocido'
        log.error("Tipo de hash desconocido o faltante")
    DisplayMessage('Argumentos obtenidos con exito')
#End ParseoArgumentos===============================================================================


#
#Nombre:
#       ValidarDirectorio
#
#Input:
#       dir = Carpeta de la cual se obtendran los hash de archivos
#
#Descripcion:
#       Valida la carpeta de la cual se obtendran los hashes
#
#Acciones:
#       Validar que la ruta sea una carpeta
#       Validar que la ruta cuente con permisos de lectura
#
def ValidarDirectorio(dir):
    log.debug("Validando permisos de lectura [+r] en el directorio")
    if not os.path.isdir(dir):
        raise argparse.ArgumentTypeError('El directorio a leer no existe')
    if os.access(dir, os.R_OK):
        return dir
    else:
        raise argparse.ArgumentTypeError('No es posible leer en el directorio')
#End ValidarDirectorio===============================================================================

#
#Nombre:
#       ValidarPermisos()
#
#Input:
#       dir = ruta del directorio a escribir logs y csv
#
#Descripcion:
#       Funcion que permite validar que la ruta sea una carpeta con permisos de escritura
#
#Acciones:
#       Validar que la ruta sea una carpeta
#       Validar que la ruta cuente con permisos de escritura
#
def ValidarPermisos(dir):
    log.debug("Validando permisos de escritura [+w] en directorio")
    if not os.path.isdir(dir):
        raise argparse.ArgumentTypeError('El directorio no existe')
    if os.access(dir, os.W_OK):
        return dir
    else:
        raise argparse.ArgumentTypeError('No es posible escribir en el directorio')
#End ValidarPermisos===============================================================================


#
#Nombre:
#       DisplayMessage
#
#Input:
#       msn (mensaje el cual se imprimira dependiendo del nivel establecido
#
#Description:
#       Funcion para imprimir los mensajes si se encuentra el parametro verbose
#
#Acciones:
#       Verificar la existencia del parametro verbose
#       Imprimir el mensaje
#
def DisplayMessage(msg):
    if gl_args.verbose:
        print(msg)
    return
#End DisplayMessage===============================================================================


#
#Nombre:
#       WalkPath
#
#Descripcion:
#       Funcion para leer todos los archivos del directorio
#
#Acciones:
#       Recorrer todos los directorios y archivos de la carpeta seleccionada
#       Calcular el hash del archivo dado
#       Utilizar un contador de exitos y errores para control
#
def WalkPath():
    contadorProcesos = 0
    contadorError = 0
    log.info("Root Paht " + gl_args.rootPath)
    log.info("Report Paht " + gl_args.reportPath)

    oCSV = _CSVWriter(gl_args.reportPath + 'fileSystemReport.csv', gl_tipoHash)
    for root, dirs, files in os.walk(gl_args.rootPath):
        for file in files:
            fname = os.path.join(root, file)
            result = HashFile(fname, file, oCSV)
            if result:
                contadorProcesos += 1
            else:
                contadorError += 1
    oCSV.writerClose()
    return contadorProcesos
#End WalkPath===============================================================================


#
#Nombre:
#       HashFile
#
#Input:
#       theFile: La ruta del archivo
#       simpleName: El nombre del archivo
#       o_result: Archivo de output
#
#Descripcion:
#       Este metodo obtiene el hash  del archivo dado
#
#Acciones:
#       Veificar si el archivo existe, no es un link o un directorio.
#       Abrir el archivo y leerlo
#       obtener informacion del archivo (metadata)
#       En base a los argumentos questablecidos calcular su hash
#       Guardar todos estos resultados en un archivo csv
#
def HashFile(theFile, simpleName, o_result):
    if os.path.exists(theFile):
        if not os.path.islink(theFile):
            if os.path.isfile(theFile):
                try:
                    f = open(theFile, 'rb')
                except IOError:
                    log.warning('Fallo al leer el archivo: ' + theFile)
                    return
                else:
                    try:
                        rd = f.read()
                    except IOError:
                        f.close()
                        log.warning('Fallo al leer el archivo: ' + theFile)
                        return
                    else:
                        theFileStats = os.stat(theFile)
                        (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime) = os.stat(theFile)
                        log.info('Procesando el archivo')
                        filesize = str(size)
                        modificacion = time.ctime(mtime)
                        acceso = time.ctime(atime)
                        creacion = time.ctime(ctime)
                        ownerID = str(uid)
                        groupID = str(gid)
                        fileMode = str(mode)
                        if gl_args.md5:
                            hash = hashlib.md5()
                            hash.update(rd)
                            hexMD5 = hash.hexdigest()
                            hashValue = hexMD5.upper()
                        elif gl_args.sha256:
                            hash = hashlib.sha256()
                            hash.update(rd)
                            hexSHA256 = hash.hexdigest()
                            hashValue = hexSHA256.upper()
                        elif gl_args.sha512:
                            hash = hashlib.sha512()
                            hash.update(rd)
                            hexSHA512 = hash.hexdigest()
                            hashValue = hexSHA512.upper()
                        else:
                            log.error("Hash no seleccionado")
                        f.close()
                        o_result.writeCSVRow(simpleName, theFile, filesize, modificacion, acceso, creacion, hashValue, ownerID, groupID, modificacion)
                        return True
            else :
                log.warning('['+repr(simpleName)+' Omitido, no es un archivo]')
                return False
        else:
            log.warning('['+repr(simpleName)+' Omitido, es un link de un archivo]')
            return False
    else:
        log.warning('['+repr(simpleName)+' La ruta no existe]')
        return False
#End HashFile===============================================================================

#
#Clase:
#       CSVWriter
#
#Descripcion:
#       Clase para facilitar el manejo de csv
#
#Metodos:
#       Constructor: (Nombre del archivo
#
#
#
class _CSVWriter:
    def __init__(self, fileName, hashType):
        try:
            self.csvFile = open(fileName, 'wb')
            self.writer = cs.writer(self.csvFile, delimiter=',', quoting=cs.QUOTE_ALL)
            self.writer.writerow(('File', 'Path', 'Size', 'Modificacion', 'Acceso', 'Creacion', hashType,
                                  'Owner', 'Group', 'Mode'))
        except Exception as ex:
            log.error("Fallo en CSV")
            print(type(ex))
            print(ex.args, ex)


    def writeCSVRow(self, fileName, filePath, size, modificacion, acceso, creacion,hashVal, owner, group, mode):
        self.writer.writerow((fileName, filePath, size, modificacion, acceso, creacion, hashVal, owner, group, mode))


    def writerClose(self):
        self.csvFile.close()