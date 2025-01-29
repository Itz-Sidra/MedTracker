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

<HomePage>:
    BoxLayout:
        orientation: 'vertical'
        
        MDBoxLayout:
            orientation: 'vertical'
            spacing: "20dp"
            padding: "15dp"
            
            MDLabel:
                text: "Hello User!"
                font_style: "H4"
                halign: "center"
                theme_text_color: "Custom"
                text_color: 0.0, 0.6, 0.5, 1
                size_hint_y: None
                height: "60dp"
                bold: True
                italic: True

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

            MDBottomNavigation:
                panel_color: 0.4, 0.8, 0.75, 1
                selected_color_background: 0.35, 0.7, 0.65, 1
                text_color_active: 1, 1, 1, 1
                size_hint_y: None
                height: "80dp"

                MDBottomNavigationItem:
                    name: 'notification'
                    text: 'Notification\\nLog'
                    icon: 'bell'

                MDBottomNavigationItem:
                    name: 'medication'
                    text: "Today's\\nMedication"
                    icon: 'pill'

                MDBottomNavigationItem:
                    name: 'tracker'
                    text: 'Intake\\nTracker'
                    icon: 'chart-bar'

                MDBottomNavigationItem:
                    name: 'schedule'
                    text: 'Schedule'
                    icon: 'calendar'

                MDBottomNavigationItem:
                    name: 'profile'
                    text: 'Me'
                    icon: 'account'
'''

class CustomCard(MDCard):
    title = StringProperty("")
    description = StringProperty("")
    card_icon = StringProperty("")

class HomePage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Set background color
        with self.canvas.before:
            Color(rgba=(0.95, 0.98, 0.98, 1))
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(size=self.update_rect, pos=self.update_rect)
        
        # Schedule the addition of cards after the widget tree is built
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

    def update_rect(self, *args):
        self.bg_rect.size = self.size
        self.bg_rect.pos = self.pos

class MedTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        Builder.load_string(KV)
        return HomePage()

if __name__ == "__main__":
    MedTrackerApp().run()
