from tkinter import *
from tkinter.font import BOLD
from PIL import Image, ImageTk
from customers import *
from offers import *
import re
from socket import *
import pickle
from tkcalendar import DateEntry
from geopy.geocoders import Nominatim
import os
import tkintermapview
from tkinter import ttk
import io



class functions:
    def __init__(self, root, sock, current_date):
        self.root = root
        self.sock = sock
        self.idnum = ""
        self.is_admin = False
        self.__current_date = current_date

        self.root.geometry("500x430+500+180")
        self.root.config(bg='#f4e7d4')
        self.menubar = Menu(self.root, tearoff=0)
        self.menubar.add_command(label="Home", command=self.home)
        self.menubar.add_command(label="Search", command=self.search)
        self.menubar.add_command(label="Map", command=self.veiw_map)
        self.menubar.add_command(label="Sign Up", command=self.sign_up)
        self.menubar.add_command(label="Log In", command=self.log_in)
        self.root.config(menu=self.menubar) 
        self.main_frame = Frame(self.root, width=500, height=500, bg='#f4e7d4')
        self.main_frame.pack(pady=10)
        self.home()
    
    @property 
    def current_date(self):
        return self.__current_date
    @current_date.setter
    def current_date(self, current_date):
        self.__current_date = current_date

    def delete_widgets(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()
        
    # Creates the home window
    def home(self):
        self.delete_widgets()
        self.root.geometry("500x450+500+180")

        frame1 = Frame(self.main_frame, bg='#f4e7d4')
        frame1.pack()
        label = Label(frame1, text='Air BnBenny\nYour Gateway to Cheap Paradise', fg='#274e57', bg='#f4e7d4', font=('Arial', 20, BOLD))
        label.pack(side=TOP, fill=X, expand=True)
        img = Image.open("photos\logo.JPG")
        img = img.resize((300, 300))
        test = ImageTk.PhotoImage(img)
        label = Label(frame1, image = test, bg='#f4e7d4')
        label.image = test
        label.pack(side=TOP, expand=True, anchor=CENTER)

        # If the client isn't signed it, then the buttons for log in and sign in are showed
        self.button = Button(frame1, text='Go Shopping', width=10, bg='#274e57', fg='#f4e7d4', command=self.search)
        self.button.pack(side=LEFT, fill=X, expand=True, pady=5, padx=5)
        if self.idnum == "":
            self.button = Button(frame1, text='Sign Up', width=10, bg='#274e57', fg='#f4e7d4', command=self.sign_up)
            self.button.pack(side=LEFT, fill=X, expand=True, pady=5, padx=5)
            self.button = Button(frame1, text='Log In', width=10, bg='#274e57', fg='#f4e7d4', command=self.log_in)
            self.button.pack(side=LEFT, fill=X, expand=True, pady=5, padx=5)
        
        frame2 = Frame(self.main_frame, bg='#f4e7d4')
        frame2.pack()
        label = Label(frame2, text=f"Current Date: {self.__current_date}", fg='#274e57', bg='#f4e7d4', font=('Arial', 10, BOLD))
        label.pack(fill=X, expand=True)

    # Creates the form for sign up
    def sign_up(self):
        self.delete_widgets()
        self.root.geometry("500x430+500+180")

        person_values = ['First Name', 'Last Name', 'Password', 'ID', 'Email']

        big_frame = LabelFrame(self.main_frame, text="Sign Up", padx=5, pady=5, font=('Arial', 15, BOLD))
        big_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)
        big_frame.config(bg='#f4e7d4')

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        big_frame.rowconfigure(0, weight=1)
        big_frame.columnconfigure(0, weight=1)

        frame1 = Frame(big_frame, padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky=W+N+S)
        frame1.config(bg='#f4e7d4')

        # Creates labels for each value in person_values
        for i in range(len(person_values)):
            label = Label(frame1, text=person_values[i], padx=5, pady=5, bg='#f4e7d4')
            label.pack(anchor=W, expand=True)

        frame2 = Frame(big_frame, padx=5, pady=5)
        frame2.grid(row=0, column=1, sticky=E+W+N+S)
        frame2.config(bg='#f4e7d4')

        entries = []
        for i in range(5):
            entry = Entry(frame2, width=50)
            entry.pack(padx=5, pady=5, anchor=W, fill=X, expand=True)
            entries.append(entry)

        # Creates button that sends the information from the entries to the check_sign_up function
        button = Button(big_frame, text='submit', bg='#274e57', fg='#f4e7d4', command=lambda: self.check_sign_up(entries))
        button.grid(row=1, column=0)

        self.err_label = Label(big_frame, text='', fg='red', bg='#f4e7d4')
        self.err_label.grid(row=1, column=1)
    
    # Checks the information given from the sign up form
    def check_sign_up(self, entries):
        # Regex statement used for email validation
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        error = ""

        # Checks whether the first name is valid
        if entries[0].get() == '' or not entries[0].get().isalpha():
            error += "Invalid First Name\n"
        # Checks whether the last name is valid
        if entries[1].get() == '' or not entries[1].get().isalpha():
            error += "Invalid Last Name\n"
        # Checks whether the password is valid
        if len(entries[2].get()) < 5:
            error += "Invalid Password\n"
        # Checks whether the ID number is valid
        if not entries[3].get().isdigit() or len(entries[3].get()) != 9:
            error += "Invalid ID\n"
        # Checks whether the email is valid using the regex statement above
        if not re.fullmatch(regex, entries[4].get()):
            error += "Invalid Email"
        
        # Updates the error label with the invalid info that it found
        self.err_label['text'] = error

        if error == '':
            # if There are now errors, the a new class object from customers is created and sent to the server
            # to be added to the database
            new_customer = customers(entries[0].get(), entries[1].get(), entries[2].get(), entries[3].get(), entries[4].get())
            data = pickle.dumps(new_customer)
            
            # Checks the exact buffer length of the data being sent
            length = len(data)
            count = 0
            while length != 0:
                length = int(length/10)
                count+=1

            buffer = (5-count)*'0' + f'{len(data)}'
            self.sock.send(buffer.encode())
            self.sock.send(data)

            # Recieves a reply whether the ID number is already used
            buffer = self.sock.recv(5).decode()
            reply = self.sock.recv(int(buffer)).decode()
            if reply == "error":
                self.err_label['text'] = "User with same ID already exists"
            else:
                # If the new customer is valid, the sign up and log in options are deleted 
                # and client feautres are added
                self.idnum = new_customer.id
                self.menubar.delete("Sign Up")
                self.menubar.delete("Log In")
                self.menubar.add_command(label="My Purchases", command=self.my_purchases) 
                self.menubar.add_command(label="Offer Place", command=self.offer_place)
                self.menubar.add_command(label="Log Out", command=self.open_popup) 
                self.home()

    # Creates the form for log in
    def log_in(self):
        self.delete_widgets()
        self.root.geometry("500x430+500+180")

        big_frame = LabelFrame(self.main_frame, text="Log In", padx=5, pady=5, font=('Arial', 15, BOLD))
        big_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)
        big_frame.config(bg='#f4e7d4')

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        big_frame.rowconfigure(0, weight=1)
        big_frame.columnconfigure(0, weight=1)

        frame1 = Frame(big_frame, padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky=W+N+S)
        frame1.config(bg='#f4e7d4')

        label = Label(frame1, text='ID number', padx=5, pady=5, bg='#f4e7d4')
        label.pack(anchor=W, expand=True)
        label = Label(frame1, text='Password', padx=5, pady=5, bg='#f4e7d4')
        label.pack(anchor=W, expand=True)

        frame2 = Frame(big_frame, padx=5, pady=5)
        frame2.grid(row=0, column=1, sticky=E+W+N+S)
        frame2.config(bg='#f4e7d4')

        entries = []
        for i in range(2):
            entry = Entry(frame2, width=50)
            entry.pack(padx=5, pady=5, anchor=W, fill=X, expand=True)
            entries.append(entry)

        # Creates button that sends the information from the entries to the check_log_in function
        button = Button(big_frame, text='submit', bg='#274e57', fg='#f4e7d4', command=lambda: self.check_log_in(entries))
        button.grid(row=1, column=0)

        self.err_label = Label(big_frame, text='', fg='red', bg='#f4e7d4')
        self.err_label.grid(row=1, column=1)
    
    # Checks the information given from the log in form
    def check_log_in(self, entries):

        error = ""
        # Checks whether the ID number is valid
        if not entries[0].get().isdigit() or len(entries[0].get()) != 9:
            error += "Invalid ID\n"
        # Checks whether the password is valid
        if len(entries[1].get()) < 5:
            error += "Invalid Password\n"
    
        # Updates the error label with the invalid info that was found
        self.err_label['text'] = error

        if error == "":
            # If there are no errors, the log in info is sent to the server to check whether 
            # a customer with the information exists in the database
            data = f'Login:{entries[0].get()},{entries[1].get()}'

            # Checks the exact buffer length of the data being sent
            length = len(data)
            count = 0
            while length != 0:
                length = int(length/10)
                count+=1

            buffer = (5-count)*'0' + f'{len(data)}'
            self.sock.send(buffer.encode())
            self.sock.send(data.encode())

            # Recieves a reply whether or not a customer exists in the database
            buffer = self.sock.recv(5).decode()
            reply = self.sock.recv(int(buffer)).decode()

            if reply == "error":
                self.err_label['text'] = "User does not exist"
            else:
                # If the customer is the admin, the the appropriate admin features are added
                if reply == "is_admin":
                    self.is_admin = True
                    self.menubar.delete("Map")
                    filemenu = Menu(self.menubar, tearoff=0)
                    filemenu.add_command(label="Map", command=self.veiw_map)
                    filemenu.add_command(label="Admin Map", command=self.admin_map_view)
                    filemenu.add_command(label="Filter Admin Map", command=self.filter_admin_map)
                    self.menubar.add_cascade(label="Maps", menu=filemenu)
                    filemenu = Menu(self.menubar, tearoff=0)
                    filemenu.add_command(label="All Rooms Data", command=self.show_all_rooms_filter)
                    filemenu.add_command(label="Add Attraction", command=self.add_attraction)
                    filemenu.add_command(labe="Change Date", command=self.change_date)
                    self.menubar.add_cascade(label="Admin Edits", menu=filemenu)

                    # The attractions are sent to the server from the local file
                    with open("attractions.txt", 'r') as file:
                        all_atr = file.readline()
                        self.sock.send('00010'.encode())
                        self.sock.send("attraction".encode())

                        # Checks the exact buffer lenght of the data being sent
                        length = len(all_atr)
                        count = 0
                        while length != 0:
                            length = int(length/10)
                            count+=1

                        buffer = (5-count)*'0' + f'{len(all_atr)}'
                        self.sock.send(buffer.encode())
                        self.sock.send(f"{all_atr}".encode())

                # Addes all of the appropraite features for a registered customer
                self.idnum = entries[0].get()
                self.menubar.delete("Sign Up")
                self.menubar.delete("Log In")
                self.menubar.add_command(label="My Purchases", command=self.my_purchases) 
                self.menubar.add_command(label="Offer Place", command=self.offer_place)
                self.menubar.add_command(label="Log Out", command=self.open_popup) 
            
            # Recieves a reply wheter or not the client needs to do a survey
            buffer = self.sock.recv(5).decode()
            reply = self.sock.recv(int(buffer)).decode()
            if reply == "room_survey":
                self.room_survey()
            self.home()
            
    # Creates the form for offering a place
    def offer_place(self):
        self.delete_widgets()

        self.root.geometry("530x500")

        offer_info = ('Country', 'City', 'Street', 'Start Date', 'End Date', 'Number Rooms', 'Price Per Night (nis)', 'Picture Directories')

        big_frame = LabelFrame(self.main_frame, text="Offer Place", padx=5, pady=5, font=('Arial', 15, BOLD))
        big_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)
        big_frame.config(bg='#f4e7d4')

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        big_frame.rowconfigure(0, weight=1)
        big_frame.columnconfigure(0, weight=1)

        frame1 = Frame(big_frame, padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky=W+N+S)
        frame1.config(bg='#f4e7d4')

        for info in offer_info:
            label = Label(frame1, text=info, padx=5, pady=5, bg='#f4e7d4')
            label.pack(anchor=W, expand=True)

        frame2 = Frame(big_frame, padx=5, pady=5)
        frame2.grid(row=0, column=1, sticky=E+W+N+S)
        frame2.config(bg='#f4e7d4')

        entries = []
        for i in range(3):
            entry = Entry(frame2, width=50)
            entry.pack(padx=5, pady=5, anchor=W, fill=X, expand=True)
            entries.append(entry)
        entries.reverse()

        # Creates two calenders for the start and end available times
        time1 = StringVar()
        time2 = StringVar()
        cal1 = DateEntry(frame2, width=25, background='darkblue', foreground='white', borderwidth=2, textvariable=time1)
        cal1.pack(padx=10, pady=10, anchor=W, fill=X, expand=True)
        cal2 = DateEntry(frame2, width=25, background='darkblue', foreground='white', borderwidth=2, textvariable=time2)
        cal2.pack(padx=10, pady=10, anchor=W, fill=X, expand=True)

        # Creates option menu for the number of room in the place
        nums = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        variable = StringVar(self.root)
        variable.set(1)
        num_rooms = OptionMenu(frame2, variable, *nums)
        num_rooms.pack(anchor=W, fill=X, expand=True)

        entry_price = Entry(frame2, width=50)
        entry_price.pack(padx=5, pady=5, anchor=W, fill=X, expand=True)

        # Creates an entry for inputing picture directories and runs the add_pic function when submitted
        self.pics = []
        entry_pic = Entry(frame2, width=50)
        entry_pic.pack(side=LEFT, padx=5, pady=5, anchor=W, fill=X, expand=True)
        button = Button(frame2, text='Add Pic', bg='#274e57', fg='#f4e7d4', command=lambda:self.add_pic(entry_pic))
        button.pack(side=LEFT, pady=5, fill=X, expand=True)

        frame3 = Frame(big_frame, padx=5, pady=5)
        frame3.grid(row=1, columnspan=2, sticky=E+W+N+S)
        frame3.config(bg='#f4e7d4')

        label = Label(frame3, text='Conditions', padx=5, pady=5, bg='#f4e7d4')
        label.pack(side=LEFT,anchor=W, expand=True)

        # Creates a text widget for additional conditions
        scrollbar = Scrollbar(frame3)
        scrollbar.pack(side= RIGHT, fill= Y)
        text = Text(frame3, width=40, height=5, yscrollcommand = scrollbar.set)
        text.pack(side=RIGHT, padx=5, pady=5, anchor=W, fill=X, expand=True)
        scrollbar.config(command=text.yview)

        # Creates button to send all of the information to the check_offer_place
        button = Button(big_frame, text='submit', width=10, bg='#274e57', fg='#f4e7d4',
            command=lambda:self.check_offer_place(entries, time1.get(), time2.get(), 
            variable.get(), entry_price.get(), text.get("1.0",'end-1c')))
        button.grid(row=2, column=0, pady=5)

        self.err_label = Label(big_frame, text='', fg='red', bg='#f4e7d4')
        self.err_label.grid(row=2, column=1)
    
    # Checks whether the submitted pictures exists and adds them to the self.pics list
    def add_pic(self, entry_pic):
        # Checks if the pictures exist
        if os.path.exists(entry_pic.get()):
            self.pics.append(entry_pic.get())
            entry_pic.delete(0,END)
            entry_pic.insert(0,'Picture Added')
        else:
            entry_pic.delete(0,END)
            entry_pic.insert(0,'Directory Not Found')
    
    # Checks the information given from the offer place form
    def check_offer_place(self, address, start_date, end_date, num_rooms, price, conditions):
        error = ""

        # Checks wehter the given address exists or not
        geolocator = Nominatim(user_agent="tutorial")
        addr = f"{address[2].get()} {address[1].get()} {address[0].get()}"
        try:
            location = geolocator.geocode(addr)
            if location is None:
                error += "Invalid Address"
        except:
            error += "Invalid Address"

        # Formats the dates according to the original format
        if '.' in start_date:
            s_date = start_date.split('.')
            start_date = [s_date[1], s_date[0], s_date[2][2:]]
            e_date = end_date.split('.')
            end_date = [e_date[1], e_date[0], s_date[2][2:]] 
        else:
            start_date = start_date.split('/')
            end_date = end_date.split('/')

        # Checks whether the start date is after the end date
        if int(start_date[2]) > int(end_date[2]):
            error += "Start Date Must Be Before End Date\n"
        elif int(start_date[2]) == int(end_date[2]):
            if int(start_date[0]) > int(end_date[0]):
                error += "Start Date Must Be Before End Date\n"
            elif int(start_date[0]) == int(end_date[0]):
                if int(start_date[1]) > int(end_date[1]):
                    error += "Start Date Must Be Before End Date\n"
        
        # Checks whether the price is valid
        if not price.isdigit():
            error += "Price Must Be In Digits\n"

        # Updates the error label with the invalid info that was found
        self.err_label['text'] = error
        
        if error == '':
            # Creates a new object from class offers and sends the new offer to the server to add to the database
            self.sock.send('00005'.encode())
            self.sock.send('offer'.encode())

            new_pics = self.send_images()
            all_pics = ' '.join(new_pics)
            new_offer = offers(self.idnum, addr, num_rooms, price, conditions, "/".join(start_date), "/".join(end_date), all_pics)

            # Checks the exact buffer lenght of the data being sent
            data = pickle.dumps(new_offer)
            length = len(data)
            count = 0
            while length != 0:
                length = int(length/10)
                count+=1

            buffer = (5-count)*'0' + f'{len(data)}'
            self.sock.send(buffer.encode())
            self.sock.send(data)
            self.home()

    # Runs when the client wants to log out
    def open_popup(self):
        # Creates a top level widget that asks if the client really wants to log out and runs accordingly
        self.top = Toplevel(self.root, bg='#274e57')
        self.top.geometry("400x150+500+180")
        self.top.title("Please Don't Goooo!")
        label = Label(self.top, text= "Are You Sure You Want To Log Out :(", bg='#274e57', fg='#f4e7d4', font=('Arial', 12, BOLD))
        label.pack(side=TOP, fill=X, expand=True, pady=2)
        button = Button(self.top, text='Yes', bg='#f4e7d4', fg='#274e57', command=self.log_out)
        button.pack(side=LEFT, padx=10, pady=10, fill=X, expand=True)
        button = Button(self.top, text='No', bg='#f4e7d4', fg='#274e57', command=lambda: self.top.destroy())
        button.pack(side=LEFT, padx=10, pady=10, fill=X, expand=True)

    # Runs the command log out
    def log_out(self):
        # If the client is admin the it removes all of the admin features
        if self.is_admin:
            self.menubar.delete("Admin Edits")
            self.menubar.delete("Maps")
            self.menubar.add_command(label="Map", command=self.veiw_map)
            self.is_admin = False
        
        # Removes all of the registered client features
        self.idnum = ""
        self.menubar.delete("Offer Place")
        self.menubar.delete("Log Out")
        self.menubar.delete("My Purchases") 
        self.menubar.add_command(label="Sign Up", command=self.sign_up)
        self.menubar.add_command(label="Log In", command=self.log_in)
        self.top.destroy()
        self.home()

    # Searhes for open places to rent
    def search(self):
        self.delete_widgets()
        self.root.geometry("550x430+500+180")

        frame = Frame(self.main_frame, bg='#f4e7d4')
        frame.pack()

        # Client can search for places close to a certain address, or by cheapest or most expensive
        label = Label(frame, text='Enter Address', fg='#274e57', bg='#f4e7d4', font=('Arial', 15, BOLD))
        label.pack(side=TOP, fill=X, expand=True)
        entry = Entry(frame, width=40)
        entry.pack(side=LEFT, anchor=NW, fill=X, expand=True, padx=5)
        OPTIONS = ['   Closest   ', 'Lowest Price ', 'Highest Price']
        variable = StringVar(frame)
        variable.set(OPTIONS[0])
        w = OptionMenu(frame, variable, *OPTIONS)
        w.pack(side=LEFT, anchor=NW, expand=True, padx=5)

        # Creates a button the sends the filter info to the search_place function
        button = Button(frame, text='enter', width=10, bg='#274e57', fg='#f4e7d4', command=lambda:self.search_place(entry.get(), variable.get()))
        button.pack(side=LEFT, anchor=NW, fill=X, expand=True)
        self.root.bind('<Return>', (lambda event:self.search_place(entry.get(), variable.get())))

        self.offer_frame = Frame(self.main_frame, bg='#f4e7d4')
        self.offer_frame.pack()
    
    # Sends and recieves from the server available places according to the filters
    def search_place(self, addr, filter):
        for widget in self.offer_frame.winfo_children():
            widget.destroy()

        # Checks the exact buffer lenght of the data being sent
        data = f"addr:{addr}:{filter}"
        length = len(data)
        count = 0
        while length != 0:
            length = int(length/10)
            count+=1

        buffer = (5-count)*'0' + f'{len(data)}'
        # Sends to the sever the filters
        self.sock.send(buffer.encode())
        self.sock.send(data.encode())

        # Recieves the available places
        buffer = self.sock.recv(5).decode()
        all_offers = pickle.loads(self.sock.recv(int(buffer)))
        all_offers.pop(-1)

        # Recieves the pictures of the places
        room_pics, atr_pics = self.get_images()

        for offer in all_offers:
            # Creates a button for each place with its picture and information
            all_pics = offer[8].split(' ')
            image = Image.open(room_pics[all_pics[0]])
            image = image.resize((200,150), Image.ANTIALIAS)
            img= ImageTk.PhotoImage(image)

            button= Button(self.offer_frame, text=f"  {offer[2]} \n Availability: {offer[3]} \n Price: {offer[6]} nis ",
                font= ('Helvetica 12 bold'), image=img, compound="left", command=lambda offer=offer:self.show_room(offer, room_pics, False))
            button.pack(side=TOP, fill=X, expand=True, pady=5, padx=5)
            button.image = img

    # Shows the map with all of the available places
    def veiw_map(self):
        self.delete_widgets()
        self.root.geometry("850x600+300+100")

        self.sock.send('00006'.encode())
        self.sock.send(f"addr::".encode())

        # Receives all of the available places
        buffer = self.sock.recv(5).decode()
        all_offers = pickle.loads(self.sock.recv(int(buffer)))

        # Recieves all of the pictures of all of the places
        room_pics, atr_pics = self.get_images()
        
        my_label = Label(self.main_frame)
        my_label.pack()

        # Creates the map widget
        self.map_widget = tkintermapview.TkinterMapView(my_label, width=800, height=600, corner_radius=0)
        self.map_widget.set_position(0, 0)
        self.map_widget.set_zoom(0)

        attractions = []
        if all_offers[-1] == '':
            all_offers.pop(-1)
        else:
            attractions = all_offers.pop(-1)

        # Creates all of the marker for the available places
        for value in all_offers:
            address = tkintermapview.convert_address_to_coordinates(value[2])
            self.create_marker(address, value, room_pics, 'red', False)

        # Creates markers for the attractions if there any
        if len(attractions) != 0:
            for atr in attractions:
                attraction = atr.split('$')
                address = tkintermapview.convert_address_to_coordinates(attraction[2])
                self.create_attraction_marker(address, attraction, atr_pics)
        
        self.map_widget.pack()
    
    # Creates admin map which can view all of the places in the system
    def admin_map_view(self):
        self.delete_widgets()
        self.root.geometry("850x600+300+100")

        self.sock.send('00012'.encode())
        self.sock.send(f"admin_addr::".encode())

        # Recieves all of the places
        buffer = self.sock.recv(5).decode()
        all_offers = pickle.loads(self.sock.recv(int(buffer)))
        room_pics, atr_pics = self.get_images()
        
        my_label = Label(self.main_frame)
        my_label.pack()

        # Creates the map widget
        self.map_widget = tkintermapview.TkinterMapView(my_label, width=800, height=600, corner_radius=0)
        self.map_widget.set_position(0, 0)
        self.map_widget.set_zoom(0)

        attractions = all_offers.pop(-1)

        # Creates markers for the places
        for value in all_offers:
            address = tkintermapview.convert_address_to_coordinates(value[2])
            # If the place is available then the marker is red
            if value[1] == '':
                self.create_marker(address, value, room_pics, 'red', True)
            # If the place is taken then the marker is green
            else:
                self.create_marker(address, value, room_pics, 'green', True)

        # Creates markers for the attractions
        for atr in attractions:
                attraction = atr.split('$')
                address = tkintermapview.convert_address_to_coordinates(attraction[2])
                self.create_attraction_marker(address, attraction, atr_pics)
        
        self.map_widget.pack()

    # Shows map with all of the places according to a filter
    def filter_admin_map(self):
        self.delete_widgets()
        self.root.geometry("850x600+300+100")
        
        frame1 = Frame(self.main_frame, bg='#f4e7d4')
        frame1.pack()

        # Creates two calenders as filters to show places that are listed in those specific dates
        time1 = StringVar()
        time2 = StringVar()
        label = Label(frame1, text='Start Date:', bg='#f4e7d4')
        label.pack(side=LEFT, fill=X, expand=True)
        cal1 = DateEntry(frame1, width=25, background='darkblue', foreground='white', borderwidth=2, textvariable=time1)
        cal1.pack(side=LEFT, padx=10, pady=10, fill=X, expand=True)
        label = Label(frame1, text='End Date:', bg='#f4e7d4')
        label.pack(side=LEFT, fill=X, expand=True)
        cal2 = DateEntry(frame1, width=25, background='darkblue', foreground='white', borderwidth=2, textvariable=time2)
        cal2.pack(side=LEFT, padx=10, pady=10, fill=X, expand=True)

        # Filter that allows the admin to see only places that are bought, open, or all of them
        filter = StringVar()
        radio = Radiobutton(frame1, variable=filter, text="All", value="All", bg='#f4e7d4')
        radio.pack(side=LEFT, fill=X, expand=True)
        radio = Radiobutton(frame1, variable=filter, text="Bought", value="Bought", bg='#f4e7d4')
        radio.pack(side=LEFT, fill=X, expand=True)
        radio = Radiobutton(frame1, variable=filter, text="Open", value="Open", bg='#f4e7d4')
        radio.pack(side=LEFT, fill=X, expand=True)

        # Sends the filter data to the view_filtered_admin_map to show the markers
        button = Button(frame1, text='search', fg='#f4e7d4', bg='#274e57', command=lambda:self.view_filtered_admin_map(time1.get(), time2.get(), filter.get()))
        button.pack(side=LEFT, fill=X, expand=True)
        self.root.bind('<Return>', (lambda event:self.view_filtered_admin_map(time1.get(), time2.get(), filter.get())))

        # Creates the map widget
        self.map_frame = Frame(self.main_frame, bg='#f4e7d4')
        self.map_frame.pack()
        my_label = Label(self.map_frame)
        my_label.pack()

        self.map_widget = tkintermapview.TkinterMapView(my_label, width=800, height=600, corner_radius=0)
        self.map_widget.set_position(0, 0)
        self.map_widget.set_zoom(0)
        self.map_widget.pack()

    def view_filtered_admin_map(self, start_date, end_date, filter):
        for widget in self.map_frame.winfo_children():
            widget.destroy()
        
        my_label = Label(self.map_frame)
        my_label.pack()

        # Creates the map widget
        self.map_widget = tkintermapview.TkinterMapView(my_label, width=800, height=600, corner_radius=0)
        self.map_widget.set_position(0, 0)
        self.map_widget.set_zoom(0)

        # Checks the exact buffer length of the data being sent
        data = f"filter_map:{start_date}-{end_date}:{filter}"
        length = len(data)
        count = 0
        while length != 0:
            length = int(length/10)
            count+=1

        buffer = (5-count)*'0' + f'{len(data)}'

        # Sends the filter to the server
        self.sock.send(buffer.encode())
        self.sock.send(data.encode())

        # Recieves the places according to the filter
        buffer = self.sock.recv(5).decode()
        all_offers = pickle.loads(self.sock.recv(int(buffer)))
        room_pics, atr_pics = self.get_images()

        # Shows markers for all of the places
        for value in all_offers:
            address = tkintermapview.convert_address_to_coordinates(value[2])
            # If the place is available then it is red
            if value[1] == '':
                self.create_marker(address, value, room_pics, 'red', True)
            # If the place is bought then it is green
            else:
                self.create_marker(address, value, room_pics, 'green', True)
        
        self.map_widget.pack()

    # Creates the markers for places
    def create_marker(self, address, value, room_pics, color, is_admin_map):
        self.map_widget.set_marker(address[0], address[1], text=value[2], marker_color_outside=color, marker_color_circle='white', command=lambda h:self.show_room(value, room_pics, is_admin_map))
    
    # Creates the markers for attractions
    def create_attraction_marker(self, address, value, atr_pics):
        self.map_widget.set_marker(address[0], address[1], text=value[0], marker_color_outside='blue', marker_color_circle='white', command=lambda h:self.show_attraction(value, atr_pics))

    # Shows the specific rooms when clicked on
    def show_room(self, details, room_pics, is_admin_map):
        room_details = ['Location', 'Availability', 'Number of Rooms', 'Price per Night (nis)', 'Conditions']
        
        self.sock.send('00007'.encode())
        self.sock.send(f'room:{details[-1]}'.encode())

        # Creates a top that shows all of the rooms data and pictures
        top = Toplevel(self.root, bg='#f4e7d4')
        top.geometry("400x200+500+180")
        top.title("Place Details")
        frame1 = Frame(top, bg='#f4e7d4')
        frame1.pack(side=LEFT)
        frame2 = Frame(top, bg='#f4e7d4')
        frame2.pack(side=LEFT)

        # Places all of the pictures of the room
        all_pics = details[8].split(' ')
        for pic in all_pics:
            img = Image.open(room_pics[pic])
            img = img.resize((200, 150))
            test = ImageTk.PhotoImage(img)
            label = Label(frame1, image = test, bg='#f4e7d4')
            label.image = test
            label.pack(expand=True, anchor=CENTER) 

        # Creates labels for the details of the rooms
        i = 2
        for detail in room_details:
            if detail == 'Availability':
                label = Label(frame2, text=f"{detail}: {details[i]}", bg='#f4e7d4', fg='#274e57')
                i += 1
            else:
                label = Label(frame2, text=f"{detail}: {details[i]}", bg='#f4e7d4', fg='#274e57')
            label.pack(side=TOP, fill=X, expand=True)
            i += 1
        
        if not is_admin_map:
            button = Button(frame2, text='Rent Place', width=100, fg='#f4e7d4', bg='#274e57', command=lambda:self.rent_place(details))
            button.pack(side=TOP, fill=X, expand=True, padx=5, pady=5)
    
    # Creates form for renting a place
    def rent_place(self, details):
        top = Toplevel(self.root, bg='#f4e7d4')
        top.geometry("500x250+500+180")
        top.title("Place Details")
        big_frame = LabelFrame(top, text="Rent Place", padx=5, pady=5, font=('Arial', 15, BOLD))
        big_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)
        big_frame.config(bg='#f4e7d4')

        top.columnconfigure(0, weight=1)
        top.rowconfigure(1, weight=1)

        big_frame.rowconfigure(0, weight=1)
        big_frame.columnconfigure(0, weight=1)

        # txtbox = ScrolledText(group1, width=40, height=10)
        # txtbox.grid(row=0, column=0,   sticky=E+W+N+S)    

        frame1 = Frame(big_frame, padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky=W+N+S)
        frame1.config(bg='#f4e7d4')

        label = Label(frame1, text='ID Number', padx=5, pady=5, bg='#f4e7d4')
        label.pack(anchor=W, expand=True)
        label = Label(frame1, text='Credit Card Number', padx=5, pady=5, bg='#f4e7d4')
        label.pack(anchor=W, expand=True)
        label = Label(frame1, text='Start Date', padx=5, pady=5, bg='#f4e7d4')
        label.pack(anchor=W, expand=True)
        label = Label(frame1, text='End Date', padx=5, pady=5, bg='#f4e7d4')
        label.pack(anchor=W, expand=True)
        
        frame2 = Frame(big_frame, padx=5, pady=5)
        frame2.grid(row=0, column=1, sticky=E+W+N+S)
        frame2.config(bg='#f4e7d4')

        entries = []
        for i in range(2):
            entry = Entry(frame2, width=50)
            entry.pack(padx=5, pady=5, anchor=W, fill=X, expand=True)
            entries.append(entry)
        
        time1 = StringVar()
        time2 = StringVar()
        cal1 = DateEntry(frame2, width=25, background='darkblue', foreground='white', borderwidth=2, textvariable=time1)
        cal1.pack(padx=10, pady=10, anchor=W, fill=X, expand=True)
        cal2 = DateEntry(frame2, width=25, background='darkblue', foreground='white', borderwidth=2, textvariable=time2)
        cal2.pack(padx=10, pady=10, anchor=W, fill=X, expand=True)
        button = Button(big_frame, text='submit', bg='#274e57', fg='#f4e7d4', 
            command=lambda: self.check_rent_place(entries, details, time1.get(), time2.get(), top))
        button.grid(row=1, column=0)

        self.err_label = Label(big_frame, text='', fg='red', bg='#f4e7d4')
        self.err_label.grid(row=1, column=1)
    
    # Checks the information given from the rent place form
    def check_rent_place(self, entries, details, start_date, end_date, top):
        error = ""
        available = details[3].split('-')
        seller_start = available[0].split('/')
        seller_end = available[1].split('/')

        # Formats the dates according to the original format
        if '.' in start_date:
            s_date = start_date.split('.')
            start_date = [s_date[1], s_date[0], s_date[2][2:]]
            e_date = end_date.split('.')
            end_date = [e_date[1], e_date[0], s_date[2][2:]] 
        else:
            start_date = start_date.split('/')
            end_date = end_date.split('/')

        # Checks if the ID number is valid
        if not entries[0].get().isdigit() or len(entries[0].get()) != 9:
            error += "Invalid ID\n"
        # Check if the credit card number is valid
        if not entries[1].get().isdigit() or len(entries[1].get()) != 16:
            error += "Invalid Credit Card Number\n"

        # Checks whether the submitted dates are between the available dates
        if int(seller_start[2]) > int(start_date[2]):
            error += "Start Date Must Not Be Before Available Date\n"
        elif int(seller_start[2]) == int(start_date[2]):
            if int(seller_start[0]) > int(start_date[0]):
                error += "Start Date Must Not Be Before Available Date\n"
            elif int(seller_start[0]) == int(start_date[0]):
                if int(seller_start[1]) > int(start_date[1]):
                    error += "Start Date Must Not Be Before Available Date\n"

        if int(end_date[2]) > int(seller_end[2]):
            error += "End Date Must Not Be After Available Date\n"
        elif int(end_date[2]) == int(seller_end[2]):
            if int(end_date[0]) > int(seller_end[0]):
                error += "End Date Must Not Be After Available Date\n"
            elif int(end_date[0]) == int(seller_end[0]):
                if int(end_date[1]) > int(seller_end[1]):
                    error += "End Date Must Not Be After Available Date\n"

        if int(start_date[2]) > int(end_date[2]):
            error += "Start Date Must Be Before End Date\n"
        elif int(start_date[2]) == int(end_date[2]):
            if int(start_date[0]) > int(end_date[0]):
                error += "Start Date Must Be Before End Date\n"
            elif int(start_date[0]) == int(end_date[0]):
                if int(start_date[1]) > int(end_date[1]):
                    error += "Start Date Must Be Before End Date\n"
        
        if error != "":
            # Updates the error label with the invalid info found
            self.err_label['text'] = error
        else:
            # Checks the exact buffer length of the data being sent
            data = f"rent: {entries[0].get()} {'/'.join(start_date)}-{'/'.join(end_date)} {details[9]}"
            length = len(data)
            count = 0
            while length != 0:
                length = int(length/10)
                count+=1

            buffer = (5-count)*'0' + f'{len(data)}'

            # Sends to the server the ID number of the client and which room 
            # the client is renting to update the database
            self.sock.send(buffer.encode())
            self.sock.send(data.encode())
            top.destroy()
            self.home()

    # Shows all of the rooms purchased by a client
    def my_purchases(self):
        self.delete_widgets()
        self.root.geometry("500x350+500+180")

        # Checks the exact buffer length of the data being sent
        data = f"id: {self.idnum}"
        length = len(data)
        count = 0
        while length != 0:
            length = int(length/10)
            count+=1

        buffer = (5-count)*'0' + f'{len(data)}'

        # Sends to the server the clients ID
        self.sock.send(buffer.encode())
        self.sock.send(data.encode())

        # Recieves places according to the clients ID
        buffer = self.sock.recv(5).decode()
        my_rooms = pickle.loads(self.sock.recv(int(buffer)))
        room_pics, atr_pics = self.get_images()

        label = Label(self.main_frame, text='My Purchases', fg='#274e57', bg='#f4e7d4', font=('Arial', 20, BOLD))
        label.pack(side=TOP, fill=X, expand=True)

        # If there are no places then the client hasn't bought any places
        if len(my_rooms) == 0:
            label = Label(self.main_frame, text="You Haven't Rented Any Places", fg='#274e57', bg='#f4e7d4', font=('Arial', 15, BOLD))
            label.pack(side=TOP, fill=X, expand=True, pady=10)
        
        # Shows all of the rooms as buttons
        for room in my_rooms:
            all_pics = room[8].split(' ')
            image = Image.open(room_pics[all_pics[0]])
            image = image.resize((200,150), Image.ANTIALIAS)
            img= ImageTk.PhotoImage(image)
            button= Button(self.main_frame, text=f" Location: {room[2]} \n Availability: {room[3]} \n Price: {room[6]} nis ", 
                font=('Helvetica 15 bold'), image=img, compound="left", command=lambda room=room:self.show_my_room(room, room_pics))
            button.pack(side=TOP, fill=X, expand=True, pady=5)
            button.image = img
    
    # Shows all of the information of the rooms
    def show_my_room(self, details, room_pics):
        room_details = ['Location', 'Availability', 'Number of Rooms', 'Price per Night (nis)', 'Conditions']
        top = Toplevel(self.root, bg='#f4e7d4')
        top.geometry("400x200+500+180")
        top.title("Place Details")
        frame1 = Frame(top, bg='#f4e7d4')
        frame1.pack(side=LEFT)
        frame2 = Frame(top, bg='#f4e7d4')
        frame2.pack(side=LEFT)

        all_pics = details[8].split(' ')
        for pic in all_pics:
            img = Image.open(room_pics[pic])
            img = img.resize((200, 150))
            test = ImageTk.PhotoImage(img)
            label = Label(frame1, image = test, bg='#f4e7d4')
            label.image = test
            label.pack(expand=True, anchor=CENTER) 

        i = 2
        for detail in room_details:
            if detail == 'Availability':
                label = Label(frame2, text=f"{detail}: {details[i]}", bg='#f4e7d4', fg='#274e57')
                i += 1
            else:
                label = Label(frame2, text=f"{detail}: {details[i]}", bg='#f4e7d4', fg='#274e57')
            label.pack(side=TOP, fill=X, expand=True)
            i += 1
        
        # Creates button with the option to cancel a purchase
        button = Button(frame2, text='Cancel Purchase', width=100, fg='#f4e7d4', bg='#274e57', command=lambda:self.cancel_purchase(details, top))
        button.pack(side=BOTTOM, fill=X, expand=True, padx=5, pady=5)
    
    # Cancels purchase of a specific room
    def cancel_purchase(self, details, top):
        # Checks the exact buffer length of the data being sent
        data = f'cancel: {details[9]}'
        length = len(data)
        count = 0
        while length != 0:
            length = int(length/10)
            count+=1

        buffer = (5-count)*'0' + f'{len(data)}'

        # Sends which room the client wants to cancel the purchase on to the server to update the database
        self.sock.send(buffer.encode())
        self.sock.send(data.encode())

        top.destroy()
        self.my_purchases()

    # Creates a top level that shows a survey on a clients stay in a place
    def room_survey(self):
        top = Toplevel(self.root, bg='#f4e7d4')
        top.geometry("320x280+500+180")
        top.title("Quick Survey")
        frame1 = Frame(top, bg='#f4e7d4')
        frame1.pack(fill=X, expand=True)
        frame2 = Frame(top, bg='#f4e7d4')
        frame2.pack(fill=X, expand=True)
        label = Label(frame1, text= "Quick Survey", fg='#274e57', bg='#f4e7d4', font=('Arial', 15, BOLD))
        label.pack(fill=X, expand=True)
        label = Label(frame1, text= "How Well Did You Enjoy Your Stay?", fg='#274e57', bg='#f4e7d4', font=('Arial', 10, BOLD))
        label.pack(fill=X, expand=True)

        var = IntVar()
        for i in range(5):
            radio = Radiobutton(frame1, variable=var, value=i+1, bg='#f4e7d4')
            radio.pack(side=LEFT, fill=X, expand=True)
            label = Label(frame2, text=i+1, bg='#f4e7d4')
            label.pack(side=LEFT, fill=X, expand=True, padx=6)

        frame3 = Frame(top, bg='#f4e7d4')
        frame3.pack(fill=X, expand=True)
        label = Label(frame3, text= "More Comments", fg='#274e57', bg='#f4e7d4', font=('Arial', 10, BOLD))
        label.pack(side=TOP, fill=X, expand=True, pady=5)
        scrollbar = Scrollbar(frame3)
        scrollbar.pack(side= RIGHT, fill= Y)
        text = Text(frame3, width=40, height=5, yscrollcommand = scrollbar.set)
        text.pack(side=TOP, padx=5, pady=5, anchor=W, fill=X, expand=True)
        scrollbar.config(command=text.yview)

        button = Button(top, text='Submit', bg='#274e57', fg='#f4e7d4', command=top.destroy)
        button.pack(fill=X, expand=True, pady=5, padx=5)

    # Shows all of the rooms that are in the database and their data
    def show_all_rooms_filter(self):
        self.delete_widgets()
        self.root.geometry("900x300+300+100")

        frame = Frame(self.main_frame, bg='#f4e7d4')
        frame.pack(pady=5)

        # Filters for the rooms
        options = ['All', 'Open', 'Bought', 'Bought By Registered User', 'Bought By Unregistered User']
        variable = StringVar(self.root)
        variable.set('All')
        option_rooms = OptionMenu(frame, variable, *options)
        option_rooms.pack(side=LEFT, fill=X, expand=True, padx=10)

        button = Button(frame, text='search', bg='#274e57', fg='#f4e7d4', command=lambda:self.show_all_rooms_data(variable.get()))
        button.pack(side=LEFT, fill=X, expand=True)

        # Creates a Treeview widget to show all of the data
        self.tv_frame = Frame(self.main_frame)
        self.tv_frame.pack(pady=20)

        self.tv = ttk.Treeview(self.tv_frame, columns=(1, 2, 3, 4, 5, 6, 7, 8), show='headings', height=8)
        self.tv.pack(side=LEFT)
        headings = ['ID Seller', 'ID Buyer', 'Address', 'Availability', 'Buyer Date', 'Num Rooms', 'Cost Per Night (nis)', 'Conditions']
        
        i = 1
        for heading in headings:
            self.tv.heading(i, text=heading)
            self.tv.column(i, anchor=CENTER, stretch=NO, width=100)
            i += 1
        
        sb = Scrollbar(self.tv_frame, orient=VERTICAL)
        sb.pack(side=RIGHT, fill=Y)
        self.tv.config(yscrollcommand=sb.set)
        sb.config(command=self.tv.yview)
        style = ttk.Style()
        style.theme_use("default")
        style.map("Treeview")


    def show_all_rooms_data(self, filter):
        for widget in self.tv_frame.winfo_children():
            widget.destroy()

        self.root.geometry("900x300+300+100")

        # Checks the exact buffer length of the data being sent
        data = f'admin_data_addr::{filter}'
        length = len(data)
        count = 0
        while length != 0:
            length = int(length/10)
            count+=1

        buffer = (5-count)*'0' + f'{len(data)}'

        # Sends to the server the filters
        self.sock.send(buffer.encode())
        self.sock.send(data.encode())

        # Recieves the rooms according to the filters
        buffer = self.sock.recv(5).decode()
        all_rooms = pickle.loads(self.sock.recv(int(buffer)))
        all_rooms.pop(-1)

        self.tv = ttk.Treeview(self.tv_frame, columns=(1, 2, 3, 4, 5, 6, 7, 8), show='headings', height=8)
        self.tv.pack(side=LEFT)
        headings = ['ID Seller', 'ID Buyer', 'Address', 'Availability', 'Buyer Date', 'Num Rooms', 'Cost Per Night (nis)', 'Conditions']
        
        i = 1
        for heading in headings:
            self.tv.heading(i, text=heading)
            self.tv.column(i, anchor=CENTER, stretch=NO, width=100)
            i += 1
        
        sb = Scrollbar(self.tv_frame, orient=VERTICAL)
        sb.pack(side=RIGHT, fill=Y)
        self.tv.config(yscrollcommand=sb.set)
        sb.config(command=self.tv.yview)

        # Inserts into the treeview table all of the places' information
        i = 0
        for value in all_rooms:
            self.tv.insert(parent='', index=i, iid=i, values=(value[0], value[1], value[2], value[3], value[4], value[5], value[6], value[7]))
            i += 1
        
        style = ttk.Style()
        style.theme_use("default")
        style.map("Treeview")
    
    # Changes current date
    def change_date(self):
        self.delete_widgets()
        self.root.geometry('500x150')

        label = Label(self.main_frame, text="Change Date", fg='#274e57', bg='#f4e7d4', font=('Arial', 20, BOLD))
        label.pack(fill=X, expand=True)
        label = Label(self.main_frame, text=f"Current Date: {self.__current_date}", fg='#274e57', bg='#f4e7d4', font=('Arial', 15, BOLD))
        label.pack(fill=X, expand=True)
        label = Label(self.main_frame, text="New Date:", fg='#274e57', bg='#f4e7d4', font=('Arial', 15, BOLD))
        label.pack(side=LEFT, fill=X, expand=True)
        time = StringVar()
        cal = DateEntry(self.main_frame, width=25, background='darkblue', foreground='white', borderwidth=2, textvariable=time)
        cal.pack(side=LEFT, fill=X, expand=True)
        button = Button(self.main_frame, text="update date", bg='#274e57', fg='#f4e7d4', command=lambda:self.update_date(time.get()))
        button.pack(fill=X, expand=True, padx=5)
    
    # Updates the current date with the server and other clients
    def update_date(self, new_date):
        # Checks the exact buffer length of the data being sent
        data = f"change_date:{new_date}"
        length = len(data)
        count = 0
        while length != 0:
            length = int(length/10)
            count+=1

        buffer = (5-count)*'0' + f'{len(data)}'
        # Sends to the server the new current date
        self.sock.send(buffer.encode())
        self.sock.send(data.encode())

        self.__current_date = new_date
        self.home()

    # Creates a form for adding an attraction
    def add_attraction(self):
        self.delete_widgets()
        self.root.geometry("540x300")

        attraction_details = ('Name of Place', 'Type of Attraction', 'Address', 'Pictures')

        big_frame = LabelFrame(self.main_frame, text="Add Attraction", padx=5, pady=5, font=('Arial', 15, BOLD))
        big_frame.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky=E+W+N+S)
        big_frame.config(bg='#f4e7d4')

        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)

        big_frame.rowconfigure(0, weight=1)
        big_frame.columnconfigure(0, weight=1)

        frame1 = Frame(big_frame, padx=5, pady=5)
        frame1.grid(row=0, column=0, sticky=W+N+S)
        frame1.config(bg='#f4e7d4')

        for detail in attraction_details:
            label = Label(frame1, text=detail, padx=5, pady=5, bg='#f4e7d4')
            label.pack(anchor=W, expand=True)

        frame2 = Frame(big_frame, padx=5, pady=5)
        frame2.grid(row=0, column=1, sticky=E+W+N+S)
        frame2.config(bg='#f4e7d4')

        entries = []
        for i in range(3):
            entry = Entry(frame2, width=50)
            entry.pack(padx=5, pady=5, anchor=W, fill=X, expand=True)
            entries.append(entry)

        self.pics = []
        entry_pic = Entry(frame2, width=50)
        entry_pic.pack(side=LEFT, padx=5, pady=5, anchor=W, fill=X, expand=True)
        button = Button(frame2, text='Add Pic', bg='#274e57', fg='#f4e7d4', command=lambda:self.add_pic(entry_pic))
        button.pack(side=LEFT, pady=5, fill=X, expand=True)

        # Creates a button which sends the attraction data to the check_attraction function
        button = Button(big_frame, text='submit', width=10, bg='#274e57', fg='#f4e7d4', command=lambda:self.check_attraction(entries))
        button.grid(row=2, column=0, pady=5)

        self.err_label = Label(big_frame, text='', fg='red', bg='#f4e7d4')
        self.err_label.grid(row=2, column=1)
    
    # Checks the information given from the add attraction form
    def check_attraction(self, entries):
        error = ""
        
        # Checks whether the name is valid
        if entries[0].get() == '':
            error += "Enter Name of the Attraction\n"
        # Checks whether the type of attractoin is valid
        if entries[1].get() == '':
            error += "Enter Type of the Attraction\n"
        # Checks whether the location is valid
        if entries[2].get() == '':
            error += "Enter Location of the Attraction\n"

        # Checks whether the location is valid
        geolocator = Nominatim(user_agent="tutorial")
        try:
            location = geolocator.geocode(entries[2].get())
            if location is None:
                error += "Invalid Address"
        except:
            error += "Invalid Address"
        
        if error != '':
            # Updates the error label with the invalid info found
            self.err_label['text'] = error
        else:
            # Sends the new attraction to the server
            self.sock.send('00014'.encode())
            self.sock.send('new attraction'.encode())

            new_pics = self.send_images()
            all_pics = ' '.join(new_pics)
            new_attraction = f"{entries[0].get()}${entries[1].get()}${entries[2].get()}${all_pics}"

            # Adds the new attraction to the local file that has all of the attractions
            with open("attractions.txt", "a") as file:
                file.write(f"%{new_attraction}")
            
            # Checks the exact buffer length of the data being sent
            length = len(new_attraction)
            count = 0
            while length != 0:
                length = int(length/10)
                count+=1

            buffer = (5-count)*'0' + f'{len(new_attraction)}'

            # Sends the new attraction to the server
            self.sock.send(buffer.encode())
            self.sock.send(new_attraction.encode())

    # Shows the attraction information and images
    def show_attraction(self, details, atr_pics):
        top = Toplevel(self.root, bg='#f4e7d4')
        top.geometry("400x200+500+180")
        top.title("Place Details")
        frame1 = Frame(top, bg='#f4e7d4')
        frame1.pack(side=LEFT, fill=X, expand=True)
        frame2 = Frame(top, bg='#f4e7d4')
        frame2.pack(side=LEFT, fill=X, expand=True)

        all_pics = details[3].split(' ')
        for pic in all_pics:
            img = Image.open(atr_pics[pic])
            img = img.resize((200, 150))
            test = ImageTk.PhotoImage(img)
            label = Label(frame1, image = test, bg='#f4e7d4')
            label.image = test
            label.pack(expand=True, anchor=CENTER) 

        for i in range(3):
            label = Label(frame2, text=f"{details[i]}", bg='#f4e7d4', fg='#274e57')
            label.pack(side=TOP, fill=X, expand=True, pady=5)

    # Recieves the pictures from the server
    def get_images(self):
        all_pics = {}
        attraction_pics = {}
        pic = b""

        # Recieves the pictures of the regular places
        while True:
            buffer = self.sock.recv(10).decode()
            packet = b''
            while len(packet) < int(buffer):
                packet += self.sock.recv(int(buffer))

            if packet == "stop".encode():       
                break                   
            if packet == "finished pic".encode():
                buffer = self.sock.recv(5).decode()
                pic_name = self.sock.recv(int(buffer)).decode()
                image_stream = io.BytesIO(pic)
                all_pics[pic_name] = image_stream
                pic = b""
            else:
                pic+=packet

        # Recieves the pictures of the attractions
        pic = b""
        while True:
            buffer = self.sock.recv(10)
            packet = b''
            while len(packet) < int(buffer):
                packet += self.sock.recv(int(buffer))

            if packet == "stop".encode():       
                break
            if packet == "finished pic".encode():
                buffer = self.sock.recv(5).decode()
                pic_name = self.sock.recv(int(buffer)).decode()
                image_stream = io.BytesIO(pic)
                attraction_pics[pic_name] = image_stream
                pic = b""
            else:
                pic+=packet

        return all_pics, attraction_pics
    
    # Sends images to the server
    def send_images(self):
        new_pics = []
        for pic in self.pics:
            # Changes the image's directory
            new_pic = pic.split('\\')
            pic_name = f'photos\\{new_pic[-1]}'
            new_pics.append(pic_name)
            
            # Reads the image
            with open(pic,'rb') as file:
                data = file.read()
                length = len(data)
                count = 0

                while length != 0:
                    length = int(length/10)
                    count+=1

                buffer = (10-count)*'0' + f'{len(data)}'
                # Sends the image to the server
                self.sock.send(buffer.encode())
                self.sock.send(data)

            # When finished sending the image it sends the name of the image
            self.sock.send('0000000012'.encode())
            self.sock.send("finished pic".encode())

            length = len(pic_name)
            count = 0
            while length != 0:
                length = int(length/10)
                count+=1

            buffer = (5-count)*'0' + f'{len(pic_name)}'
            self.sock.send(buffer.encode())
            self.sock.send(f"{pic_name}".encode())
        
        # Stops sending images
        self.sock.send('0000000004'.encode())
        self.sock.send("stop".encode())
        return new_pics