"""
post_office.py

Contains the class PostOffice that is used to send "letters" objects that
register with it. A registered object can receive a "letter" from the post
office that is sent by another object registered with the post office.

Registration is performed by sending a desired id and callback function to
the post office. The id specified is returned from the register call, but it may
be altered to provide unique ids inside the post office instance. The callback
is responsible for sending the message to the appropriate location by whatever
protocol is available.

In order to send a message, command, etc., the info to be sent must be wrapped
in a letter instance. The letter instance contains a recipient address, sender
address (return address), content type (maybe), and the content in packed form
which for now is a json string made from the actual content.

class Letter
The Letter class is used to send information through the post office to other
entities.

"""

class Letter:
    """ used to send information from one entity to another. It consists of
    a return address, recipient address, and information"""
    
    def __init__( self, recipient, sender, info):
        self._to = recipient
        self._from = sender
        self._info = info
    

class PostOffice:
    """Contains the class PostOffice that is used to send "letters" to objects
    that register with it. A registered object can receive a "letter" from the
    post office that is sent by another object registered with the post office.
    """
   
   
    def __init__(self):
        """initialization. There are no passed-in parms"""
        self._registrants = {}


    def register( self, id=None, callback=None):
        """Register with the po so you can send and receive mail. Id is a string
        that identifies the registree. It will be altered if not unique within
        the dictionary key that stores registrant info. callback is a function
        responsible for receiving messages sent to the registrant."""
        self._registrants[id] = callback

    
    def post_letter( self, letter=None):
        """send a letter through the post office."""
        if letter != None:
            print(f"To: {letter._to},  from: {letter._from}, info: {letter._info}")
            cb = self._registrants[letter._to]
            cb(letter)
        else:
            print("send a letter through the post office.")

if __name__ == "__main__":
    
    id1 = "<1>"
    id2 = "<2>"
    
    def cb3(letter):
        print("in cb3")
        print(f"To: {letter._to},  from: {letter._from}, info: {letter._info}")
    
    def cb4(letter):
        print("In cb4")
        print(f"To: {letter._to},  from: {letter._from}, info: {letter._info}")
        