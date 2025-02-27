from flet import *
import asyncio
import datetime
import json
import os
import time  # Add this import for time.sleep()
import serial
import serial.tools.list_ports

# Error handling feature
ports = list(serial.tools.list_ports.comports())
for port in ports:
    print(port.device)

# Connect to Arduino 
ser = serial.Serial("COM11", baudrate=9600, timeout=1)

class MedicationSchedule:
    def __init__(self):
        self.filename = "medication_schedule.json"
        self.schedule = self.load_schedule()
        print(f"Initialized MedicationSchedule with data: {self.schedule}")  # Debug print

    def load_schedule(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    # Clean up any null keys and merge their data
                    if "null" in data:
                        if None in data:
                            # Merge null and None keys if both exist
                            data["null"].extend(data[None])
                            del data[None]
                    print(f"Loaded schedule from file: {data}")
                    return data
            except json.JSONDecodeError:
                print("Invalid JSON file, starting fresh")
                return {}
        print("No existing schedule file, starting with empty schedule")
        return {}

    def save_schedule(self):
        # Ensure we're not using None or "null" as keys
        if None in self.schedule:
            del self.schedule[None]
        
        # Handle the case where email is None
        schedule_to_save = {}
        for email, medications in self.schedule.items():
            if email is None or email == "null":
                continue  # Skip null entries
            schedule_to_save[email] = medications

        with open(self.filename, 'w') as f:
            json.dump(schedule_to_save, f)
        print(f"Saved schedule to file: {schedule_to_save}")

    def add_medication(self, email, name, time, specific_time, type):
        if not email or email == "null":
            print("Warning: Attempting to add medication without valid email")
            return
            
        print(f"Adding medication for {email}: {name}")
        if email not in self.schedule:
            print(f"Creating new schedule for {email}")
            self.schedule[email] = []
            
        self.schedule[email].append({
            "name": name,
            "time": time,
            "specific_time": specific_time,
            "type": type
        })
        print(f"Updated schedule: {self.schedule}")
        self.save_schedule()
    
    def get_user_medications(self, email):
        if not email or email == "null":
            print("Warning: Attempting to get medications without valid email")
            return []
            
        medications = self.schedule.get(email, [])
        print(f"Retrieved medications for {email}: {medications}")
        return medications

    def update_medication_time(self, email, index, new_time, new_specific_time):
        if email in self.schedule and 0 <= index < len(self.schedule[email]):
            self.schedule[email][index]["time"] = new_time
            self.schedule[email][index]["specific_time"] = new_specific_time
            self.save_schedule()

class UserAuth:
    def __init__(self):
        self.filename = "users.json"
        self.users = self.load_users()
        print(f"Loaded users: {self.users}")  # Debug print

    def load_users(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f)
        print(f"Saved users: {self.users}")  # Debug print

    def register_user(self, email, password, name):
        print(f"Attempting to register user: {email}")  # Debug print
        if email in self.users:
            return False, "Email already registered"
        
        self.users[email] = {
            "password": password,  # hides the password
            "name": name
        }
        self.save_users()
        print(f"User registered successfully: {email}")  # Debug print
        return True, "Registration successful"

    def login_user(self, email, password):
        print(f"Attempting to login user: {email}")  # Debug print
        print(f"Current users: {self.users}")  # Debug print
        if email not in self.users:
            print(f"Email not found: {email}")  # Debug print
            return False, "Email not found"
        if self.users[email]["password"] != password:
            print("Incorrect password")  # Debug print
            return False, "Incorrect password"
        print(f"Login successful for: {email}")  # Debug print
        return True, self.users[email]["name"]

async def main(page: Page):
    page.bgcolor = "#2C2C2C"
    page.title = "Med Tracker"
    page.window_width = 320
    page.window_height = 650

    current_user_email = None

    med_schedule = MedicationSchedule()
    user_auth = UserAuth()
    page.refs = {
        "time_dropdown": Ref[Dropdown](),
        "specific_time_field": Ref[TextField](),
        "logout_button": Ref[ElevatedButton]()
    }


    async def start_arduino_handler():
        while True:
            try:
                if ser.in_waiting:
                    response = ser.readline().decode().strip()
                    if response:
                        print(f"Received from Arduino: {response}")
                        # Process responses here or call a separate function
                        # You could use page.update() within a lock if needed
            except Exception as e:
                print(f"Arduino communication error: {e}")
            await asyncio.sleep(0.1)

    asyncio.create_task(start_arduino_handler())

    # Medicine Cards
    def create_medication_card(med, index):
        print(f"Creating card for medication: {med}")  # Debug print
        icon = Icon(name=icons.MEDICAL_SERVICES_OUTLINED if med["type"] == "Tablet" else icons.MEDICATION, color="white")
        time_display = f"Before {med['time']}"
        hour_value = ""
        minute_value = ""
        if med.get("specific_time") and len(med.get("specific_time", "")) == 5:
            parts = med.get("specific_time").split(":")
            if len(parts) == 2:
                hour_value = parts[0]
                minute_value = parts[1]

        # Create dropdowns for hour and minute
        hour_dropdown = Dropdown(
            value=hour_value,
            options=[dropdown.Option(f"{i:02d}") for i in range(24)],  # 00-23 hours
            width=100,
            bgcolor="white",
            color="black",
            border_radius=8,
            visible=False  # Initially hidden
        )

        minute_dropdown = Dropdown(
            value=minute_value,
            options=[dropdown.Option(f"{i:02d}") for i in range(60)],  # 00-59 minutes
            width=100,
            bgcolor="white",
            color="black",
            border_radius=8,
            visible=False  # Initially hidden
        )

        # Create edit fields but initially hide them
        name_field = TextField(
            value=med["name"],
            width=200,
            bgcolor="white",
            border_radius=8,
            border_color="#ccc",
            color="black",
            visible=False  # Initially hidden
        )
        
        time_dropdown = Dropdown(
            value=med["time"],
            options=[
                dropdown.Option("breakfast"),
                dropdown.Option("lunch"),
                dropdown.Option("dinner"),
                dropdown.Option("bedtime")
            ],
            width=160,
            bgcolor="white",
            color="black",
            border_radius=8,
            visible=False  # Initially hidden
        )
        
        specific_time_field = TextField(
            value=med.get("specific_time", ""),
            hint_text="HH:MM",
            width=160,
            bgcolor="white",
            border_radius=8,
            border_color="#ccc",
            visible=False  # Initially hidden
        )

        # Labels for edit fields
        name_label = Text("Name:", color="white", size=12, visible=False)
        time_label = Text("Time:", color="white", size=12, visible=False)
        specific_time_label = Text("Specific time:", color="white", size=12, visible=False)
        
        # Save button (initially hidden)
        save_button = ElevatedButton(
            "Save", 
            bgcolor="#32887A", 
            color="white",
            style=ButtonStyle(shape=RoundedRectangleBorder(radius=8)),
            visible=False
        )
        
        # Edit and Delete buttons (initially visible)
        edit_button = ElevatedButton(
            "Edit", 
            bgcolor="#32887A", 
            color="white",
            style=ButtonStyle(shape=RoundedRectangleBorder(radius=8))
        )
        
        delete_button = ElevatedButton(
            "Delete", 
            bgcolor="#D32F2F", 
            color="white",
            style=ButtonStyle(shape=RoundedRectangleBorder(radius=8))
        )
        
        # Container for all the elements
        card_column = Column(
            controls=[
                Row(   # Shows medication name and time
                    controls=[
                        icon,
                        Column(
                            controls=[
                                Text(med["name"], weight="bold", color="white"),
                                Text(time_display, color="white", size=12)
                            ],
                        ),
                        Container(width=10),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN
                ),
                # Edit fields section (initially hidden)
                Container(height=10, visible=False),
                Row(
                    controls=[name_label, name_field],
                    visible=False
                ),
                Container(height=5, visible=False),
                Row(
                    controls=[time_label, time_dropdown],
                    visible=False
                ),
                Container(height=5, visible=False),
                Column(
                    controls=[
                        specific_time_label,
                        Row([
                            Column([
                                Text("Hour", color="white", size=10),
                                hour_dropdown
                            ]),
                            Container(width=5),
                            Column([
                                Text("Minute", color="white", size=10),
                                minute_dropdown
                            ])
                        ])
                    ],
                    visible=False
                ),
                Container(height=10),
                # Buttons row
                Row(
                    controls=[edit_button, delete_button],
                    alignment=MainAxisAlignment.END
                )
            ],
        )
        
        # Function to toggle edit mode
        def toggle_edit_mode(e):
            # Hide regular display
            edit_button.visible = False
            
            # Show edit fields
            name_label.visible = True
            name_field.visible = True
            time_label.visible = True
            time_dropdown.visible = True
            specific_time_label.visible = True
            hour_dropdown.visible = True  # Show hour dropdown
            minute_dropdown.visible = True  # Show minute dropdown
            
            # Show save button and replace edit button with it
            save_button.visible = True
            
            # Replace buttons in the row
            card_column.controls[-1].controls = [save_button, delete_button]
            
            # Show spacers
            for i in range(1, 7):
                card_column.controls[i].visible = True
                
            page.update()
        
        # Set the edit button click handler
        edit_button.on_click = toggle_edit_mode
        
        # Function to save edits
        def save_edit(e):
            new_name = name_field.value
            new_time = time_dropdown.value
            
            # Combine hour and minute into specific time format
            new_specific_time = ""
            if hour_dropdown.value and minute_dropdown.value:
                new_specific_time = f"{hour_dropdown.value}:{minute_dropdown.value}"

            if current_user_email in med_schedule.schedule and 0 <= index < len(med_schedule.schedule[current_user_email]):
                # Save original values to check if specific time was changed
                original_specific_time = med_schedule.schedule[current_user_email][index].get("specific_time", "")
                
                # Update local schedule
                med_schedule.schedule[current_user_email][index]["name"] = new_name
                med_schedule.schedule[current_user_email][index]["time"] = new_time
                med_schedule.schedule[current_user_email][index]["specific_time"] = new_specific_time
                med_schedule.save_schedule()
                
                # If a specific time is provided, update the Arduino schedule
                if new_specific_time and len(new_specific_time) == 5:
                    try:
                        # Check if time changed or was newly added
                        if original_specific_time != new_specific_time or not original_specific_time:
                            # Format command for Arduino to update the schedule
                            # First we send a DELETE command if it had a previous time
                            if original_specific_time:
                                delete_cmd = f"DELETE:{index}\n"
                                ser.write(delete_cmd.encode())
                                print(f"Sent delete to Arduino before update: {delete_cmd}")
                                time.sleep(0.1)  # Wait for processing
                            
                            # Then send the new time as if it's a new entry
                            add_cmd = f"{new_specific_time}:{new_name}\n"
                            ser.write(add_cmd.encode())
                            print(f"Sent new time to Arduino: {add_cmd}")
                            
                            # Wait for confirmation
                            time.sleep(0.1)
                            if ser.in_waiting:
                                response = ser.readline().decode().strip()
                                print(f"Arduino response to update: {response}")
                    except Exception as ex:
                        print(f"Error sending update to Arduino: {ex}")
                
                # If specific time was removed, delete from Arduino
                elif original_specific_time and not new_specific_time:
                    try:
                        delete_cmd = f"DELETE:{index}\n"
                        ser.write(delete_cmd.encode())
                        print(f"Sent delete to Arduino for removed time: {delete_cmd}")
                    except Exception as ex:
                        print(f"Error sending delete to Arduino: {ex}")
                        
                switch_to_home()  # Refresh home page

        # Set the save button click handler
        save_button.on_click = save_edit
        
        # Delete medication
        def delete_medication(e):
            if current_user_email in med_schedule.schedule:
                # Send delete command to Arduino if there's a specific time
                if med.get("specific_time"):
                    try:
                        command = f"DELETE:{index}\n"
                        ser.write(command.encode())
                        print(f"Sent delete command to Arduino: {command}")
                    except Exception as ex:
                        print(f"Error sending delete command to Arduino: {ex}")
                        
                del med_schedule.schedule[current_user_email][index]
                med_schedule.save_schedule()
                switch_to_home()  # Refresh home page

        # Set the delete button click handler
        delete_button.on_click = delete_medication

        return Container(
            content=card_column,
            bgcolor="#32887A",
            border_radius=12,
            padding=15,
            margin=margin.only(bottom=10),
            shadow=BoxShadow(blur_radius=10, color=colors.BLACK12, offset=Offset(2, 2))
        )

    def toggle_logout_button():
        # Toggle visibility of logout button
        logout_btn = page.refs["logout_button"].current
        logout_btn.visible = not logout_btn.visible
        page.update()

    def logout():
        nonlocal current_user_email
        # Reset the current user
        current_user_email = None
        # Hide the logout button
        page.refs["logout_button"].current.visible = False
        # Navigate to the login page
        switch_to_login()
    
    # Home page
    def create_home_page():
        nonlocal current_user_email
        print(f"Creating home page for user: {current_user_email}")

        if current_user_email:
            medications = med_schedule.get_user_medications(current_user_email)
            print(f"Retrieved medications: {medications}")
            med_cards = [create_medication_card(med, i) for i, med in enumerate(medications)]
            print(f"Created {len(med_cards)} medication cards")
        else:
            print("No user email found")
            med_cards = []
        
        return Container(
            width=320,
            height=650,
            bgcolor="#E0F2F1",
            content=Stack(
                controls=[
                    Container(
                        width=320,
                        height=650,
                        padding=padding.only(left=20, right=20, top=20, bottom=80),
                        content=Column(
                            controls=[
                                Container(
                                    content=Row(
                                        controls=[
                                            Column(
                                                controls=[
                                                    Text("Hello!", size=16, color="black"),
                                                    Text(user_auth.users.get(current_user_email, {}).get("name", "User"), 
                                                        size=24, weight="bold", color="black")
                                                ]
                                            ),
                                            Container(
                                                content=IconButton(
                                                    icon=icons.ACCOUNT_CIRCLE,
                                                    icon_color="black",
                                                    on_click=lambda _: toggle_logout_button(),
                                                ),
                                                bgcolor="#E0F2F1",
                                                border_radius=50
                                            )
                                        ],
                                        alignment=MainAxisAlignment.SPACE_BETWEEN
                                    )
                                ),
                                Container(
                                    margin=margin.only(top=20),
                                    content=Column(
                                        controls=[
                                            Text(
                                                "Today's Medications",
                                                size=20,
                                                weight="bold",
                                                color="black"
                                            ),
                                            # Make the medication list scrollable
                                            Container(
                                                height=450,  # Set a fixed height for scrolling
                                                content=ListView(
                                                    controls=med_cards,
                                                    spacing=5,
                                                    padding=10,
                                                    auto_scroll=False
                                                ),
                                                border_radius=10,
                                            )
                                        ]
                                    )
                                ),
                            ]
                        ),
                    ),
                    Container(
                        ref=page.refs["logout_button"],
                        content=ElevatedButton(
                            "Logout",
                            bgcolor="#D32F2F",
                            color="white",
                            on_click=lambda _: logout(),
                        ),
                        right=20,
                        top=60,  # Position it below the account icon
                        visible=False,  # Initially hidden
                    ),
                    Container(
                        width=320,
                        bottom=0,
                        content=create_navigation_bar()
                    )
                ]
            )
        )

    def create_schedule_page():
        name_field = TextField(
            label="Medication Name",
            border_color="#26A69A",
            color="black",
        )
        
        time_field = Dropdown(
            label="Time of Day", color="grey",  # find a nice color for this
            options=[
                dropdown.Option("breakfast"),
                dropdown.Option("lunch"),
                dropdown.Option("dinner"),
                dropdown.Option("bedtime")
            ],
            border_color="#26A69A"
        )
        
        hour_dropdown = Dropdown(
            label="Hour",
            options=[dropdown.Option(f"{i:02d}") for i in range(24)],  # 00-23 hours
            width=100,
            border_color="#26A69A"
        )

        minute_dropdown = Dropdown(
            label="Minute",
            options=[dropdown.Option(f"{i:02d}") for i in range(60)],  # 00-59 minutes
            width=100,
            border_color="#26A69A"
        )
        
        type_dropdown = Dropdown(
            label="Type", color = "grey",
            options=[
                dropdown.Option("Tablet"),
                dropdown.Option("Capsule")
            ],
            border_color="#26A69A"
        )

        def add_medication(e):
            if name_field.value and time_field.value and type_dropdown.value:
                # Combine hour and minute into specific time format
                specific_time = ""
                if hour_dropdown.value and minute_dropdown.value:
                    specific_time = f"{hour_dropdown.value}:{minute_dropdown.value}"
                
                # First add to the app's internal schedule
                med_schedule.add_medication(
                    current_user_email,
                    name_field.value,
                    time_field.value,
                    specific_time,
                    type_dropdown.value
                )

                # Format the command for Arduino
                if specific_time and len(specific_time) == 5:
                    try:
                        # You could extend this protocol to include medication name
                        # Format: TIME:NAME (e.g., "08:30:Aspirin")
                        command = f"{specific_time}:{name_field.value}\n"
                        ser.write(command.encode())
                        print(f"Sent to Arduino: {command}")
                        
                        # Wait for confirmation
                        time.sleep(0.1)
                        if ser.in_waiting:
                            response = ser.readline().decode().strip()
                            print(f"Arduino response: {response}")
                            
                            # Show feedback to user based on response
                            if response.startswith("ADDED:"):
                                # Could display a snackbar or dialog here
                                print("Schedule successfully added to dispenser")
                            else:
                                print("Warning: Arduino did not confirm schedule")
                        
                    except Exception as ex:
                        print(f"Error sending to Arduino: {ex}")
                        # Show error message to user

                # Reset fields and update UI
                name_field.value = ""
                time_field.value = None
                hour_dropdown.value = None
                minute_dropdown.value = None
                type_dropdown.value = None
                switch_to_home()
                page.update()

        return Container(
            width=320,
            height=650,
            bgcolor="#E0F2F1",
            padding=20,
            content=Stack(
            controls=[
                Container(
                    width=320,
                    height=650,
                    padding=padding.only(left=20, right=20, top=20, bottom=80),
                    content=Column(
                        controls=[
                            Text("Add Medication Schedule", size=24, weight="bold", color="black"),
                            Container(height=20),
                            name_field,
                            Container(height=10),
                            time_field,
                            Container(height=10),
                            Text("Specific Time", size=14, color="black"),
                            #Container(height=5),
                            Row([
                                Column([
                                    Text("Hour", size=12, color="black"), 
                                    hour_dropdown
                                ]),
                                Container(width=10),  # Add spacing
                                Column([
                                    Text("Minute", size=12, color="black"),
                                    minute_dropdown
                                ])
                            ]),
                            Container(height=10),
                            type_dropdown,
                            Container(height=20),
                            ElevatedButton(
                                "Add Medication",
                                bgcolor="#26A69A",
                                color="white",
                                width=200,
                                on_click=add_medication
                            ),
                        ]
                    ),
                ),
                Container(
                    width=320,
                    bottom=0,
                    content=create_navigation_bar()
                )
            ]
        )
    )

    def handle_arduino_responses():
        """Function to continuously check for and handle Arduino responses"""
        while True:
            try:
                if ser.in_waiting:
                    response = ser.readline().decode().strip()
                    print(f"Received from Arduino: {response}")
                    
                    if response.startswith("ARDUINO:READY"):
                        print("Arduino is ready")
                    elif response.startswith("ADDED:"):
                        time_added = response.split(":")[1]
                        print(f"Schedule confirmed: {time_added}")
                    elif response.startswith("DISPENSED:"):
                        dispensed_time = response.split(":")[1]
                        print(f"Medication dispensed at {dispensed_time}")
                        # You could update UI or send notification here
                    elif response.startswith("ERROR:"):
                        error_info = response.split(":")[1]
                        print(f"Arduino error: {error_info}")
                        # Handle error accordingly
            except Exception as e:
                print(f"Error reading from Arduino: {e}")
                break
            time.sleep(0.1)  # Small delay to prevent CPU hogging

        
    def create_navigation_bar():
        return Container(
            width=320,
            padding=padding.only(left=20, right=20, top=10, bottom=10),
            bgcolor="#26A69A",
            border_radius=border_radius.only(top_left=15, top_right=15),
            content=Row(
                alignment=MainAxisAlignment.SPACE_AROUND,
                controls=[
                    IconButton(
                        icon=icons.HOME,
                        icon_color="white",
                        icon_size=24,
                        tooltip="Home",
                        on_click=lambda _: switch_to_home(),
                    ),
                    IconButton(
                        icon=icons.CALENDAR_MONTH,
                        icon_color="white",
                        icon_size=24,
                        tooltip="Schedule",
                        on_click=lambda _: switch_to_schedule(),
                    ),
                ],
            ),
        )

    def create_signup_page():
        name_field = TextField(
            label="Full Name",
            border_color="white",
            color="white",
            cursor_color="white"
        )
        
        email_field = TextField(
            label="Email",
            border_color="white",
            color="white",
            cursor_color="white"
        )
        
        password_field = TextField(
            label="Password",
            password=True,
            border_color="white",
            color="white",
            cursor_color="white"
        )
        
        confirm_password_field = TextField(
            label="Confirm Password",
            password=True,
            border_color="white",
            color="white",
            cursor_color="white"
        )
        
        error_text = Text(
            color="red",
            size=12,
            visible=False
        )

        def handle_signup(e):
            if not all([
                name_field.value,
                email_field.value,
                password_field.value,
                confirm_password_field.value
            ]):
                error_text.value = "Please fill in all fields"
                error_text.visible = True
                page.update()
                return

            if password_field.value != confirm_password_field.value:
                error_text.value = "Passwords do not match"
                error_text.visible = True
                page.update()
                return

            success, message = user_auth.register_user(
                email_field.value,
                password_field.value,
                name_field.value
            )

            if success:
                switch_to_home()
            else:
                error_text.value = message
                error_text.visible = True
                page.update()

        return Container(
            width=320,
            height=650,
            bgcolor="#26A69A",
            border_radius=35,
            padding=padding.all(20),
            content=Column(
                controls=[
                    Container(
                        margin=margin.only(top=40),
                        content=Text(
                            "Sign Up",
                            size=32,
                            color="white",
                            weight=FontWeight.BOLD,
                            text_align=TextAlign.CENTER,
                        ),
                    ),
                    Container(height=30),
                    name_field,
                    Container(height=20),
                    email_field,
                    Container(height=20),
                    password_field,
                    Container(height=20),
                    confirm_password_field,
                    Container(height=10),
                    error_text,
                    Container(height=30),
                    ElevatedButton(
                        content=Text(
                            "Sign Up",
                            weight=FontWeight.BOLD,
                        ),
                        width=200,
                        bgcolor="#E0F2F1",
                        color="black",
                        on_click=handle_signup,
                    ),
                    Container(height=20),
                    TextButton(
                        text="Already have an account? Login",
                        on_click=lambda _: switch_to_login(),
                        style=ButtonStyle(
                            color={"": colors.WHITE},
                        ),
                    ),
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
            ),
        )

    def create_login_page():
        email_field = TextField(
            label="Email",
            border_color="white",
            color="white",
            cursor_color="white",
        )
        
        password_field = TextField(
            label="Password",
            password=True,
            border_color="white",
            color="white",
            cursor_color="white",
        )

        error_text = Text(
            color="red",
            size=12,
            visible=False
        )

        def handle_login(e):
            nonlocal current_user_email
            print("Login button clicked!")  # Debug print
            print(f"Email entered: {email_field.value}")  # Debug print
        
            if not email_field.value or not password_field.value:
                print("Missing fields")  # Debug print
                error_text.value = "Please fill in all fields"
                error_text.visible = True
                page.update()
                return

            print("Attempting login...")  # Debug print
            success, name = user_auth.login_user(
                email_field.value,
                password_field.value
            )
            print(f"Login success: {success}, Response: {name}")  # Debug print

            if success:
                print("Login successful, switching to home")  # Debug print
                current_user_email = email_field.value
                switch_to_home()
            else:
                print(f"Login failed: {name}")  # Debug print
                error_text.value = name
                error_text.visible = True
                page.update()

        return Container(
            width=320,
            height=650,
            bgcolor="#26A69A",
            border_radius=35,
            padding=padding.all(20),
            content=Column(
                controls=[
                    Container(
                        margin=margin.only(top=40),
                        content=Text(
                            "Login",
                            size=32,
                            color="white",
                            weight=FontWeight.BOLD,
                            text_align=TextAlign.CENTER,
                        ),
                    ),
                    Container(height=40),
                    email_field,
                    Container(height=20),
                    password_field,
                    Container(height=10),
                    error_text,
                    Container(height=40),
                    ElevatedButton(
                        text="Login",
                        width=200,
                        bgcolor="#E0F2F1",
                        color="black",
                        on_click=handle_login
                    ),
                    Container(height=20),
                    TextButton(
                        text="Don't have an account? Sign Up",
                        on_click=lambda _: switch_to_signup(),
                        style=ButtonStyle(
                            color={"": colors.WHITE},
                        ),
                    ),
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
            ),
        )

    def create_welcome_page():
        return Container(
            width=320,
            height=650,
            bgcolor="#26A69A",
            border_radius=35,
            padding=padding.symmetric(horizontal=20),
            content=Column(
                controls=[
                    Container(
                        margin=margin.only(top=355),
                        content=Text(
                            "Your personal \nassistant, but for \nyour pills!",
                            size=22,
                            color="white",
                            weight=FontWeight.BOLD,
                            text_align=TextAlign.CENTER,
                        ),
                    ),
                    Container(
                        margin=margin.only(top=5, bottom=25),
                        content=Text(
                            "Your daily dose, perfectly \non time.",
                            size=16,
                            color="white",
                            text_align=TextAlign.CENTER,
                        ),
                    ),
                    Container(
                        width=200,
                        height=45,
                        content=ElevatedButton(
                            content=Text(
                                "Sign Up",
                                text_align=TextAlign.CENTER,
                                weight=FontWeight.BOLD,
                                on_click=lambda _: switch_to_signup()
                            ),
                            bgcolor="#E0F2F1",
                            color="black",
                            width=200,
                            on_click=lambda _: switch_to_signup(),
                        ),
                    ),
                    Container(
                        margin=margin.only(top=10),
                        content=TextButton(
                            text="Already have an account? Login",
                            on_click=lambda _: switch_to_login(),
                            style=ButtonStyle(
                                color={"": colors.WHITE},
                            ),
                        ),
                    ),
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
            ),
        )

    def switch_to_signup():
        outer_container.content = create_signup_page()
        page.update()
    
    def switch_to_welcome(e=None):
        # Capsule images for the welcome page
        capsule_positions = [
            (0, 10), (60, 12), (160, 15), (250, 8),
            (0, 102), (90, 115), (165, 120), (250, 100),
            (0, 210), (100, 220), (190, 230), (250, 190)
        ]

        capsules = [
            Container(
                content=Image(src=f"capsule_{i + 1}.png", width=50, height=50, fit="contain"),
                left=pos[0],
                top=pos[1],
                width=90,
                height=90
            )
            for i, pos in enumerate(capsule_positions)
        ]

        # Welcome page content
        welcome_page = Container(
            width=320,
            height=650,
            bgcolor="#26A69A",
            border_radius=35,
            content=Stack(
                controls=[
                    *capsules,
                    Container(
                        width=320,
                        height=650,
                        padding=padding.symmetric(horizontal=20),
                        content=Column(
                            controls=[
                                Container(
                                    margin=margin.only(top=355),
                                    content=Text(
                                        value="Your personal \n assistant, but for \nyour pills!",
                                        size=22,
                                        color="white",
                                        weight=FontWeight.BOLD,
                                        text_align=TextAlign.CENTER,
                                    ),
                                ),
                                Container(
                                    margin=margin.only(top=5, bottom=25),
                                    content=Text(
                                        value="Your daily dose, perfectly \non time.",
                                        size=16,
                                        color="white",
                                        text_align=TextAlign.CENTER,
                                    ),
                                ),
                                Container(
                                    width=200,
                                    height=45,
                                    content=ElevatedButton(
                                        content=Text(
                                            value="Sign Up",
                                            text_align=TextAlign.CENTER,
                                            weight=FontWeight.BOLD,
                                        ),
                                        bgcolor="#E0F2F1",
                                        color="black",
                                        width=200,
                                        on_click=lambda _: switch_to_signup(),
                                    ),
                                ),
                                Container(
                                    margin=margin.only(top=10),
                                    content=TextButton(
                                        text="Already have an account? Login",
                                        on_click=lambda _: switch_to_login(),
                                        style=ButtonStyle(
                                            color="white",
                                            text_style=TextStyle(size=14),
                                        ),
                                    ),
                                ),
                            ],
                            horizontal_alignment=CrossAxisAlignment.CENTER,
                            alignment=MainAxisAlignment.START,
                        ),
                    ),
                ],
            ),
        )
        outer_container.content = welcome_page
        page.update()

    def switch_to_login():
        outer_container.content = create_login_page()
        page.update()

    def switch_to_home():
        outer_container.content = create_home_page()
        page.update()

    def switch_to_schedule():
        outer_container.content = create_schedule_page()
        page.update()

    # Initial loading page
    loading_page = Container(
        width=320,
        height=650,
        bgcolor="#E0F2F1",
        border_radius=35,
        content=Column(
            controls=[
                Image(
                    src="logo.png",
                    width=200,
                    height=200,
                ),
                Text(
                    value="Stay on Track,\nStay Healthy!!",
                    size=24,
                    color="black",
                    weight=FontWeight.BOLD,
                    text_align=TextAlign.CENTER,
                ),
            ],
            alignment=MainAxisAlignment.CENTER,
            horizontal_alignment=CrossAxisAlignment.CENTER,
        ),
    )

    outer_container = Container(content=loading_page)
    page.add(outer_container)

    async def delayed_switch():
        await asyncio.sleep(3)
        switch_to_welcome()

    await delayed_switch()

app(target=main)
