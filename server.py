import re
from socket import *
from select import select
import mysql.connector
from customers import *
from offers import *
import pickle
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import datetime
import time
import _thread

# Connects to the mysql database
db = mysql.connector.connect(
    host='34.65.247.122',
    user="root",
    passwd="benny",
    database="benny_db"
)

mycursor = db.cursor()

# Main TCP sockets that run the connection
all_sockets = []
conn_sock = socket(AF_INET,SOCK_STREAM)
all_sockets.append(conn_sock)
conn_sock.bind(("localhost",55000))
conn_sock.setsockopt(IPPROTO_TCP, TCP_NODELAY, 1)
conn_sock.listen(3)

# UDP socket that is used to broadcast the date to other clients
udp_sock = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP)
udp_sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
udp_sock.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)

surveys_to_send = []   # List of clients that need to do a survey after staying at a place
attractions = []       # List of attractions
timed_rooms = []
date = datetime.datetime.now()
current_date = date.strftime("%x")

# At the start of each run the server checks whether there are places that need to be deleted
def check_places_dates(current_date):
    # Fetches all of the rooms that are bought
    mycursor.execute("SELECT * FROM offers WHERE ID_buyer != ''")
    all_offers = mycursor.fetchall()
    if '.' in current_date:
            date_now = current_date.split('.')
            date_now = [date_now[1], date_now[0], date_now[2][2:]]
    else:
        date_now = current_date.split('/')

    for offer in all_offers:
        delete = False
        buyer_date = offer[4].split('-')
        end_buyer = buyer_date[1].split('/')
        
        # Checks whether the bought dates have expired
        if int(date_now[2]) > int(end_buyer[2]):
            delete = True
        elif int(date_now[2]) == int(end_buyer[2]):
            if int(date_now[0]) > int(end_buyer[0]):
                delete = True
            elif int(date_now[0]) == int(end_buyer[0]):
                if int(date_now[1]) > int(end_buyer[1]):
                    delete = True
        if delete:
            # Updates the database of places whos bought dates have expired to be open
            surveys_to_send.append(offer[1])
            mycursor.execute(f"UPDATE offers SET ID_buyer = '', buyer_date = '' WHERE offer_ID = {offer[9]}")
            db.commit()

    # Fetches all of the places from the database
    mycursor.execute("SELECT * FROM offers")
    all_offers = mycursor.fetchall()

    for offer in all_offers:
        delete = False
        available = offer[3].split('-')
        end_date = available[1].split('/')
        
        # Checks if the available dates have expired
        if int(date_now[2]) > int(end_date[2]):
            delete = True
        elif int(date_now[2]) == int(end_date[2]):
            if int(date_now[0]) > int(end_date[0]):
                delete = True
            elif int(date_now[0]) == int(end_date[0]):
                if int(date_now[1]) > int(end_date[1]):
                    delete = True
        if delete:
            # Deletes all of the places whos available dates have expired from the database
            mycursor.execute(f"DELETE FROM offers WHERE offer_ID = '{offer[9]}'")
            db.commit()

# Checks whether a person with a given ID already exists in the database for the check sign up
def check_person(person, curr_socket):
    mycursor.execute(f"SELECT * FROM person WHERE IDnum = '{person.id}'")
    rows = mycursor.fetchall()

    # If the person exists it returns an error, else it returns fine 
    if len(rows) != 0:
        curr_socket.send("00005".encode())
        curr_socket.send('error'.encode())
    else:
        curr_socket.send("00004".encode())
        curr_socket.send('fine'.encode())
        add_to_DB(person)

