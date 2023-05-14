class Member:
    def __init__(self,uid,name,birth):
        self.uid = uid
        self.name = name
        self.birth = birth
        
    def __json__(self):
        return {
            'uid' : self.uid,
            'name' : self.name,
            'birth' : self.birth,
        }
        
class livestock:
    def __init__(self,uid,livestock_type,name,cattle,is_pregnancy = False,num = None):
        self.uid = uid
        self.livestock_type = livestock_type
        self.num = num
        self.name = name
        self.cattle = cattle
        self.is_pregnancy = is_pregnancy
    def __json__(self):
        return {
            'uid' : self.uid,
            'livestock_type' : self.livestock_type,
            'num' : self.num,
            'name' : self.name,
            'cattle' : self.cattle,
            'is_pregnancy' : self.is_pregnancy
        }

class cam:
    def __init__(self,uid,livestock_type,num = None):
        self.uid = uid
        self.livestock_type = livestock_type
        self.num = num
        
    def __json__(self):
        return {
            'uid': self.uid,
            'livestock_type': self.livestock_type,
            'num': self.num
        }