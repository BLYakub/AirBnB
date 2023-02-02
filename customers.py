class customers:
    def __init__(self, fname, lname, password, id, email):
        self.__fname = fname
        self.__lname = lname
        self.__password = password
        self.__id = id
        self.__email = email
    
    @property 
    def fname(self):
        return self.__fname
    @fname.setter
    def fname(self, fname):
        self.__fname = fname

    @property
    def lname(self):
        return self.__lname
    @lname.setter
    def lname(self, lname):
        self.__lname = lname
    
    @property
    def id(self):
        return self.__id
    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def email(self):
        return self.__email
    @email.setter
    def email(self, email):
        self.__email = email

    @property
    def password(self):
        return self.__password
    @password.setter
    def password(seld, password):
        seld.__password = password
