#-------------------------------------------------------------------------------
# Copyright (c) 2015 Christian Garbers.
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Simplified BSD License
# which accompanies this distribution
# 
# Contributors:
#     Christian Garbers - initial API and implementation
#-------------------------------------------------------------------------------
from Tkinter import *
import re
import tkMessageBox
import tkFileDialog
import my_control
import copy

class MainFrame(Text):    
    def __init__(self, parent, control = my_control.Control):
        control = control(self)
        scrollbar = Scrollbar(parent)
        Text.__init__(self, parent,bg='grey',yscrollcommand=scrollbar.set)
        parent.title('ToLsTOy - Twenty Led Tower cOntrol')
        scrollbar.config(command=self.yview)
        self.idle_frame = IdleFrame(self)
        self.idle_frame.grid(row=0,column=0)
        self.button_ico_frame = Frame(self) 
        self.start_all_button = Button(self.button_ico_frame, text="Start", 
                                       command=self.start_all)        
        icon = Canvas(self.button_ico_frame,width=64, height=64)
        self.bitmap = PhotoImage(file="ColSymb.gif")
        icon.create_image((32,32),image=self.bitmap)
        icon.grid(row=0,column=0, sticky=W)
        self.start_all_button.grid(row=0,column=1, sticky=E)
        self.button_ico_frame.grid(row=0,column=1, sticky=W+E)
        self.color_table = LightTable(self)
        self.color_table.grid(row=1,column=0,sticky=N)        
        self.shock_table = ShockTable(self)
        self.shock_table.grid(row=1,column=1,sticky=N)
        self.grid(column=0,row=0)
        scrollbar.grid(column=1,row=0)
        self.control = control
        

    def start_all(self):
        '''
        Method called by hitting the start Button
        '''
        
        color_protocol = self.color_table.get_all_values()
        shock_protocol = self.shock_table.get_all_values()
        
        if color_protocol and shock_protocol:
            print 'hello'
            self.config(bg='red')
            self.button_ico_frame.config(bg='red')
            self.start_all_button = Button(self.button_ico_frame, text="Stop", 
                                       command=self.stop)
            self.start_all_button.grid(row=0,column=1, sticky=E)
            self.update()
            self.control.set_values(color_protocol, shock_protocol)
    
    def stop(self):
        self.control.stop = True

    def thread_done(self):
        self.start_all_button = Button(self.button_ico_frame, text="Start", 
                                       command=self.start_all)
        self.start_all_button.grid(row=0,column=1, sticky=E)
        self.config(bg='grey')
        self.button_ico_frame.config(bg='grey')

class IdleFrame(Frame):
    '''
    Class modeling the Idle Frame
    '''
    def __init__(self, parent):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=3)
        self.parent = parent
        Label(self, text="Idle colors for all", fg="black").grid(row=0)
        Label(self, text="blue:", fg="black",relief=SUNKEN, 
                     borderwidth=1, justify=RIGHT).grid(row=1, column=0, 
                                                        sticky=E)
        self.blue = Text(self,height=1,width=15)
        self.blue.insert(END, '000,000,000,000')
        self.blue.grid(row=1, column=1)
        Label(self,text="syntax: A,B,C,D", fg="black").grid(row=1, column=2)
        Label(self, text="green:", fg="black",relief=SUNKEN, 
                     borderwidth=1, justify=RIGHT).grid(row=2, column=0, 
                                                        sticky=E)
        self.green = Text(self,height=1,width=15)
        self.green.insert(END, '000,000,000,000')
        self.green.grid(row=2, column=1)
        self.blue.bind('<KeyRelease>',self.key_pressed)
        self.green.bind('<KeyRelease>',self.key_pressed)
    
    def get_colors(self):
        '''
        returns the colors set by the user in this frame
        returns: ([blue_A,blue_B,blue_C,blue_D],[green_A,green_B,green_C,green_D])
        '''
        # Error checking needed
        pattern ='\d+,\d+,\d+,\d+$'
        if re.match(pattern, self.blue.get(1.0, END)) and re.match(pattern, self.green.get(1.0, END)):
            self.config(bg='green')
            return ([int(e) for e in self.blue.get(1.0, END)[:15].split(',')],
               [int(e) for e in self.green.get(1.0, END)[:15].split(',')])
        else:
            self.config(bg='red')
            return 0
        
    def key_pressed(self, event):
        colors = self.get_colors()
        if colors:
            self.parent.control.idle_event(colors)
            
