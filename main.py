from flet import *
import asyncio
import datetime
import json
import os

class MedicationSchedule:
    def __init__(self):
        self.filename = "medication_schedule.json"
        self.schedule = self.load_schedule()

    def load_schedule(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return []

    def save_schedule(self):
        with open(self.filename, 'w') as f:
            json.dump(self.schedule, f)

    def add_medication(self, name, time, specific_time, type):
        self.schedule.append({
            "name": name,
            "time": time,
            "specific_time": specific_time,
            "type": type
        })
        self.save_schedule()

    def update_medication_time(self, index, new_time, new_specific_time):
        if 0 <= index < len(self.schedule):
            self.schedule[index]["time"] = new_time
            self.schedule[index]["specific_time"] = new_specific_time
            self.save_schedule()

    def get_todays_medications(self):
        return self.schedule

class UserAuth:
    def __init__(self):
        self.filename = "users.json"
        self.users = self.load_users()

    def load_users(self):
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                return json.load(f)
        return {}

    def save_users(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f)

    def register_user(self, email, password, name):
        if email in self.users:
            return False, "Email already registered"
        
        self.users[email] = {
            "password": password,  # hides the password
            "name": name
        }
        self.save_users()
        return True, "Registration successful"

    def login_user(self, email, password):
        if email not in self.users:
            return False, "Email not found"
        if self.users[email]["password"] != password:  # verify hidden
            return False, "Incorrect password"
        return True, self.users[email]["name"]

async def main(page: Page):
    page.bgcolor = "#2C2C2C"
    page.title = "Med Tracker"
    page.window_width = 320
    page.window_height = 650

    med_schedule = MedicationSchedule()
    user_auth = UserAuth()
    page.refs = {"time_dropdown": Ref[Dropdown](), "specific_time_field": Ref[TextField]()}

    def show_time_dialog(index, current_time, current_specific_time):
        def update_medication_time(e):
            new_time = page.refs["time_dropdown"].current.value
            new_specific_time = page.refs["specific_time_field"].current.value
            med_schedule.update_medication_time(index, new_time, new_specific_time)
            dlg.open = False
            switch_to_home()
            page.update()

        dlg = AlertDialog(
            title=Text("Update Medication Time"),
            content=Column(
                controls=[
                    Dropdown(
                        label="Time of Day",
                        value=current_time,
                        options=[
                            dropdown.Option("breakfast"),
                            dropdown.Option("lunch"),
                            dropdown.Option("dinner"),
                            dropdown.Option("bedtime")
                        ],
                        width=200,
                        ref=page.refs["time_dropdown"]
                    ),
                    TextField(
                        label="Specific Time (HH:MM)",
                        value=current_specific_time,
                        width=200,
                        ref=page.refs["specific_time_field"]
                    )
                ],
                spacing=10,
            ),
            actions=[
                TextButton("Cancel", on_click=update_medication_time),
                TextButton("Update", on_click=update_medication_time),
            ],
            actions_alignment="end",
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    def create_medication_card(med, index):
        icon = Icon(name=icons.MEDICAL_SERVICES_OUTLINED if med["type"] == "Tablet" else icons.MEDICATION)
        time_display = f"Before {med['time']}"
        if med.get("specific_time"):
            time_display += f" ({med['specific_time']})"
            
        return Container(
            content=Row(
                controls=[
                    icon,
                    Column(
                        controls=[
                            Text(med["name"], weight="bold", color="white"),  # Added medication name
                            Text(time_display, color="white", size=12)
                        ],
                    ),
                    Container(width=10),
                    IconButton(
                        icon=icons.NOTIFICATIONS_NONE,
                        icon_color="white",
                        on_click=lambda e: show_time_dialog(index, med["time"], med.get("specific_time", ""))
                    )
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor="#7DAEA3",
            border_radius=15,
            padding=15,
            margin=margin.only(bottom=10)
        )

    def create_home_page():
        medications = med_schedule.get_todays_medications()
        med_cards = [create_medication_card(med, i) for i, med in enumerate(medications)]
        
        return Container(
            width=320,
            height=650,
            bgcolor="#E0F2F1",
            padding=padding.all(20),
            content=Column(
                controls=[
                    Container(
                        content=Row(
                            controls=[
                                Column(
                                    controls=[
                                        Text("Hello!", size=16, color="#666666"),
                                        Text("Med Tracker", size=24, weight="bold")
                                    ]
                                ),
                                Container(
                                    content=Icon(icons.ACCOUNT_CIRCLE),
                                    bgcolor="#E0F2F1",
                                    border_radius=50
                                )
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN
                        )
                    ),
                    Container(
                        margin=margin.only(top=20),
                        padding=20,
                        bgcolor="#26A69A",
                        border_radius=15,
                        content=Row(
                            controls=[
                                Column(
                                    controls=[
                                        Text(
                                            "Your today's task\nalmost done!",
                                            color="white",
                                            size=16,
                                            weight="bold"
                                        ),
                                        ElevatedButton(
                                            "View Task",
                                            bgcolor="white",
                                            color="#26A69A"
                                        )
                                    ]
                                ),
                                ProgressRing(
                                    value=85,
                                    width=8,
                                    height=80,
                                    color="white",
                                    bgcolor="#4DB6AC"
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
                                    weight="bold"
                                ),
                                Column(controls=med_cards)
                            ]
                        )
                    ),
                    create_navigation_bar()
                ]
            )
        )

    def create_schedule_page():
        name_field = TextField(
            label="Medication Name",
            border_color="#26A69A"
        )
        
        time_field = Dropdown(
            label="Time of Day",
            options=[
                dropdown.Option("breakfast"),
                dropdown.Option("lunch"),
                dropdown.Option("dinner"),
                dropdown.Option("bedtime")
            ],
            border_color="#26A69A"
        )
        
        specific_time_field = TextField(
            label="Specific Time (HH:MM)",
            border_color="#26A69A",
            helper_text="Optional: Enter time in 24-hour format"
        )
        
        type_dropdown = Dropdown(
            label="Type",
            options=[
                dropdown.Option("Tablet"),
                dropdown.Option("Capsule")
            ],
            border_color="#26A69A"
        )

        def add_medication(e):
            if name_field.value and time_field.value and type_dropdown.value:
                med_schedule.add_medication(
                    name_field.value,
                    time_field.value,
                    specific_time_field.value,
                    type_dropdown.value
                )
                name_field.value = ""
                time_field.value = None
                specific_time_field.value = ""
                type_dropdown.value = None
                switch_to_home()
                page.update()

        return Container(
            width=320,
            height=650,
            bgcolor="#E0F2F1",
            padding=20,
            content=Column(
                controls=[
                    Text("Add Medication Schedule", size=24, weight="bold"),
                    Container(height=20),
                    name_field,
                    Container(height=10),
                    time_field,
                    Container(height=10),
                    specific_time_field,
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
                    Container(height=20),
                    create_navigation_bar()
                ]
            )
        )

    def create_navigation_bar():
        return Container(
            padding=15,
            bgcolor="#26A69A",
            border_radius=15,
            content=Row(
                controls=[
                    TextButton(
                        content=Column(
                            controls=[
                                Icon(icons.ACCESS_TIME_FILLED, color="white"),
                                Text("Today's\nMedication", color="white", size=12)
                            ],
                            horizontal_alignment=CrossAxisAlignment.CENTER
                        ),
                        on_click=lambda _: switch_to_home()
                    ),
                    TextButton(
                        content=Column(
                            controls=[
                                Icon(icons.CALENDAR_MONTH, color="white"),
                                Text("Schedule", color="white", size=12)
                            ],
                            horizontal_alignment=CrossAxisAlignment.CENTER
                        ),
                        on_click=lambda _: switch_to_schedule()
                    )
                ],
                alignment=MainAxisAlignment.SPACE_EVENLY
            )
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
            if not email_field.value or not password_field.value:
                error_text.value = "Please fill in all fields"
                error_text.visible = True
                page.update()
                return

            success, message = user_auth.login_user(
                email_field.value,
                password_field.value
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
                        content=Text(
                            "Login",
                            weight=FontWeight.BOLD,
                        ),
                        width=200,
                        bgcolor="#E0F2F1",
                        color="black",
                        on_click=handle_login,
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
                                weight=FontWeight.BOLD
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
                                            weight=FontWeight.BOLD
                                        ),
                                        bgcolor="#E0F2F1",
                                        color="black",
                                        width=200,
                                        on_click=lambda _: print("Sign Up Clicked!"),
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