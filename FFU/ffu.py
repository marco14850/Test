#
# p-fish : Python First Forensic Unified Program
# Author: HackerOps FCFM
# 2020
# Version BETA 1.0
#
# Tiempor Trabajado total = 4 horas
#

import logging
import time
import platform as pla
import multiprocessing
import logging
import argparse
import os
import subprocess


def parseo_argumentos():
    parser = argparse.ArgumentParser("First Forensics Unified Program BETA 1.0 HackerOps-FCFM")
    parser.add_argument('-v', '--verbose', help='Despliega mensajes de error e informativos',
                        action='store_true', default=False)
    parser.add_argument('-oD', '--outputDir', help='Especificas el nombre del directorio de salida',
                        type=str, required=True)
    parser.add_argument('-wP', '--wifiPassword', help='Extraer las credenciales de wifi del equipo local',
                        action='store_true', required=False, default=False)
    gl_args = parser.parse_args()
    imprimir_mensaje("Argumentos con exito", gl_args)
    crear_directorio(gl_args.outputDir)
    return gl_args


def imprimir_mensaje(msg,gl_args):
    if gl_args.verbose:
        print(msg)


def ejecutar_comando(comando, parametros , outputDir):
    x = os.popen(comando + ' ' + parametros)
    guardar_salida(comando, x.read(), outputDir)


def guardar_salida(comando, resultado, outputDir):
    with open(outputDir + '\\' + comando + '.txt', 'w') as out:
        out.write(resultado)

#####################
#Referencia https://nitratine.net/blog/post/get-wifi-passwords-with-python/
#####################
def extraer_wifi(outputDir):
    result = "{:<30}| {}".format("SSID", "Password")
    netsh = subprocess.check_output(['netsh', 'wlan', 'show', 'profiles']).decode('utf-8', errors="backslashreplace").split('\n')
    profiles = [i.split(":")[1][1:-1] for i in netsh if ":" in i]
    for i in profiles:
        try:
            results = subprocess.check_output(['netsh', 'wlan', 'show', 'profile', i, 'key=clear']).decode('utf-8', errors="backslashreplace").split('\n')
            results = [b.split(":")[1][1:-1] for b in results if ("clave" or "Key") in b]
            try:
                result += "\n{:<30}| {}".format(i, results[0])
            except IndexError:
                result += "\n{:<30}| {}".format(i, "")
        except:
            imprimir_mensaje("[+] NETSH: Formato no encontrado en " + i)
    guardar_salida("netsh", result, outputDir)


def crear_directorio(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)



#
#Winpmem:
#Url: https://github.com/Velocidex/c-aff4
#

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='[+] %(asctime)s-%(levelname)s: %(message)s')
    startTime = time.time()
    try:
        gl_args = parseo_argumentos()
        process = []
        process.append(multiprocessing.Process(target=ejecutar_comando, args=("dir", "", gl_args.outputDir)))
        process.append(multiprocessing.Process(target=ejecutar_comando, args=("dir", "", gl_args.outputDir)))
        process.append(multiprocessing.Process(target=ejecutar_comando, args=("ping", "8.8.8.8", gl_args.outputDir)))
        process.append(multiprocessing.Process(target=ejecutar_comando, args=("arp", "-a", gl_args.outputDir)))
        process.append(multiprocessing.Process(target=ejecutar_comando, args=("ipconfig", "/all", gl_args.outputDir)))
        if gl_args.wifiPassword:
            process.append(multiprocessing.Process(target=extraer_wifi, args=(gl_args.outputDir,)))
        for p in process:
            p.start()
        for p in process:
            p.join()
        endTime = time.time()
        duration = endTime - startTime
        logging.info("Sistema operativo" + pla.system() + " Version: " + pla.version())
        logging.info("Tiempo de ejecucion: " + str(duration))
        logging.info("El programa se ejecuto con exito")
    except Exception as ex:
        logging.error("Fallo en la ejecucion \n" + str(type(ex)) + "\n"+str(ex.args))