# Checks the log in information
def check_log_in(data, curr_socket):
    info = re.findall(r'Login:(.+)', data)
    info2 = info[0].split(',')

    # Searches in the database for a person with the same ID number and password
    mycursor.execute(f"SELECT * FROM person WHERE IDnum='{info2[0]}' AND password='{info2[1]}'")
    check_person = mycursor.fetchall()

    # If there is no person then it returns error
    if len(check_person) == 0:
        curr_socket.send("00005".encode())
        curr_socket.send("error".encode())

    # Else it checks if the person is the admin or not and responds accordingly
    else:
        if check_person[0][5] == 1:
            curr_socket.send("00008".encode())
            curr_socket.send('is_admin'.encode())
        else:
            curr_socket.send("00009".encode())
            curr_socket.send('not_admin'.encode())
            
        send_surveys(info2[0], curr_socket)

# Adds customers or offers to the database
def add_to_DB(object):
    if type(object) is customers:
        mycursor.execute("INSERT INTO person (Fname, Lname, password, IDnum, email, isadmin) \
            VALUES (%s, %s, %s, %s, %s, %s)", (object.fname, object.lname, object.password, object.id, object.email, False))
    
    else:
        mycursor.execute("INSERT INTO offers (ID_seller, ID_buyer, address, available, buyer_date, \
            num_rooms, price, conditions, pics) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (object.ID_seller, "", 
            object.address, object.start_date + '-' + object.end_date, '', object.num_rooms, object.price, object.conditions, object.pics))
    db.commit()

# Returns places according to given filters
def search(data, curr_socket):
    addr = data.split(':')

    # If it is from an admin then it fetches all of the rooms
    if addr[0] == 'admin_addr':
        if addr[2] == '':
            mycursor.execute("SELECT * FROM offers")
            all_offers = mycursor.fetchall()
    
    # Checks the filters for the show all data function from the client and fetches the places accordingly
    elif addr[0] == 'admin_data_addr':
        if addr[2] == 'All':
            mycursor.execute("SELECT * FROM offers")
        elif addr[2] == 'Open':
            mycursor.execute("SELECT * FROM offers WHERE ID_buyer = ''")
        else:
            mycursor.execute("SELECT * FROM offers WHERE ID_buyer != ''")
        
        all_offers = mycursor.fetchall()

    # If it isn't from a admin then it fetches all of the places that are open
    else:
        mycursor.execute("SELECT * FROM offers WHERE ID_buyer = ''")
        offers = mycursor.fetchall()
        # all_offers = filter(lambda element: element[-1] not in timed_rooms, offers)
        all_offers = []
        for offer in offers:
            if str(offer[-1]) not in timed_rooms:
                all_offers.append(offer)

    # Appends all of the rooms to the all_rooms list
    if addr[2] == '' or addr[2] == 'All' or addr[2] == 'Bought':
        all_rooms = []
        for offer in all_offers:
            all_rooms.append(offer)

    elif 'Bought' in addr[2]:
        # Checks whether the purchased rooms were purhased by a registered or unregistered customer
        mycursor.execute("SELECT * FROM person")
        all_people = mycursor.fetchall()

        reg_offers = []
        unreg_offers = []
        for offer in all_offers:
            for person in all_people:
                if offer[1] == person[3]:
                    reg_offers.append(offer)
                    break
            if offer not in reg_offers:
                unreg_offers.append(offer)
        
        # Adds the rooms to all_rooms
        if 'Registered' in addr[2]:
            all_rooms = reg_offers
        else:
            all_rooms = unreg_offers

    elif addr[2] == '   Closest   ':
        # Gets all of the rooms in order by closest to a given address
        if addr[1] != '':
            dict_offer = {}
            addr = addr[1]
            for offer in all_offers:
                geolocator = Nominatim(user_agent="tutorial")
                location1 = geolocator.geocode(addr)
                location2 = geolocator.geocode(offer[2])
                distance = geodesic((location1.latitude, location1.longitude), (location2.latitude, location2.longitude)).kilometers
                dict_offer[distance] = offer
            dict_offer = dict(sorted(dict_offer.items()))
            all_rooms = list(dict_offer.values())
        else:
            all_rooms = []
            for offer in all_offers:
                all_rooms.append(offer)
    else:
        # Gets all of the rooms in order by cheepest or most expensive
        dict_offer = {}
        for offer in all_offers:
            dict_offer[offer[6]] = offer

        if addr[2] == 'Lowest Price ':
            dict_offer = dict(sorted(dict_offer.items()))
            all_rooms = list(dict_offer.values())
        else:
            dict_offer = dict(sorted(dict_offer.items(), reverse=True))
            all_rooms = list(dict_offer.values())

    # Adds attractions to the list
    if len(attractions) == 0:
        all_rooms.append('')
    else:
        all_rooms.append(attractions)

    # Checks the exact buffer length of the data being sent
    data = pickle.dumps(all_rooms)
    length = len(data)
    count = 0
    while length != 0:
        length = int(length/10)
        count+=1

    buffer = (5-count)*'0' + f'{len(data)}'

    # Sends the rooms to the client
    curr_socket.send(buffer.encode())
    curr_socket.send(data)

    # Sends the images to the client
    if addr[0] != 'admin_data_addr':
        send_images(all_rooms, curr_socket, True)

