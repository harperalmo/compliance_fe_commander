"""
commands.py

Classes to list commands and their attributes. A command has a name, a possibly
0-length list of parameter names, and whether it should be blocking or
non-blocking

A Command object stores information for a single command.

A CommandList object provides a list of commands and their attributes for the
GUI cmd creation system. Any new command additions should be added to the
CommandList cmd_list attribute.

An instance of CommandList is useful for accessing the list of commands for a
user of the system. The public_dict_ attribute can be used to get a command's
attributes for user choices. Lookup is by command name.

A CommandInterpreter object takes a command created by the user and transforms
it into several more atomic commands. They are more atomic with respect to the
axes. Also move commands will be prefaced by some z and t up commands for
safety reasons. The list of commands will be fed into the cmds_to_send queue and
a message will be sent to the CommMarshal object that there are new commands to
send over to the backend
"""

from PyQt5.QtCore import (pyqtSignal,
                          QObject,
                          )
import post_office

_axis_separator = '&' #used for mutli-axis cmds to separate the axes in display


print("Importing commands.py")

class Command:
    """Stores info for a single command. Probably just for internal use,
but could be used in other areas if needed. Note that its use is to supply
various options for the creation of a specific command to be sent to the
backend, not the specific command itself. Initial use is to populate the UI
with commands for user selection"""
    def __init__(self, name=None, axis_list=None, parm_list=None, blocking=True):
        self.name = name
        self.axis_list = axis_list
        self.parm_list = parm_list
        self.blocking = blocking

        
class CommandList:
    """Provides the list of commands a user can invoke. Add new commands to the
    _public_cmd_list structure. For each command, the following is provided:
    
    name:  This is the name that is used to invoke the command and also is used
    in a dictionary to look up a command and get its other attributes.
    
    axis_list: This lists the axes that the command is valid for. Enter the list
    as a comma separated string. It is unpacked at initialization.
    
    parm_list: This is a list of 0 or more parameter names that the command
    requires. Again, this is a comma-separated string of names. It is also
    unpacked at initialization. If there are no parms, use empty string "" to
    indicate.
    
    blocking: This is a boolean that is True if the command should be a blocking
    call to the backend, False if non-blocking.
    
    CommandList creates a dictionary attribute called public_dict_ that can be used to
    lookup     commands by the command name. The value will be the command
    object that allows the various attributes (axes, parm names, blocking needs)
    to be retrieved. Note that the command name is also one of the values. This
    may not be needed but could be useful to insure that the correct command
    object is retrieved.
    
    CommandList also keeps some information for commands, specifically increment
    distance for the increment commands. This needs to be stored on the front
    side for script content and translation from an increment command into a
    distance command that is ultimately given to the backend for processing.
    
    There is also a similar structure for internal private commands such as
    sending startup info. This is in the _private_cmd_list structure.

    """
    
    #list of commands that is read in to Command list. Add new commands to this
    #list
    #Format: name is dict keyword, then tuple of axes the command applies to,
    #param names string, and finally a boolean value indicating whether or not
    #the command should be blocking. The axis and param name list should be
    #comma separated.
    _public_cmd_list = [("get_axis_name","x,y,z,t","", True), #used for comm level
                 ("move_rel","x,y","distance", True),#move relative - => backwrd
                 ("move_abs","x,y","location", True),#move absolute
                 ("z_down", "z","", True),
                 ("z_up", "z", "", True),
                 ("to_point", "x&y", "x_location,y_location", True),
                 ("set_inc", "x&y", "distance", True),
                 ("inc_left", "x", "", True),
                 ("inc_right", "x", "", True),
                 ("inc_away", "y", "", True),
                 ("inc_towards", "y", "", True),
                 ("set_axis_mac_ids","m","", True),
             ]
    #This is the dictionary that stores the commands and their attributes. The
    #command name is the keyword and the value for each keyword is the command
    #object
    public_dict_ = {}
    _need_public_dict = True  #Used to insure we create the dict only 1 time.
    #Subsequent CommandList instantiations will simply use the already created
    #public_dict_ sructure.
    
    #Moving by an increment moves in some x or y direction by some speciffied
    #distance. The current assumption is that increments are the same for both
    #x and y axes. The actual distance measurements are in user units, which for
    #now are inches.
    increment_distance = None
    
    
    _private_cmd_list = [("set_axis_mac_ids","m","", False), #used for comm level

             ]
    #This is the dictionary that stores dinternal commands and their attributes.
    #The command name is the keyword and the value for each keyword is the
    #command object
    private_dict_ = {}
    _need_private_dict = True  #Used to insure we create the dict only 1 time.
    #Subsequent CommandList instantiations will simply use the already created
    #public_dict_ sructure.
    
    
    
      
    def __init__(self):
        
        if self.__class__._need_public_dict:
            for c in self._public_cmd_list:
                name, axes, parm_names, blocking = c
                assert name, "empty name in command object"
                assert axes, "Commmand axis list empty"
                axis_list = [axis.strip() for axis in axes.strip().split(',')]
                parm_list = [parm.strip() for parm in parm_names.strip().split(',')]

                assert blocking, "Need to specify blocking needs"
            
                cmd = Command(name, axis_list, parm_list, blocking)
                self.__class__.public_dict_.setdefault(name , cmd)
            self.__class__._need_public_dict = False

        if self.__class__._need_private_dict:
            for c in self._private_cmd_list:
                name, axes, parm_names, blocking = c
                assert name, "empty name in command object"
                assert axes, "Commmand axis list empty"
                axis_list = [axis.strip() for axis in axes.strip().split(',')]
                parm_list = [parm.strip() for parm in parm_names.strip().split(',')]

         
                cmd = Command(name, axis_list, parm_list, blocking)
                self.__class__.private_dict_.setdefault(name , cmd)
            self.__class__._need_private_dict = False
            
    def set_increment(self, distance):
        self.__class__.increment_distance = distance
        
    