class  ProtocolTable(Frame):
    '''
    This class models the Table which describes who the application should 
    change the LEDs over time. In some sense it is the experiment protokol
    '''
    def __init__(self, parent, colums, colsizes):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=3)
        self.parent = parent
        self.colsizes = colsizes
        self.rows=[]
        self.load_button = Button(self,text="Load", command=self.load)
        self.load_button.grid(row=0,columnspan=5,sticky=W+E)
        self.save_button = Button(self,text="Save", command=self.save)
        self.save_button.grid(row=1,columnspan=5,sticky=W+E)
        for counter,col in enumerate(colums):
            Label(self, text=col, fg="black",relief=SUNKEN, 
                     borderwidth=0, justify=RIGHT).grid(row=2, column=counter)
        self.row_offset = 3
        self.add_row(3)
        
    def add_row(self, row):
        self.rows.insert(row-self.row_offset, TableRow(self,row,
                                                       cols=self.colsizes))
        for counter,row in enumerate(self.rows):
            row.row = self.row_offset+counter
            row.grid()
    
    def get_all_values(self):
        result = [e.get_all_values() for e in self.rows]
        if result.count(False):
            return False
        else:
            result
    
    def save(self):
        _file = tkFileDialog.asksaveasfile(mode='w')
        data = self.get_all_values()
        if data:
            for e in data[:-1]:
                for i in e:
                    _file.write('%s\t'%i)
                _file.write('\n')
    
    def load(self):
        _file = tkFileDialog.askopenfile(mode='r')
        txt = _file.readlines()
        txt.reverse()
        self.rows=[]
        for counter,e in enumerate(txt):
            this_row = [eval(i.strip('\n')) for i in e.split('\t')[:-1]]
            self.add_row(self.row_offset)
            row = self.rows[0]
            for text,this_text in zip(row.texts[1:],this_row):
                if this_text:
                    event = dummy()
                    event.widget = text
                    text.insert(1.0,str(this_text).strip(']').strip('[').replace(' ',''))
                    self.text_field_change(event)
    
    def text_field_change(self, event):
        row = int(event.widget.grid_info()['row'])
        row = self.rows[row-self.row_offset]
        column = int(event.widget.grid_info()['column'])
        if column == 1:
            if len(event.widget.get(1.0,END))>1:
                [e.delete(1.0, END) for e in row.texts[2:]]
                [e.config(bg='black',state=DISABLED) for e in row.texts[2:]]
            else:
                [e.config(bg='white', state=NORMAL) for e in row.texts[2:]]
            
            value = re.findall('\d+,\d+', event.widget.get(1.0,END))
            if value:
                event.widget.config(bg='green')
                value = value[0].split(',')
                row.values[column-1] = [int(value[0]),int(value[1])]
            elif not len(event.widget.get(1.0,END))>1:
                event.widget.config(bg='white')
                row.values[column-1] = False
            else:
                event.widget.config(bg='red')
                row.values[column-1] = False                

        elif column == 2:
            if len(event.widget.get(1.0,END))>1:
                row.texts[1].delete(1.0, END)
                row.texts[1].config(bg='black',state=DISABLED)
            else:
                row.texts[1].config(bg='white', state=NORMAL)
            
            value = re.findall('\d+$|\d+\.\d+', event.widget.get(1.0,END))
            if value:
                event.widget.config(bg='green')
                value = float(value[0])
                row.values[column-1] = value
            
            elif not len(event.widget.get(1.0,END))>1:
                event.widget.config(bg='white')
                row.values[column-1] = False
            else:
                event.widget.config(bg='red')
                row.values[column-1] = False
        
        

