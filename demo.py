from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
from kivy.uix.scrollview import ScrollView

class HomePage(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Main Layout
        layout = MDBoxLayout(orientation="vertical", spacing=10)

        # Header
        header = MDLabel(
            text="Hello User!",
            font_style="H4",
            halign="center",
            theme_text_color="Custom",
            text_color=(0, 0.5, 0.5, 1),
            size_hint=(1, None),
            height="48dp"
        )
        layout.add_widget(header)

        # Scrollable content to manage space better on smaller screens
        scroll_view = ScrollView(size_hint=(1, None), size=(self.width, self.height))
        content = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        content.height = self.height  # Adjust height for scrollable content

        # Grid layout for buttons
        grid = MDGridLayout(cols=2, spacing=15, padding=10, size_hint=(1, None), height="400dp")
        grid.add_widget(
            MDRaisedButton(
                text="Upcoming Dose\nYou're all set! No medication scheduled right now—stay healthy & take care!",
                md_bg_color=(0.6, 0.8, 0.8, 1),
                size_hint=(None, None),
                width="180dp",
                height="100dp"
            )
        )
        grid.add_widget(
            MDRaisedButton(
                text="Intake Tracker\nKeep track of what matters!",
                md_bg_color=(0.6, 0.8, 0.8, 1),
                size_hint=(None, None),
                width="180dp",
                height="100dp"
            )
        )
        grid.add_widget(
            MDRaisedButton(
                text="Notification Log\nNo notifications for now!",
                md_bg_color=(0.6, 0.8, 0.8, 1),
                size_hint=(None, None),
                width="180dp",
                height="100dp"
            )
        )
        grid.add_widget(
            MDRaisedButton(
                text="Schedule\nSchedule your medications easily and never miss a dose. Your well-being matters!",
                md_bg_color=(0.6, 0.8, 0.8, 1),
                size_hint=(None, None),
                width="180dp",
                height="100dp"
            )
        )
        content.add_widget(grid)
        scroll_view.add_widget(content)
        layout.add_widget(scroll_view)

        # Bottom Navigation Bar
        bottom_nav = MDBottomNavigation()
        bottom_nav.add_widget(
            MDBottomNavigationItem(
                name="notification_log",
                text="Notification Log",
                icon="bell"
            )
        )
        bottom_nav.add_widget(
            MDBottomNavigationItem(
                name="medication",
                text="Today's Medication",
                icon="pill"
            )
        )
        bottom_nav.add_widget(
            MDBottomNavigationItem(
                name="intake_tracker",
                text="Intake Tracker",
                icon="chart-bar"
            )
        )
        bottom_nav.add_widget(
            MDBottomNavigationItem(
                name="schedule",
                text="Schedule",
                icon="calendar"
            )
        )
        bottom_nav.add_widget(
            MDBottomNavigationItem(
                name="me",
                text="Me",
                icon="account"
            )
        )
        layout.add_widget(bottom_nav)

        self.add_widget(layout)


# Main App
class MedTrackerApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        return HomePage()

if __name__ == "__main__":
    MedTrackerApp().run()