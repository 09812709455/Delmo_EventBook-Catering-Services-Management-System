import sqlite3
from datetime import datetime 

admin_username = "anne"
admin_password = "camille28"

def initialize_database():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    # Create menu table
    cursor.execute(''' 
        CREATE TABLE IF NOT EXISTS menu (
            menu_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            item_name TEXT NOT NULL
        )
    ''')
    
    

    # Check if the menu table is empty
    cursor.execute('SELECT COUNT(*) FROM menu')
    if cursor.fetchone()[0] == 0:
        # Define the default menu items
        default_menu = [
            ("Appetizers", "Mini Tarts"),
            ("Appetizers", "Bruschetta"),
            ("Main Course", "Grilled Chicken"),
            ("Main Course", "Herb-Crusted Salmon"),
            ("Desserts", "Wedding Cake"),
            ("Desserts", "Chocolate Fountain"),
            ("Drinks", "Iced Tea"),
            ("Drinks", "Lemonade"),
        ]

        # Insert default menu items into the menu table
        cursor.executemany('''
            INSERT INTO menu (category, item_name) VALUES (?, ?)
        ''', default_menu)  # Pass both the query and the list of tuples

    conn.commit()
    conn.close()

def create_bookings_table():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_date TEXT NOT NULL,
            event_time TEXT NOT NULL,
            location TEXT NOT NULL,
            chefs_name TEXT NOT NULL,
            wait_staff_name TEXT NOT NULL,
            event_coordinator_name TEXT NOT NULL,
            decor_specialist_name TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            booking_date TEXT NOT NULL
        );
    ''')

    try:
        # Attempt to create the 'selected_menu_items' table
        cursor.execute('''
            CREATE TABLE selected_menu_items (
                menu_item_id INTEGER NOT NULL,
                booking_id INTEGER NOT NULL,
                category TEXT,
                item_name TEXT,
                FOREIGN KEY(menu_item_id) REFERENCES menu(menu_id),
                FOREIGN KEY(booking_id) REFERENCES bookings(booking_id),
                PRIMARY KEY (menu_item_id, booking_id)
            )
        ''')
        print("Created 'selected_menu_items' table.")
    
    except sqlite3.OperationalError as e:
        if 'table selected_menu_items already exists' in str(e):
            print()
        else:
            print(f"Error creating 'selected_menu_items' table: {e}")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            booking_id INTEGER NOT NULL,
            payment_amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            payment_type TEXT,
            FOREIGN KEY(booking_id) REFERENCES bookings(booking_id)
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            client_id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            address TEXT,
            contact_number TEXT,
            email TEXT
        );
    ''')

    conn.commit()
    conn.close()

