#
# p-fish : Python File System Hash Program
# Author: KITO
# 2020
# Version 1.0
# Libro Python Forensics
#
import logging
import time
import sys
import _pfish


if __name__ == '__main__':
    PFISH_VERSION = 1.0
    logging.basicConfig(level=logging.INFO, format='[+] %(asctime)s-%(levelname)s:%(message)s')
    startTime = time.time()
    logging.info("Bienvenido a la herramienta p-fish version " + str(PFISH_VERSION))
    logging.info("Sistema Operativo: " + sys.platform)
    logging.info("Python Version: " + sys.version)
    endTIme = time.time()
    _pfish.ParseoArgumentos()
    _pfish.WalkPath()
    duration = endTIme - startTime
    logging.info("Duracion: " + str(duration))
    logging.info("El programa termino con su flujo normal")