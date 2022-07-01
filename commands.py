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
user of the system. The dict_ attribute can be used to get a command's
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
    """Provides the list of commands for our system. Add new commands to the
    _cmd_list structure. For each command, the following is provided:
    
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
    
    CommandList creates a dictionary attribute called dict_ that can be used to
    lookup     commands by the command name. The value will be the command
    object that allows the various attributes (axes, parm names, blocking needs)
    to be retrieved. Note that the command name is also one of the values. This
    may not be needed but could be useful to insure that the correct command
    object is retrieved.
    
    CommandList also keeps some information for commands, specifically increment
    distance for the increment commands. This needs to be stored on the front
    side for script content and translation from an increment command into a
    distance command that is ultimately given to the backend for processing.

    """
    
    #list of commands that is read in to Command list. Add new commands to this
    #list
    #Format: name is dict keyword, then tuple of axes the command applies to,
    #param names string, and finally a boolean value indicating whether or not
    #the command should be blocking. The axis and param name list should be
    #comma separated.
    _cmd_list = [("get_axis_name","x,y,z,t","", True), #used for comm level
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
             ]
    #This is the dictionary that stores the commands and their attributes. The
    #command name is the keyword and the value for each keyword is the command
    #object
    dict_ = {}
    _need_dict = True  #Used to insure we create the dict only 1 time.
    #Subsequent CommandList instantiations will simply use the already created
    #dict_ sructure.
    
    #Moving by an increment moves in some x or y direction by some speciffied
    #distance. The current assumption is that increments are the same for both
    #x and y axes. The actual distance measurements are in user units, which for
    #now are inches.
    increment_distance = None
    
      
    def __init__(self):
        
        if self.__class__._need_dict:
            for c in self._cmd_list:
                name, axes, parm_names, blocking = c
                assert name, "empty name in command object"
                assert axes, "Commmand axis list empty"
                axis_list = [axis.strip() for axis in axes.strip().split(',')]
                parm_list = [parm.strip() for parm in parm_names.strip().split(',')]

                assert blocking, "Need to specify blocking needs"
            
                cmd = Command(name, axis_list, parm_list, blocking)
                self.__class__.dict_.setdefault(name , cmd)
            self.__class__._need_dict = False
            
    def set_increment(distance):
        self.__class__.increment_distance = distance
        
    def get_command(self, cmd_name, axis, parm_list, blocking):
        #create command list
        print(f"Sending <{cmd_name}> to {axis}, with {parm_list} and blocking = {blocking}.")
        
class CommandInterpreter(QObject):
    '''Responsible for transforming a user-created command into several commands
    to the backend to insure safe movement, more "atomic" commands with respect
    to the axis work needed to carry out the command task, and breaking hybrid
    commands into simpler commands for the backend.'''
    #signals for inter-object communication
    gotNewCommands = pyqtSignal() #tell CommMarshal that commands are available.
    
    def __init__(self):
        super().__init__()
        self.cmds_to_send = [] #CommMarshal will get commands here
    
    
    def send_command(self, name, axis, parm_list, block):
        """ The ui that gets a user-created command should call this to start
        the process that sends the command to the backend  This should be a call
        to the ESP32 over serial comm I believe. NOT an Emit????"""
        print(f"Need to process <{name}>")
        self.gotNewCommands.emit()
        