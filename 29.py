from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.uix.scrollview import ScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarListItem
from kivymd.uix.label import MDLabel
from kivymd.uix.progressbar import MDProgressBar
from kivy.clock import Clock
from plyer import filechooser
import requests
import os

BASE_URL = "http://127.0.0.1:5000"
# BASE_URL = "https://your-render-service.onrender.com"

KV = '''
<SelectionForm>:
    orientation: 'vertical'
    size_hint_y: None
    height: self.minimum_height
    padding: dp(20)
    spacing: dp(12)

    # Title bar
    MDBoxLayout:
        size_hint_y: None
        height: dp(48)
        id: header_bar
        md_bg_color: 0.29, 0.69, 0.31, 1
        padding: dp(10)

        MDLabel:
            text: "Ronald's Electronic Shop"
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 1
            font_style: "H6"
            halign: "center"
            valign: "middle"
            size_hint_x: 1

    MDTextField:
        id: name_input
        hint_text: "Full Name"
        mode: "rectangle"
        size_hint_x: 1

    MDTextField:
        id: contact_input
        hint_text: "Contact Number"
        mode: "rectangle"
        size_hint_x: 1

    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(10)
        size_hint_y: None
        height: dp(48)
        size_hint_x: 1

        MDRaisedButton:
            id: unit_btn
            text: root.unit
            md_bg_color: root.theme_color
            on_release: root.open_popup("unit")
            size_hint_x: 1

        MDRaisedButton:
            id: inches_btn
            text: root.inches
            md_bg_color: root.theme_color
            on_release: root.open_popup("inches")
            size_hint_x: 1

        MDRaisedButton:
            id: brand_btn
            text: root.brand
            md_bg_color: root.theme_color
            on_release: root.open_popup("brand")
            size_hint_x: 1

    MDRaisedButton:
        id: address_btn
        text: root.address
        md_bg_color: root.theme_color
        on_release: root.open_popup("address")
        size_hint_y: None
        height: dp(48)
        pos_hint: {"center_x": 0.5}
        size_hint_x: 1

    MDTextField:
        id: issue_desc
        hint_text: "Issue Description"
        mode: "rectangle"
        multiline: True
        size_hint_x: 1

    MDRaisedButton:
        id: issue_btn
        text: root.issue
        md_bg_color: root.theme_color
        on_release: root.open_popup("issue")
        size_hint_y: None
        height: dp(48)
        pos_hint: {"center_x": 0.5}
        size_hint_x: 1

    MDRaisedButton:
        id: upload_photo_btn
        text: "Upload Photo"
        md_bg_color: root.theme_color
        size_hint_y: None
        height: dp(48)
        pos_hint: {"center_x": 0.5}
        size_hint_x: 1
        on_release: app.upload_photo()

    MDBoxLayout:
        size_hint_y: None
        height: dp(70)
        padding: [0, dp(20), 0, 0]

        MDRaisedButton:
            id: submit_btn
            text: "Submit"
            md_bg_color: root.theme_color
            size_hint_x: 1
            pos_hint: {"center_x": 0.5}
            on_release: app.start_progress()
'''

class SelectionForm(MDBoxLayout):
    unit = StringProperty("Select Unit")
    inches = StringProperty("Select Inches")
    brand = StringProperty("Select Brand")
    issue = StringProperty("Select Issue")
    address = StringProperty("Select Address")
    theme_color = ListProperty([0.53, 0.81, 0.98, 1])
    dialog = None

    def open_popup(self, category):
        options = {
            "unit": ["LED TV", "Laptop", "Refrigerator", "Electric Fan", "Others"],
            "inches": ["14", "15.6", "17", "32", "42", "55", "Others"],
            "brand": ["Samsung", "LG", "Sony", "Acer", "Dell", "Others"],
            "address": ["Poblacion", "Nanga", "Bagacay", "Others"],
            "issue": ["No Power", "No Display", "Overheating", "Noise", "Others"]
        }
        items = []
        for option in options.get(category, []):
            items.append(
                OneLineAvatarListItem(
                    text=option,
                    on_release=lambda x, c=category: self.set_selection(c, x.text)
                )
            )
        self.dialog = MDDialog(title=f"Select {category.capitalize()}", type="simple", items=items)
        self.dialog.open()

    def set_selection(self, category, value):
        setattr(self, category, value)
        if self.dialog:
            self.dialog.dismiss()

class MainApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        Builder.load_string(KV)
        root = MDScreen()
        scroll = ScrollView()
        self.form = SelectionForm()
        scroll.add_widget(self.form)
        root.add_widget(scroll)
        self.photo_path = None
        self.progress_dialog = None
        self.progress_bar = None
        self.progress_label = None
        return root

    def upload_photo(self):
        paths = filechooser.open_file(title="Pick a photo", filters=[("Image files", "*.png;*.jpg;*.jpeg")])
        if paths:
            self.photo_path = paths[0]
            print("Photo selected:", self.photo_path)

    def start_progress(self):
        # Create a proper layout for the dialog content
        box = MDBoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=dp(90))
        self.progress_bar = MDProgressBar(value=0, max=100)
        self.progress_label = MDLabel(text="0%", halign="center")

        box.add_widget(self.progress_bar)
        box.add_widget(self.progress_label)

        self.progress_dialog = MDDialog(title="Processing...", type="custom", content_cls=box)
        self.progress_dialog.open()

        # Schedule updates every 0.1s (10 seconds total)
        self.progress_value = 0
        Clock.schedule_interval(self.update_progress, 0.1)

    def update_progress(self, dt):
        self.progress_value += 1
        if self.progress_value > 100:
            self.progress_dialog.dismiss()
            Clock.unschedule(self.update_progress)
            self.submit()  # Send after 10s
            return False
        self.progress_bar.value = self.progress_value
        self.progress_label.text = f"{self.progress_value}%"

    def submit(self):
        url = f"{BASE_URL}/send-to-telegram"
        payload = {
            "name": self.form.ids.name_input.text or "",
            "contact": self.form.ids.contact_input.text or "",
            "unit": self.form.unit or "",
            "inches": self.form.inches or "",
            "brand": self.form.brand or "",
            "address": self.form.address or "",
            "issue": self.form.issue or "",
            "issue_desc": self.form.ids.issue_desc.text or "",
        }
        try:
            if self.photo_path and os.path.exists(self.photo_path):
                with open(self.photo_path, "rb") as f:
                    r = requests.post(url, data=payload, files={"photo": f}, timeout=20)
            else:
                r = requests.post(url, json=payload, timeout=20)

            print("Submitted:", r.status_code, r.text)

            # Show success dialog
            success_dialog = MDDialog(
                title="✔ Success",
                text="Message sent to Telegram!",
                size_hint=(0.8, None),
                height=dp(150)
            )
            success_dialog.open()

        except Exception as e:
            print("Submit error:", e)
            error_dialog = MDDialog(
                title="❌ Error",
                text=f"Failed to send: {str(e)}",
                size_hint=(0.8, None),
                height=dp(150)
            )
            error_dialog.open()

if __name__ == '__main__':
    MainApp().run()