# Updates the database if a client rented a place
def rent_place(data):
    info = data.split(' ')
    mycursor.execute(f"UPDATE offers SET ID_buyer = '{info[1]}', buyer_date = '{info[2]}' WHERE offer_ID = {info[3]}")
    db.commit()

# Searches for places that have been bought by a certain customer using ID number
def search_by_id(data, curr_socket):
    data = data.split(' ')
    # Fetches all of the places that have been bought with the same ID
    mycursor.execute(f"SELECT * FROM offers WHERE ID_buyer = '{data[1]}'")
    all_rooms = mycursor.fetchall()

    # Checks the exact buffer length of the data being sent
    data = pickle.dumps(all_rooms)
    length = len(data)
    count = 0
    while length != 0:
        length = int(length/10)
        count+=1

    buffer = (5-count)*'0' + f'{len(data)}'
    
    # Sends the places to the client
    curr_socket.send(buffer.encode())
    curr_socket.send(data)

    send_images(all_rooms, curr_socket, False)

# Updates the database and cancels a purchase of a specific place
def cancel_purchase(data):
    data = data.split(' ')
    mycursor.execute(f"UPDATE offers SET ID_buyer = '', buyer_date = '' WHERE offer_ID = '{data[1]}'")
    db.commit()

# Checks if the given ID is in surveys_to_send, if it is then the server says to the client to run a survey
# otherwise it says no
def send_surveys(id, curr_socket):
    if id in surveys_to_send:
        curr_socket.send("00011".encode())
        curr_socket.send('room_survey'.encode())
        surveys_to_send.remove(id)
    else:
        curr_socket.send("00014".encode())
        curr_socket.send('no_room_survey'.encode())

# Sends a broadcast message to all users through the UDP socket the new date that the admin set
def change_date(data):
    global current_date
    date = data.split(':')
    new_date = date[1]

    try:
        udp_sock.sendto(data.encode(), ('<broadcast>', 55554))
    except:
        pass

    current_date = new_date
    check_places_dates(current_date)

