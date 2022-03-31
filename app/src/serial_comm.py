#!/usr/bin/env python
from enum import auto
import db
import serial
import time

from queue import Queue, Empty
from threading import *

from fastapi_utils.enums import StrEnum


class PrinterCommand(StrEnum):
    FLUSH_Q_RESET = auto()  # command id of the command to send, see treat_cmd()
    CANCEL_PRINT = auto()
    EMERGENCY_STOP = auto()
    PAUSE_PRINT = auto()
    RESUME_PRINT = auto()
    INITIALIZE_MONITORING = auto()
    AUTO_HOME = auto()
    PAUSE_CHANGEF = auto()
    PREHEAT_PLA = auto()
    COOLDOWN = auto()

    MOVE_X1 = auto()
    MOVE_X10 = auto()
    MOVE_X_1 = auto()  # -
    MOVE_X_10 = auto()  # -

    MOVE_Y1 = auto()
    MOVE_Y10 = auto()
    MOVE_Y_1 = auto()
    MOVE_Y_10 = auto()

    MOVE_Z1 = auto()
    MOVE_Z10 = auto()
    MOVE_Z_1 = auto()
    MOVE_Z_10 = auto()


class PrinterManager:
    def __init__(self) -> None:
        self.current_print = None
        self.paused = False
        self.qFile = Queue()
        self.qCmd = Queue()

        self.s = self.openConnection()
        self.advancement = []
        self.pos = []
        self.currentPrintTotSize = 0

    @property
    def printing(self):
        return self.current_print is not None and not self.paused

    def openConnection(self) -> serial:
        """opens a serial connection

        Args:
            port (str, optional): The serial port to connect to. Defaults to '/dev/ttyACM0'.

        Returns:
            serial: the serial connection to use
        """
        printer_connected = False
        while not printer_connected:
            try:
                s = serial.Serial('/dev/ttyACM1', 115200)
                printer_connected = True
            except serial.SerialException:
                try:
                    s = serial.Serial('/dev/ttyACM0', 115200)
                    printer_connected = True
                except serial.SerialException:
                    print("Printer not plugged")
                    time.sleep(1)

        # Wake up grbl
        s.write("\r\n\r\n".encode())
        time.sleep(2)   # Wait for grbl to initialize
        s.flushInput()  # Flush startup text in serial input

        return s

    def outputGcode(self, gcode: str) -> str:
        print('SendingForOutput: ' + gcode)
        self.s.write(gcode.encode() + '\n'.encode())
        grbl_out = " "
        grbl_out = self.s.readline()
        return str(grbl_out.strip())

    def sendGcode(self, gcode: str):
        print('[DEBUG] [GCODE] out: ' + gcode),
        # Send g-code block to grbl
        self.s.write(gcode.encode() + '\n'.encode())
        grbl_out = self.s.readline()
        print('[DEBUG] [GCODE] in: ' + str(grbl_out.strip()))
        grbl_string = str(grbl_out.strip())
        if grbl_string.find('T') == 5 or grbl_string.find('T') == 2:
            dictTemp = parseRcvTemp(grbl_string)
            print(dictTemp)
            storeToDb(dictTemp)
        if grbl_string.find('X') == 2:
            dictXYZ = parseRcvXYZ(grbl_string)
            print(dictXYZ)
            self.pos[0] = dictXYZ.get('X')
            self.pos[1] = dictXYZ.get('Y')
            self.pos[2] = dictXYZ.get('Z')

    # add all file to the main queue (qFile)
    def fillQueueGcodeFile(self, file: str):
        with open(file, 'r') as f:
            for line in f:
                l = line.strip()
                l = remove_comment(l)
                if len(l) == 0:
                    continue
                self.qFile.put(l)
        self.currentPrintTotSize = self.qFile.qsize()

    def get_cmd(self):
        try:
            cmd = self.qCmd.get_nowait()
        except Empty:
            cmd = False
        return cmd

    def treat_cmd(self, cmd):
        if not cmd:
            return False
        if cmd == PrinterCommand.FLUSH_Q_RESET and not self.printing:
            with self.qFile.mutex:
                self.qFile.queue.clear()
            self.sendGcode('M199')  # reset

        if cmd == PrinterCommand.CANCEL_PRINT:
            with self.qFile.mutex:
                self.qFile.queue.clear()
            self.sendGcode('M601')
            self.sendGcode('M117 Print Stoped')
            self.sendGcode('G91 Z ')
            self.sendGcode('G1 Z15')
            self.sendGcode('G90 Z ')

            self.qCmd.put(PrinterCommand.COOLDOWN)    
            self.current_print = None
            return True

        elif cmd == PrinterCommand.EMERGENCY_STOP:
            self.current_print = None
            self.sendGcode('M112')
            return True

        elif cmd == PrinterCommand.PAUSE_PRINT and self.printing:
            self.sendGcode('M601')
            self.sendGcode('M117 Print Paused')
            self.sendGcode('G91 Z ')
            self.sendGcode('G1 Z15')
            self.sendGcode('G90 Z ')

            self.paused = True

            return True

        elif cmd == PrinterCommand.RESUME_PRINT and self.paused:
            self.paused = False
            self.sendGcode('M602')
            self.sendGcode('M117 Print Resumed')
            self.sendGcode('G91 Z')
            self.sendGcode('G1 Z-15')
            self.sendGcode('G90 Z')
            self.paused = False

            return True

        elif cmd == PrinterCommand.INITIALIZE_MONITORING:
            self.sendGcode('M105')

            return True
        elif cmd == PrinterCommand.AUTO_HOME and not self.printing:

            self.sendGcode('G28')

            return True

        elif cmd == PrinterCommand.PAUSE_CHANGEF:
            self.current_print = None
            self.sendGcode('M600')

            return True

        elif cmd == PrinterCommand.PREHEAT_PLA and not self.printing:
            self.sendGcode('M104 S200')
            self.sendGcode('M140 S60')

            return True

        elif cmd == PrinterCommand.COOLDOWN and not self.printing:
            self.sendGcode('M104 S0')
            self.sendGcode('M140 S0')

            return True

        elif cmd == PrinterCommand.MOVE_X1 and not self.printing:
            self.sendGcode('G0 X10 F3000')
            self.sendGcode('G91')

            return True

        elif cmd == PrinterCommand.MOVE_X_1 and not self.printing:
            self.sendGcode('G0 X-10 F3000')
            self.sendGcode('G91')

            return True

        elif cmd == PrinterCommand.MOVE_Y1 and not self.printing:
            self.sendGcode('G0 Y10 F3000')
            self.sendGcode('G91')

            return True

        elif cmd == PrinterCommand.MOVE_Y_1 and not self.printing:
            self.sendGcode('G0 Y-10 F3000')
            self.sendGcode('G91')

            return True

        elif cmd == PrinterCommand.MOVE_Z1 and not self.printing:
            self.sendGcode('G0 Z10 F3000')
            self.sendGcode('G91')

            return True

        elif cmd == PrinterCommand.MOVE_Z10 and not self.printing:
            self.sendGcode('G0 Z100 F3000')
            self.sendGcode('G91')

            return True

        elif cmd == PrinterCommand.MOVE_Z_1 and not self.printing:
            self.sendGcode('G0 Z-10 F3000')
            self.sendGcode('G91')

            return True

        elif cmd == PrinterCommand.MOVE_Z_10 and not self.printing:
            self.sendGcode('G0 Z-100 F3000')
            self.sendGcode('G91')

            return True

    def manage_printer_thread_target(self, pos):
        while True:
            try:
                self.pos = pos
                j = 0
                i = 1
                while True:
                    i += 1
                    if self.printing:
                        if i % 5 == 0 and not i % 10 == 0:
                            self.sendGcode('M105')
                        elif i % 10 == 0:
                            self.sendGcode('M114')
                    else:
                        # time.sleep(1)
                        if j % 2 == 0:
                            self.sendGcode('M105')
                            time.sleep(1)
                            j += 1
                        else:
                            self.sendGcode('M114')
                            time.sleep(1)
                            j += 1

                    cmd = self.get_cmd()
                    should_skip = self.treat_cmd(cmd)
                    if should_skip:
                        continue  # reset the while

                    if self.printing:
                        line = self.qFile.get()
                        self.sendGcode(line)
                        if self.qFile.empty():
                            self.paused=False
                            self.current_print=None
            except serial.SerialException:
                print("Printer not plugged")
                self.s = self.openConnection()


