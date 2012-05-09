import time
import ctypes
import threading 

class LEDTowers:
    '''
    Class modeling the LED Towers. it interfaces the IO Card using the DASK 
    Routines provides with PCI_Dask.dll. There are several CLASS Variables
    that defines hardware mapping for LEDTowers.
    SDI_PORT: Port Used for the SDI Communication
    CLK_PORT: Port USED As Clock Port
    LDAC*_PORT: Ports used for the ldac communication
    CS*_PORTS: Ports used for Calble select
    The ccurrent hardware supports three ldacs and three cables where CS1 and 
    LDAC1 are all the BLue leds CS2 and LDAC2 are the Green leds and CS3 and 
    LDAC3 is the shock generator. Further detail of the communication interface
    can be found in the Documentation of the AD7304/AD7305 Chip used and the
    Documentaion of the IO Card (P4248)

    '''
    SDI_PORT = 0
    CLK_PORT = 1
    LDAC1_PORT = 2
    LDAC2_PORT = 3
    LDAC3_PORT = 4
    CS1_PORT = 5
    CS2_PORT = 6
    CS3_PORT = 7
    BLUE_LDAC = LDAC1_PORT
    GREEN_LDAC = LDAC2_PORT
    BLUE_CS = CS1_PORT
    GREEN_CS = CS2_PORT  
    
    def __init__(self):
        '''
        The init function will try to initialize the Hadrware 
        it will either set self.io to the identifier bof the initilized card 
        or to a negative value if it failed. This will only work under Windows 
        though. To interface between the DASK dll and python we here use ctypes
        '''
        self.current_status = '00000000'
        self.io = ctypes.windll.LoadLibrary('PCI-Dask')
        self.card = self.io.Register_Card(9, 0)        
        error = self.io.DIO_PortConfig(self.card, 0, 2)
        print 'port config',error
        error = self.io.DIO_PortConfig(self.card, 1, 2)
        print 'port config', error
        self.DO_WritePort = self.io.DO_WritePort
    
    
    def send_shock_event(self, event):
        '''
        send out a the shock event to the Towers
        '''
        self.write(LEDTowers.LDAC3_PORT, LEDTowers.CS3_PORT, event.intensity)
    
    def send_light_event(self, event):
        '''
        Interprets the event and send out the correct signals to the Towers        
        '''
        # left side  while we could set each quadrant individually due to 
        # historic reasons we set quadrant 0&2 and 1&3 together
        self.write(LEDTowers.BLUE_LDAC, LEDTowers.BLUE_CS, event.blue[0], a1='0', 
                   a0='0')
        self.write(LEDTowers.BLUE_LDAC, LEDTowers.BLUE_CS, event.blue[1], a1='0', 
                   a0='1')
        self.write(LEDTowers.BLUE_LDAC, LEDTowers.BLUE_CS, event.blue[2], a1='1', 
                   a0='0')
        self.write(LEDTowers.BLUE_LDAC, LEDTowers.BLUE_CS, event.blue[3], a1='1', 
                   a0='1')
        
        self.write(LEDTowers.GREEN_LDAC, LEDTowers.GREEN_CS, event.green[0], a1='0', 
                   a0='0')
        self.write(LEDTowers.GREEN_LDAC, LEDTowers.GREEN_CS, event.green[1], a1='0', 
                   a0='1')  
        self.write(LEDTowers.GREEN_LDAC, LEDTowers.GREEN_CS, event.green[2], a1='1', 
                   a0='0')         
        self.write(LEDTowers.GREEN_LDAC, LEDTowers.GREEN_CS, event.green[3], a1='1', 
                   a0='1') 
    
    def write(self, ldac_port, cs_port, value, a1='1', a0='1',SA='1',SI='1'):
        '''
        Writes a complete Set of intsructions to the Towers
        ldac_port: Is an integer indicating the ldac port to be used
        cs_port: Is an integer indicating the cs port to be used
        value: is the value that should be given via sdi. it be an 8uint (0-255)
        a1,a2: Flags indicating the LEDs to be set. (1,2,3,4 quadrant as bit 
               pattern. eg. a1=0,a2=0 is led1 and a1=1,a2=0 is led2 )
        '''
        #print value, ldac_port, cs_port
        # We start with an 8 char long string wo which we append the binary 
        # peresenattion of the give intensity. of the combinded string we take 
        # the last 8 chars
        intensity = '00000000'
        intensity += bin(value)[2:]
        value = intensity[-8:]
        # initialize before real transmission
        self.current_status = list('00000000')
        ## LDAC and CS all to high
        self.current_status[7-LEDTowers.LDAC1_PORT] = '1'
        self.current_status[7-LEDTowers.LDAC2_PORT] = '1'
        self.current_status[7-LEDTowers.LDAC3_PORT] = '1'
        self.current_status[7-LEDTowers.CS1_PORT] = '1'
        self.current_status[7-LEDTowers.CS2_PORT] = '1'
        self.current_status[7-LEDTowers.CS3_PORT] = '1'
        ## CLK starts with 0
        self.current_status[7-LEDTowers.CLK_PORT] = '0'
        # this seems unnecesary
        self.current_status[7-ldac_port] = '1'
        # select cable
        self.current_status[7-cs_port%7] = '0'
        self.write_to_port(self.current_status)
        
        # We send SA and SI first booth need to be high
        self.__sdi__(SA)
        if value > '00000000':
            self.__sdi__(SI)
        else:
            self.__sdi__('0')
        # Next we send A1 and A0
        self.__sdi__(a1)
        self.__sdi__(a0)
        # Now we can send the 8 Value bits
        [self.__sdi__(e) for e in value]
        # unselect cable
        self.current_status[7-cs_port%7] = '1'
        self.write_to_port(self.current_status)
        # And flip Buffer to
        self.current_status[7-ldac_port] = '0'
        self.write_to_port(self.current_status)
        self.current_status[7-ldac_port] = '1'
        self.write_to_port(self.current_status)

    
    def __sdi__(self, bit):
        '''
        Helper functions ending out high or low biut to the sdi port
        the setting off the bit is fellowed by one clock cycle (ON-OFF)
        '''
        self.current_status[7-LEDTowers.SDI_PORT] = bit
        self.write_to_port(self.current_status)
        self.current_status[7-LEDTowers.CLK_PORT] = '1'
        self.write_to_port(self.current_status)
        self.current_status[7-LEDTowers.CLK_PORT] = '0'
        self.write_to_port(self.current_status)      
        
    
    def write_to_port(self, bins, port=0):
        '''
        Method that finally writes data out to the crad
        bins: a list of chars ('1' or '0')with length 8. the list holds the 
        binary 8bit pattern to be written to the io card 
        '''
        #print bins, int(''.join(bins), 2)
