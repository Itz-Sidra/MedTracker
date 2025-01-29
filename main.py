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

    def add_medication(self, name, time, type):
        self.schedule.append({
            "name": name,
            "time": time,
            "type": type
        })
        self.save_schedule()

    def get_todays_medications(self):
        return self.schedule

async def main(page: Page):
    page.bgcolor = "#2C2C2C"
    page.title = "Med Tracker"
    page.window_width = 320
    page.window_height = 650

    med_schedule = MedicationSchedule()

    def create_medication_card(med):
        icon = Icon(name=icons.MEDICAL_SERVICES_OUTLINED if med["type"] == "Tablet" else icons.MEDICATION)
        return Container(
            content=Row(
                controls=[
                    icon,
                    Column(
                        controls=[
                            Text(med["type"], weight="bold", color="white"),
                            Text(f"Before {med['time']}", color="white", size=12)
                        ],
                    ),
                    Container(width=10),
                    Icon(name=icons.NOTIFICATIONS_NONE, color="white")
                ],
                alignment=MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor="#7DAEA3",
            border_radius=15,
            padding=15,
            margin=margin.only(bottom=10)
        )

    def create_home_page():
        todays_meds = med_schedule.get_todays_medications()
        med_cards = [create_medication_card(med) for med in todays_meds]

        return Container(
            width=320,
            height=650,
            bgcolor="#E0F2F1",
            padding=padding.all(20),
            content=Column(
                controls=[
                    # Header
                    Container(
                        content=Row(
                            controls=[
                                Column(
                                    controls=[
                                        Text("Hello!", size=16, color="#666666"),
                                        Text("XYZ ABC", size=24, weight="bold")
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
                    
                    # Progress Card
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
                                            color="#26A69A",
                                            style=ButtonStyle(
                                                shape={
                                                    "": RoundedRectangleBorder(radius=8),
                                                }
                                            ),
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

                    # Today's Medications Section
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

                    # Navigation Bar
                    Container(
                        margin=margin.only(top=20),
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
                ]
            )
        )

    def create_schedule_page():
        def add_medication(e):
            med_name = name_field.value
            med_time = time_field.value
            med_type = type_dropdown.value
            
            if med_name and med_time and med_type:
                med_schedule.add_medication(med_name, med_time, med_type)
                name_field.value = ""
                time_field.value = ""
                type_dropdown.value = None
                switch_to_home()
                page.update()

        name_field = TextField(
            label="Medication Name",
            border_color="#26A69A"
        )
        
        time_field = Dropdown(
            label="Time",
            options=[
                dropdown.Option("breakfast"),
                dropdown.Option("lunch"),
                dropdown.Option("dinner"),
                dropdown.Option("bedtime")
            ],
            border_color="#26A69A"
        )
        
        type_dropdown = Dropdown(
            label="Type",
            options=[
                dropdown.Option("Tablet"),
                dropdown.Option("Capsule")
            ],
            border_color="#26A69A"
        )

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
                    # Navigation Bar
                    Container(
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
                ]
            )
        )

    def create_login_page():
        def handle_login(e):
            # Add your login validation here
            switch_to_home()

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
                    TextField(
                        label="Email",
                        border_color="white",
                        color="white",
                        cursor_color="white",
                    ),
                    Container(height=20),
                    TextField(
                        label="Password",
                        password=True,
                        border_color="white",
                        color="white",
                        cursor_color="white",
                    ),
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
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
            ),
        )

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
    phone_container = Container(
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

    outer_container = Container(content=phone_container)
    page.add(outer_container)

    async def delayed_switch():
        await asyncio.sleep(3)
        switch_to_welcome()

    await delayed_switch()

app(target=main)