class LightTable(ProtocolTable):
    '''
    Class modeling the Color Table in the GUI
    '''
    def __init__(self, parent):
        ProtocolTable.__init__(self, parent,
                               ['line','jmp,#','time[s]','Blue','Green'],
                               [8,8,8,15,15])    
    def get_all_values(self):
        '''
        Evaluate the Lines of the Light Table
        Show a Dialog when an mismatch happend and return False
        Return the well formatted lines otherwise        
        '''
        result = [e.values for e in self.rows]
        result = copy.deepcopy(result)
        result.append([False,1,[0,0,0,0],[0,0,0,0]])
        return result
    
    def text_field_change(self, event):
        ProtocolTable.text_field_change(self, event)
        row = int(event.widget.grid_info()['row'])
        row = self.rows[row-self.row_offset]
        column = int(event.widget.grid_info()['column'])
        if column >= 3 :
            value = re.findall('\d+,\d+,\d+,\d+', event.widget.get(1.0,END))
            if value:
                event.widget.config(bg='green')
                value = value[0].split(',')
                row.values[column-1] = [int(e) for e in value]
            elif not len(event.widget.get(1.0,END))>1:
                event.widget.config(bg='white')
                row.values[column-1] = False
            else:
                event.widget.config(bg='red')
                row.values[column-1] = False             

                

class ShockTable(ProtocolTable):
    '''
    Class modeling the Shock Table in the GUI
    '''
    def __init__(self,parent):
        ProtocolTable.__init__(self, parent, 
                               ['line','jmp,#','time[s]','Intensity'],[8,8,8,8])   
    
    def get_all_values(self):
        '''
        Evaluate the Lines of the Light Table
        Show a Dialog when an mismactch happens and return False
        Return the well formatted lines otherwise        
        '''
        result = [e.values for e in self.rows]
        result.append([False,1,0])
        return result
    
    def text_field_change(self, event):
        ProtocolTable.text_field_change(self, event)
        row = int(event.widget.grid_info()['row'])
        row = self.rows[row-self.row_offset]
        column = int(event.widget.grid_info()['column'])
        if column >= 3 :
            value = re.findall('\d+', event.widget.get(1.0,END))
            if value:
                event.widget.config(bg='green')
                row.values[column-1] = int(value[0])
            elif not len(event.widget.get(1.0,END))>1:
                event.widget.config(bg='white')
                row.values[column-1] = False
            else:
                event.widget.config(bg='red')
                row.values[column-1] = False   
    
class TableRow:
    def __init__(self, parent, row, cols =[3,7,7,7,7] ):
        self.parent = parent
        self.texts = []
        self.row = row
        for counter,col in enumerate(cols):
            _tmp = Text(parent,height=1,width=col,borderwidth=0)
            _tmp.grid(row=row, column = counter)
            _tmp.bind('<KeyRelease>', parent.text_field_change)
            self.texts.append(_tmp)
        self.texts[0].insert(END, row)
        self.texts[0].config(state=DISABLED)
        #self.texts[1].bind('<KeyRelease>', self.jumper_line_changed)
        #self.texts[2].bind('<KeyRelease>', self.time_line_changed)
        self.add_line = Button(parent,text='add',command=self.add_row, height=1)
        self.add_line.grid(row=row,column=5)        
        self.values = [False for e in cols]
    
#    def jumper_line_changed(self, event):
#        if len(self.texts[1].get(1.0,END))>1:
#            [e.delete(1.0, END) for e in self.texts[2:]]
#            [e.config(bg='red',state=DISABLED) for e in self.texts[2:]]
#        else:
#            [e.config(bg='white', state=NORMAL) for e in self.texts[2:]]
#    
#    def time_line_changed(self, event):
#        if len(self.texts[2].get(1.0,END))>1:
#            self.texts[1].delete(1.0, END) 
#            self.texts[1].config(bg='red',state=DISABLED)
#        else:
#            self.texts[1].config(bg='white', state=NORMAL)
    
    def add_row(self):
        self.parent.add_row(self.row)

    def grid(self):
        for counter, text in enumerate(self.texts):
            text.grid_forget()
            text.grid(row=self.row, column=counter)
        self.add_line.grid_forget()
        self.add_line.grid(row=self.row, column=len(self.texts))
        self.texts[0].config(state=NORMAL)
        self.texts[0].delete(1.0,END)
        self.texts[0].insert(END, self.row-self.parent.row_offset)
        self.texts[0].config(state=DISABLED)
        
    def get_all_values(self):
        return [e.get(1.0,END) for e in self.texts]

class dummy:
    pass  
if __name__ == '__main__':
    root = Tk()
    app = MainFrame(root)
    root.mainloop()