#        error = self.io.DO_WritePort(self.card, port, int(''.join(bins), 2));
        error = self.DO_WritePort(self.card, port, int(''.join(bins), 2));
#        print error

class Control(threading.Thread):
    def __init__(self, gui, hardware_abstraction = LEDTowers()):
        threading.Thread.__init__(self) 
        self.gui = gui
        self.last_event_timestamp = 0
        self.led_towers = hardware_abstraction
        self.stop = False
        self.led_towers.write(0, 0, 0, a1='0', a0='0',SA='0',SI='0')
        
    def set_values(self, color_protocol, shock_protocol):        
        #=======================================================================
        # First we cycle through the color protocol and add ColorEvents as 
        # needed into a color event list. After all events have been added we 
        # cycle through the list and calculate the actual timepoints of the 
        # Events. Then we do the same with the Shock protocol. We then combine
        # both events lists and sort it with respect to timepoints. After that
        # we can execute the events in order of the resulting event list 
        self.color_event_list = self.get_color_event_list(color_protocol)
        self.shock_event_list = self.get_shock_event_list(shock_protocol)
        self.color_event_list = self.calculate_timepoints(self.color_event_list)
        self.shock_event_list = self.calculate_timepoints(self.shock_event_list)
        self.color_event_list.extend(self.shock_event_list)
        self.event_list = self.color_event_list
        self.event_list.sort()
        self.stop = False
        
        #=======================================================================
        # Now we can really start sending out the events to the towers
        #=======================================================================
        self.start()
    
    def run(self):
        for counter,event in enumerate(self.event_list):
            if counter<len(self.event_list)-1:
                if self.stop:
                    break
                time_to_next_event = self.event_list[counter+1].start - event.start
                time1 = time.time()
                self.sendEvent(event)
                print 'this event took [s]:', time.time() - time1
                time.sleep(time_to_next_event)
            else:
                self.sendEvent(event)
        # set current off
        self.led_towers.write(0, 0, 0, a1='0', a0='0',SA='0',SI='0')
        self.gui.thread_done()
        threading.Thread.__init__(self)
    
    def idle_event(self, colors):
        event = ColorEvent(0, colors[0], colors[1])
        self.sendEvent(event)
    
    def sendEvent(self, event):
        '''
        Send the Event out to the LED Towers        
        '''      
        if isinstance(event, ShockEvent):
            self.led_towers.send_shock_event(event)
        else:
            self.led_towers.send_light_event(event)
    

    def calculate_timepoints(self, event_list):
        '''
        cycle through event_list and add timpoints to the events as accordingly
        '''
        timepoint = 0
        for event in event_list:
            event.start = timepoint
            timepoint += event.duration
        return event_list
            
    def get_shock_event_list(self, shock_protocol):
        '''
        Create a List of ShockEvents from the entries in shock_protocol
        return: A List of ShockEvents
        '''
        shock_event_list = []
        line_counter = 0
        while line_counter < len(shock_protocol):
            if shock_protocol[line_counter][1]:
                shock_event_list.append(ShockEvent(
                                        shock_protocol[line_counter][1],
                                        shock_protocol[line_counter][2]))
            elif shock_protocol[line_counter][0]:
                new_line_counter = shock_protocol[line_counter][0][0]-1
                shock_protocol[line_counter][0][1] -= 1
                if shock_protocol[line_counter][0][1] == 0:
                    shock_protocol[line_counter][0] = False
                line_counter = new_line_counter
            line_counter += 1
        return shock_event_list  
    
    def get_color_event_list(self, color_protocol):
        '''
        Cretae a List of ColorEvents from the entries in color_protocol
        return: A List of ColorEvents
        '''
        color_event_list = []
        line_counter = 0
        while line_counter < len(color_protocol):
            if color_protocol[line_counter][1]:
                color_event_list.append(ColorEvent(
                                        color_protocol[line_counter][1],
                                        color_protocol[line_counter][2],
                                        color_protocol[line_counter][3]))
            elif color_protocol[line_counter][0]:
                new_line_counter = color_protocol[line_counter][0][0]-1  
                color_protocol[line_counter][0][1]-=1    
                if color_protocol[line_counter][0][1]==0:
                    color_protocol[line_counter][0] = False
                line_counter = new_line_counter   
            line_counter += 1
        return color_event_list
                
                
        
class ColorEvent:
    '''
    Class modeling Color Events. Basically this is a class holding values for
    the values to be send to the LED Towers, event duration and a start 
    timepoint when this events shall occur
    '''
    def __init__(self, duration, blue, green):
        self.duration = duration
        self.blue = blue
        self.green = green
        self.start = 0
    
    def __cmp__(self, other):
        if self.start < other.start:
            return -1
        elif self.start == other.start:
            return 0
        elif self.start > other.start:
            return 1
    def __repr__(self):
        return str((self.start, self.blue, self.green))

class ShockEvent:
    '''
    Class modeling shock Events. Basically this is a class holding values for
    shock intensity, an event duration and a start
    when this events shall occur
    '''
    def __init__(self,duration,intensity):
        self.duration = duration
        self.intensity = intensity
        self.start = 0
    
    def __cmp__(self, other):
        if self.start < other.start:
            return -1
        elif self.start == other.start:
            return 0
        elif self.start > other.start:
            return 1
    def __repr__(self):
        return str((self.start, self.intensity))