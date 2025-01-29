from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView
from kivy.graphics import Color, Rectangle
from kivymd.uix.button import MDIconButton
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock

# Define custom styles
KV = '''
<CustomCard>:
    orientation: 'vertical'
    size_hint: None, None
    size: "180dp", "150dp"
    md_bg_color: 0.4, 0.8, 0.75, 1  # Turquoise color
    radius: [15, 15, 15, 15]
    elevation: 2
    padding: "10dp"
    spacing: "5dp"

    MDLabel:
        text: root.title
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        font_style: "Subtitle1"
        bold: True
        size_hint_y: None
        height: self.texture_size[1]

    MDLabel:
        text: root.description
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 0.9
        font_style: "Caption"
        size_hint_y: None
        height: self.texture_size[1]

    MDIconButton:
        icon: root.card_icon
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        pos_hint: {"center_x": .5}

MDScreen:
    BoxLayout:
        orientation: 'vertical'

        # Top Section with "Hello User"
        MDBoxLayout:
            size_hint_y: None
            height: "50dp"
            md_bg_color: 0.2, 0.6, 0.6, 1
            padding: "10dp"
            MDLabel:
                text: "Hello, User!"
                font_style: "H6"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1

        # Main Screen Content
        ScreenManager:
            id: screen_manager

            Screen:
                name: 'home'
                ScrollView:
                    MDGridLayout:
                        id: card_grid
                        cols: 2
                        adaptive_height: True
                        padding: "10dp"
                        spacing: "10dp"

            Screen:
                name: 'notification_log'
                MDLabel:
                    text: "Notification Log Screen"
                    halign: 'center'

            Screen:
                name: 'today_medication'
                MDLabel:
                    text: "Today's Medication Screen"
                    halign: 'center'

            Screen:
                name: 'intake_tracker'
                MDLabel:
                    text: "Intake Tracker Screen"
                    halign: 'center'

            Screen:
                name: 'schedule'
                MDLabel:
                    text: "Schedule Screen"
                    halign: 'center'

            Screen:
                name: 'profile'
                MDLabel:
                    text: "Profile Screen"
                    halign: 'center'

        # Bottom Navigation
        MDBottomNavigation:
            panel_color: 0.2, 0.6, 0.6, 1  # Adjust the background color
            text_color_active: 1, 1, 1, 1
            radius: [30, 30, 0, 0]  # Top-left and top-right rounded corners

            MDBottomNavigationItem:
                name: 'home'
                text: "Home"
                icon: "home"
                on_tab_press: app.show_home()

            MDBottomNavigationItem:
                name: 'notification_log'
                text: "Notification Log"
                icon: "bell"
                on_tab_press: app.show_notification_log()

            MDBottomNavigationItem:
                name: 'today_medication'
                text: "Today's Medication"
                icon: "clock"
                on_tab_press: app.show_today_medication()

            MDBottomNavigationItem:
                name: 'intake_tracker'
                text: "Intake Tracker"
                icon: "clipboard-list"
                on_tab_press: app.show_intake_tracker()

            MDBottomNavigationItem:
                name: 'schedule'
                text: "Schedule"
                icon: "calendar"
                on_tab_press: app.show_schedule()

            MDBottomNavigationItem:
                name: 'profile'
                text: "Me"
                icon: "account"
                on_tab_press: app.show_profile()
'''

class CustomCard(MDCard):
    title = StringProperty("")
    description = StringProperty("")
    card_icon = StringProperty("")

class MedTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        Builder.load_string(KV)
        return Builder.load_string(KV)

    def show_home(self):
        self.root.ids.screen_manager.current = 'home'
        print("Navigating to Home")

    def show_notification_log(self):
        self.root.ids.screen_manager.current = 'notification_log'
        print("Navigating to Notification Log")

    def show_today_medication(self):
        self.root.ids.screen_manager.current = 'today_medication'
        print("Navigating to Today's Medication")

    def show_intake_tracker(self):
        self.root.ids.screen_manager.current = 'intake_tracker'
        print("Navigating to Intake Tracker")

    def show_schedule(self):
        self.root.ids.screen_manager.current = 'schedule'
        print("Navigating to Schedule")

    def show_profile(self):
        self.root.ids.screen_manager.current = 'profile'
        print("Navigating to Profile")


if __name__ == "__main__":
    MedTrackerApp().run()