def add_client(client_name, address, contact_number, email):
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO clients (client_name, address, contact_number, email)
        VALUES (?, ?, ?, ?)
    ''', (client_name, address, contact_number, email))
    conn.commit()
    print(f"Client '{client_name}' has been added to the system.")

    cursor.execute("PRAGMA table_info(bookings);")
    columns = [col[1] for col in cursor.fetchall()]
    if "client_id" not in columns:
        cursor.execute("ALTER TABLE bookings ADD COLUMN client_id INTEGER;")

    conn.commit()
    conn.close()

def selected_menu_items_schema():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    cursor.execute("PRAGMA table_info(selected_menu_items)")
    columns = [column[1] for column in cursor.fetchall()]

    if 'category' not in columns:
        cursor.execute('ALTER TABLE selected_menu_items ADD COLUMN category TEXT')
        print("Added 'category' column to 'selected_menu_items' table.")
    if 'item_name' not in columns:
        cursor.execute('ALTER TABLE selected_menu_items ADD COLUMN item_name TEXT')
        print("Added 'item_name' column to 'selected_menu_items' table.")
    
    conn.commit()
    conn.close()

def view_menu():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()
    
    RESET = "\033[0m"
    YELLOW_FG = "\033[33m"
    RED_FG = "\033[31m"
    CYAN_FG = "\033[36m"
    BLUE_FG = "\033[34m"

    # Header with Box Design
    print(f"{CYAN_FG}")
    print("========================================")
    print("|           VIEW MENU                  |")
    print("========================================")
    print(f"{RESET}")
    # Fetch items from the database
    cursor.execute('SELECT menu_id, category, item_name FROM menu ORDER BY category, menu_id')
    rows = cursor.fetchall()

    if rows:
        current_category = None
        # Loop through and print the menu items
        for row in rows:
            menu_id, category, item_name = row
            if category != current_category:
                # Print category header
                print(f"{CYAN_FG}Category: {category}{RESET}")
                print(f"{CYAN_FG}-----------------{RESET}")
                current_category = category
            # Print item details with ID
            print(f"{YELLOW_FG}- {item_name} ({BLUE_FG}MENU ID: {menu_id}{RESET})")
    else:
        # Message if no items are available
        print(f"{RED_FG}No menu items available.{RESET}")

    # Close database connection
    conn.close()

def add_menu_item():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    RESET = "\033[0m"
    YELLOW_FG = "\033[33m"
    GREEN_FG = "\033[32m"
    RED_FG = "\033[31m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"

    # Icon characters
    CHECK_ICON = "\u2705"  # Checkmark
    CROSS_ICON = "\u274C"  # Cross
    ARROW_ICON = "\u2794"

    # Printing the header with design and color
    print(f"{CYAN_FG}\n====================================")
    print(f"        ➕ ADD MENU ITEM      {RESET}")
    print(f"{CYAN_FG}====================================\n{RESET}")

    # Input section
    category = input(f"{BLUE_FG}📋 Enter the category (e.g., Appetizers, Main Course, Desserts, Drinks): {RESET}").strip()
    item_name = input(f"{BLUE_FG}🍽️ Enter the name of the item: {RESET}").strip()

    # Confirmation section with color and icon
    print(f"\n{GREEN_FG}{CHECK_ICON} You are about to add the following item:{RESET}")
    print(f"{YELLOW_FG}Category: {category}{RESET}")
    print(f"{YELLOW_FG}Item Name: {item_name}{RESET}")
    confirm = input(f"{GREEN_FG}{ARROW_ICON} Do you want to add this item? (yes/no): {RESET}").strip().lower()

    if confirm == 'yes':
        print(f"\n{CHECK_ICON} {GREEN_FG}Item added successfully!{RESET}")
    else:
        print(f"\n{CROSS_ICON} {RED_FG}Item not added.{RESET}")
    if confirm == "yes":
        try:
            cursor.execute('''
                INSERT INTO menu (category, item_name) VALUES (?, ?)
            ''', (category, item_name))
            conn.commit()
            print(f"{YELLOW_FG}Menu item '{item_name}' added successfully under '{category}' category.{RESET}")
        except Exception as e:
            print(f"{RED_FG}Error adding menu item: {e}{RESET}")
    else:
        print(f"{YELLOW_FG}Operation cancelled. No item was added.{RESET}")

    conn.close()

def update_menu_item():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    RESET = "\033[0m"
    YELLOW_FG = "\033[33m"
    GREEN_FG = "\033[32m"
    RED_FG = "\033[31m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"

    # Icon characters
    CHECK_ICON = "\u2705"  # Checkmark (✔)
    CROSS_ICON = "\u274C"  # Cross (✖)
    INFO_ICON = "\u2139"   # Information icon (ℹ)
    ARROW_ICON = "\u2794"  # Arrow (➔)

    print(f"{CYAN_FG}\n====================================")
    print(f"|          {ARROW_ICON} UPDATE MENU ITEM {ARROW_ICON}         |{RESET}")
    print(f"{CYAN_FG}===================================={RESET}\n")

    view_menu()  # Display the current menu for user reference

    # Prompt for item ID
    item_id = input(f"{GREEN_FG}🔢 Enter the ID of the item to update: {RESET}").strip()

    try:
        item_id = int(item_id)
    except ValueError:
        print(f"{RED_FG}{CROSS_ICON} Invalid ID. Please enter a valid number.{RESET}")
        return
    cursor.execute('SELECT menu_id, category, item_name FROM menu WHERE menu_id = ?', (item_id,))
    item = cursor.fetchone()

    if item:
        print(f"{INFO_ICON} {BLUE_FG}Current Item: {item[1]} - {item[2]}{RESET}")
        new_category = input(f"{ARROW_ICON} {GREEN_FG}Enter new category (current: {item[1]}): {RESET}").strip()
        new_item_name = input(f"{ARROW_ICON} {GREEN_FG}Enter new item name (current: {item[2]}): {RESET}").strip()

        # Use the current values if no new input is provided
        new_category = new_category if new_category else item[1]
        new_item_name = new_item_name if new_item_name else item[2]

        # Confirmation message
        print(f"\n{INFO_ICON} {BLUE_FG}You are about to update the item to:{RESET}")
        print(f"{CHECK_ICON} {YELLOW_FG}Category: {new_category}{RESET}")
        print(f"{CHECK_ICON} {YELLOW_FG}Item Name: {new_item_name}{RESET}")

        confirm = input(f"{ARROW_ICON} {GREEN_FG}Do you want to proceed with the update? (yes/no): {RESET}").strip().lower()

        if confirm == "yes":
            try:
                cursor.execute('''
                    UPDATE menu 
                    SET category = ?, item_name = ? 
                    WHERE menu_id = ?
                ''', (new_category, new_item_name, item_id))
                conn.commit()
                print(f"{GREEN_FG}{CHECK_ICON} Menu item updated successfully!{RESET}")
                view_menu()  # Display the updated menu
            except Exception as e:
                print(f"{RED_FG}{CROSS_ICON} Error updating menu item: {e}{RESET}")
        else:
            print(f"{YELLOW_FG}{CROSS_ICON} Menu item update canceled.{RESET}")
    else:
        print(f"{YELLOW_FG}{INFO_ICON} No item found with ID {item_id}. Please try again.{RESET}")

    conn.close()

def delete_menu_item():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    RESET = "\033[0m"
    YELLOW_FG = "\033[33m"
    GREEN_FG = "\033[32m"
    RED_FG = "\033[31m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"

    # Icons
    CHECK_ICON = "\u2705"  # Checkmark (✔)
    CROSS_ICON = "\u274C"  # Cross (✖)
    INFO_ICON = "\u2139"   # Information icon (ℹ)
    ARROW_ICON = "\u2794"  # Arrow (➔)

    print(f"{CYAN_FG}\n====================================")
    print(f"|          DELETE MENU ITEM         |{RESET}")
    print(f"{CYAN_FG}===================================={RESET}")

    view_menu()  # Display the menu before deleting
    item_id = input(f"{ARROW_ICON} {GREEN_FG}🔴 Enter the ID of the item to delete: {RESET}").strip()

    try:
        item_id = int(item_id)
    except ValueError:
        print(f"{RED_FG}{CROSS_ICON} Invalid ID. Please enter a valid number.{RESET}")
        conn.close()
        return

    # Fetch item details
    cursor.execute('SELECT menu_id, category, item_name FROM menu WHERE menu_id = ?', (item_id,))
    item = cursor.fetchone()

    if item:
        print(f"{INFO_ICON} {BLUE_FG}Current Item: {item[1]} - {item[2]}{RESET}")

        confirm = input(f"\n{ARROW_ICON} {GREEN_FG}Are you sure you want to delete '{item[2]}' from category '{item[1]}'? (yes/no): {RESET}").strip().lower()

        if confirm == "yes":
            cursor.execute('DELETE FROM menu WHERE menu_id = ?', (item_id,))
            conn.commit()
            print(f"{GREEN_FG}{CHECK_ICON} Menu item '{item[2]}' deleted successfully.{RESET}")
        else:
            print(f"{YELLOW_FG}{CROSS_ICON} Menu item deletion canceled.{RESET}")
    else:
        print(f"{YELLOW_FG}{INFO_ICON} No item found with ID {item_id}. Please try again.{RESET}")

    conn.close()

def add_booking():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    RESET = "\033[0m"
    YELLOW_FG = "\033[33m"
    GREEN_FG = "\033[32m"
    RED_FG = "\033[31m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"

    # Icons
    CHECK_ICON = "\u2705"  # Checkmark (✔)
    CROSS_ICON = "\u274C"  # Cross (✖)
    INFO_ICON = "\u2139"   # Information icon (ℹ)
    ARROW_ICON = "\u2794"  # Arrow (➔)

    print(f"{CYAN_FG}\n====================================")
    print(f"|          {ARROW_ICON} ADD NEW BOOKING {ARROW_ICON}     |{RESET}")
    print(f"{CYAN_FG}===================================={RESET}")

    # Gather booking details
    print(f"{CYAN_FG}+-------------------------------+")
    print(f"|        Provide Details        |")
    print(f"+-------------------------------+{RESET}")

    client_name = input(f"{BLUE_FG}| 📛 Client's Name:{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    event_type = input(f"{BLUE_FG}| 🎉 Event Type:{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    event_date = input(f"{BLUE_FG}| 📅 Event Date (YYYY-MM-DD):{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    event_time = input(f"{BLUE_FG}| 🕒 Event Time (HH:MM):{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    location = input(f"{BLUE_FG}| 📍 Event Location:{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    chefs_name = input(f"{BLUE_FG}| 👨‍🍳 Chef's Name:{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    wait_staff_name = input(f"{BLUE_FG}| 🧑‍🍳 Wait Staff's Name:{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    event_coordinator_name = input(f"{BLUE_FG}| 🧑‍💼 Event Coordinator's Name:{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")
    decor_specialist_name = input(f"{BLUE_FG}| 🎨 Decor Specialist's Name:{RESET}").strip()
    print(f"{CYAN_FG}+-------------------------------+{RESET}")

    print(f"\n{CYAN_FG}Thank you! All details have been recorded.{RESET}")
    # Validate input fields
    if not client_name or not event_type or not location or not chefs_name or not wait_staff_name:
        print(f"{RED_FG}{CROSS_ICON} Error: All fields are required. Please try again.{RESET}")
        return

    booking_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    selected_items = []
    while True:
        print(f"\n{BLUE_FG}Select Menu Items for the Event:{RESET}")
        view_menu()  # Function to view the menu
        selected_items_input = input(f"{ARROW_ICON} {GREEN_FG}Enter the IDs of selected menu items (comma separated): {RESET}").strip().split(",")

        for item_id in selected_items_input:
            try:
                item_id = int(item_id.strip())
                selected_items.append(item_id)
                print(f"{GREEN_FG}{CHECK_ICON} Added menu item with ID: {item_id}{RESET}")
            except ValueError:
                print(f"{RED_FG}{CROSS_ICON} Invalid item ID '{item_id}'. Skipping.{RESET}")

        add_more = input(f"{BLUE_FG}Do you want to add more menu items? (yes/no): {RESET}").strip().lower()
        if add_more != "yes":
            break

    if not selected_items:
        print(f"{GREEN_FG}{CROSS_ICON} No menu items selected. Exiting booking process.{RESET}")
        return

    # Payment details
    try:
        total_amount = float(input(f"{BLUE_FG}Enter the total event payment amount (₱): {RESET}").strip())
    except ValueError:
        print(f"{RED_FG}{CROSS_ICON} Invalid payment amount. Exiting booking process.{RESET}")
        return

    print(f"\n{CYAN_FG}====================================")
    print(f"          PAYMENT OPTIONS           {RESET}")
    print(f"{CYAN_FG}===================================={RESET}")
    print(f"{BLUE_FG}1. 💳 Full Payment (₱{total_amount * 0.9:.2f} with 10% discount){RESET}")
    print(f"{BLUE_FG}2. 💰 Installments (₱{total_amount / 2:.2f} upfront and ₱{total_amount - total_amount / 2:.2f} before the event date){RESET}")
    payment_option = input(f"{ARROW_ICON} {GREEN_FG}Choose a payment option (1 or 2): {RESET}").strip()

    if payment_option == "1":
        payment_amount = total_amount * 0.9
        payment_type = "Full Payment"
    elif payment_option == "2":
        payment_amount = total_amount / 2
        payment_type = "Installments - Upfront"
    else:
        print(f"{YELLOW_FG}{CROSS_ICON} Invalid payment option selected. Exiting booking process.{RESET}")
        return

    payment_date = input(f"{GREEN_FG}Enter payment date (YYYY-MM-DD): {RESET}").strip()

    print(f"\n{CYAN_FG}--- Booking Summary ---{RESET}")
    print(f"{BLUE_FG}Client: {client_name}{RESET}")
    print(f"{BLUE_FG}Event Type: {event_type}, Event Date: {event_date}, Event Time: {event_time}{RESET}")
    print(f"{BLUE_FG}Location: {location}{RESET}")
    print(f"{BLUE_FG}Total Payment: ₱{total_amount:.2f}{RESET}")
    print(f"{BLUE_FG}Payment Status: {payment_type}{RESET}")

    confirm = input(f"\n{ARROW_ICON} {GREEN_FG}Do you want to add this booking as pending? (yes/no): {RESET}").strip().lower()

    if confirm == "yes":
        try:
            # Insert booking details
            cursor.execute(''' 
                INSERT INTO bookings (
                    client_name, event_type, event_date, event_time, location,
                    chefs_name, wait_staff_name, event_coordinator_name, decor_specialist_name,
                    status, booking_date
                ) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            ''', (client_name, event_type, event_date, event_time, location,
                  chefs_name, wait_staff_name, event_coordinator_name, decor_specialist_name, booking_date))
            conn.commit()

            booking_id = cursor.lastrowid  # Retrieve the generated booking ID
            print(f"{GREEN_FG}{CHECK_ICON} Booking for '{client_name}' added as pending. Booking ID: {booking_id}{RESET}")

            # Insert selected menu items
            for item_id in selected_items:
                cursor.execute(''' 
                    SELECT category, item_name FROM menu WHERE menu_id = ? 
                ''', (item_id,))
                category, item_name = cursor.fetchone()

                cursor.execute(''' 
                    INSERT INTO selected_menu_items (menu_item_id, booking_id, category, item_name)
                    VALUES (?, ?, ?, ?)
                ''', (item_id, booking_id, category, item_name))
                conn.commit()

            # Insert payment details
            cursor.execute(''' 
                INSERT INTO payments (booking_id, payment_amount, payment_type, payment_date)
                VALUES (?, ?, ?, ?)
            ''', (booking_id, payment_amount, payment_type, payment_date))
            conn.commit()

            print(f"{GREEN_FG}{CHECK_ICON} Payment details recorded: ₱{payment_amount:.2f} ({payment_type}) on {payment_date}.{RESET}")

        except sqlite3.Error as e:
            print(f"{RED_FG}{CROSS_ICON} Error adding booking: {e}{RESET}")
            conn.rollback()
    else:
        print(f"{YELLOW_FG}{CROSS_ICON} Booking not added.{RESET}")

    conn.close()
    
def update_booking():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    RESET = "\033[0m"
    YELLOW_FG = "\033[33m"
    GREEN_FG = "\033[32m"
    RED_FG = "\033[31m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"
    # Icons
    CHECK_ICON = "\u2705"  # Checkmark (✔)
    CROSS_ICON = "\u274C"  # Cross (✖)
    ARROW_ICON = "\u2794"  # Arrow (➔)

    # Function to print a boxed text
    def print_boxed(text, color=BLUE_FG):
        print(f"{color}{'=' * (len(text) + 32)}")
        print(f"{color}| {text}                             |")
        print(f"{color}{'=' * (len(text) + 32)}{RESET}")

    print_boxed("UPDATE BOOKING", CYAN_FG)

    # Show available bookings
    print(f"{BLUE_FG}Available Bookings:{RESET}")
    cursor.execute(''' 
        SELECT booking_id, client_name, event_type, status FROM bookings
    ''')
    bookings = cursor.fetchall()

    if bookings:
        print(f"\n{BLUE_FG}Booking ID | Client Name | Event Type | Status{RESET}")
        for booking in bookings:
            print(f"{GREEN_FG}{booking[0]} | {booking[1]} | {booking[2]} | {booking[3]}{RESET}")
    else:
        print(f"{YELLOW_FG}{CROSS_ICON} No bookings available.{RESET}")
        conn.close()
        return

    booking_id = input(f"\n{GREEN_FG}Enter the Booking ID to update: {RESET}").strip()

    try:
        booking_id = int(booking_id)
    except ValueError:
        print(f"{RED_FG}{CROSS_ICON} Invalid ID. Please enter a valid number.{RESET}")
        conn.close()
        return
    
    cursor.execute(''' 
        SELECT booking_id, client_name, event_type, event_date, event_time, location, 
               chefs_name, wait_staff_name, event_coordinator_name, decor_specialist_name, status 
        FROM bookings WHERE booking_id = ? 
    ''', (booking_id,))
    booking = cursor.fetchone()

    if booking:
        # Check if the booking is confirmed
        if booking[10] == "confirmed":
            print(f"{GREEN_FG}{CROSS_ICON} Booking ID {booking_id} is already confirmed and cannot be updated.{RESET}")
            conn.close()
            return
        
        # Display current booking details
        print(f"\n{CYAN_FG}Current Booking Details:{RESET}")
        print(f"{BLUE_FG}Client: {booking[1]}, Event Type: {booking[2]}, Date: {booking[3]}, Time: {booking[4]}{RESET}")
        print(f"{BLUE_FG}Location: {booking[5]}, Chef: {booking[6]}, Wait Staff: {booking[7]}{RESET}")
        print(f"{BLUE_FG}Coordinator: {booking[8]}, Decor Specialist: {booking[9]}, Status: {booking[10]}{RESET}")

        # Update booking details
        client_name = input(f"{GREEN_FG}Enter new client name (current: {booking[1]}): {RESET}").strip() or booking[1]
        event_type = input(f"{GREEN_FG}Enter new event type (current: {booking[2]}): {RESET}").strip() or booking[2]
        event_date = input(f"{GREEN_FG}Enter new event date (current: {booking[3]}): {RESET}").strip() or booking[3]
        event_time = input(f"{GREEN_FG}Enter new event time (current: {booking[4]}): {RESET}").strip() or booking[4]
        location = input(f"{GREEN_FG}Enter new location (current: {booking[5]}): {RESET}").strip() or booking[5]
        chefs_name = input(f"{GREEN_FG}Enter new chef's name (current: {booking[6]}): {RESET}").strip() or booking[6]
        wait_staff_name = input(f"{GREEN_FG}Enter new wait staff's name (current: {booking[7]}): {RESET}").strip() or booking[7]
        event_coordinator_name = input(f"{GREEN_FG}Enter new coordinator's name (current: {booking[8]}): {RESET}").strip() or booking[8]
        decor_specialist_name = input(f"{GREEN_FG}Enter new decor specialist's name (current: {booking[9]}): {RESET}").strip() or booking[9]

        # Update the booking in the database
        cursor.execute(''' 
            UPDATE bookings
            SET client_name = ?, event_type = ?, event_date = ?, event_time = ?, location = ?, 
                chefs_name = ?, wait_staff_name = ?, event_coordinator_name = ?, decor_specialist_name = ? 
            WHERE booking_id = ? 
        ''', (client_name, event_type, event_date, event_time, location, chefs_name, wait_staff_name,
              event_coordinator_name, decor_specialist_name, booking_id))
        conn.commit()

        # Get the total payment amount
        total_amount = float(input(f"\n{GREEN_FG}Enter the total event payment amount (₱): {RESET}").strip())

        print(f"\n{CYAN_FG}====================================")
        print(f"          PAYMENT OPTIONS           ")
        print(f"{CYAN_FG}===================================={RESET}")
        # Show payment options
        print(f"{BLUE_FG}1. Full Payment (₱{total_amount * 0.9:.2f} with 10% discount){RESET}")
        print(f"{BLUE_FG}2. Installments (₱{total_amount / 2:.2f} upfront and ₱{total_amount / 2:.2f} before the event date){RESET}")
        payment_option = input(f"{ARROW_ICON} {GREEN_FG}Choose a payment option (1 or 2): {RESET}").strip()

        if payment_option == "1":
            # Full payment with 10% discount
            full_payment_amount = total_amount * 0.9
            print(f"{GREEN_FG}Full payment selected. Total payment after discount: ₱{full_payment_amount:.2f}{RESET}")
            payment_type = "Full Payment"
            total_payment = full_payment_amount  # Total event payment after discount

        elif payment_option == "2":
            # Installment payment
            upfront_payment = total_amount / 2
            remaining_payment = total_amount / 2
            print(f"{YELLOW_FG}Installment selected. Upfront payment: ₱{upfront_payment:.2f}. Remaining: ₱{remaining_payment:.2f}.{RESET}")
            payment_type = "Installments - Upfront"
            total_payment = total_amount  # Total event payment (full amount, just split into parts)

        else:
            print(f"{YELLOW_FG}{CROSS_ICON} Invalid payment option selected. Exiting booking process.{RESET}")
            return

        # Enter payment date
        payment_date = input(f"{GREEN_FG}Enter payment date (YYYY-MM-DD): {RESET}").strip()

        # Check if a payment entry already exists for this booking
        cursor.execute(''' 
            SELECT payment_id FROM payments WHERE booking_id = ? 
        ''', (booking_id,))
        payment = cursor.fetchone()

        if payment:
            # If a payment already exists, update the payment details
            cursor.execute(''' 
                UPDATE payments
                SET payment_amount = ?, payment_type = ?, payment_date = ?
                WHERE booking_id = ? 
            ''', (total_payment, payment_type, payment_date, booking_id))
            conn.commit()
            print(f"{YELLOW_FG}{CHECK_ICON} Payment details for booking ID {booking_id} updated successfully.{RESET}")
        else:
            # If no payment exists, insert a new payment entry
            cursor.execute(''' 
                INSERT INTO payments (booking_id, payment_amount, payment_type, payment_date)
                VALUES (?, ?, ?, ?)
            ''', (booking_id, total_payment, payment_type, payment_date))
            conn.commit()
            print(f"{YELLOW_FG}{CHECK_ICON} Payment details for booking ID {booking_id} added successfully.{RESET}")

        conn.close()

    else:
        print(f"{RED_FG}{CROSS_ICON} No booking found with ID {booking_id}. Please try again.{RESET}")
        conn.close()

def view_booking():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"
    RED_FG = "\033[31m"

    CROSS_ICON = "\u274C"  # Cross
    INFO_ICON = "\u2139"   # Information icon
    ARROW_ICON = "\u2794"  # Arrow

    print(f"{CYAN_FG}\n===================================={RESET}")
    print(f"{CYAN_FG}|        VIEW BOOKING DETAILS      |{RESET}")
    print(f"{CYAN_FG}===================================={RESET}")

    # Show available bookings
    print(f"{BLUE_FG}\nAvailable Bookings:{RESET}")
    cursor.execute(''' 
        SELECT booking_id, client_name, event_type FROM bookings
    ''')
    bookings = cursor.fetchall()

    if bookings:
        print(f"{GREEN_FG}-------------------------------------------------------{RESET}")
        print(f"{GREEN_FG}| Booking ID | Client Name     | Event Type           |{RESET}")
        print(f"{GREEN_FG}-------------------------------------------------------{RESET}")

        # Rows with booking details
        for booking in bookings:
            print(f"{YELLOW_FG}| {booking[0]:<10} | {booking[1]:<20} | {booking[2]:<15} |{RESET}")

        # Footer line for completeness
        print(f"{GREEN_FG}-------------------------------------------------------{RESET}")
    else:
        print(f"{YELLOW_FG}{CROSS_ICON} No bookings available.{RESET}")
        conn.close()
        return

    booking_id = input(f"\n{ARROW_ICON} {GREEN_FG}Enter the Booking ID to view details: {RESET}").strip()

    try:
        booking_id = int(booking_id)
    except ValueError:
        print(f"{RED_FG}{CROSS_ICON} Invalid ID. Please enter a valid number.{RESET}")
        conn.close()
        return
    
    cursor.execute(''' 
        SELECT booking_id, client_name, event_type, event_date, event_time, location, 
               chefs_name, wait_staff_name, event_coordinator_name, decor_specialist_name, status 
        FROM bookings WHERE booking_id = ? 
    ''', (booking_id,))
    booking = cursor.fetchone()

    if booking:
        # Display booking details
        print(f"\n{CYAN_FG}" + "="*40)
        print(f"|          Booking Details             |")
        print("="*40 + f"{RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Booking ID:         {RESET}{booking[0]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Client:            {RESET}{booking[1]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Event Type:        {RESET}{booking[2]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Date:              {RESET}{booking[3]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Time:              {RESET}{booking[4]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Location:          {RESET}{booking[5]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Chef:              {RESET}{booking[6]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Wait Staff:        {RESET}{booking[7]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Event Coordinator: {RESET}{booking[8]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Decor Specialist:  {RESET}{booking[9]}{YELLOW_FG} {RESET}")
        print(f"{YELLOW_FG}| {ARROW_ICON} Status:            {RESET}{booking[10]}{YELLOW_FG} {RESET}")
        print(f"{CYAN_FG}" + "="*40 + f"{RESET}")

        # Show selected menu items
        cursor.execute(''' 
            SELECT menu_item_id, category, item_name FROM selected_menu_items WHERE booking_id = ? 
        ''', (booking_id,))
        selected_items = cursor.fetchall()

        if selected_items:
            print(f"\n{CYAN_FG}Selected Menu Items:{RESET}")
            for item in selected_items:
                print(f"{INFO_ICON} {YELLOW_FG}Item ID: {RESET}{item[0]} | {YELLOW_FG}Category: {RESET}{item[1]} | {YELLOW_FG}Item Name: {RESET}{item[2]}")
        else:
            print(f"\n{RED_FG}{INFO_ICON} No menu items selected yet.{RESET}")

        # Show payment details
        cursor.execute(''' 
            SELECT payment_id, payment_amount, payment_date FROM payments WHERE booking_id = ? 
        ''', (booking_id,))
        payment = cursor.fetchone()

        if payment:
            print(f"\n{CYAN_FG}Payment Details:{RESET}")
            print(f"{INFO_ICON} {YELLOW_FG}Payment ID: {RESET}{payment[0]}, {YELLOW_FG}Amount: {RESET}₱{payment[1]:.2f}, {YELLOW_FG}Date: {RESET}{payment[2]}")
        else:
            print(f"\n{RED_FG}{INFO_ICON} No payment details found.{RESET}")
        
    else:
        print(f"{RED_FG}{CROSS_ICON} No booking found with ID {booking_id}. Please try again.{RESET}")

    conn.close()

def delete_booking():
    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"
    RED_FG = "\033[31m"
    CHECK_ICON = "\u2705"  # Checkmark
    CROSS_ICON = "\u274C"  # Cross
    INFO_ICON = "\u2139"   # Information icon
    ARROW_ICON = "\u2794"  # Arrow

    print(f"{CYAN_FG}\n===================================={RESET}")
    print(f"{BLUE_FG}|           DELETE BOOKING           |{RESET}")
    print(f"{CYAN_FG}===================================={RESET}")

    # Query to fetch unique bookings (removing duplicates caused by multiple payments)
    cursor.execute(''' 
        SELECT DISTINCT b.booking_id, b.client_name, b.event_type, 
               p.payment_amount, p.payment_type
        FROM bookings b
        LEFT JOIN payments p ON b.booking_id = p.booking_id
        ORDER BY b.booking_id ASC
    ''')
    bookings = cursor.fetchall()

    if bookings:
        print(f"\n{GREEN_FG}--- All Bookings ---{RESET}")
        for booking in bookings:
            booking_id, client_name, event_type, payment_amount, payment_type = booking
            payment_details = f"₱{payment_amount:.2f} ({payment_type})" if payment_amount else "None"
            print(f"{YELLOW_FG}ID:{RESET} {booking_id:<5} | {YELLOW_FG}Client:{RESET} {client_name:<20} | {YELLOW_FG}Event Type:{RESET} {event_type:<12} | {YELLOW_FG}Payment:{RESET} {payment_details}")

        # Ask the user to enter the ID of the booking to delete
        booking_id_to_delete = input(f"\n{ARROW_ICON} {BLUE_FG}Enter the ID of the booking to delete: {RESET}").strip()

        try:
            booking_id_to_delete = int(booking_id_to_delete)
        except ValueError:
            print(f"{RED_FG}{CROSS_ICON} Invalid input. Please enter a valid booking ID.{RESET}")
            conn.close()
            return

        # Fetch the full booking details based on booking_id
        cursor.execute('SELECT * FROM bookings WHERE booking_id = ?', (booking_id_to_delete,))
        booking = cursor.fetchone()

        if booking:
            # Display the full booking details
            print(f"\n{CYAN_FG}" + "="*40)
            print(f"|          Booking Details          |")
            print("="*40 + f"{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Booking ID:         {RESET}{booking[0]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Client:            {RESET}{booking[1]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Event Type:        {RESET}{booking[2]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Date:              {RESET}{booking[3]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Time:              {RESET}{booking[4]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Location:          {RESET}{booking[5]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Chef:              {RESET}{booking[6]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Wait Staff:        {RESET}{booking[7]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Event Coordinator: {RESET}{booking[8]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Decor Specialist:  {RESET}{booking[9]}{YELLOW_FG} |{RESET}")
            print(f"{YELLOW_FG}| {ARROW_ICON} Status:            {RESET}{booking[10]}{YELLOW_FG} |{RESET}")
            print(f"{CYAN_FG}" + "="*40 + f"{RESET}")

            print(f"\n{CYAN_FG}--- Selected Menu Items ---{RESET}")
            cursor.execute(''' 
                SELECT menu_item_id, category, item_name 
                FROM selected_menu_items 
                WHERE booking_id = ? 
            ''', (booking_id_to_delete,))
            rows = cursor.fetchall()

            for row in rows:
                menu_item_id, category, item_name = row
                print(f"{INFO_ICON} {YELLOW_FG}Item ID:{RESET} {menu_item_id} | {YELLOW_FG}Category:{RESET} {category} | {YELLOW_FG}Item Name:{RESET} {item_name}")

            print(f"\n{CYAN_FG}--- Payment Details ---{RESET}")
            cursor.execute(''' 
                SELECT payment_amount, payment_date, payment_type 
                FROM payments 
                WHERE booking_id = ? 
            ''', (booking_id_to_delete,))
            payments = cursor.fetchall()

            if payments:
                for payment in payments:
                    payment_amount, payment_date, payment_type = payment
                    print(f"{INFO_ICON} {YELLOW_FG}Payment Amount:{RESET} ₱{payment_amount:.2f}")
                    print(f"{INFO_ICON} {YELLOW_FG}Payment Date:{RESET} {payment_date}")
                    print(f"{INFO_ICON} {YELLOW_FG}Payment Type:{RESET} {payment_type}")
            else:
                print(f"{RED_FG}{INFO_ICON} No payment recorded for this booking.{RESET}")

            # Confirm deletion without payment update
            confirm = input(f"\n{ARROW_ICON} {RED_FG}Are you sure you want to delete this booking? (yes/no): {RESET}").strip().lower()

            if confirm == "yes":
                try:
                    # Delete related data in selected_menu_items and payments first
                    cursor.execute('DELETE FROM selected_menu_items WHERE booking_id = ?', (booking_id_to_delete,))
                    cursor.execute('DELETE FROM payments WHERE booking_id = ?', (booking_id_to_delete,))

                    # Now delete the booking itself
                    cursor.execute('DELETE FROM bookings WHERE booking_id = ?', (booking_id_to_delete,))
                    conn.commit()
                    print(f"{GREEN_FG}{CHECK_ICON} Booking ID {booking_id_to_delete} has been successfully deleted.{RESET}")
                except sqlite3.Error as e:
                    print(f"{RED_FG}{CROSS_ICON} Error deleting booking: {e}{RESET}")
            else:
                print(f"{YELLOW_FG}{INFO_ICON} Deletion canceled.{RESET}")
        else:
            print(f"{RED_FG}{CROSS_ICON} No booking found with ID {booking_id_to_delete}. Please try again.{RESET}")
    else:
        print(f"{RED_FG}{CROSS_ICON} No bookings available to delete.{RESET}")

    conn.close()


def admin_menu():
    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    BLUE_FG = "\033[34m"
    CYAN_FG = "\033[36m"
    RED_FG = "\033[31m"
    ARROW_ICON = "\u2794"  # Arrow

    while True:
        print(f"\n{CYAN_FG}\n====================================={RESET}")
        print(f"{CYAN_FG}|             ADMIN MENU            |{RESET}")
        print(f"{CYAN_FG}====================================={RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} 📜 [1] View Menu{RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} ➕ [2] Add Menu Item{RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} 📝 [3] Update Menu Item{RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} ❌ [4] Delete Menu Item{RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} 🗓️ [5] Add Booking{RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} 🛠️ [6] Update Booking{RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} 📅 [7] View Booking{RESET}")
        print(f"{YELLOW_FG}{ARROW_ICON} 🗑️ [8] Delete Booking{RESET}")
        print(f"{RED_FG}{ARROW_ICON} 🚪 [9] Exit{RESET}")
        print(f"{CYAN_FG}-------------------------------------{RESET}")
        choice = input(f"\n{CYAN_FG}{ARROW_ICON} Enter your choice: {RESET}").strip()
        
        if choice == "1":
            view_menu()
        elif choice == "2":
            add_menu_item()
        elif choice == "3":
            update_menu_item()
        elif choice == "4":
            delete_menu_item()
        elif choice == "5":
            add_booking()
        elif choice == "6":
            update_booking()
        elif choice == "7":
            view_booking()
        elif choice == "8":
            delete_booking()
        elif choice == "9":

            RESET = "\033[0m"
            GREEN_FG = "\033[32m"
            CYAN_FG = "\033[36m"
            RED_FG = "\033[31m"
            BLUE_FG = "\033[34m"

            print(f"{RED_FG}\n❌ Are you sure you want to exit the admin menu?{RESET}")
            print(f"{GREEN_FG}{ARROW_ICON} 1. Log out (return to the main menu){RESET}")
            print(f"{GREEN_FG}{ARROW_ICON} 2. Exit the program{RESET}")
            exit_choice = input(f"{CYAN_FG}{ARROW_ICON} Enter your choice (1 for Log out, 2 for Exit): {RESET}").strip()

            if exit_choice == "1":
                print(f"{BLUE_FG}{ARROW_ICON} Returning to the main menu..LOG OUT...{RESET}")
                log_out()
                return  
            elif exit_choice == "2":
                print(f"{RED_FG}❌ Exiting the program...{RESET}")
                exit()  # Exit the program
            else:
                print(f"{RED_FG}❌ Invalid choice. Please try again.{RESET}")

def admin_login():
    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    RED_FG = "\033[31m"
    BLUE_FG = "\033[34m"
    ARROW_ICON = "\u2794"  # Arrow icon

    # Admin credentials
    admin_username = "anne"  # Example username
    admin_password = "camille28"  # Example password

    while True:  # Loop to keep asking until correct credentials
        print(f"{BLUE_FG}\n" + "="*30)
        print("|       👨‍💼ADMIN LOGIN      |")
        print("="*30 + f"{RESET}")

        while True:  # Loop until successful login
            print(f"{YELLOW_FG}------------------------------------")
            username = input(f"{YELLOW_FG}{ARROW_ICON} 📛 Username: {RESET}").strip()
            print(f"{YELLOW_FG}------------------------------------")
            password = input(f"{YELLOW_FG}{ARROW_ICON} 🔑 Password: {RESET}").strip()
            print(f"{YELLOW_FG}------------------------------------")
            
            if username == admin_username and password == admin_password:
                print(f"{GREEN_FG}\n🎉 Logged in successfully! Welcome, Admin. {RESET}")
                print(f"{YELLOW_FG}-------------------------------------------")
                admin_menu()  # Call the admin menu if login is successful
                break  # Exit the loop if login is successful
            else:
                print(f"{RED_FG}❌ Invalid username or password. Please try again.{RESET}")
        

def log_out():
    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    RED_FG = "\033[31m"
    BLUE_FG = "\033[34m"
    ARROW_ICON = "\u2794"  # Arrow icon

    print(f"{BLUE_FG}\n===== 🚪 LOG OUT ====={RESET}")
    
    username = input(f"{YELLOW_FG}{ARROW_ICON} 📛 Username: {RESET}").strip()
    password = input(f"{YELLOW_FG}{ARROW_ICON} 🔑 Password: {RESET}").strip()
    
    if username == admin_username and password == admin_password:
        print(f"{GREEN_FG}\n🎉Successfully logged out. Returning to the main menu...{RESET}")
        main_menu()  # Calls the main function (you may want to replace this with actual redirection to the main menu)
    else:
        print(f"{RED_FG}\n❌Incorrect credentials. Log out canceled. Returning to Admin Menu...{RESET}")
        admin_menu() 

def main_menu():
    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    RED_FG = "\033[31m"
    CYAN_FG = "\033[36m"
    ARROW_ICON = "\u2794"  # Arrow icon

    # Welcome message with colors and icons
    print(f"{CYAN_FG}====================================================")
    print(f"{CYAN_FG}|       🍽️ Catering Services Management System      |{RESET}")
    print(f"{CYAN_FG}===================================================={RESET}")
    print(f"{YELLOW_FG}✨Welcome to the Catering Services Management System!✨{RESET}")
    print(f"{YELLOW_FG}Please select your role to proceed:{RESET}")
    print(f"{CYAN_FG}-----------------------------------------------------{RESET}")
    print(f"{GREEN_FG}{ARROW_ICON} [1] 👨‍💼 Admin{RESET}")
    print(f"{GREEN_FG}{ARROW_ICON} [2] 👥 User{RESET}")
    print(f"{CYAN_FG}-----------------------------------------------------{RESET}")
    # Take input from the user
    choice = input(f"\n{YELLOW_FG}🎯 Enter your choice (1 or 2): {RESET}").strip()   # Take input from the user

    if choice == "1":
        admin_login()  # Admin login function
    elif choice == "2":
        user_menu()  # User menu function (if defined)
    else:
        print(f"{RED_FG}Invalid choice, Please try again...{RESET}")
        main_menu() 

def user_menu():
    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    RED_FG = "\033[31m"
    CYAN_FG = "\033[36m"
    ARROW_ICON = "\u2794"  # Arrow icon

    while True:
        # Print the user menu with colors and icons
        print(f"\n{CYAN_FG}===================================={RESET}")
        print(f"{CYAN_FG}|           {ARROW_ICON} USER MENU {ARROW_ICON}          |{RESET}")
        print(f"{CYAN_FG}===================================={RESET}")
        print(f"{GREEN_FG}{ARROW_ICON} [1] View Your Bookings{RESET}")
        print(f"{GREEN_FG}{ARROW_ICON} [2] Place Order{RESET}")

        choice = input(f"\n{YELLOW_FG}{ARROW_ICON} Enter your choice: {RESET}").strip()

        if choice == "1":
            view_booking()  # Function to view bookings
        elif choice == "2":
            place_order()  # Function to place order
            break  # Break the loop after placing an order
        else:
            print(f"{RED_FG}Invalid choice. Please select a valid option.{RESET}")

def place_order():
    # Icons and Colors
    RESET = "\033[0m"
    GREEN_FG = "\033[32m"
    YELLOW_FG = "\033[33m"
    RED_FG = "\033[31m"
    CYAN_FG = "\033[36m"
    ARROW_ICON = "\u27A4" 
    CHECK_MARK_ICON = "\u2714"  # Check mark icon for success
    CROSS_MARK_ICON = "\u274C"  # Cross mark icon for errors

    conn = sqlite3.connect("event_book_catering.db")
    cursor = conn.cursor()

    print(f"\n{CYAN_FG}===================================={RESET}")
    print(f"{CYAN_FG}|           PLACE ORDER            |{RESET}")
    print(f"{CYAN_FG}===================================={RESET}\n")

    while True:  # Loop to ask the user if they want to place an order
        want_to_place_order = input(f"{YELLOW_FG}{ARROW_ICON} Do you want to place an order? (yes/no): {RESET}").strip().lower()

        if want_to_place_order == "yes":
            booking_id = input(f"{YELLOW_FG}{ARROW_ICON} Enter your Booking ID: {RESET}").strip()

            cursor.execute(''' 
                SELECT booking_id, client_name, event_type, event_date, event_time, location, status 
                FROM bookings 
                WHERE booking_id = ? 
            ''', (booking_id,))
            booking = cursor.fetchone()

            if booking:
                booking_id, client_name, event_type, event_date, event_time, location, status = booking
                print(f"\n{GREEN_FG}Booking ID: {booking_id}{RESET}")
                print(f"{CYAN_FG}------------------------------------{RESET}")
                print(f"{GREEN_FG}  {ARROW_ICON} Client Name: {RESET}{YELLOW_FG}{client_name}{RESET}")
                print(f"{CYAN_FG}------------------------------------{RESET}")
                print(f"{GREEN_FG}  {ARROW_ICON} Event Type: {RESET}{YELLOW_FG}{event_type}{RESET}")
                print(f"{CYAN_FG}------------------------------------{RESET}")
                print(f"{GREEN_FG}  {ARROW_ICON} Event Date: {RESET}{YELLOW_FG}{event_date}{RESET}")
                print(f"{CYAN_FG}------------------------------------{RESET}")
                print(f"{GREEN_FG}  {ARROW_ICON} Event Time: {RESET}{YELLOW_FG}{event_time}{RESET}")
                print(f"{CYAN_FG}------------------------------------{RESET}")
                print(f"{GREEN_FG}  {ARROW_ICON} Location: {RESET}{YELLOW_FG}{location}{RESET}")
                print(f"{CYAN_FG}------------------------------------{RESET}")
                print(f"{GREEN_FG}  {ARROW_ICON} Status: {RESET}{YELLOW_FG}{status}{RESET}")
                print(f"{CYAN_FG}------------------------------------\n{RESET}")
                if status == "pending":
                    confirm = input(f"{YELLOW_FG}Do you want to place an order for this booking? (yes/no): {RESET}").strip().lower()
                    if confirm == "yes":
                        print(f"{CYAN_FG}------------------------------------{RESET}")
                        address = input(f"{YELLOW_FG}{ARROW_ICON} Enter your Address: {RESET}").strip()
                        print(f"{CYAN_FG}------------------------------------{RESET}")
                        contact_number = input(f"{YELLOW_FG}{ARROW_ICON} Enter your Contact Number: {RESET}").strip()
                        print(f"{CYAN_FG}------------------------------------{RESET}")
                        email = input(f"{YELLOW_FG}{ARROW_ICON} Enter your Email: {RESET}").strip()
                        print(f"{CYAN_FG}------------------------------------{RESET}")

                        # Check if client already exists in the clients table (using the latest client name)
                        cursor.execute(''' 
                            SELECT client_id FROM clients WHERE client_name = ? AND email = ? 
                        ''', (client_name, email))
                        client = cursor.fetchone()

                        if not client:
                            # Add new client to the `clients` table
                            cursor.execute(''' 
                                INSERT INTO clients (client_name, address, contact_number, email) 
                                VALUES (?, ?, ?, ?) 
                            ''', (client_name, address, contact_number, email))
                            client_id = cursor.lastrowid
                            print(f"{GREEN_FG}{CHECK_MARK_ICON} New client '{client_name}' has been added to the system.{RESET}")
                        else:
                            client_id = client[0]
                            print(f"{YELLOW_FG}{CHECK_MARK_ICON} Client '{client_name}' already exists in the system.{RESET}")

                        # Update the status of the booking
                        cursor.execute(''' 
                            UPDATE bookings 
                            SET status = 'confirmed' 
                            WHERE booking_id = ? 
                        ''', (booking_id,))
                        conn.commit()

                        print(f"{GREEN_FG}{CHECK_MARK_ICON} Booking ID {booking_id} has been confirmed and linked to Client ID {client_id}.{RESET}")
                        break  # Exit the loop after successful order placement
                    else:
                        print(f"{RED_FG}{CROSS_MARK_ICON} No changes made.{RESET}")
                        break  # Exit the loop if the user doesn't want to place an order
                else:
                    print(f"{RED_FG}{CROSS_MARK_ICON} Booking ID {booking_id} is not pending and cannot be modified.")
            else:
                print(f"{RED_FG}{CROSS_MARK_ICON} No booking found for Booking ID '{booking_id}'. Please try again.{RESET}")
        elif want_to_place_order == "no":
            print(f"{GREEN_FG}Exiting the place order process.{RESET}")
            break  # Exit the loop if the user doesn't want to place an order
        else:
            print(f"{RED_FG}{CROSS_MARK_ICON} Invalid choice. Please enter 'yes' or 'no'.{RESET}")
    
    conn.close()

if __name__ == "__main__":
    initialize_database()  
    create_bookings_table()
    selected_menu_items_schema()
    main_menu()
