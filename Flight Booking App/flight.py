class FlightBookingSystem:
    def __init__(self):
        self.flights = {
            'PK101' : {'destination' : 'Karachi' , 'seats' : 10},
            'PK202' : {'destination' : 'Lahore' , 'seats' : 5},
            'PK303' : {'destination' : 'Islamabad' , 'seats' : 8},
        }

        self.bookings = {}

    def display_flights(self):
        print("\nAvailable Flights: ")
        for flight , details in self.flights.items():
            print(f"{flight} : {details['destination']} - seats Available : {details['seats']}")
    
    def book_flight(self):
        name = input("Enter You'r Name: ")
        self.display_flights()
        flight_no = input("Enter Flight Number To Book: ") 

        if flight_no in self.flights and self.flights[flight_no]['seats'] > 0:
            self.flights[flight_no]['seats'] -= 1
            self.bookings[name] = flight_no
            print(f"Booking sucessful {name} booked on {flight_no} to {self.flights[flight_no]['destination']}.")
        
        else:
            print("Invalid flight number or no seats available")
        
    def view_bookings(self):
        print("\nYour Bookings")

        if not self.bookings:
            print("No bookings yet.")
        
        else:
            for name , flight_no in self.bookings.items():
                print(f"{name}: Flight {flight_no} to {self.flights[flight_no]['destination']}")
    
    def cancel_booking(self):

        name = input("Enter your name to cancel booking: ")
        if name in self.bookings:
            flight_no = self.bookings.pop(name)
            self.flights[flight_no]['seats'] += 1

            print(f"Booking for {name} on {flight_no} has been canceled")
        
        else:
            print("No bookings found under this name")
    
    def menu(self):

        while True:
            print("\nFlight Booking System")
            print("1. View Flights")
            print("2. Book Flight")
            print("3. View My Bookings")
            print("4. Cancel Booking")
            print("5. Exit")

            choice = input("Enter your choice: ")
        
            if choice == '1':

                self.display_flights()

            elif choice == '2':

                self.book_flight()

            elif choice == '3':

                self.view_bookings()

            elif choice == '4':

                self.cancel_booking()

            elif choice == '5':

                print("Thank you for useing the Flight Booking System")
                break

            else:
                print("Invalid choice, please try again")

if __name__ == "__main__":
    
    system = FlightBookingSystem()

    system.menu()
