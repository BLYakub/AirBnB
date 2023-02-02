class offers:
    def __init__(self, ID_seller, address, num_rooms, price, conditions, start_date, end_date, pics):
        self.__ID_seller = ID_seller
        self.__address = address
        self.__num_rooms = num_rooms
        self.__price = price
        self.__conditions = conditions
        self.__start_date = start_date
        self.__end_date = end_date
        self.__pics = pics

    @property 
    def ID_seller(self):
        return self.__ID_seller
    @ID_seller.setter
    def ID_seller(self, ID_seller):
        self.__ID_seller = ID_seller

    @property 
    def address(self):
        return self.__address
    @address.setter
    def fname(self, address):
        self.__address = address

    @property 
    def num_rooms(self):
        return self.__num_rooms
    @num_rooms.setter
    def num_rooms(self, num_rooms):
        self.__num_rooms = num_rooms

    @property 
    def price(self):
        return self.__price
    @price.setter
    def price(self, price):
        self.__price = price
    
    @property 
    def conditions(self):
        return self.__conditions
    @conditions.setter
    def conditions(self, conditions):
        self.__conditions = conditions
    
    @property 
    def start_date(self):
        return self.__start_date
    @start_date.setter
    def start_date(self, start_date):
        self.__start_date = start_date
    
    @property 
    def end_date(self):
        return self.__end_date
    @end_date.setter
    def end_date(self, end_date):
        self.__end_date = end_date

    @property 
    def pics(self):
        return self.__pics
    @pics.setter
    def pics(self, pics):
        self.__pics = pics

        