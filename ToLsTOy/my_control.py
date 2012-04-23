import time

class Control:
    def __init__(self, main_frame):
        self.main_frame = main_frame
        self.last_event_timestamp = 0
    
    def start(self, color_protocol, shock_protocol):        
        #=======================================================================
        # First we cycle through the color protocol and add ColorEvents as 
        # needed into a color event list. After all events have been added we 
        # cycle through the list and calculate the actual timepoints of the 
        # Events. Then we do the same with the Shock protocol. We then combine
        # both events lists and sort it with respect to timepoints. After that
        # we can execute the events in order of the resulting event list 
        #=======================================================================
        color_event_list = self.get_color_event_list(color_protocol)
        shock_event_list = self.get_shock_event_list(shock_protocol)
        color_event_list = self.calculate_timepoints(color_event_list)
        shock_event_list = self.calculate_timepoints(shock_event_list)
        color_event_list.extend(shock_event_list)
        event_list = color_event_list
        event_list.sort()
        
        #=======================================================================
        # Now we can really start sending out the events to the towers
        #=======================================================================
        for counter,event in enumerate(event_list):
            if counter<len(event_list)-1:
                time_to_next_event = event_list[counter+1].start - event.start
                self.sendEvent(event)
                time.sleep(time_to_next_event/1000.0)
            else:
                self.sendEvent(event)
                
        print event_list
    
    def sendEvent(self,event):
        '''
        Send teh Evnt out to the LED Towers        
        '''
        new_last_event_timestamp = time.time()
        print event, self.last_event_timestamp -  new_last_event_timestamp
        self.last_event_timestamp = new_last_event_timestamp
    
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
    def __init__(self,duration,left,right):
        self.duration = duration
        self.left = left
        self.right = right
        self.start = 0
    
    def __cmp__(self, other):
        if self.start < other.start:
            return -1
        elif self.start == other.start:
            return 0
        elif self.start > other.start:
            return 1
    def __repr__(self):
        return str((self.start, self.left, self.right))

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

class LEDTowers:
    '''
    Class modelig the LED Towers. it interfaces the IO Card end send out the 
    messages. It also keeps track of current status etc.
    '''
    SDI_PORT = 0
    CLK_PORT = 1
    LDAC1_PORT = 2
    LDAC2_PORT = 3
    LDAC3_PORT = 4
    CS1_PORT = 5
    CS2_PORT = 6
    CS3_PORT = 7    