class CommandInterpreter(QObject):
    '''Responsible for transforming a user-created command into several commands
    to the backend to insure safe movement, more "atomic" commands with respect
    to the axis work needed to carry out the command task, and breaking hybrid
    commands into simpler commands for the backend.'''
    #signals for inter-object communication
  #  gotNewCommands = pyqtSignal() #tell CommMarshal that commands are available.
    
    MY_PO_ID = "CommandInterpreter_1"
    
    def __init__(self, po):
        super().__init__()
        self.cmds_to_send = [] #CommMarshal will get commands here
        print(f"in CmdIntrp, msg in po: {po.id_msg}")
        self.post_office = po
        self.post_office.register(self.MY_PO_ID, self.mail_call)
        
    
    def mail_call( self,letter ):
        print(f"CmdInterp: you've got mail in Cmd_intrp.  {letter}")
        
    
    def create_low_level_public_cmd_list( self, cmd_name, axes,
                                          parm_list, block):
        """takes the parts of a high level command created by the user
        and returns a list of low level commands that are sent along to
        the back end via the marshaller.
        TO DO: Handle mutli-axis commands and safety insertions, e.g. z axis
        up before movement, as well as pause to stop stuff in order to take a
        measurement. Perhaps a gui red/green button is needed to indicate
        pause state...
        NOTE: The passed in parm list may have 0 or more parameters, so
        parsing into command sets need to consider this"""
        
        #Create a single commmand for each axis in a multi-axis command
        axis_list = axes.split(sep=_axis_separator)
        cmds = []
        for axis in axis_list:
            #create cmd list
            print(f'in create_low_level..., parm_list is {parm_list}')
            n = cmd_name; a = axis;
            p = []
            for parm in parm_list:
                p.append(parm)
            cmd = [n, a, p, block]
            print(f"cmds.py.lowlevel: cmd = {cmd}")
            cmds.append(cmd)
        return cmds
    
        
    
    
    def send_command(self, cmd_name, axes, parm_list, block):
        """ The ui that gets a user-created command should call this to start
        the process that sends the command to the backend  This should be a call
        to the ESP32 over serial comm I believe. NOT an Emit????"""
        
        #TOO: Map command into 1 or more lower level commands. This results
        #in a cmd_list that needs to be sent to the marshaller, via the
        #data_link, one at a time
        cmd_list = self.create_low_level_public_cmd_list( cmd_name, axes,
                                                   parm_list, block)
        for cmd in cmd_list:
            letter = post_office.Letter('DataLink_1', self.MY_PO_ID, cmd)
            self.post_office.post(letter)

        #self.gotNewCommands.emit()
        