def parseRcvTemp(rep: str) -> dict:
    """takes a 'M105' response and converts it into a dict'

    Args:
        rep (str): the temp response from the printer 

    Returns:
        dict: the temp in a dictionary format
    """
    indT = rep.find('T')
    indSlashT = rep.find('/')

    indB = rep.find('B')
    indSlashB = rep.find('/', indB)

    indA = rep.find('A')
    indSlashA = rep.find('/', indA)

    tempNozle = rep[indT+2:indSlashT-1]
    tempGoalNozle = rep[indSlashT+1:indB-1]

    tempBed = rep[indB+2:indSlashB-1]
    # tempGoalBed = rep[indSlashB+1:indA-1]  # for mini
    tempGoalBed = rep[indSlashB+1:indSlashB+4]  # for mk3S (and mini)

    tempAir = rep[indA+2:indSlashA-1]

    dico = {"NozleTemp": int(float((tempNozle))), "GoalTempNozle": int(float(tempGoalNozle)),
            "TempBed": int(float(tempBed)), "TempGoalBed": int(float(tempGoalBed)),
            "TempAir": int(float(tempAir))}

    return dico


def parseRcvXYZ(rep: str) -> dict:
    indX = rep.find('X')

    indY = rep.find('Y')

    indZ = rep.find('Z')

    indE = rep.find('E')

    x = rep[indX+2:indY-1]
    y = rep[indY+2:indZ-1]
    z = rep[indZ+2:indE-1]

    dico = {"X": float(x), "Y": float(y), "Z": float(z)}
    return dico


def remove_comment(string):
    """Remove comments from GCode if any"""
    if string.find(';') == -1:
        return string
    return string[:string.index(';')]


def storeToDb(dictTemp: dict):
    """uses the db.py function to store the parsed temp into the db

    Args:
        dictTemp (dict): parsed dictionary (temps)
    """
    db.storeFromDictTemp(dictTemp)
