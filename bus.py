# app.py
import streamlit as st
import json
import os

# ------------------- Classes -------------------
class Bus:
    def __init__(self, b_no=0, total_seats=0, source="unknown", destination="unknown", ticket_price=0.0, seats=None):
        self.b_no = int(b_no)
        self.total_seats = int(total_seats)
        self.source = source
        self.destination = destination
        self.ticket_price = float(ticket_price)
        self.seats = seats if seats is not None else [False] * (self.total_seats + 1)

    def seat_layout(self):
        layout = ""
        for i in range(1, self.total_seats + 1):
            layout += f"Seat {i}: {'Reserved' if self.seats[i] else 'Available'}  "
            if i % 4 == 0:
                layout += "\n"
        return layout

class Passenger:
    def __init__(self, name="unknown", age=0, seat_no=0, bus_no=0, amountPaid=0.0, paymentDone=False, paymentMode="None"):
        self.name = name
        self.age = int(age)
        self.seat_no = int(seat_no)
        self.bus_no = int(bus_no)
        self.amountPaid = float(amountPaid)
        self.paymentDone = paymentDone
        self.paymentMode = paymentMode

# ------------------- Data Storage -------------------
buses = []
passengers = []

# ------------------- File Persistence -------------------
BUS_FILE = "buses.json"
PASS_FILE = "passengers.json"

def save_data():
    # Buses
    bus_list = []
    for b in buses:
        bus_list.append({
            "b_no": b.b_no,
            "total_seats": b.total_seats,
            "source": b.source,
            "destination": b.destination,
            "ticket_price": b.ticket_price,
            "seats": b.seats
        })
    with open(BUS_FILE, "w") as f:
        json.dump(bus_list, f)
    
    # Passengers
    pass_list = []
    for p in passengers:
        pass_list.append({
            "name": p.name,
            "age": p.age,
            "seat_no": p.seat_no,
            "bus_no": p.bus_no,
            "amountPaid": p.amountPaid,
            "paymentDone": p.paymentDone,
            "paymentMode": p.paymentMode
        })
    with open(PASS_FILE, "w") as f:
        json.dump(pass_list, f)

def load_data():
    global buses, passengers
    if os.path.exists(BUS_FILE):
        with open(BUS_FILE, "r") as f:
            bus_list = json.load(f)
        buses = [Bus(**b) for b in bus_list]

    if os.path.exists(PASS_FILE):
        with open(PASS_FILE, "r") as f:
            pass_list = json.load(f)
        passengers = [Passenger(**p) for p in pass_list]

# Load previous data on app start
load_data()

# ------------------- Helper Functions -------------------
def search_bus(bus_no):
    for b in buses:
        if b.b_no == bus_no:
            return b
    return None

def add_bus(bus_no, total_seats, source, destination, price):
    if search_bus(bus_no):
        st.warning(f"Bus {bus_no} already exists!")
        return
    buses.append(Bus(bus_no, total_seats, source, destination, price))
    save_data()
    st.success(f"Bus {bus_no} added successfully!")

def book_seat(bus_no, seat_no, name, age, mode):
    bus = search_bus(bus_no)
    if not bus:
        st.warning(f"Bus {bus_no} not found!")
        return
    if seat_no <= 0 or seat_no > bus.total_seats:
        st.warning(f"Invalid seat number {seat_no}")
        return
    if bus.seats[seat_no]:
        st.warning(f"Seat {seat_no} already reserved!")
        return
    bus.seats[seat_no] = True
    p = Passenger(name, age, seat_no, bus_no, bus.ticket_price, True, mode)
    passengers.append(p)
    save_data()
    st.success(f"Seat {seat_no} booked for {name} on Bus {bus_no}!")

def cancel_seat(bus_no, seat_no):
    bus = search_bus(bus_no)
    if not bus:
        st.warning(f"Bus {bus_no} not found!")
        return
    if seat_no <= 0 or seat_no > bus.total_seats:
        st.warning(f"Invalid seat number {seat_no}")
        return
    if not bus.seats[seat_no]:
        st.warning(f"Seat {seat_no} is not reserved!")
        return
    bus.seats[seat_no] = False
    removed = False
    for i, p in enumerate(passengers):
        if p.bus_no == bus_no and p.seat_no == seat_no:
            passengers.pop(i)
            removed = True
            st.info(f"Refunding amount: {p.amountPaid}")
            break
    save_data()
    if removed:
        st.success(f"Seat {seat_no} on Bus {bus_no} cancelled.")
    else:
        st.info("Seat freed but passenger record not found.")

# ------------------- Streamlit UI -------------------
st.title("Bus Ticket Booking System")
menu = ["Add Bus", "Show Buses", "Book Seat", "Cancel Seat", "Show Passengers"]
choice = st.sidebar.selectbox("Menu", menu)

# (UI code same as before...)



if choice == "Add Bus":
    st.subheader("Add New Bus")
    bus_no = st.number_input("Bus Number", min_value=1, step=1)
    total_seats = st.number_input("Total Seats", min_value=1, step=1)
    source = st.text_input("Source")
    destination = st.text_input("Destination")
    price = st.number_input("Ticket Price", min_value=0.0, step=0.1)
    if st.button("Add Bus"):
        add_bus(bus_no, total_seats, source, destination, price)

elif choice == "Show Buses":
    st.subheader("All Buses")
    if not buses:
        st.info("No buses available.")
    for b in buses:
        st.text(f"Bus {b.b_no}: {b.source} -> {b.destination}, Price: {b.ticket_price}, Seats: {b.total_seats}")
        st.text(b.seat_layout())
        st.text("--------------------")

elif choice == "Book Seat":
    st.subheader("Book a Seat")

    bus_no = st.number_input("Bus Number", min_value=1, step=1, key="book_bus_no")
    bus = search_bus(bus_no)

    if bus:
        st.write("### Seat Layout")

        # Make a 4-column seat grid
        cols = st.columns(4)

        for i in range(1, bus.total_seats + 1):
            col = cols[(i - 1) % 4]

            if bus.seats[i] == False:
                # Available: green button
                if col.button(f"{i}", key=f"seat_{i}", help="Available Seat"):
                    st.session_state["selected_seat"] = i
            else:
                # Reserved: red disabled button
                col.button(f"{i} ❌", key=f"seat_{i}_disabled", disabled=True)

        st.write("---")

        # Auto-filled seat number when user clicks a seat
        selected = st.session_state.get("selected_seat", None)
        seat_no = st.number_input("Seat Number", min_value=1, step=1, value=selected if selected else 1)

        name = st.text_input("Passenger Name")
        age = st.number_input("Age", min_value=0, step=1)
        mode = st.selectbox("Payment Mode", ["Cash", "Card", "UPI"])

        if st.button("Book Seat"):
            book_seat(bus_no, seat_no, name, age, mode)
            st.session_state["selected_seat"] = None



elif choice == "Cancel Seat":
    st.subheader("Cancel a Seat")
    bus_no = st.number_input("Bus Number", min_value=1, step=1, key="cancel_bus_no")
    seat_no = st.number_input("Seat Number", min_value=1, step=1, key="cancel_seat_no")
    if st.button("Cancel Seat"):
        cancel_seat(bus_no, seat_no)

elif choice == "Show Passengers":
    st.subheader("All Passengers")
    if not passengers:
        st.info("No passengers booked yet.")
    for p in passengers:
        st.text(f"{p.name} | Age: {p.age} | Bus: {p.bus_no} | Seat: {p.seat_no} | Paid: {p.amountPaid} | Mode: {p.paymentMode}")
