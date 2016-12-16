import octoprint.printer
from .. import roboprinter
import re
import signal

class PConsole(octoprint.printer.PrinterCallback):



    position = []
    position_ready = False
    #dictionary for eeprom
    eeprom_ready = False
    steps_per_unit = {}
    maximum_feed_rate = {}
    maximum_acceleration = {}
    accelerations = {}
    advanced_variables = {}
    home_offset = {}
    PID = {}
    filament_settings = {}
    zoffset = {}
    eeprom = {}
    counter = 0

    def on_printer_add_message(self, data):

        #roboprinter.printer_instance._logger.info(data)

        #get the EEPROM
        M92 = data.find('M92')
        M203 = data.find('M203')
        M201 = data.find('M201')
        M204 = data.find('M204')
        M205 = data.find('M205')
        M206 = data.find('M206')
        M301 = data.find('M301')
        M200 = data.find('M200')
        M851 = data.find('M851')
        _Zoffset_update = data.find('Z Offset')


        #Steps Per Unit
        if M92 != -1:
            roboprinter.printer_instance._logger.info("M92 "+ str(self.counter))
            p = "X([0-9.]+) Y([0-9.]+) Z([0-9.]+) E([0-9.]+)"
            spu = re.findall(p, data)
            if spu != []:
                self.steps_per_unit = {
                    'X' : float(spu[0][0]),
                    'Y' : float(spu[0][1]),
                    'Z' : float(spu[0][2]),
                    'E' : float(spu[0][3])
                }
                self.counter += 1
        #Maximum Feed Rate
        elif M203 != -1:
            roboprinter.printer_instance._logger.info("M203 "+ str(self.counter))
            p = "X([0-9.]+) Y([0-9.]+) Z([0-9.]+) E([0-9.]+)"
            mfr = re.findall(p, data)

            if mfr != []:
                self.maximum_feed_rate = {
                    'X' : float(mfr[0][0]),
                    'Y' : float(mfr[0][1]),
                    'Z' : float(mfr[0][2]),
                    'E' : float(mfr[0][3])
                }
                self.counter += 1
        #Maximun Acceleration
        elif M201 != -1:

            p = "X([0-9.]+) Y([0-9.]+) Z([0-9.]+) E([0-9.]+)"
            ma = re.findall(p, data)
            if ma != []:
                roboprinter.printer_instance._logger.info("M201 "+ str(self.counter))
                self.maximum_acceleration = {
                    'X' : float(ma[0][0]),
                    'Y' : float(ma[0][1]),
                    'Z' : float(ma[0][2]),
                    'E' : float(ma[0][3])
                }
                self.counter += 1
        #Accelerations
        elif M204 != -1:
            roboprinter.printer_instance._logger.info("M204 "+ str(self.counter))
            p = "P([0-9.]+) R([0-9.]+) T([0-9.]+)"
            accel = re.findall(p, data)

            if accel != []:
                self.accelerations = {
                    'P' : float(accel[0][0]),
                    'R' : float(accel[0][1]),
                    'T' : float(accel[0][2])

                    }
                self.counter += 1
        #advanced variables
        elif M205 != -1:
            roboprinter.printer_instance._logger.info("M205 "+ str(self.counter))
            p = "S([0-9.]+) T([0-9.]+) B([0-9.]+) X([0-9.]+) Z([0-9.]+) E([0-9.]+)"
            av = re.findall(p, data)
            if av != []:
                self.advanced_variables = {
                    'S' : float(av[0][0]),
                    'T' : float(av[0][1]),
                    'B' : float(av[0][2]),
                    'X' : float(av[0][3]),
                    'Z' : float(av[0][4]),
                    'E' : float(av[0][5])
                }
                self.counter += 1
        #home offset
        elif M206 != -1:
            roboprinter.printer_instance._logger.info("M206 "+ str(self.counter))
            p = "X([0-9.]+) Y([0-9.]+) Z([0-9.]+)"
            ho = re.findall(p, data)

            if ho != []:
                self.home_offset = {
                    'X' : float(ho[0][0]),
                    'Y' : float(ho[0][1]),
                    'Z' : float(ho[0][2])
                }
                self.counter += 1
        #PID settings
        elif M301 != -1:
            roboprinter.printer_instance._logger.info("M301 "+ str(self.counter))
            p = "P([0-9.]+) I([0-9.]+) D([0-9.]+)"
            pid = re.findall(p, data)

            if pid != []:
                self.PID = {
                    'P' : float(pid[0][0]),
                    'I' : float(pid[0][1]),
                    'D' : float(pid[0][2])
                }
                self.counter += 1
        #filament settings

        elif M200 != -1:
            roboprinter.printer_instance._logger.info("M200 "+ str(self.counter))
            p = "D([0-9.]+)"
            fs = re.findall(p, data)

            if fs != []:
                self.filament_settings = {
                    'D' : float(fs[0])
                }
                self.counter += 1
        #Zoffset
        elif M851 != -1:

            p = "Z([-0-9.00]+)"
            zo = re.findall(p, data)

            if zo != []:
                self.zoffset = {

                    'Z' : float(zo[0])

                }
                self.counter += 1
                roboprinter.printer_instance._logger.info("M851 "+ str(self.counter))

        #Zoffset update
        elif _Zoffset_update != -1:
            p = "Z Offset ([-0-9.00]+)"
            zo = re.findall(p, data)

            if zo != []:
                roboprinter.printer_instance._logger.info('Zoffset Background Update ' + str(zo[0]))
                self.zoffset['Z'] =  float(zo[0])
                self.eeprom['z offset'] = self.zoffset

        else:
            #get the position
            p = "X:([0-9.]+) Y:([0-9.]+) Z:([0-9.]+)"
            temp_pos = re.findall(p, data)
            if temp_pos != []:
                self.position = temp_pos[0]
                roboprinter.printer_instance._logger.info('Position Update')
                roboprinter.printer_instance._logger.info(str(self.position))
                self.position_ready = True

        if self.counter >= 10:
            self.eeprom = {
                'steps per unit' : self.steps_per_unit,
                'max feed rate' : self.maximum_feed_rate,
                'max acceleration' : self.maximum_acceleration,
                'accelerations' : self.accelerations,
                'advanced variables' : self.advanced_variables,
                'home offset' : self.home_offset,
                'PID' : self.PID,
                'filament settings' : self.filament_settings,
                'z offset' : self.zoffset
            }
            self.counter = 0
            self.eeprom_ready = True
            roboprinter.printer_instance._logger.info(self.eeprom)
        #roboprinter.printer_instance._logger.info(self.counter)

    def query_eeprom(self):
        roboprinter.printer_instance._printer.commands('M501')

    def get_eeprom(self):
        self.counter = 0
        self.eeprom_ready = False
        roboprinter.printer_instance._printer.commands('M501')

        while (self.eeprom_ready == False):
            pass

        return self.eeprom
    def generate_eeprom(self):
        self.eeprom_ready = False
        roboprinter.printer_instance._printer.commands('M501')

    def get_old_eeprom(self):
        pass
        return self.eeprom

    def get_position(self):
        roboprinter.printer_instance._printer.commands('M114')

        while (self.position_ready == False):
            pass

        self.position_ready = False
        return self.position
    def initialize_eeprom(self):
        self.steps_per_unit = {
            'X' : 0,
            'Y' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.maximum_feed_rate = {
            'X' : 0,
            'Y' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.maximum_acceleration = {
            'X' : 0,
            'Y' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.accelerations = {
            'P' : 0,
            'R' : 0,
            'T' : 0
        }
        self.advanced_variables = {
            'S' : 0,
            'T' : 0,
            'B' : 0,
            'X' : 0,
            'Z' : 0,
            'E' : 0
        }
        self.home_offset = {
            'X' : 0,
            'Y' : 0,
            'Z' : 0
        }
        self.PID = {
            'P' : 0,
            'I' : 0,
            'D' : 0
        }
        self.filament_settings = {
            'D' : 0
        }
        self.zoffset = {
            'Z' : 0
        }
        self.eeprom = {
            'steps per unit' : self.steps_per_unit,
            'max feed rate' : self.maximum_feed_rate,
            'max acceleration' : self.maximum_acceleration,
            'accelerations' : self.accelerations,
            'advanced variables' : self.advanced_variables,
            'home offset' : self.home_offset,
            'PID' : self.PID,
            'filament settings' : self.filament_settings,
            'z offset' : self.zoffset
        }



pconsole = PConsole()
