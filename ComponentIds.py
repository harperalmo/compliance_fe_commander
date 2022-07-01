"""
  ComponentIds manages the ids for the axis handler components and the
  command marshaller. Presently, these are mac addresses used for esp-now
  communication protocol.
"""
import json

class ComponentIdManager:
    """ Manages access to component ids used for communication in the system."""
    
    __storage_name = "componentIds.json"
    __component_dict = {}
    
    #constants for type of id return value. See get_id, a method that uses these
    #to specify type of return value
    STRING = 1
    BYTES  = 2
    
    def __init__(self):
        print('in nit')
        self.__component_dict = {}
        self.__get_current_ids()
        
        
    def __get_current_ids(self):
        """Private function used to get current ids into dictionary. The file
        uses dictionary format."""
        #access the contents of the storage file
        with open(self.__storage_name) as json_file:
            self.__component_dict = json.load(json_file)
            print(f"dict read in: {self.__component_dict}")
            
                     
    def mac_str_to_bytes(self, mac_str):
        """ given a mac address as a string in the form hh:hh:hh:hh:hh:hh,
        the equivalent valued byte array is returned that can be used to
        specify components for comm"""
        mac_vals = mac_str.split(':')
        mac_addr_bytes = [int(b, 16) for b in mac_vals]
            
        return bytes(mac_addr_bytes)
        
    def mac_bytes_to_str(self,mac_addr_bytes):
        """converts a mac address in byte string form to mac address as
            a string in the form hh:hh:hh:hh:hh:hh"""
        rtn_str = ""
        b_array = list(mac_addr_bytes)
        for v in b_array:
            v_str = str(hex(v))
            v_str = v_str.lstrip('0x')
            if len(v_str) == 1:
                v_str = '0'+v_str
            rtn_str = rtn_str + v_str + ':'
            
        rtn_str.rstrip(':')
        return rtn_str
        
    def get_id(self, keyword, format=BYTES):
        """Returns the comm id for the provided keyword. The format can be
        used to return the id as either the bytes (BYTES)needed for establishing
        communication (espnow mac id as byte string) or as a STRING that can
        be used to display to users.
        format = [BYTES, STRING]"""
        
        id = self.__component_dict[keyword]
        if format == self.BYTES:
            id = self.mac_str_to_bytes(id)
        return id
    
    def replace_id(self, keyword, id_str):
        """Replaces the id with the passed in string. For espnow, the id must be
        a mac address string in the form hh:hh:hh:hh:hh:hh."""
        #TODO:   Need to check to make sure keyword exists"
        if keyword in self.__component_dict:
            self.__component_dict.update({keyword:id_str})
            self.__update_storage()
        else:
            printf("replace_id: keyword not found!")
            
    def __update_storage(self):
        """ Updates the storage file to reflect current state of the
            components dictionary. This is done when an id gets updated."""
        #jsonize the dictionary so it can be written into the file
        new_contents = json.dumps(self.__component_dict, indent = 4)
        f = open(self.__storage_name, "w")
        f.write(new_contents)
        f.close()
        
    
        
if __name__ == "__main__":
    cv = ComponentIdManager()
    print(f"x_axis id in bytes: {cv.get_id('x_axis')}")
    print(f"x_axis id as string: {cv.get_id('x_axis', cv.STRING)}")
    print(f"marshaller id in bytes: {cv.get_id('marshaller')}")
    print(f"marshaller id as string: {cv.get_id('marshaller', cv.STRING)}")
    
    
    

                
        
        