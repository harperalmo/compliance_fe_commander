"""
  ComponentIds manages the ids for the axis handler components and the
  command marshaller. Presently, these are mac addresses used for esp-now
  communication protocol.
  TO DO: Check out use of _component_list and replace, update functionality.
  IT IS BROKEN
"""
import json

class ComponentIdManager:
    """ Manages access to component ids used for communication in the system."""
    
    _storage_name   = "componentIds.json"
    _component_list = []
    _mac_dict= {}
    
    #constants for type of id return value. See get_id, a method that uses these
    #to specify type of return value
    STRING = 1
    BYTES  = 2
    
    def __init__(self):
        print('in init')
        self._get_current_mac_ids()
        
        
    def _get_current_mac_ids(self):
        """Private function used to get current ids into dictionary. The file
        uses dictionary format."""
        #access the contents of the storage file
        with open(self._storage_name) as json_file:
            self._component_list = json.load(json_file)
            self._mac_dict = self._component_list[1]
            print(f"dict read in: {self._mac_dict}")
            print(f"Component list read in: {self._component_list}")
            
                     
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
        return rtn_str.rstrip(':')
  
  
    def get_id(self, keyword, rtn_format=BYTES):
        """Returns the comm id for the provided keyword. The format can be
        used to return the id as either the bytes (BYTES)needed for establishing
        communication (espnow mac id as byte string) or as a STRING that can
        be used to display to users.
        format = [BYTES, STRING]"""
        
        mac_id = self._mac_dict[keyword]
        if rtn_format == self.BYTES:
            mac_id = self.mac_str_to_bytes(mac_id)
        return mac_id
    
    def replace_id(self, keyword, id_str):
        """Replaces the id with the passed in string. For espnow, the id must be
        a mac address string in the form hh:hh:hh:hh:hh:hh."""
        #TODO:   Need to check to make sure keyword exists"
        if keyword in self._component_dict:
            self._component_dict.update({keyword:id_str})
            self._update_storage()
        else:
            printf("replace_id: keyword not found!")
            
    def _update_storage(self):
        """ Updates the storage file to reflect current state of the
            components dictionary. This is done when an id gets updated."""
        #jsonize the dictionary so it can be written into the file
        new_contents = json.dumps(self._component_dict, indent = 4)
        f = open(self._storage_name, "w")
        f.write(new_contents)
        f.close()
        
    
        
if __name__ == "__main__":
    cv = ComponentIdManager()
    print(f"x_axis id in bytes: {cv.get_id('x')}")
    print(f"x_axis id as string: {cv.get_id('x', cv.STRING)}")
    print(f"marshaller id in bytes: {cv.get_id('m')}")
    print(f"marshaller id as string: {cv.get_id('m', cv.STRING)}")
    
    
    

                
        
        