# Sends to the client places according to the date filters and availability filters
def filter_admin_map(data, curr_socket):
    data = data.split(':')
    dates = data[1].split('-')

    # Formats the dates according to the original format
    if '.' in dates[0]:
        s_date = dates[0].split('.')
        start_date = [s_date[1], s_date[0], s_date[2][2:]]
        e_date = dates[1].split('.')
        end_date = [e_date[1], e_date[0], s_date[2][2:]] 
    else:
        start_date = dates[0].split('/')
        end_date = dates[1].split('/')
    filter = data[2]

    # If the filter is All it fetches all places from the database
    if filter == 'All':
        mycursor.execute("SELECT * FROM offers")
    # If the filter is All it fetches all places that have been bought from the database
    elif filter == 'Bought':
        mycursor.execute("SELECT * FROM offers WHERE ID_buyer != ''")
    # Else it fetches all places that are available for purchase from the database
    else:
        mycursor.execute("SELECT * FROM offers WHERE ID_buyer = ''")
    
    all_offers = mycursor.fetchall()
    offers_to_send = []
    # Then it checks for all of the offers if the range of the dates that it was 
    # bought for is in between the filter dates
    for offer in all_offers:
        send_offer = True
        av_date = offer[3].split('-')
        start_av_date = av_date[0].split('/')
        end_av_date = av_date[1].split('/')

        if int(start_date[2]) > int(end_av_date[2]):
            send_offer = False
        elif int(start_date[2]) == int(end_av_date[2]):
            if int(start_date[0]) > int(end_av_date[0]):
                send_offer = False
            elif int(start_date[0]) == int(end_av_date[0]):
                if int(start_date[1]) > int(end_av_date[1]):
                    send_offer = False
        
        if int(start_av_date[2]) > int(end_date[2]):
            send_offer = False
        elif int(start_av_date[2]) == int(end_date[2]):
            if int(start_av_date[0]) > int(end_date[0]):
                send_offer = False
            elif int(start_av_date[0]) == int(end_date[0]):
                if int(start_av_date[1]) > int(end_date[1]):
                    send_offer = False

        if send_offer:
            offers_to_send.append(offer)
        
    # Checks the exact buffer length of the data being sent
    data = pickle.dumps(offers_to_send)
    length = len(data)
    count = 0
    while length != 0:
        length = int(length/10)
        count+=1

    buffer = (5-count)*'0' + f'{len(data)}'

    # Sends the places to the client
    curr_socket.send(buffer.encode())
    curr_socket.send(data)

    # Sends the images of the places to the client
    send_images(offers_to_send, curr_socket, False)

# Gets new images from the client and saves it to the photos folder
def get_images(curr_socket):
    pic = b""

    while True:
        # Receives the image
        buffer = curr_socket.recv(10).decode()
        packet = b''
        while len(packet) < int(buffer):
            packet += curr_socket.recv(int(buffer))
        if packet == "stop".encode():       
            break                   
        if packet == "finished pic".encode():
            # Receives the name of the image then saves it in the photo folder
            buffer = curr_socket.recv(5).decode()
            pic_name = curr_socket.recv(int(buffer)).decode()
            with open(f"{pic_name}",'wb') as save:
                save.write(pic)
            pic = b""
        else:
            pic+=packet

# Sends to the client the images for each place
def send_images(list_places, curr_socket, send_atrs):

    if send_atrs:
        atr_places = list_places.pop(-1)
    
    # Goes over each place in the list and sends to the client the images
    for place in list_places:
        pics = place[8].split(' ')
        for pic in pics:
            # Reads the image file
            with open(pic,'rb') as file:
                data = file.read()

                # Checks the exact buffer length of the data being sent
                length = len(data)
                count = 0
                while length != 0:
                    length = int(length/10)
                    count+=1

                buffer = (10-count)*'0' + f'{len(data)}'
                # Sends the image to the client
                curr_socket.send(buffer.encode())
                curr_socket.send(data)

            # Finished sending the image
            curr_socket.send('0000000012'.encode())
            curr_socket.send("finished pic".encode())

            # Sends the name of the image
            length = len(pic)
            count = 0
            while length != 0:
                length = int(length/10)
                count+=1

            buffer = (5-count)*'0' + f'{len(pic)}'
            curr_socket.send(buffer.encode())
            curr_socket.send(f"{pic}".encode())
    
    # Stops sending place images
    curr_socket.send('0000000004'.encode())
    curr_socket.send("stop".encode())

    if send_atrs:
        # Goes over each attraction in the list and sends to the client the images
        for place in atr_places:
            place = place.split('$')
            pics = place[-1].split(' ')
            for pic in pics:
                # Reads the image file
                with open(pic,'rb') as file:
                    data = file.read()
                    
                    # Checks the exact buffer length of the data being sent
                    length = len(data)
                    count = 0
                    while length != 0:
                        length = int(length/10)
                        count+=1

                    buffer = (10-count)*'0' + f'{len(data)}'
                    # Sends the image to the client
                    curr_socket.send(buffer.encode())
                    curr_socket.send(data)

                # Finished sending the image
                curr_socket.send('0000000012'.encode())
                curr_socket.send("finished pic".encode())
                
                # Sends the name of the image
                length = len(pic)
                count = 0
                while length != 0:
                    length = int(length/10)
                    count+=1

                buffer = (5-count)*'0' + f'{len(pic)}'
                curr_socket.send(buffer.encode())
                curr_socket.send(f"{pic}".encode())

    # Stops sending attraction images
    curr_socket.send('0000000004'.encode())
    curr_socket.send("stop".encode())

