

class CoustomObjInFile:

    objs = []

    def get_custom_objs(self,structure):
        for element in structure:
            name = element.get(key("name"))
            # bodylength = element.get(key("bodylength"))
            # bodyoffset = element.get(key("bodyoffset"))
            nameoffset = element.get(key("nameoffset"))
            offset = element.get(key("offset"))
            typename = element.get(key("typename"))

            obj = CustomObj(name,nameoffset,offset,typename)

            self.objs.append(obj)

            substructure = element.get(key("substructure"))
            if substructure:
                self.search_child_substructure(substructure)
                
                continue
            else:
                continue
        return self.objs      


    def search_child_substructure(self,child_substructure):
        for element in child_substructure:
            name = element.get(key("name"))
            nameoffset = element.get(key("nameoffset"))
            offset = element.get(key("offset"))
            typename = element.get(key("typename"))

            obj = CustomObj(name,nameoffset,offset,typename)
            self.objs.append(obj)

            substructure = element.get(key("substructure"))
            if substructure:
                self.search_child_substructure(substructure)
                continue
            else:
                continue



def key(child_key):
    return f"key.{child_key}"

class CustomObj:
    name: str
    nameoffset: int
    offset: int
    typename:str

    def to_map(self):
        map = {}
        map["name"] = self.name
        map["nameoffset"] = self.nameoffset
        map["offset"] = self.offset
        map["typename"] = self.typename
        return map 

    def __init__(self,name,nameoffset,offset,typename):
        self.name = name
        self.nameoffset = nameoffset
        self.offset = offset
        self.typename = typename