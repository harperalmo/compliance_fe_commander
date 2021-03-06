"""data_link.py
NOTE: This was changed from marshaller_comm.py to help differentiate between
the marshaller object that runs on a microprocessor (currently esp32). The
MarshallerComm class has been changed to DataLink. This also makes more sense
if the DataLink is used to send data somewhere else beside the marshaller, eg.
a display for debug info, etc.

class DataLink is used to provide serial communication between the
commander objects and the Marshaller component, which at the time of this
writing is an ESP32 attached to the Pi via serial lines. It appears that PyQt5
never got a QtSerial class to use for serial commmunication.

This code uses ideas found in a blog article called PyQt Serial Terminal.
This blog article is by Jeremy P Bentham, copyright 2019. It is found at
https://iosoft.blog/2019/04/30/pyqt-serial-terminal/

The idea is to run the actual port monitoring functionality as thread. Rather
than direct calls, a queue is used to transfer data btween the main thread
running the gui and the data_link communication thread. Polling is used to
check for data in a queue that needs to be processed.
"""
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot, QByteArray, QThread
import serial
import time
import queue
import post_office
import json

TO_BACKEND_Q_SIZE     = 50
TO_POST_OFFICE_Q_SIZE = 50
SERIAL_TIMEOUT        = 0.1


class DataLink( QThread ):
    """DataLink handles communications betweeen the marshaller component
    and the post office object. The DataLink monitors the serial port
    from a secondary thread that uses polling to check for data coming from
    the marshaller component or post office, send data to the respective
    locaton. Data is posted into queues that are checked by signal/slot methods
    that PyQt5 implements.

    NOTE: There is a time-since-last-transmission check in run() where the
    uart.write occurs to make sure that messages don't get processed to
    quickly. The uart is very slow to get to ready state after a write.
    TODO: Check to see if read poses the same problems.
    """
    
    MY_PO_ID  = "DataLink_1"
    
    def __init__( self, post_office ):
        QThread.__init__(self)
        self._post_office = post_office
        self._post_office.register(self.MY_PO_ID, self.backend_transport_callback)
        
        self.to_backend_q     = queue.Queue(TO_BACKEND_Q_SIZE)
        self.to_post_office_q = queue.Queue(TO_POST_OFFICE_Q_SIZE)
        self.running = True #boolean used to indicate run() should continue.
        
    def backend_transport_callback(self, letter):
        """Post Office calls this to deliver a letter to this DataLink
        object. This will presumably be a command or message for the backend,
        but it could be a message this object well. This method must first check
        to see if it is for us (and deal with it) before sending it on to
        the marshaller component over serial. Any letter placed in to_backend_q
        will be assumed to be headed to the marshaller for processing."""
        
        #TO DO: deal with message to us. Any mail place in the to_backend
        #queue is assumed to be headed to the Marshaller or backend, so
        #mail headed solely to this object must be handled here and NOT placed
        #in the queue.
        
        #Add letter to queue for processing when the run thread activates. Any
        #letter added to the queue is assumed to be for the backend.
        self.to_backend_q.put(letter)
        print(f"mail call for DataLink. Letter is:")
        print(f"To:      {letter.destination()}")
        print(f"From:    {letter.source()}")
        print(f"Content: {letter.content()}")


    def str_bytes(self,s):
        return s.encode('utf-8')


    def uart_receive(self, s):
        if type(s) is str:
            rtn_str = s
        else:
            rtn_str = ""
            for b in s:
                rtn_str = rtn_str + chr(b)
        return( rtn_str)
                
           
    def uart_send(self, s ):
        print(f"uart sending: {s}")
        

    def serialize( self, str_list):
        """ Serializes a list of string elements using json in order to
        transport over uart"""
        return json.dumps(str_list)
    
 
    def run(self):
        """This is the async routine that is used for the thread process. It's
        job is to manage the serial port and move messages to the appropriate
        queues so other routines may process them."""
        
        self.uart = serial.Serial(port     = '/dev/serial0',
                           baudrate = 115200,
                           parity   = serial.PARITY_NONE,
                           stopbits = serial.STOPBITS_ONE,
                           bytesize = serial.EIGHTBITS,
                           timeout  = SERIAL_TIMEOUT)
        time.sleep(SERIAL_TIMEOUT*1.2)
        self.uart.flushInput()
        WRITE_TIME_DELAY = 0.5 #seconds
        start_time = time.perf_counter()
        
        while self.running:
            s = self.uart.read(self.uart.in_waiting or 1)
            if s:
                #We have letter from backend
                msg = self.uart_receive(s)
                #Need to send to PO
                print(f"run got backend message: {msg}")
                
            #Deal with mail addressed to us. Any     
            if not self.to_backend_q.empty():
                letter = self.to_backend_q.get()
                content = letter.content()
                print(f"in run, content: <{content}>")
                #tx_data = str(self.to_backend_q.get())
                send_str = self.serialize(content)
                print(f"after serialize: <{send_str}>")
                #Need a timeout so uart can keep up with cmd processing
                #time.sleep(0.3) #perhaps this should be in the post_office.post
                current_time = time.perf_counter()
                elapsed_time = current_time - start_time
                print(f"st: {start_time}, ct: {current_time}, et = {elapsed_time}")
                start_time = current_time
                if elapsed_time < WRITE_TIME_DELAY:
                    time.sleep( WRITE_TIME_DELAY- elapsed_time)
                    start_time = time.perf_counter()
                self.uart.write(self.str_bytes(send_str))
                
                
        if self.uart:
            self.uart.close()
            self.uart = None
 