def timer(room_num):  
    timer = 60;
    while timer:
        time.sleep(1)
        timer -= 1

    global timed_rooms
    timed_rooms.remove(room_num)

def run_timer(data):
    global timed_rooms
    data = data.split(':')
    timed_rooms.append(data[1])
    _thread.start_new_thread(lambda:timer(data[1]), ())

# Runs the check_places_dates every time the server runs
check_places_dates(current_date)

# Runs the connection between the server and the clients
while True:
    read,write,error =  select(all_sockets, all_sockets,[])
    for curr_socket in read:

        # If it is a new connection then it is added to the list of sockets
        if curr_socket == conn_sock:
            client_sock,addr = conn_sock.accept()
            all_sockets.append(client_sock)

            # Server sends to the client the current date
            client_sock.send(current_date.encode())
        else:
            # Else it recieves data from a certain client
            try:
                buffer = curr_socket.recv(5).decode()
                data = curr_socket.recv(int(buffer))
            except:
                all_sockets.remove(curr_socket)
                continue
            if not data:
                all_sockets.remove(curr_socket)
            else:
                try:
                    data = pickle.loads(data)
                except:        
                    data = data.decode()

                # If the type of data is customers then it is a 
                # new customer that needs to be added to the database
                if type(data) is customers:
                    check_person(data, curr_socket)

                # If it is a offer than it is a new offer that needs to be added to the database
                elif 'offer' in data:
                    get_images(curr_socket)
                    buffer = curr_socket.recv(5).decode()
                    data = curr_socket.recv(int(buffer))
                    data = pickle.loads(data)
                    add_to_DB(data)
                
                # Checks the log in information
                elif "Login" in data:
                    check_log_in(data, curr_socket)
                
                # Runs the seatch funtion according to given filters in the data
                elif 'addr' in data:
                    search(data, curr_socket)
                
                # Updates the database about a customer renting a place
                elif 'rent' in data:
                    rent_place(data)
                
                # Returns all places owned by the customer with the given ID number
                elif 'id' in data:
                    search_by_id(data, curr_socket)

                # Updates database if a customer cancels on a purchase
                elif 'cancel' in data:
                    cancel_purchase(data)
                
                # Sends to all other clients the new date set by the admin
                elif 'change_date' in data:
                    change_date(data)
                
                # Receives attractions from the admin and sends it to other clients when needed
                elif 'attraction' in data:
                    if 'new' in data:
                        get_images(curr_socket)

                    buffer = curr_socket.recv(5).decode()
                    data = curr_socket.recv(int(buffer)).decode()
                    all_atrs = data.split('%')

                    for atr in all_atrs:
                        if atr not in attractions:
                            attractions.append(atr)
                
                # Sends filtered admin data
                elif 'filter' in data:
                    filter_admin_map(data, curr_socket)

                elif 'room' in data:
                    run_timer(data)

                
