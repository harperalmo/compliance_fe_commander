"""
  ComponentIds manages the ids for the axis handler components and the
  command marshaller. Presently, these are mac addresses used for esp-now
  communication protocol.
  
  The component names and their ids are stored in a file who's name is stored
  in the member attribute __storage_name. This is a json file. The components
  include the marshaller attached to the Raspberry pi and the axis handlers on
  the backend. The marshaller and axis handlers are referred to by the strings
  'm', 'x', 'y', 'z', and 't' respectively. The storage file contains a list
  with 2 elements, the first is a dictionary containing the pubic names used
  for labels, etc. that are displayed to the user referenced by the m,x,y,z,t
  strings, e.g. 'y':'y_axis'. the second element is a dictionary of unique ids
  accessed with the m,x,y,x,t strings, e.g. 'z':'c4:dd:57:b8:e8:e8'. Users
  may update the ids as needed. Perhaps in another version, it will be possible
  to change the public names as well, but for this version, only the ids may be
  changed.
"""
import json

class ComponentIdManager:
    """ Manages access to component ids used for communication in the system."""
    
    #component info 
    __storage_name = "componentIds.json" #file storage for component info
    __comp_names_dict = {}  #All component names
    __comp_ids_dict = {}    #Existing components

    
    #constants for type of id return value. See get_id, a method that uses these
    #to specify type of return value
    STRING = 1
    BYTES  = 2
    #for getting keyword names for axis and fmarshaller components. Used when
    #adding a new axis mac id, possibly other things.
        
    def __init__(self):
        
        #read in the current component names and ids. Note that there are public
        #names for each component, but not necassarily an id for each. This
        #allows us to add components programmatically as project development
        #continues

        self.__get_current_names_and_ids() #Populate the component info dicts.
        
        
    def __get_current_names_and_ids(self):
        """Private function used to get component names and current existing
           ids into dictionary. """
        #access the contents of the storage file
        with open(self.__storage_name) as json_file:
            json_data = json.load(json_file)
            self.__comp_names_dict = json_data[0]
            self.__comp_ids_dict = json_data[1]
            json_file.close()
            
                     
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
        """Returns the comm id for the provided keyword or None if the keywork.
           is not found. The format can be used to return the id as either the
           bytes (BYTES)needed for establishing communication (espnow mac id as
           byte string) or as a STRING that can be used to display to users.
           format = [BYTES, STRING]"""
        if keyword in self.__comp_ids_dict:
            id = self.__comp_ids_dict[keyword]
            if format == self.BYTES:
                id = self.mac_str_to_bytes(id)
            return id
        else:
            return None
    
    def get_current_component_names(self):
        """Returns a list of current existing component names"""
        return list(self.__comp_ids_dict.keys())
    
    def get_component_label( self, keyword):
        """returns a component label for one of the component ids, which are
        'm', 'x', 'y', 'z', and 't' for the marshaller and axis handlers"""
        if keyword in self.__comp_names_dict:
            return self.__comp_names_dict[keyword]
        else:
            print("get_compoent_label: KEWORD NOT FOUND!")
            return None
         
    
    def replace_id(self, keyword, id_str):
        """Replaces the id with the passed in string. For espnow, the id must be
        a mac address string in the form hh:hh:hh:hh:hh:hh. If the keyword is
        not already in the dictionary, it will be added. keys better be
        correct, i.e, not up to the user.
        If the id string is None, the particular keyword/value pair willl
        be removed from the component id dictionary if it exists. This allows
        components to be removed during development."""
        update_storage = False
        if keyword in self.__comp_names_dict:
            #check for removal
            if id_str == None:
                if keyword in self.__comp_ids_dict:
                    del self.__comp_ids_dict[keyword] #no id &exists, so remove
                    update_storage = True
                else: #no name and no id string - do nothing
                    update_storage = False
            else: #valid name and non-empty string
                self.__comp_ids_dict.update({keyword:id_str})
                update_storage = True
                
            if update_storage:
                self.__update_storage()
        else:
            print(f'replace_id got bad keyword: {keyword}. Not updating.')

            
    def __update_storage(self):
        """ Updates the storage file to reflect current state of the
            components dictionary. This is done when an id gets updated."""
        #jsonize the dictionary so it can be written into the file
        data = [self.__comp_names_dict, self.__comp_ids_dict]
        new_contents = json.dumps(data, indent = 4)
        f = open(self.__storage_name, "w")
        f.write(new_contents)
        f.close()
        
    
        
if __name__ == "__main__":
    cv = ComponentIdManager()
    print(f"x_axis id in bytes: {cv.get_id('x_axis')}")
    print(f"x_axis id as string: {cv.get_id('x_axis', cv.STRING)}")
    print(f"marshaller id in bytes: {cv.get_id('m')}")
    print(f"marshaller id as string: {cv.get_id('m', cv.STRING)}")
    names = cv.get_current_component_names()
    print(names)
    
    
    
    

                
        
        