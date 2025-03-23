import streamlit as st

class FlightBookingSystem:
    def __init__(self):
        self.initialize_data()

    def initialize_data(self):
        if 'flights' not in st.session_state:
            st.session_state.flights = {
                'PK101': {'destination': 'Karachi', 'seats': 10, 'time': '08:00 AM', 'status': 'On Time'},
                'PK202': {'destination': 'Lahore', 'seats': 5, 'time': '11:30 AM', 'status': 'Delayed'},
                'PK303': {'destination': 'Islamabad', 'seats': 8, 'time': '03:45 PM', 'status': 'On Time'},
            }
        if 'bookings' not in st.session_state:
            st.session_state.bookings = {}

    def display_flights(self):
        st.subheader("🛫 Available Flights")
        flight_data = []
        for flight, details in st.session_state.flights.items():
            flight_data.append([
                flight,
                details['destination'],
                details['time'],
                details['seats'],
                details['status']
            ])
        
        st.table({
            "Flight Number": [f[0] for f in flight_data],
            "Destination": [f[1] for f in flight_data],
            "Departure Time": [f[2] for f in flight_data],
            "Available Seats": [f[3] for f in flight_data],
            "Status": [f"🟢 {f[4]}" if f[4] == 'On Time' else f"🔴 {f[4]}" for f in flight_data]
        })

    def book_flight(self, name, flight_no):
        if flight_no in st.session_state.flights:
            if st.session_state.flights[flight_no]['seats'] > 0:
                st.session_state.flights[flight_no]['seats'] -= 1
                st.session_state.bookings[name] = {
                    'flight': flight_no,
                    'destination': st.session_state.flights[flight_no]['destination'],
                    'time': st.session_state.flights[flight_no]['time']
                }
                return True
        return False

    def view_bookings(self):
        st.subheader("📖 Your Bookings")
        if not st.session_state.bookings:
            st.warning("No bookings yet.")
        else:
            booking_data = []
            for name, details in st.session_state.bookings.items():
                booking_data.append([
                    name,
                    details['flight'],
                    details['destination'],
                    details['time']
                ])
            
            st.table({
                "Passenger Name": [b[0] for b in booking_data],
                "Flight Number": [b[1] for b in booking_data],
                "Destination": [b[2] for b in booking_data],
                "Departure Time": [b[3] for b in booking_data]
            })

    def cancel_booking(self, name):
        if name in st.session_state.bookings:
            flight_no = st.session_state.bookings[name]['flight']
            st.session_state.flights[flight_no]['seats'] += 1
            del st.session_state.bookings[name]
            return True
        return False

def main():
    st.set_page_config(page_title="Pakistan Air Booking", page_icon="✈️")
    system = FlightBookingSystem()

    st.title("✈️ Pakistan Air Booking System")
    st.markdown("---")

    menu_options = {
        "View Flights": "🛫",
        "Book Flight": "📅",
        "My Bookings": "📖",
        "Cancel Booking": "❌",
        "Flight Status": "🕒"
    }
    
    menu_choice = st.sidebar.radio(
        "Navigation Menu",
        list(menu_options.keys()),
        format_func=lambda x: f"{menu_options[x]} {x}"
    )

    if menu_choice == "View Flights":
        system.display_flights()

    elif menu_choice == "Book Flight":
        st.subheader("📅 Book a Flight")
        with st.form("booking_form"):
            name = st.text_input("Passenger Name")
            flight_no = st.selectbox(
                "Select Flight",
                options=list(st.session_state.flights.keys()),
                format_func=lambda x: f"{x} to {st.session_state.flights[x]['destination']} ({st.session_state.flights[x]['time']})"
            )
            
            if st.form_submit_button("Book Flight"):
                if name and flight_no:
                    if system.book_flight(name, flight_no):
                        st.success(f"✅ Booking successful! {name} booked on {flight_no} to {st.session_state.flights[flight_no]['destination']}")
                    else:
                        st.error("❌ Booking failed. No seats available or invalid flight number.")
                else:
                    st.warning("⚠️ Please fill all fields")

    elif menu_choice == "My Bookings":
        system.view_bookings()

    elif menu_choice == "Cancel Booking":
        st.subheader("❌ Cancel Booking")
        with st.form("cancel_form"):
            name = st.text_input("Enter your name to cancel booking")
            if st.form_submit_button("Cancel Booking"):
                if system.cancel_booking(name):
                    st.success(f"✅ Booking for {name} has been canceled")
                else:
                    st.error("❌ No bookings found under this name")

    elif menu_choice == "Flight Status":
        st.subheader("🕒 Flight Status")
        system.display_flights()

    st.sidebar.markdown("---")
    st.sidebar.info(
        "**Note:** All bookings are subject to availability. "
        "Please check flight status regularly for updates."
    )

if __name__ == "__main__":
    main()