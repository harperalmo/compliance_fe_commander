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
print("importing post_office.py")

def letter_from_list( letter_as_list):
    """Can be used to get a letter object from a list in the form
    ['desintation id', 'source id', 'content']. Returns a letter object that
    contains the list values"""
    return Letter(letter_as_list[0], letter_as_list[1], letter_as_list[2])

class Letter:
    """ used to send information from one entity to another. It consists of
    a return address, recipient address, and information"""
    
    def __init__( self, destination_id=None, source_id=None, info=None):
        self._to = destination_id
        self._from = source_id
        self._content = info
        
    def source(self):
        return self._from
    
    def destination(self):
        return self._to
    
    def content(self):
        return self._content
    
    
    def letter_to_list(self):
        return ( [self._to, self._from, self._content])
    
    def letter_from_list( self, letter_as_list):
        """Can be used to get a letter object from a list in the form
        ['desintation id', 'source id', 'content']. Returns a letter object that
        contains the list values. There must be a better way, but one can
        create an empty letter to use to call this: l=Letter(); l.letter_..."""
        return Letter(letter_as_list[0], letter_as_list[1], letter_as_list[2])
    
 #   def unpack(self, packed_letter):
  #      return Letter(packed_letter[0],packed_letter[1], packed_letter[2])
    

class PostOffice:
    """Contains the class PostOffice that is used to send "letters" to objects
    that register with it. A registered object can receive a "letter" from the
    post office that is sent by another object registered with the post office.
    """
   
   
    def __init__(self, msg):
        """initialization. There are no passed-in parms"""
        self._registrants = {}
        self.id_msg = msg


    def register( self, id=None, callback=None):
        """Register with the po so you can send and receive mail. Id is a string
        that identifies the registree. It will be altered if not unique within
        the dictionary key that stores registrant info. callback is a function
        responsible for receiving messages sent to the registrant."""
        self._registrants[id] = callback

    
    def post( self, letter=None):
        """send a letter through the post office."""
        if letter != None:
            cb = self._registrants[letter.destination()]
            cb(letter)
        else:
            print("Letter not supplied! it is None")

if __name__ == "__main__":
    
    class LetterWriter1:
        def __init__(self):
            self.myid = "LW1"
        
        def callback1(self, letter):
            sent_from = letter.source()
            sent_to   = letter.destination()
            info = letter.content()
            print(f"Callback1: {sent_from} sent a letter to {sent_to} stating <{info}>")
            
        def my_id(self):
            return self.myid
        

    class LetterWriter2:
        def __init__(self):
            self.myid = "LW2"
        
        def callback2(self, letter):
            sent_from = letter.source()
            sent_to   = letter.destination()
            info = letter.content()
            print(f"Callback2: {sent_from} sent a letter to {sent_to} stating <{info}>")
        
        def my_id(self):
            return self.myid

    po = PostOffice('module test')
    lw1 = LetterWriter1()
    lw2 = LetterWriter2()

    po.register(lw1.my_id(), lw1.callback1)
    po.register(lw2.my_id(), lw2.callback2)


        