"""
commmand_main.py
Frontside GUI for sending commands to backend. This is the top level
module for the program. It contains the main routine and starts the
GUI.

Contains the class CmdInputDisplay, which displays the GUI and connects it to
the lower level part of the program.

The commands module contains the CommandsList class that is responsible for
supplying the list of user commands that run the compliance system. After some
processing, commands are sent on to the communications module server_comm's
objects which send the commands on to the backside where a command actually gets
to perform.

There are various qt signal/slot relationships for event updates between these
objects.

TODO:
  Revist axis names. It might be cleaner to use list of lists for axis names
  since some commands are for 1 axis and some are for 2. Instead of 'x,y,z,t'
  we would have [['x'],['y'],['z'],['t']] and instead of 'x&y' we would have
  [['x','y']]. This may cause issues populating the gui fields.

"""

import sys
from PyQt5.QtCore import pyqtSlot, QDataStream, QIODevice, Qt
from PyQt5.QtWidgets import QApplication, QDialog
from PyQt5.uic import loadUi
from functools import partial 




from  post_office import PostOffice, Letter
import commands
import component_ids
import data_link

#Make modules stored in py_compliance_proj/common available
import sys
sys.path.insert(0, '/media/loki9/USBDRV1/softDev/py_compliance_proj/common')



