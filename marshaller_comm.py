"""marshaller_comm.py
class MarshallerComm is used to provide serial communication between the
commander objects and the Marshaller component, which at the time of this
writing is an ESP32 attached to the Pi via serial lines. It appears that PyQt5
never got a QtSerial class to use for serial commmunication.

This code uses ideas found in a blog article called PyQt Serial Terminal.
This blog article is by Jeremy P Bentham, copyright 2019. It is found at
https://iosoft.blog/2019/04/30/pyqt-serial-terminal/

The idea is to run the actual port monitoring functionality as thread. Rather
than direct calls, a queue is used to transfer data btween the main thread
running the gui and the marshaller communication thread. Polling is used to
check for data in a queue that needs to be processed.
"""
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QByteArray, QThread
import serial
import queue
import post_office

TO_MARSHALL_Q_SIZE    = 50
TO_POST_OFFICE_Q_SIZE = 50

class MarshallerComm( QThread ):
    """MarshallerComm handles communications betweeen the marshaller component
    and the post office object. The marshallercomm monitors the serial port
    from a secondary thread that uses polling to check for data coming from
    the marshaller component or post office, send data to the respective
    locaton. Data is posted into queues that are checked by signal/slot methods
    that PyQt5 implements. """
    
    def __init__( self, post_office ):
        QThread.__init__(self)
        self._post_office = post_office
        self._post_office.register('m', self.send_to_marshaller_callback)
        
        self.to_marshall_q    = queue.Queue(TO_MARSHALL_Q_SIZE)
        self.to_post_office_q = queue.Queue(TO_POST_OFFICE_Q_SIZE)
        self.running = True #boolean used to indicate run() should continue.
        
    def send_to_marshaller_callback(self, letter):
        """callback used by post office to start sending data across the
        communication channel to the marshaller component (esp32 via serial)."""
        self.to_marshall_q.put(letter)
        print(f"Marshaller added letter to q. Letter is:")
        print(f"To:      {letter.destination()}")
        print(f"From:    {letter.source()}")
        print(f"Content: {letter.content()}")
        
        
#   def retrieve_marshaller_letter(self):
#    ser = serial.Serial(port     = '/dev/serial0',
#                            baudrate = 115200,
#                            parity   = serial.PARITY_NONE,
#                            stopbits = serial.STOPBITS_ONE,
#                            bytesize = serial.EIGHTBITS,
#                            timeout  = 0. 1 )
 
