# -*- coding: utf-8 -*-
# @Author: Matt Pedler & Robo3D
# @Date:   2018-02-27 12:42:45
# @Last Modified by:   Matt Pedler
# @Last Modified time: 2018-02-28 10:55:15


'''
###########################################################################
############################# EEPROM ######################################
###########################################################################

This file captures the EEPROM from the Serial line. This will only capture
specified M-Codes from a Marlin based printer. 

Captured M-Codes:
M92
M203
M201
M204
M205
M206
M218
M301
M304
M851
M900
'''
from __future__ import absolute_import
import time


class EEPROM_Handler(object):
    _home_offset = {}
    _probe_offset = {}
    _feed_rate = {}
    _PID = {}
    _BPID = {}
    _steps_per_unit = {}
    _accelerations = {}
    _max_accelerations = {}
    _advanced_variables = {}
    _linear_advanced = {}
    _hotend_offset = {}
    cur_time = 0

    def __init__(self, _logger, printer=None):
        super(EEPROM_Handler, self).__init__()
        
        self._logger = _logger
        self._logger.info("EEPROM_Handler Starting up")
        self.registered_callbacks = {}

        self.printer = printer

    def is_eeprom_message(self, data):
        find_data = ['M92', 'M203', 'M201', 'M204', 'M205', 'M206', 'M218', 'M301', 'M304', 'M851', 'M900']
        for query in find_data:
            found = data.find(query)

            if found != -1:
                return True

        return False

    def on_EEPROM_Message(self, data):
        
        find_data = ['M92', 'M203', 'M201', 'M204', 'M205', 'M206', 'M218', 'M301', 'M304', 'M851', 'M900']

        acceptable_finds = {
                            'M92': self.find_M92,
                            'M203': self.find_M203,
                            'M201': self.find_M201,
                            'M204': self.find_M204,
                            'M205': self.find_M205,
                            'M206': self.find_M206,
                            'M218': self.find_M218,
                            'M301': self.find_M301,
                            'M304': self.find_M304,
                            'M851': self.find_M851,
                            'M900': self.find_M900,

        }

        #Simple switch function
        for query in find_data:
            found = data.find(query)

            if found != -1:
                #execute dictionary function
                acceptable_finds[query](data)
                break   

    '''
    Query EEPROM will ask if the printer is printing or not and either perform an M503 or an M501
    This will trigger an automatic collection of the EEPROM.
    '''
    def query_eeprom(self):
        self.cur_time = time.time()
        if self.printer._comm is None or not self.printer._comm.isOperational() or self.printer._comm.isPrinting() or self.printer._comm.isPaused():
            self.printer.commands('M503')
        else:
            self.printer.commands('M501')

    '''
    Get EEPROM Dict will return a dictionary of the current captured EEPROM. This will not return
    THE current EEPROM, Just the most recently captured one. During printing this function may not have the 
    most up to date information.
    '''
    def get_eeprom_dict(self):
        eeprom_dict = {
            'M92': self.steps_per_unit, 
            'M203': self.feed_rate, 
            'M201': self.max_accelerations, 
            'M204': self.accelerations, 
            'M205': self.advanced_variables, 
            'M206': self.home_offset, 
            'M218': self.hotend_offset, 
            'M301': self.PID, 
            'M304': self.BPID, 
            'M851': self.probe_offset, 
            'M900': self.linear_advanced
        }
        return eeprom_dict

    def parse_M_commands(self, data, command):
        return_dict = {}
        #cut M command
        data = data.replace(command, "")
        #remove all spaces
        data = data.replace(" ", "")

        
        acceptable_data = ['X', 'Y', 'Z', 'E', 'P', 'I', 'D', 'R', 'T' , 'S', 'B', 'K']
        
        while [x for x in acceptable_data if (x in data)] != []: #this is the equivalent of if 'X' in data or 'Y' in data or 'Z' in data ect
            if data.find("X") != -1:
                var_data = self.scrape_data(data, "X")
                end_var_data = var_data.replace('X','')
                return_dict['X'] = float(end_var_data)    
                data = data.replace(var_data, '')
                
    
            elif data.find("Y") != -1:
                var_data = self.scrape_data(data, "Y")
                end_var_data = var_data.replace('Y','')
                return_dict['Y'] = float(end_var_data)    
                data = data.replace(var_data, '')
                
    
            elif data.find("Z") != -1:
                var_data = self.scrape_data(data, "Z")
                end_var_data = var_data.replace('Z','')
                return_dict['Z'] = float(end_var_data)    
                data = data.replace(var_data, '')
                
    
            elif data.find("E") != -1 and data.find("T0") != -1 and command != "M205":
                var_data = self.scrape_data(data, "E")
                end_var_data = var_data.replace('E', '')
                return_dict['T0 E'] = float(end_var_data)
                data = data.replace(var_data, '')
                data = data.replace("T0", '')
                
    
            elif data.find("E") != -1 and data.find("T1") != -1 and command != "M205":
                var_data = self.scrape_data(data, "E")
                end_var_data = var_data.replace('E', '')
                return_dict['T1 E'] = float(end_var_data)
                data = data.replace(var_data, '')
                data = data.replace("T1", '')
                
    
            elif data.find("E") != -1 :
                var_data = self.scrape_data(data, "E")
                end_var_data = var_data.replace('E', '')
                return_dict['E'] = float(end_var_data)    
                data = data.replace(var_data, '')
                

            elif data.find("P") != -1:
                var_data = self.scrape_data(data, "P")
                end_var_data = var_data.replace('P', '')
                return_dict['P'] = float(end_var_data)    
                data = data.replace(var_data, '')
                

            elif data.find("I") != -1:
                var_data = self.scrape_data(data, "I")
                end_var_data = var_data.replace('I', '')
                return_dict['I'] = float(end_var_data)    
                data = data.replace(var_data, '')
                

            elif data.find("D") != -1:
                var_data = self.scrape_data(data, "D")
                end_var_data = var_data.replace('D', '')
                return_dict['D'] = float(end_var_data)    
                data = data.replace(var_data, '')
                

            elif data.find("R") != -1:
                var_data = self.scrape_data(data, "R")
                end_var_data = var_data.replace('R','')
                return_dict['R'] = float(end_var_data)    
                data = data.replace(var_data, '')
                

            elif data.find("T") != -1:
                var_data = self.scrape_data(data, "T")
                end_var_data = var_data.replace('T','')
                return_dict['T'] = float(end_var_data)    
                data = data.replace(var_data, '')
                

            elif data.find("B") != -1:
                var_data = self.scrape_data(data, "B")
                end_var_data = var_data.replace('B','')
                return_dict['B'] = float(end_var_data)    
                data = data.replace(var_data, '')
                

            elif data.find("S") != -1:
                var_data = self.scrape_data(data, "S")
                end_var_data = var_data.replace('S','')
                return_dict['S'] = float(end_var_data)    
                data = data.replace(var_data, '')

            elif data.find("K") !=-1:
                var_data = self.scrape_data(data, "K")
                end_var_data = var_data.replace('K','')
                return_dict['K'] = float(end_var_data)    
                data = data.replace(var_data, '')
                


        return return_dict

    def scrape_data(self, data, scraper):
        start_pos = data.find(scraper)
    
        if start_pos == -1:
            print("Cannot find data for scraper: " + str(scraper))
            return False
    
        end_pos = self.find_next_space(data[start_pos:len(data)], scraper)
    
        scraped = data[start_pos:start_pos + end_pos]
    
        return scraped
        

    def find_next_space(self, data, scraper):
        counter = 0
        acceptable_input = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '.', scraper]
        for i in data:
            counter += 1
            if i not in acceptable_input:
                break
            
        if counter == len(data):
            return len(data)
        else:
            return counter -1

    def merge_dicts(self, *dict_args):
        result = {}
        for dictionary in dict_args:
            result.update(dictionary)
        return result

    #This is for debugging. 
    def dict_logger(self, dictionary, indent = 0):
        indent_string = ""
        for x in range(indent):
            indent_string += "|"

        for item in dictionary:
            if type(dictionary[item]) is dict:
                if indent == 0:
                    self._logger.info("")
                self._logger.info(indent_string + item + ":")
                self.dict_logger(dictionary[item], indent=(indent+1))
            else:
                report_string = indent_string + str(item) + ": " + str(dictionary[item])
                self._logger.info(report_string)
    
    #Steps Per Unit
    def find_M92(self, data):
        #self._logger.info("M92 "+ str(self.counter))
        self.steps_per_unit = self.merge_dicts(self.steps_per_unit,self.parse_M_commands(data, 'M92'))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M92 getting it in " + str(finished_time) + " ms")

    #Maximum Feed Rate
    def find_M203(self, data):
        #self._logger.info("M203 "+ str(self.counter))
        self.feed_rate = self.merge_dicts(self.feed_rate, self.parse_M_commands(data, "M203"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M203 getting it in " + str(finished_time) + " ms")

    #Maximun Acceleration
    def find_M201(self, data):
        self.max_accelerations = self.merge_dicts(self.max_accelerations, self.parse_M_commands(data, "M201"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M201 getting it in " + str(finished_time) + " ms")

    #Accelerations
    def find_M204(self, data):
        #self._logger.info("M204 "+ str(self.counter))
        
        self.accelerations = self.merge_dicts(self.accelerations, self.parse_M_commands(data, "M204"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M204 getting it in " + str(finished_time) + " ms")

    #advanced variables
    def find_M205(self, data):
        #self._logger.info("M205 "+ str(self.counter))
        
        self.advanced_variables = self.merge_dicts(self.advanced_variables, self.parse_M_commands(data, "M205"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M205 getting it in " + str(finished_time) + " ms")

    #home offset
    def find_M206(self, data):
        self.home_offset = self.merge_dicts(self.home_offset, self.parse_M_commands(data, "M206"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M206 getting it in " + str(finished_time) + " ms")

    #hotend offset
    def find_M218(self, data):
        self.hotend_offset = self.merge_dicts(self.hotend_offset, self.parse_M_commands(data, "M218"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M118 getting it in " + str(finished_time) + " ms")


    #PID settings
    def find_M301(self, data):
        #self._logger.info("M301 " + data)
        self.PID = self.merge_dicts(self.PID, self.parse_M_commands(data, 'M301'))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M301 getting it in " + str(finished_time) + " ms")

    def find_M304(self, data):
        #self._logger.info("M301 "+ str(self.counter))
        
        self.BPID = self.merge_dicts(self.BPID, self.parse_M_commands(data, "M304"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M304 getting it in " + str(finished_time) + " ms")

    #Zoffset
    def find_M851(self, data):

        self.probe_offset = self.merge_dicts(self.probe_offset, self.parse_M_commands(data, "M851"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M851 getting it in " + str(finished_time) + " ms")
        #EEPROM is ready
        self.eeprom_ready = True

    #Zoffset update
    def find_zoffset(self,data):
        data = data.replace('Z Offset', "M851") #make it an M851 command
        self.probe_offset = self.merge_dicts(self.probe_offset, self.parse_M_commands(data, "M851"))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("ZOffset getting it in " + str(finished_time) + " ms")

    #Linear Advanced M900
    def find_M900(self, data):
        #self._logger.info("M301 " + data)
        self.linear_advanced = self.merge_dicts(self.linear_advanced, self.parse_M_commands(data, 'M900'))
        finished_time = (time.time() - self.cur_time) * 1000
        self._logger.info("M900 getting it in " + str(finished_time) + " ms")    

    

    ####################
    # EEPROM Variables #
    ####################

    @property
    def home_offset(self):
        return self._home_offset

    @home_offset.setter
    def home_offset(self, value):
        self._home_offset = value
        var_id = 'M206'


    @property
    def hotend_offset(self):
        return self._hotend_offset

    @hotend_offset.setter
    def hotend_offset(self, value):
        self._hotend_offset = value
        var_id = 'M218'

        
    @property
    def probe_offset(self):
        return self._probe_offset

    @probe_offset.setter
    def probe_offset(self, value):
        self._probe_offset = value
        var_id = 'M851'


    @property
    def feed_rate(self):
        return self._feed_rate

    @feed_rate.setter
    def feed_rate(self, value):
        self._feed_rate = value
        var_id = 'M203'


    @property
    def PID(self):
        return self._PID

    @PID.setter
    def PID(self, value):
        self._PID = value
        var_id = 'M301'


    @property
    def BPID(self):
        return self._BPID

    @BPID.setter
    def BPID(self, value):
        self._BPID = value
        var_id = 'M304'


    @property
    def steps_per_unit(self):
        return self._steps_per_unit

    @steps_per_unit.setter
    def steps_per_unit(self, value):
        self._steps_per_unit = value
        var_id = 'M92'


    @property
    def accelerations(self):
        return self._accelerations

    @accelerations.setter
    def accelerations(self, value):
        self._accelerations = value
        var_id = 'M204'


    @property
    def max_accelerations(self):
        return self._max_accelerations

    @max_accelerations.setter
    def max_accelerations(self, value):
        self._max_accelerations = value
        var_id = 'M201'


    @property
    def advanced_variables(self):
        return self._advanced_variables

    @advanced_variables.setter
    def advanced_variables(self, value):
        self._advanced_variables = value
        var_id = 'M205'


    @property
    def linear_advanced(self):
        return self._linear_advanced

    @linear_advanced.setter
    def linear_advanced(self, value):
        self._linear_advanced = value
        var_id = 'M900'