class CmdInputDisplay(QDialog):
    """Dialog for allowing the user to enter commands to send to the backend.
    """
    #Dialog status strings
    START_UP = "Starting up..."
    READY    = "Ready"
    
    def __init__(self):
        super(CmdInputDisplay, self).__init__()
        loadUi('cmd_main.ui', self)

        #initial widget configuration
        self.gBx_chat.setEnabled(False)
        self._status = self.START_UP
        self.lbl_status.setText(self._status)
        
        
        #component setup
        self.__comp_mgr = component_ids.ComponentIdManager()
        self.__current_component_names = self.__comp_mgr.get_current_component_names()
        self.__set_component_labels()       
        

      
        #This dictionary will help populate the mac address boxes. Maybe the
        #boxes are a dumb idea. A string might have worked well
        #WARNING: THESE KEYS NEED TO BE THE SAME AS THE KEYS USED IN STORAGE FILE!!!
        self.__mac_addr_dict = {'m':[self.led_m_ma1,self.led_m_ma2,self.led_m_ma3,self.led_m_ma4,self.led_m_ma5,self.led_m_ma6],
                              'x':[self.led_x_ma1,self.led_x_ma2,self.led_x_ma3,self.led_x_ma4,self.led_x_ma5,self.led_x_ma6],
                              'y':[self.led_y_ma1,self.led_y_ma2,self.led_y_ma3,self.led_y_ma4,self.led_y_ma5,self.led_y_ma6],
                              'z':[self.led_z_ma1,self.led_z_ma2,self.led_z_ma3,self.led_z_ma4,self.led_z_ma5,self.led_z_ma6],
                              't':[self.led_t_ma1,self.led_t_ma2,self.led_t_ma3,self.led_t_ma4,self.led_t_ma5,self.led_t_ma6]}

        
        self.rb_edit_mac.setChecked(False)
        self.__set_mac_boxes_edit_state(True)
        
        self.__load_mac_addresses()
    
      
        self.cmds = commands.CommandList()
        self.__populate_commands()

        self.post_office = PostOffice( "commander_main.py")
        self.cmd_interpreter = commands.CommandInterpreter( self.post_office)
        
        self.data_link = data_link.DataLink(self.post_office)
        
        #signals and slots
        self.rb_edit_mac.toggled.connect(self.on_edit_mac_toggle)
        self.pBtn_send_message.clicked.connect(self.send_command_to_client)
        self.pBtn_close.clicked.connect(self.close_dlg)
        self.cBx_command.currentTextChanged.connect(self.command_changed)
        
        self.rb_edit_mac.setChecked(False)
        self.pBtn_save_m_mac.clicked.connect(lambda: self.on_save_btn_clicked('m'))
        self.pBtn_save_x_mac.clicked.connect(lambda: self.on_save_btn_clicked('x'))
        self.pBtn_save_y_mac.clicked.connect(lambda: self.on_save_btn_clicked('y'))
        self.pBtn_save_z_mac.clicked.connect(lambda: self.on_save_btn_clicked('z'))
        self.pBtn_save_t_mac.clicked.connect(lambda: self.on_save_btn_clicked('t'))
        
        self.data_link.start()
        self.ready_for_business()
        
    def __set_component_labels(self):
        """Adds text lables to the gui labels identifying the ids for the
           components."""
        self.lbl_m.setText( self.__comp_mgr.get_component_label('m'))
        self.lbl_x.setText( self.__comp_mgr.get_component_label('x'))
        self.lbl_y.setText( self.__comp_mgr.get_component_label('y'))
        self.lbl_z.setText( self.__comp_mgr.get_component_label('z'))
        self.lbl_t.setText( self.__comp_mgr.get_component_label('t'))
        
    def __load_mac_addresses(self):
        """Populates the mac address table"""
        for name in self.__current_component_names:
            mac_addr = self.__comp_mgr.get_id( name, self.__comp_mgr.STRING)
            mac_boxes = self.__mac_addr_dict[name]
            mac_vals = mac_addr.split(':')
            for(widget, mac_val) in zip(mac_boxes, mac_vals):
                widget.setText(mac_val)
                
 
    def __populate_commands(self):
        """Needs refactoring and cleanup"""
        cmd_list = list(self.cmds.dict_.keys())
        self.cBx_command.setMaxCount(len(cmd_list))
        self.cBx_command.addItems(cmd_list)
        
        self.update_command_attribs( cmd_list[0])
        
    
    def __set_mac_boxes_edit_state(self, state):
        """sets the mac address boxes to either read only or editable."""
        box_lists = self.__mac_addr_dict.values()
        for box_list in box_lists:
            for box in box_list:
                box.setReadOnly(state)
                   
        
    def on_edit_mac_toggle(self):
        if self.rb_edit_mac.isChecked() == True:
            enabled_state = True
            read_only     = False
        else:
            enabled_state = False
            read_only     = True
        
        self.__set_mac_boxes_edit_state(read_only)
        self.pBtn_save_m_mac.setEnabled(enabled_state)
        self.pBtn_save_x_mac.setEnabled(enabled_state)
        self.pBtn_save_y_mac.setEnabled(enabled_state)
        self.pBtn_save_z_mac.setEnabled(enabled_state)
        self.pBtn_save_t_mac.setEnabled(enabled_state)



    def update_command_attribs(self, command):
        #get the command object
        cmd = self.cmds.dict_[command]
        #check parm list for number of parms and hide/show needed parm edits
        parms = cmd.parm_list
        parm_count = len(parms)
        assert 0 < parm_count < 3, "parm count is wrong"
        if parm_count == 2:
            self.display_parm_field( self.lbl_parm1, self.le_parm1, parms[0])
            self.display_parm_field( self.lbl_parm2, self.le_parm2, parms[1])
        elif parm_count ==1 and len(parms[0]) != 0:
            self.hide_parm_field(self.lbl_parm2, self.le_parm2)
            self.display_parm_field( self.lbl_parm1, self.le_parm1, parms[0])
        else:
            self.hide_parm_field(self.lbl_parm1, self.le_parm1)
            self.hide_parm_field(self.lbl_parm2, self.le_parm2)
            
        axes = cmd.axis_list
        self.cBx_axis.setMaxCount(0)
        self.cBx_axis.setMaxCount(len(axes))
        self.cBx_axis.addItems(axes)
            
    def display_parm_field(self, label, edit_field, parm_name):
         label.setText(parm_name)
         label.show()
         edit_field.show()
         
    def hide_parm_field(self, label, edit_field):
          label.hide()
          edit_field.hide()
          
       
    def command_changed(self, command):
        self.update_command_attribs( command)

        
    @pyqtSlot()
    def ready_for_business(self):
        self._status=self.READY
        self.lbl_status.setText(self._status)
        self.gBx_chat.setEnabled(True)
        self.pBtn_send_message.setEnabled(True)
    
    
    def on_save_btn_clicked(self, axis):
        """ Reads id from gui boxes, forms id string and sends to the
        component id manager for an update of the id for that component."""
        mb = self.__mac_addr_dict[axis]
        id_str = mb[0].text() +':' + mb[1].text() +':'+ mb[2].text() +':' + \
                 mb[3].text() + ':' + mb[4].text() +':' + mb[5].text()
        print(f'on_save_btn id str: {id_str}')
        if len(id_str )<= len(':::::'):
               id_str = None
        self.__comp_mgr.replace_id(axis, id_str)
        self.rb_edit_mac.setChecked(False)
        
    
    @pyqtSlot()
    def send_command_to_client(self):
        name = self.cBx_command.currentText()
        axis = self.cBx_axis.currentText()
        parm_list = []
        if self.lbl_parm1.isVisible():
            parm_list.append( (self.lbl_parm1.text().strip(), self.le_parm1.text().strip()))
        if self.lbl_parm2.isVisible():
            parm_list.append( (self.lbl_parm2.text().strip(), self.le_parm2.text().strip()))
        block = self.cmds.dict_[name].blocking
        self.cmd_interpreter.send_command( name, axis, parm_list, block )
    
    @pyqtSlot()
    def close_dlg(self):
        self.reject()
        
    
    
def main():
    app = QApplication(sys.argv)
    dlg=CmdInputDisplay()
    dlg.show()
    sys.exit(app.exec ())

if __name__=="__main__":
    main()