class LEDTowers:
    '''
    Class modeling the LED Towers. it interfaces the IO Card end send out the 
    messages. It also keeps track of current status etc.
    '''
    SDI_PORT = 0
    CLK_PORT = 1
    LDAC1_PORT = 3
    LDAC2_PORT = 4
    LDAC3_PORT = 5
    CS1_PORT = 0
    CS2_PORT = 1
    CS3_PORT = 2
    BLUE_LDAC = LDAC1_PORT
    GREEN_LDAC = LDAC2_PORT
    BLUE_CS = CS1_PORT
    GREEN_CS = CS2_PORT  
    
    def __init__(self):
        self.current_status = '00000000'
        self.current_statusB = '00000000'
#        self.io = ctypes.windll.LoadLibrary('PCI-Dask')
#        self.card = self.io.Register_Card(9, 0)        
#        error = self.io.DIO_PortConfig(self.card, 0, 2)
#        print 'port config',error
#        error = self.io.DIO_PortConfig(self.card, 1, 2)
#        print 'port config', error
           
    def send_light_event(self, left, right):
        # left side  while we could set each quadrant individually due to 
        # historic reasons we set quadrant 0&2 and 1&3 together
        self.write(LEDTowers.LDAC1_PORT, LEDTowers.CS1_PORT, left[1], a1='0', 
                   a0='0')
        self.write(LEDTowers.LDAC1_PORT, LEDTowers.CS1_PORT, left[0], a1='0', 
                   a0='1')
        self.write(LEDTowers.LDAC1_PORT, LEDTowers.CS1_PORT, right[1], a1='1', 
                   a0='0')
        self.write(LEDTowers.LDAC1_PORT, LEDTowers.CS1_PORT, right[0], a1='1', 
                   a0='1')
    
    def write(self, ldac_port, cs_port, value, a1='1', a0='1'):
        print value
        intensity = '00000000'
        intensity += bin(value)[2:]
        value = intensity[-8:]
        self.current_status = list('00000000')
        self.current_statusB = list('00000000')
        self.current_status[7-LEDTowers.LDAC1_PORT] = '1'
        self.current_status[7-LEDTowers.LDAC2_PORT] = '1'
        self.current_status[7-LEDTowers.LDAC3_PORT] = '1'
        self.current_statusB[7-LEDTowers.CS1_PORT%7] = '1'
        self.current_statusB[7-LEDTowers.CS2_PORT%7] = '1'
        self.current_statusB[7-LEDTowers.CS3_PORT%7] = '1'
        self.current_status[7-LEDTowers.CLK_PORT] = '0'
        self.current_status[7-ldac_port] = '1'
        self.current_statusB[7-cs_port%7] = '0'
        self.write_to_port(self.current_status)
        self.write_to_port(self.current_statusB, port=1)
        # We send SA and SI first booth need to be high
        self.__sdi__('1')
        self.__sdi__('1')
        # Next we send A1 and A0
        self.__sdi__(a1)
        self.__sdi__(a0)
        # Now we can send the 8 Value bits
        [self.__sdi__(e) for e in value]
        self.current_statusB[7-cs_port%7] = '1'
        self.write_to_port(self.current_status)
        self.write_to_port(self.current_statusB, port=1)
        self.current_status[7-ldac_port] = '0'
        self.write_to_port(self.current_status)
        self.current_status[7-ldac_port] = '1'
        self.write_to_port(self.current_status)
    
    def __sdi__(self, bit):
        self.current_status[7-LEDTowers.SDI_PORT] = bit
        self.write_to_port(self.current_status)
        self.current_status[7-LEDTowers.CLK_PORT] = '1'
        self.write_to_port(self.current_status)
        self.current_status[7-LEDTowers.CLK_PORT] = '0'
        self.write_to_port(self.current_status)      
        
    
    def write_to_port(self, bins, port=0):
        pass
        print bins, int(''.join(bins), 2)
        #error = self.io.DO_WritePort(self.card, port, int(''.join(bins), 2));
        #print error
if __name__ == '__main__':
    x = LEDTowers()
    x.send_light_event([255,0],[0,255])