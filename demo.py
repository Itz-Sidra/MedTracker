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
from kivymd.uix.screenmanager import MDScreenManager

KV = '''
<CustomCard>:
    orientation: 'vertical'
    size_hint: None, None
    size: "280dp", "180dp"
    md_bg_color: 0.30, 1.94, 1.79, 0.6
    radius: [20, 20, 20, 20]
    elevation: 3
    padding: "20dp"
    spacing: "10dp"

    MDLabel:
        text: root.title
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        font_style: "H5"
        bold: True
        size_hint_y: None
        height: self.texture_size[1]
        halign: "left"

    MDLabel:
        text: root.description
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 0.9
        font_style: "Body1"
        size_hint_y: None
        height: self.texture_size[1]

    MDIconButton:
        icon: root.card_icon
        theme_text_color: "Custom"
        text_color: 1, 1, 1, 1
        pos_hint: {"center_x": .75}
        user_font_size: "100sp"

<HomePage>:
    MDBoxLayout:
        orientation: 'vertical'
        spacing: "20dp"
        padding: "15dp"
        md_bg_color: 1, 1, 1, 1

        MDLabel:
            text: "Hello User!"
            font_style: "H3"
            halign: "center"
            theme_text_color: "Custom"
            text_color: 0.10, 0.44, 0.41, 1
            size_hint_y: None
            height: "80dp"
            bold: True

        ScrollView:
            id: scroll_view
            size_hint_y: 1

            MDGridLayout:
                id: card_grid
                cols: 2
                spacing: "15dp"
                padding: "10dp"
                size_hint_y: None
                height: self.minimum_height

<MainScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        md_bg_color: 1, 1, 1, 1

        MDScreenManager:
            id: screen_manager

            HomePage:
                name: 'home'

            MDScreen:
                name: 'notification_log'
                MDLabel:
                    text: "Notification Log Screen"
                    halign: 'center'

            MDScreen:
                name: 'today_medication'
                MDLabel:
                    text: "Today's Medication Screen"
                    halign: 'center'

            MDScreen:
                name: 'intake_tracker'
                MDLabel:
                    text: "Intake Tracker Screen"
                    halign: 'center'

            MDScreen:
                name: 'schedule'
                MDLabel:
                    text: "Schedule Screen"
                    halign: 'center'

            MDScreen:
                name: 'profile'
                MDLabel:
                    text: "Profile Screen"
                    halign: 'center'

        MDCard:
            size_hint_y: None
            height: "80dp"
            md_bg_color: 0.33, 0.84, 0.82, 1
            radius: [20, 20, 0, 0]
            elevation: 0
            padding: "10dp"

            MDBoxLayout:
                spacing: "20dp"
                padding: "10dp"

                MDIconButton:
                    icon: "home"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    on_release: app.switch_screen('home')

                MDIconButton:
                    icon: "bell"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    on_release: app.switch_screen('notification_log')

                MDIconButton:
                    icon: "clock"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    on_release: app.switch_screen('today_medication')

                MDIconButton:
                    icon: "clipboard-list"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    on_release: app.switch_screen('intake_tracker')

                MDIconButton:
                    icon: "calendar"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    on_release: app.switch_screen('schedule')

                MDIconButton:
                    icon: "account"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    on_release: app.switch_screen('profile')
'''

class CustomCard(MDCard):
    title = StringProperty("")
    description = StringProperty("")
    card_icon = StringProperty("")

class HomePage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self.add_cards)

    def add_cards(self, *args):
        cards_data = [
            ("Upcoming Dose", "You're all set! No medication scheduled right now", "clock"),
            ("Intake Tracker", "Keep track of what matters!", "clipboard-check"),
            ("Notification Log", "No notifications for now!", "bell"),
            ("Schedule", "Schedule your medications easily", "calendar"),
        ]

        for title, desc, icon in cards_data:
            card = CustomCard(
                title=title,
                description=desc,
                card_icon=icon
            )
            self.ids.card_grid.add_widget(card)

class MainScreen(MDScreen):
    pass

class MedTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        Builder.load_string(KV)
        return MainScreen()

    def switch_screen(self, screen_name):
        self.root.ids.screen_manager.current = screen_name
        print(f"Navigating to {screen_name}")

if __name__ == "__main__":
    MedTrackerApp().run()
