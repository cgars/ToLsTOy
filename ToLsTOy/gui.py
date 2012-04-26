from Tkinter import *
import re
import tkMessageBox
import my_control

class MainFrame(Text):    
    def __init__(self, parent, control = my_control.Control()):
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
            self.control.start(color_protocol, shock_protocol)

class IdleFrame(Frame):
    '''
    Class modeling the Idle Frame
    '''
    def __init__(self, parent):
        Frame.__init__(self, parent, relief=RIDGE, borderwidth=3)
        self.parent = parent
        Label(self, text="Idle colors for all", fg="black").grid(row=0)
        Label(self, text="left color:", fg="black",relief=SUNKEN, 
                     borderwidth=1, justify=RIGHT).grid(row=1, column=0, 
                                                        sticky=E)
        self.left_color = Text(self,height=1,width=7)
        self.left_color.insert(END, '000,000')
        self.left_color.grid(row=1, column=1)
        Label(self,text="syntax: green,blue", fg="black").grid(row=1, column=2)
        Label(self, text="right color:", fg="black",relief=SUNKEN, 
                     borderwidth=1, justify=RIGHT).grid(row=2, column=0, 
                                                        sticky=E)
        self.right_color = Text(self,height=1,width=7)
        self.right_color.insert(END, '000,000')
        self.right_color.grid(row=2, column=1)
        self.left_color.bind('<KeyRelease>',self.key_pressed)
    
    def get_colors(self):
        '''
        returns the colors set by the user in this frame
        returns: ([left_green,left_blue],[right_green,right_blue])
        '''
        # Error checking needed
        pattern ='\d+,\d+$'
        if re.match(pattern, self.left_color.get(1.0, END)):
            self.config(bg='green')
            return ([int(e) for e in self.left_color.get(1.0, END)[:7].split(',')],
               [int(e) for e in self.right_color.get(1.0, END)[:7].split(',')])
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
    
    def load(self):
        pass
    def save(self):
        data = self.get_all_values()
        if data:
            print data

class LightTable(ProtocolTable):
    '''
    Class modeling the Color Table in the GUI
    '''
    def __init__(self, parent):
        ProtocolTable.__init__(self, parent,
                               ['line','jmp,#','time[s]','G_l,B_l','G_r,B_r'],
                               [8,8,8,8,8])    
    def get_all_values(self):
        '''
        Evaluate the Lines of the Light Table
        Show a Dialog when an mismatch happend and return False
        Return the well formatted lines otherwise        
        '''
        result = []
        for line in [e.get_all_values() for e in self.rows]:
            _tmp_result = [False,False,False,False]
            # check jmp line
            if  len(line[1])>1:
                pattern = 'd+,\d+$'
                value = re.findall(pattern, line[1])
                if value:
                    value = value[0]
                    value = value.split(',')
                    _tmp_result[0]=[int(value[0]),int(value[1])]
                else:
                    tkMessageBox.showerror(
                    'Uh Oh', 'Error in Line %s with column jmp;#'%line[0])
                    return False
            # check time line
            if  len(line[2])>1:
                pattern = '\d+$|\d+\.\d+'
                value = re.findall(pattern, line[2])
                if value:
                    value = value[0]
                    value = float(value)
                    _tmp_result[1]=int(value)
                else:
                    tkMessageBox.showerror(
                    'Uh Oh', 'Error in Line %s with column time[s];#'%line[0]) 
                    return False  
            
            # check left led line
            if  len(line[3])>1:
                pattern = '\d+,\d+'
                value = re.findall(pattern, line[3])
                if value:
                    value = value[0]
                    value = value.split(',')
                    _tmp_result[2]=[int(value[0]),int(value[1])]
                else:
                    tkMessageBox.showerror(
                    'Uh Oh', 'Error in Line %s with column G_l,B_l;#'%line[0])
                    return False
            
            # check right led line
            if  len(line[4])>1:
                pattern = '\d+,\d+'
                value = re.findall(pattern, line[4])
                if value:
                    value = value[0]
                    value = value.split(',')
                    _tmp_result[3]=[int(value[0]),int(value[1])]
                else:
                    tkMessageBox.showerror(
                    'Uh Oh', 'Error in Line %s with column G_r,B_r;#'%line[0])
                    return False
            result.append(_tmp_result)
        result.append([False,1,self.parent.idle_frame.get_colors()[0],
                       self.parent.idle_frame.get_colors()[1]])
        return result

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
        result = []
        for line in [e.get_all_values() for e in self.rows]:
            _tmp_result = [False,False,False]
            # check jmp line
            if  len(line[1])>1:
                pattern = '\d+,\d+$'
                value = re.findall(pattern, line[1])
                if value:
                    value = value[0]
                    value = value.split(',')
                    _tmp_result[0]=[int(value[0]),int(value[1])]
                else:
                    tkMessageBox.showerror(
                    'Uh Oh', 'Error in Line %s with column jmp,#'%line[0])
                    return False
            # check time line
            if  len(line[2])>1:
                pattern = '\d+$|\d+\.\d+'
                value = re.findall(pattern, line[2])
                if value:
                    value = value[0]
                    value = float(value)
                    _tmp_result[1]=int(value)
                else:
                    tkMessageBox.showerror(
                    'Uh Oh', 'Error in Line %s with column time[s];#'%line[0]) 
                    return False  
            # check shock line
            if  len(line[3])>1:
                pattern = '\d+$'
                value = re.findall(pattern, line[3])
                if value:
                    value = value[0]
                    _tmp_result[2] = int(value)
                else:
                    tkMessageBox.showerror(
                    'Uh Oh', 'Error in Line %s with column Intensity;#'%line[0])
                    return False
            result.append(_tmp_result)
        result.append([False,1,0])
        return result
    
class TableRow:
    def __init__(self, parent,row, cols =[3,7,7,7,7] ):
        self.parent = parent
        self.texts = []
        self.row = row
        for counter,col in enumerate(cols):
            _tmp = Text(parent,height=1,width=col,borderwidth=0)
            _tmp.grid(row=row, column = counter)
            self.texts.append(_tmp)
        self.texts[0].insert(END, row)
        self.texts[0].config(state=DISABLED)
        self.add_line = Button(parent,text='add',command=self.add_row, height=1)
        self.add_line.grid(row=row,column=5)
        

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
    
if __name__ == '__main__':
    root = Tk()
    app = MainFrame(root)
    root.mainloop()