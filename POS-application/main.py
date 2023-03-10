import tensorflow as tf
#import tflite_runtime.interpreter as tflite

import numpy as np
import json

import pandas as pd
import psycopg2

from PIL import Image

from datetime import date, timedelta
import datetime
from decimal import *
from kivymd.app import MDApp

from kivy.uix.screenmanager import ScreenManager, Screen

from kivy.properties import ObjectProperty

from kivy.uix.button import Button
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton

from kivymd.uix.list import ThreeLineListItem

from kivy.lang.builder import Builder
from kivy.core.window import Window
from kivy.metrics import dp

from kivymd.uix.label import MDLabel
from kivy.utils import platform

from backend_kivyagg import FigureCanvas
import matplotlib.pyplot as plt

import os
from twilio.rest import Client

########################### IMPORTS ###########################

if platform == "android":
    from android.permissions import request_permissions, Permission, check_permission
    from android.storage import app_storage_path

    permission = request_permissions([Permission.CAMERA])
    while (True):
        if (check_permission('android.permission.CAMERA')):
            break
    app_files_path = app_storage_path() + "/app"
    if not os.path.exists(app_files_path + "/kivy_image"):  # check if image path is in app storage
        os.mkdir(app_files_path + "/kivy_image")

# screen resolution: 320, 568
# For testing on computer
Window.size = (700, 300)
# For app build
# Window.fullscreen = True

screen_helper = """
<MenuButton@ScatterLayout>:
    size_hint: .25,.20
    rotation: 90
<SmallButton@Button>:
    size_hint: .17,.1
<CustomizationButton@Button>:
    font_size: self.width / 13
    size_hint: .30,.25
<Button>:
    background_normal: ''
    background_color: app.change_button_color()
    # background_color: (0, 155 / 255.0, 1, 1)  # default button color
<MenuScreen> 
    MenuButton:
        pos_hint: {'center_x':0.22,'center_y':0.5}
        Button:
            text: 'Checkout'
            on_press: root.manager.current = 'checkout'
    MenuButton:
        pos_hint: {'center_x':0.36,'center_y':0.5}    
        Button:
            text: 'Inventory'
            on_press: root.manager.current = 'inventory'
    MenuButton:
        pos_hint: {'center_x':0.50,'center_y':0.5}
        Button:
            text: 'Return'
            on_press: root.manager.current = 'return'
    MenuButton:
        pos_hint: {'center_x':0.64,'center_y':0.5}
        Button:
            text: 'Statistics'
            on_press: root.manager.current = 'statistics'
    MenuButton:
        pos_hint: {'center_x':0.78,'center_y':0.5}
        Button:
            text: 'Customization'
            on_press: root.manager.current = 'customization'
<CheckoutScreen>:
    on_pre_enter:
        root.add_keyboard()
        root.keys.delete_search()
    SmallButton:
        text: 'Delete'
        pos_hint: {'center_x':0.3,'center_y':0.25}
        on_release: root.keys.delete_search()
    SmallButton:
        text: 'Enter'
        pos_hint: {'center_x':0.7,'center_y':0.25}
        on_release: root.manager.current = 'checkout_table'
    SmallButton:
        text: 'Menu'
        pos_hint: {'center_x':0.1,'center_y':0.1}
        on_press: root.manager.current = 'menu'
    SmallButton:
        text: 'Cart'
        pos_hint: {'center_x':0.65,'center_y':0.1}
        on_press:  root.manager.current = 'checkout_cart'
    SmallButton:
        text: 'Camera'
        pos_hint: {'center_x':0.9,'center_y':0.1}
        on_press: root.manager.current = 'camera'
<CheckoutTableScreen>:
    on_pre_enter: root.load_table()
    SmallButton:
        text: 'Back'
        pos_hint: {'center_x':0.9,'center_y':0.1}
        on_press: root.manager.current = 'checkout'
<CheckoutKeypadScreen>:
    on_pre_enter: 
        root.add_keypad()
        root.keys.delete_search()
    SmallButton:
        text: 'Cart'
        on_press: root.check_user_error()
    SmallButton:
        text: 'Back'
        pos_hint: {'center_x':0.25,'center_y':0.05}
        on_press: root.manager.current = 'checkout'
<CheckoutCartScreen>:
    on_pre_enter: 
        root.cashier_cart()
        root.display_price()
    MDBoxLayout:
        orientation: 'vertical'
        size_hint: (0.6, 1)
        MDScrollView:
            size_hint: (0.9, 0.8)
            do_scroll_y: True
            do_scroll_x: False
            bar_color: 0, 0, 0, 1
            bar_width: 6
            MDList:
                id: cart_container
                width: root.width - 1
                height: self.minimum_height
                size_hint: (None, None)
    SmallButton:
        text: 'Back'
        pos_hint: {'center_x':0.3,'center_y':0.1}
        on_press: root.manager.current = 'checkout'
    SmallButton:    
        text: 'Remove'
        pos_hint: {'center_x':0.55,'center_y':0.1}
        on_press: root.manager.current = 'remove_from_cart'
    SmallButton:
        text: 'Done'
        pos_hint: {'center_x':0.8,'center_y':0.1}
        on_press: 
            root.update_customer_orders_db()
            root.manager.current = 'menu'
        on_release: root.clear_list()
    MDLabel:
        id: price_label
        text: "$0.00"
        pos_hint: {'center_x':1.3,'center_y':0.6}
        font_size: 22
        bold: True
<RemoveFromCartScreen>:
    on_pre_enter: 
        root.add_keyboard()
        root.keys.delete_search()
    SmallButton:
        text: 'Remove'
        size_hint: (None, None)
        size: (90, 70)
        on_press: root.check_user_error()
    SmallButton:
        text: 'Back'
        pos_hint: {'center_x':0.25,'center_y':0.05}
        size_hint: (None, None)
        size: (90, 70)
        on_press: root.manager.current = 'checkout_cart'
<SendReceiptScreen>:
    name: 'send_receipt'
    on_pre_enter: 
        root.add_keypad()
        root.keys.delete_search()
    SmallButton:
        text: 'Back'
        pos_hint: {'center_x':0.7,'center_y':0.1}
        on_press: root.manager.current = 'menu'
    SmallButton:
        text: 'Done'
        pos_hint: {'center_x':0.9,'center_y':0.1}
        on_press: root.send_text()
<CameraScreen>:
    MDBoxLayout:
        orientation: 'vertical'
        Camera:
            id: camera
            resolution: (640,480)
            play: True
            allow_stretch: True
        MDIconButton:
            icon: 'camera'
            pos_hint: {'center_x':0.5,'center_y':0.9}
            on_press: root.capture()
    MDLabel:
        id: prediction_label
        text: "Prediction: "
        font_size: 32
        pos_hint: {'x':0.08,'y':-.4}
    SmallButton:
        text: 'Checkout'
        pos_hint: {'center_x':0.9,'center_y':0.09}
        on_press:
            root.manager.transition.direction = 'right'
            root.manager.current = 'checkout'
<InventoryScreen>:
    name: 'inventory'
    on_pre_enter: root.addInvTable()
    MDBoxLayout:
        orientation: 'vertical'
        MDFloatLayout:
            SmallButton:
                text: 'Back'
                pos_hint: {'center_x':0.06,'center_y':0.06}
                on_press: root.manager.current = 'menu'
            SmallButton:
                text: 'Add Item'
                pos_hint: {'center_x':0.25,'center_y':0.06}
                on_press: root.manager.current = 'additemname'
            SmallButton:
                text: 'Remove Item'
                pos_hint: {'center_x':0.44,'center_y':0.06}
                on_press: root.manager.current = 'removeitem'
            SmallButton:
                text: 'Refresh Table'
                pos_hint: {'center_x':0.705,'center_y':0.06}
                on_press: root.manager.current = 'inventory'
<UpdateInvItemScreen>:
    on_pre_enter:
        root.add_keypad()
        root.keys.delete_search()
    MDRectangleFlatButton:
        text: 'Back'
        pos_hint: {'center_x':0.4,'center_y':0.1}
        on_press: root.manager.current = 'inventory'
    MDRectangleFlatButton:
        text: 'Update'
        pos_hint: {'center_x':0.6,'center_y':0.1}
        # on_press: if root.keys.ids.searchbar.text != '0' : root.manager.current = 'return_cart'
        on_press: root.updatePriceQuery(root.keys.ids.searchbar.text)
        on_press: root.check_user_error(root.keys.ids.searchbar.text)
        on_release: root.keys.delete_search()
        #on_release: root.manager.current = 'inventory'
        #on_release: root.modify_quantity()
<UpdateInvPriceScreen>:
    on_pre_enter:
        root.add_keypad()
        root.keys.delete_search()
    MDRectangleFlatButton:
        text: 'Back'
        pos_hint: {'center_x':0.4,'center_y':0.1}
        on_press: root.manager.current = 'inventory'
    MDRectangleFlatButton:
        text: 'Update'
        pos_hint: {'center_x':0.6,'center_y':0.1}
        on_press: root.check_user_error(root.keys.ids.searchbar.text)
        on_release: root.keys.delete_search()
<AddItemNameScreen>:
    name: 'additemname'
    on_pre_enter: root.add_keyboard()
    on_pre_enter: root.keys.delete_search()
    MDTextField:
        id: searchbar
        disabled: True
        multiline: False
        pos_hint: {'center_x':0.5,'center_y':0.9}
        size_hint_x: None
        width: 300
    SmallButton:
        text: 'Delete'
        pos_hint: {'center_x':0.3,'center_y':0.25}
        on_release: root.keys.delete_search()                
    SmallButton:
        text: 'Confirm'
        pos_hint: {'center_x':0.7,'center_y':0.25}
        size_hint: (None, None)
        on_press: root.check_user_error(root.keys.ids.searchbar.text)
    SmallButton:
        text: 'Menu'
        pos_hint: {'center_x':0.1,'center_y':0.1}
        on_press: root.manager.current = 'menu'
<RemoveItemScreen>:
    name: 'removeitem'
    on_pre_enter: root.add_keyboard()
    on_pre_enter: root.keys.delete_search()
    MDTextField:
        id: searchbar
        disabled: True
        multiline: False
        pos_hint: {'center_x':0.5,'center_y':0.9}
        size_hint_x: None
        width: 300
    SmallButton:
        text: 'Delete'
        pos_hint: {'center_x':0.3,'center_y':0.25}
        on_release: root.keys.delete_search()                    
    SmallButton:
        text: 'Remove'
        pos_hint: {'center_x':0.7,'center_y':0.25}
        on_press: root.check_user_error(root.keys.ids.searchbar.text)
    SmallButton:
        text: 'Menu'
        pos_hint: {'center_x':0.1,'center_y':0.1}
        on_press: root.manager.current = 'menu'                    
<AddItemPriceScreen>:
    name: 'additemprice'
    on_pre_enter:
        root.add_keypad()
        root.keys.delete_search()
    MDTextField:
        id: searchbar
        disabled: True
        multiline: False
        pos_hint: {'center_x':0.5,'center_y':0.9}
        size_hint_x: None
        width: 300
    SmallButton:
        text: 'Delete'
        pos_hint: {'center_x':0.3,'center_y':0.25}
        on_release: root.keys.delete_search()
    SmallButton:
        text: 'Confirm'
        pos_hint: {'center_x':0.7,'center_y':0.25}
        on_press: root.check_user_error(root.keys.ids.searchbar.text)
    SmallButton:
        text: 'Menu'
        pos_hint: {'center_x':0.1,'center_y':0.1}
        on_press: root.manager.current = 'menu'
<AddItemQuantityScreen>:
    name: 'additemquantity'
    on_pre_enter:
        root.add_keypad()
        root.keys.delete_search()
    MDTextField:
        id: searchbar
        disabled: True
        multiline: False
        pos_hint: {'center_x':0.5,'center_y':0.9}
        size_hint_x: None
        width: 300
    SmallButton:
        text: 'Delete'
        pos_hint: {'center_x':0.3,'center_y':0.25}
        on_release: root.keys.delete_search()
    SmallButton:
        text: 'Confirm'
        pos_hint: {'center_x':0.7,'center_y':0.25}
        on_press: root.check_user_error(root.keys.ids.searchbar.text)
    SmallButton:
        text: 'Menu'
        pos_hint: {'center_x':0.1,'center_y':0.1}
        on_press: root.manager.current = 'menu'
<ReturnScreen>:
    on_pre_enter: 
        root.add_keypad()
        root.keys.delete_search()
    SmallButton:
        text: 'Back'
        pos_hint: {'center_x':0.4,'center_y':0.1}
        on_press: root.manager.current = 'menu'
    SmallButton:
        text: 'Enter'
        pos_hint: {'center_x':0.6,'center_y':0.1}
        on_press: root.inputvalidation()
<ReturnCartScreen>:
    on_pre_enter: root.temp_connection()
<ReturnAmountScreen>:
    on_pre_enter:
        root.add_keypad()
        root.keys.delete_search()
    SmallButton:
        text: 'Done'
        pos_hint: {'center_x':0.6,'center_y':0.1}
        on_press: root.update_db()
    SmallButton:
        text: 'Back'
        pos_hint: {'center_x':0.4,'center_y':0.1}
        on_press: root.manager.current = 'return_cart'
<StatisticsScreen>
    FloatLayout:
        id: box
        size_hint: (0.7, 1.13)
    AnchorLayout:
        id: backButton
        anchor_x: 'right'
        anchor_y: 'bottom'
        Button
            size_hint: 0.3, 0.1
            font_size: root.width / 32
            text: "Back"
            on_release: root.manager.current = 'menu'
    GridLayout:
        cols: 1
        size_hint: 0.3, .5
        font_size: 10
        pos_hint: {'x': 0.7, 'y': .5}
        Button:
            id: btn1
            text: "By Month"
            font_size: 10
            size_hint: 0.3, .10
            pos_hint: {'x': 0.7, 'y': .5}
            on_press: root.by_month()
        Button:
            id: btn2
            text: "By Year"
            font_size: 10
            size_hint: 0.3, .10
            pos_hint: {'x': 0.7, 'y': 0.70}
            on_press: root.by_year()
        Button:
            id: btn3
            text: "Last 7 days"
            font_size: 10
            size_hint: 0.3, .10
            pos_hint: {'x': 0.7, 'y': 0.90}
            on_press: root.by_week()
        Button:
            id: btn4
            text: "Last 30 days"
            font_size: 10
            size_hint: 0.3, .10
            pos_hint: {'x': 0.7, 'y': 1.10}
            on_press: root.last_thirty()
        Button:
            id: btn5
            text: "Top Sellers"
            font_size: 10
            size_hint: 0.3, .10
            pos_hint: {'x': 0.7, 'y': 1.3}
            on_press: root.top_sellers()

<CustomizationScreen>:
    CustomizationButton:
        pos_hint: {'center_x':0.5,'center_y':0.7}
        text: 'Change Background Color'
        on_release: root.manager.current = 'background_color'
    CustomizationButton:
        pos_hint: {'center_x':0.5,'center_y':0.3}
        text: 'Change Button Color'
        on_release: root.manager.current = 'button_color'
    SmallButton:
        pos_hint: {'center_x':0.1,'center_y':0.1}
        text: 'Menu'
        on_release: root.manager.current = 'menu'
<BackgroundColorScreen>:
    ColorPicker:
        on_color: root.on_color(self, self.color)
    MDAnchorLayout:
        anchor_x: 'right'
        anchor_y: 'top'
        Button:
            id: btn
            size_hint: 0.2, 0.1
            text: "Go Back"
            on_release: root.manager.current = 'menu' 
    MDAnchorLayout:
        anchor_x: 'right'
        anchor_y: 'bottom'
        Button:
            id: btn1
            size_hint: 0.2, 0.1
            text: "Confirm"
            on_press: root.on_press()
<ButtonColorScreen>:
    ColorPicker:
        on_color: root.on_color(self, self.color)
    MDAnchorLayout:
        anchor_x: 'right'
        anchor_y: 'top'
        Button:
            id: btn
            size_hint: 0.2, 0.1
            text: "Go Back"
            on_release: root.manager.current = 'menu' 
    MDAnchorLayout:
        anchor_x: 'right'
        anchor_y: 'bottom'
        Button:
            id: btn1
            size_hint: 0.2, 0.1
            text: "Confirm"
            on_press: root.on_press()
<KeyManager>:
    pos_hint: {'center_x':0.5,'center_y':0.5}
    MDTextField:
        id: searchbar
        hint_text: 'Enter'
        disabled: True
        multiline: False
        pos_hint: {'center_x':0.5,'center_y':0.9}
        size_hint_x: None
        width: 300
        line_color_normal: app.theme_cls.accent_color
        color_mode: 'primary'
<Manager>:
    canvas.before:
        Color:
            rgba: app.change_background_color()
        Rectangle:
            pos: self.pos
            size: self.size
    id: screen_manager
    menu_screen: menu_screen
    checkout_screen: checkout_screen
    checkout_table_screen: checkout_table_screen
    checkout_keypad_screen: checkout_keypad_screen
    checkout_cart_screen : checkout_cart_screen
    remove_from_cart_screen : remove_from_cart_screen
    send_receipt_screen: send_receipt_screen
    camera_screen: camera_screen
    inventory_screen: inventory_screen
    update_inv: update_inv
    update_inv_price: update_inv_price
    add_item_name_screen: add_item_name_screen
    remove_item_screen: remove_item_screen
    add_item_price_screen: add_item_price_screen
    add_item_quantity_screen: add_item_quantity_screen
    return_screen: return_screen
    return_cart_screen : return_cart_screen
    return_amount_screen  : return_amount_screen
    statistics_screen: statistics_screen
    customization_screen: customization_screen
    background_color_screen: background_color_screen
    button_color_screen: button_color_screen
    MenuScreen:
        id: menu_screen
        name: 'menu'
        manager: screen_manager
    CheckoutScreen:
        id: checkout_screen
        name: 'checkout'
        manager: screen_manager
    CheckoutTableScreen:
        id: checkout_table_screen
        name: 'checkout_table'
        manager: screen_manager
    CheckoutKeypadScreen:
        id: checkout_keypad_screen
        name: 'checkout_keypad'
        manager: screen_manager
    CheckoutCartScreen:
        id: checkout_cart_screen
        name: 'checkout_cart'
        manager: screen_manager
    RemoveFromCartScreen:
        id: remove_from_cart_screen
        name: 'remove_from_cart'
        manager: screen_manager
    SendReceiptScreen:
        id: send_receipt_screen
        name: 'send_receipt'
        manager: screen_manager
    CameraScreen:
        id: camera_screen
        name: 'camera'
        manager: screen_manager
    InventoryScreen:
        id: inventory_screen
        name: 'inventory'
        manager: screen_manager
    UpdateInvItemScreen:
        id: update_inv
        name: 'update_inv_qty'
        manager: screen_manager
    UpdateInvPriceScreen:
        id: update_inv_price
        name: 'updateInvPrice'
        manager: screen_manager
    ReturnScreen:
        id: return_screen
        name: 'return'
        manager: screen_manager
    AddItemNameScreen:
        id: add_item_name_screen
        name: 'additemname'
        manager: screen_manager
    RemoveItemScreen:
        id: remove_item_screen
        name: 'removeitem'
        manager: screen_manager
    AddItemPriceScreen:
        id: add_item_price_screen
        name: 'additemprice'
        manager: screen_manager
    AddItemQuantityScreen:
        id: add_item_quantity_screen
        name: 'additemquantity'
        manager: screen_manager
    ReturnCartScreen:
        id: return_cart_screen
        name: 'return_cart'
        manager: screen_manager
    ReturnAmountScreen:
        id: return_amount_screen
        name: 'return_amount'
        manager: screen_manager
    StatisticsScreen:
        id: statistics_screen
        name: 'statistics'
        manager: screen_manager
    CustomizationScreen:
        id: customization_screen
        name: 'customization'
        manager: screen_manager
    BackgroundColorScreen:
        id: background_color_screen
        name: 'background_color'
        manager: screen_manager
    ButtonColorScreen:
        id: button_color_screen
        name: 'button_color'
        manager: screen_manager
"""


########################### SCREEN HELPER ###########################

class KeyManager(Screen):
    new_item = []

    # Keyboard Start
    # The class is a MDBoxlayout which
    # contains functions for the keyboard and keypad as well
    # as supporting functions for the two
    def keyboard(self):
        row1 = 'qwertyuiop'
        row2 = 'asdfghjkl'
        row3 = 'zxcvbnm<'
        for i in range(len(row1)):
            key = Button(text=row1[i], pos_hint={'center_x': (i + 1) * 0.084, 'center_y': 0.7}, size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row1[i]: self.get_key(key))
            self.add_widget(key)

        for i in range(len(row2)):
            key = Button(text=row2[i], pos_hint={'center_x': (i + 1.65) * 0.084, 'center_y': 0.55},
                         size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row2[i]: self.get_key(key))
            self.add_widget(key)

        for i in range(len(row3)):
            key = Button(text=row3[i], pos_hint={'center_x': (i + 1.8) * 0.084, 'center_y': 0.40},
                         size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row3[i]: self.get_key(key))
            self.add_widget(key)

        key = Button(text='SPACE', pos_hint={'center_x': 0.4914, 'center_y': 0.25}, size_hint=(0.16, 0.13))
        key.bind(on_press=lambda x, key=' ': self.get_key(key))
        self.add_widget(key)

    # Keyboard End

    # Keypad Start
    # This function creates a keypad by creating a button widget for each letter in the keypad
    # There are 3 loops which represent the 3 rows in the keypad and as the button is created for each key
    # Each key is added to KeyManager box layout
    def keypad(self):
        row1 = '789'
        row2 = '456'
        row3 = '123'
        row4 = '.0<'
        for i in range(len(row1)):
            key = Button(text=row1[i], pos_hint={'center_x': (i + 4.5) * 0.09, 'center_y': 0.7}, size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row1[i]: self.get_key(key))
            self.add_widget(key)
        for i in range(len(row2)):
            key = Button(text=row2[i], pos_hint={'center_x': (i + 4.5) * 0.09, 'center_y': 0.55}, size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row2[i]: self.get_key(key))
            self.add_widget(key)
        for i in range(len(row3)):
            key = Button(text=row3[i], pos_hint={'center_x': (i + 4.5) * 0.09, 'center_y': 0.40}, size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row3[i]: self.get_key(key))
            self.add_widget(key)
        for i in range(len(row4)):
            key = Button(text=row4[i], pos_hint={'center_x': (i + 4.5) * 0.09, 'center_y': 0.25}, size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row4[i]: self.get_key(key))
            self.add_widget(key)

    def modify_keypad_row4(self):
        row4 = '-0<'
        for i in range(len(row4)):  # Create conditional for UpdateInvScreen
            key = Button(text=row4[i], pos_hint={'center_x': (i + 4.5) * 0.09, 'center_y': 0.25}, size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row4[i]: self.get_key(key))
            self.add_widget(key)

    def modify_keypad_for_AdditemQty(self):
        row4 = ['0', '', '<']
        for i in range(len(row4)):  # Create conditional for UpdateInvScreen
            key = Button(text=row4[i], pos_hint={'center_x': (i + 4.5) * 0.09, 'center_y': 0.25}, size_hint=(0.08, 0.13))
            key.bind(on_press=lambda x, key=row4[i]: self.get_key(key))
            self.add_widget(key)

    # Keypad End

    # Supporting Functions Start
    # This function gets key value from keyboard or keypad and adds it to the searchbar
    def get_key(self, key):
        global item
        item = None

        self.prior_key = self.ids.searchbar.text
        if key != '<':
            if self.prior_key == "Search: ":
                self.ids.searchbar.text = ''
                self.ids.searchbar.text = f'Search: {key}'
            else:
                self.ids.searchbar.text = f'{self.prior_key}{key}'
        else:
            self.ids.searchbar.text = f'{self.prior_key[:-1]}'

        item = self.ids.searchbar.text

    # This function deletes all text in search field
    def delete_search(self):
        self.ids.searchbar.text = ""
        if 'item' in globals():
            del globals()['item']

    # This function returns string in search text field
    def get_item(self):
        if 'item' in globals():
            return item
        return False
    # Supporting Functions End
    ########################### KEY MANAGER ###########################


class MenuScreen(Screen):
    pass
    ########################### MENU SCREEN ###########################


class CheckoutScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(CheckoutScreen, self).__init__(**kwargs)
        self.created = False

    # This function adds a keymanager object which contains creates the keyboard
    def add_keyboard(self):
        if not self.created:
            self.keys.keyboard()
            self.add_widget(self.keys)
            self.keys.ids.searchbar.hint_text = "Enter Item Name"
            self.created = True
    ########################### CHECKOUT SCREEN ###########################


class CheckoutTableScreen(Screen):
    def __init__(self, **kwargs):
        super(CheckoutTableScreen, self).__init__()
        self.row_info = []

    def load_table(self):
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()

        query = ""
        item = KeyManager().get_item()
        if item == False:
            query = "select item_name, price, quantity from inventory_db"
        else:
            query = "select item_name, price, quantity from inventory_db where item_name like '%" + item + "%'"

        cur.execute(query)
        inv = cur.fetchall()
        table = MDDataTable(
            size_hint=(0.7, 1),
            check=False,
            use_pagination=True,
            column_data=[("Item Name", dp(27)),
                         ("Price", dp(18)),
                         ("Quantity", dp(18)),
                         ],
            row_data=inv
        )

        table.bind(on_row_press=lambda x, row=self.on_row_press: self.keypad_screen())
        table.bind(on_row_press=self.row_pressed)

        conn.close()
        cur.close()
        self.add_widget(table)

    def keypad_screen(self):
        self.manager.current = 'checkout_keypad'

    def on_row_press(self, instance_row):
        """Called when a table row is clicked."""

    def row_pressed(self, instance_table, instance_row):
        """Called when a table row is clicked."""
        # global self.row_info
        self.row_info = []
        start_index, end_index = instance_row.table.recycle_data[instance_row.index]["range"]
        for i in range(start_index, end_index + 1):
            self.row_info.append(instance_row.table.recycle_data[i]["text"])
    ########################### CHECKOUT TABLE SCREEN ###########################


class CheckoutKeypadScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(CheckoutKeypadScreen, self).__init__(**kwargs)
        self.created = False
        self.cameraFlag = False

    # This function adds a keymanager object which contains creates the keyboard
    def add_keypad(self):
        if not self.created:
            self.keys.keypad()
            self.add_widget(self.keys)

            self.keys.ids.searchbar.hint_text = "Enter Item Quantity"
            self.created = True

    def check_user_error(self):
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        if self.manager.checkout_keypad_screen.cameraFlag:
            cur.execute(
                f"SELECT quantity FROM inventory_db WHERE item_name='{self.manager.camera_screen.prediction}'")
            curr_quantity = cur.fetchone()
        else:
            cur.execute(
                f"SELECT quantity FROM inventory_db WHERE item_name='{self.manager.checkout_table_screen.row_info[0]}'")
            curr_quantity = cur.fetchone()

        if self.keys.ids.searchbar.text == "":
            no_input = MessagePopup(f"Enter amount of {self.manager.checkout_table_screen.row_info[0]} to add to cart")
            no_input.open()
        elif int(self.keys.ids.searchbar.text) > int(curr_quantity[0]):
            over_order = MessagePopup(
                f"There is only {int(curr_quantity[0])} {self.manager.checkout_table_screen.row_info[0]}(s) in inventory")
            over_order.open()
        else:
            self.manager.current = 'checkout_cart'
            self.manager.checkout_cart_screen.cashier_cart()
        cur.close()
        conn.close()
    ########################### CHECKOUT KEYPAD SCREEN ###########################


class CheckoutCartScreen(Screen):
    def __init__(self, **kwargs):
        super(CheckoutCartScreen, self).__init__(**kwargs)
        self.total_price = 0.00  # to use to insert into customer_orders_db
        self.item_list = []
        self.item_name = ""
        self.quantity_list = []
        self.price_list = []
        self.price = 0.00  # to place inside MDList
        self.d1 = ""  # current date in yyyy/mm/dd format
        self.rec_dialog = None
        self.receipt_str = ""

    def cashier_cart(self, *args):
        if not self.manager.checkout_table_screen.row_info and not self.manager.checkout_keypad_screen.cameraFlag:
            pass
        else:
            today = date.today()
            self.d1 = today.strftime("%Y-%m-%d")
            if not self.manager.checkout_keypad_screen.cameraFlag:
                self.price = (float(self.manager.checkout_table_screen.row_info[1])) * float(

                    self.manager.checkout_keypad_screen.keys.ids.searchbar.text)

                self.item_name = self.manager.checkout_table_screen.row_info[0].capitalize()
            if self.manager.checkout_keypad_screen.cameraFlag:
                self.item_name = self.manager.camera_screen.prediction
                connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
                conn = psycopg2.connect(connection_string)
                conn.set_session(autocommit=True)
                cur = conn.cursor()
                query = "select price from inventory_db where item_name ='" + self.item_name + "';"
                cur.execute(query)
                itemprice = cur.fetchall()

                self.price = float(*itemprice[0])
                cur.close()
                conn.close()

            self.ids.cart_container.add_widget(
                ThreeLineListItem(text="Item name: " + self.item_name.capitalize(),
                                  secondary_text="Quantity: " + self.manager.checkout_keypad_screen.keys.ids.searchbar.text,
                                  tertiary_text="Price: " + "${:.2f}".format(self.price)))
            self.item_list.append(self.item_name)
            self.quantity_list.append(int(self.manager.checkout_keypad_screen.keys.ids.searchbar.text))
            self.price_list.append(self.price)
            self.total_price += self.price
            self.manager.checkout_table_screen.row_info.clear()
            self.manager.checkout_keypad_screen.keys.ids.searchbar.text = ''
            self.manager.checkout_keypad_screen.cameraFlag = False

    def update_customer_orders_db(self):
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()

        query = 'insert into customer_orders_db (total_cost, list_of_items_bought, quantity_of_each_item_bought, ' \
                'date_of_purchase) values (%s, %s, %s, %s) returning receipt_number'
        val = ("{:.2f}".format(self.total_price), self.item_list, self.quantity_list, self.d1)

        if not self.item_list and not self.quantity_list and self.price == 0.00:
            MessagePopup("Error: The Cart is Empty").startup()
        else:
            cur.execute(query, val)
            r_num = cur.fetchone()[0]
            self.receipt_str += str("Receipt Number:" + str(r_num) + '\n')
            for i in range(len(self.item_list)):
                self.receipt_str += str("*****************\n") + str("Item #" + str(i + 1) + '\n')
                self.receipt_str += str("Item Name: " + str(self.item_list[i]) + "\nQuantity: " + str(
                    self.quantity_list[i]) + "\nPrice: " + "${:.2f}".format(self.price_list[i]) + '\n')
            cur.execute(
                f"SELECT quantity FROM inventory_db WHERE item_name='{str(self.item_list[i].lower())}'")
            curr_quantity = cur.fetchone()
            print(curr_quantity)
            cur.execute(
                f"update inventory_db set quantity = {int(curr_quantity[0]) - int(self.quantity_list[i])} where item_name ='{str(self.item_list[i].lower())}'")
            self.receipt_str += str("\nTotal Price: " + "${:.2f}".format(self.total_price) + '\n')
            self.rec_dialog = MDDialog(title="",
                                       type="custom",
                                       content_cls=MDLabel(text="Send receipt as text message",
                                                           ),
                                       buttons=[
                                           MDRaisedButton(text="Yes", text_color='#000000',
                                                          on_press=self.close_rec,
                                                          on_release=self.go_receipt),
                                           MDFlatButton(text="No", text_color="#000000",
                                                        on_press=self.close_rec,
                                                        on_release=self.go_menu),
                                       ])
            self.rec_dialog.open()
        cur.close()
        conn.close()

    def update_cart(self):
        self.total_price = 0
        self.manager.checkout_cart_screen.ids.cart_container.clear_widgets()
        for i in range(len(self.item_list)):
            self.ids.cart_container.add_widget(
                ThreeLineListItem(text="Item name: " + self.item_list[i].capitalize(),
                                  secondary_text="Quantity: " + str(self.quantity_list[i]),
                                  tertiary_text="Price: " + "${:.2f}".format(self.price_list[i])))
            self.total_price += self.price_list[i]
        self.display_price()

    def close_rec(self, inst):
        self.rec_dialog.dismiss()

    def go_receipt(self, obj):
        self.manager.current = 'send_receipt'

    def go_menu(self, obj):
        self.manager.current = 'menu'

    # resets all variables and lists for next transaction
    def clear_list(self):
        self.ids.cart_container.clear_widgets()
        self.item_list.clear()
        self.quantity_list.clear()
        self.manager.checkout_table_screen.row_info.clear()
        self.manager.checkout_keypad_screen.keys.ids.searchbar.text = ''
        self.price = 0.00
        self.total_price = 0.00

    # fix: dynamically displaying current total price on screen+
    def display_price(self):
        self.ids.price_label.text = "${:.2f}".format(self.total_price)  # return self.price_label.text
    ########################### CHECKOUT CART SCREEN ###########################


class RemoveFromCartScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(RemoveFromCartScreen, self).__init__(**kwargs)
        self.created = False

    # This function adds a keymanager object which contains creates the keyboard
    def add_keyboard(self):
        if not self.created:
            self.keys.keyboard()
            self.add_widget(self.keys)
            self.keys.ids.searchbar.hint_text = "Enter Item Name"
            self.created = True

    def check_user_error(self):
        i_name = self.keys.ids.searchbar.text.title()
        if self.keys.ids.searchbar.text == "":
            no_input = MessagePopup(f"Enter an item to remove from cart")
            no_input.open()
        elif i_name not in self.manager.checkout_cart_screen.item_list:
            not_in_cart = MessagePopup(f"{i_name} is not in the cart")
            not_in_cart.open()
        else:
            index = self.manager.checkout_cart_screen.item_list.index(i_name)
            self.manager.checkout_cart_screen.item_list.pop(index)
            self.manager.checkout_cart_screen.price_list.pop(index)
            self.manager.checkout_cart_screen.quantity_list.pop(index)
            self.manager.checkout_cart_screen.update_cart()
            self.manager.current = 'checkout_cart'


class SendReceiptScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(SendReceiptScreen, self).__init__(**kwargs)
        self.created = False

    def add_keypad(self):
        if not self.created:
            self.keys.keypad()
            self.add_widget(self.keys)
            self.keys.ids.searchbar.hint_text = "Enter Phone Number"
            self.created = True

    def send_text(self):
        if len(self.keys.ids.searchbar.text) != 11 or '.' in self.keys.ids.searchbar.text:
            MessagePopup("Phone Number must be in format 1 123 456 7890").startup()
            self.keys.ids.searchbar.text = ""
            return

        # Find your Account SID and Auth Token at twilio.com/console
        # and set the environment variables. See http://twil.io/secure
        # account_sid = os.environ['TWILIO_ACCOUNT_SID']
        # auth_token = os.environ['TWILIO_AUTH_TOKEN']
        client = Client('ACfa17efcd7c57fa5ea28e148b23ea5d3e', '0e34fbe7befe052834847ebcedf0bf99')
        phone = self.keys.ids.searchbar.text
        msg = self.manager.checkout_cart_screen.receipt_str
        message = client.messages \
            .create(
            body=msg,
            from_='+19498282943',
            to=phone,
        )
        self.manager.checkout_cart_screen.receipt_str = ""
        self.manager.current = 'menu'


class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super(CameraScreen, self).__init__(**kwargs)
        self.prediction_prob = None
        self.prediction = None
        self.confirm = None

    def capture(self, *args):
        camera = self.ids['camera']
        camera.export_to_png('Fruit.png')

        self.preprocess('Fruit.png')

    def preprocess(self, filepath):
        new_img = Image.open('Fruit.png')
        img = new_img.resize((100, 100))
        img = img.convert('RGB')
        img = np.array(img)
        img = np.expand_dims(img, axis=0)
        img = img.astype('float32') / 255

        self.model_prediction(img)

    def model_prediction(self, img):
        # Load TFLite model and allocate tensors.
        interpreter = tf.lite.Interpreter(model_path="cnn_fruits.tflite")  # cnn_fruits.tflite
        interpreter.allocate_tensors()

        # Get input and output tensors.
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        input_data = img
        interpreter.set_tensor(input_details[0]['index'], input_data)

        interpreter.invoke()

        # The function `get_tensor()` returns a copy of the tensor data.
        output_data = interpreter.get_tensor(output_details[0]['index'])
        output_label = output_data.argmax(axis=1)

        prediction_index = output_label.item()

        self.prediction_prob = output_data[0][prediction_index] * 100
        self.prediction_prob = round(self.prediction_prob, 2)

        with open('class_labels.json') as read_file:
            class_dict = json.load(read_file)
            labels = class_dict["class_labels"]

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        query1 = "SELECT unnest(ARRAY_AGG(DISTINCT item_name)) from inventory_db"
        cur.execute(query1)
        item_list = cur.fetchall()
        item_list = [i[0] for i in item_list]
        self.prediction = labels[prediction_index]

        self.ids.prediction_label.text = "Prediction: " + self.prediction + " " + str(self.prediction_prob) + "%"
        match = False
        for x in item_list:
            if x == self.prediction:
                match = True
                if match is True: break
            else:
                match = False
        if match is True:
            self.confirm = MessagePopup(str(self.ids.prediction_label.text))
            self.confirm.add_widget(
                MDFlatButton(text="Confirm Item", pos_hint={'center_x': 0.2, 'center_y': 0.01},
                             on_press=self.go_amount))
            self.confirm.startup()
        else:
            self.invalid = MessagePopup(str(self.ids.prediction_label.text))
            self.invalid.add_widget(
                MDFlatButton(text="Invalid Item, Try Again", pos_hint={'center_x': 0.2, 'center_y': 0.01},
                             on_press=self.restart))
            self.invalid.startup()
        conn.close()
        cur.close()

    def go_amount(self, obj):
        self.manager.checkout_keypad_screen.cameraFlag = True
        self.manager.current = 'checkout_keypad'
        self.confirm.dismiss()

    def restart(self, obj):
        self.manager.current = 'camera'
        self.invalid.dismiss()

    ########################### CAMERA SCREEN ###########################


class InventoryScreen(Screen):
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(InventoryScreen, self).__init__(**kwargs)
        # self.row_info = []
        self.created = False

    # Adding Inventory MDDatatable to MDFloatLayout inside a MDBoxLayout
    def addInvTable(self):
        global inv_table
        inv_table = None
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute('select * from inventory_db order by product_id')
        inv = cur.fetchall()

        window_sizes = Window.size
        if window_sizes[1] < window_sizes[0]:
            dpVal = (window_sizes[0] - window_sizes[1]) * 0.0325
        else:
            dpVal = (window_sizes[1] - window_sizes[0]) * 0.0325

        inv_table = MDDataTable(
            pos_hint={'center_x': 0.5, 'center_y': 0.60},
            size_hint=(1, 0.8),
            use_pagination=True,
            rows_num=3,
            background_color_selected_cell="#44bbe3",
            column_data=[("Product ID", dp(dpVal)),
                         ("Item Name", dp(dpVal)),
                         ("Price", dp(dpVal)),
                         ("Quantity", dp(dpVal))
                         ],
            row_data=inv
        )

        cur.close()
        conn.close()
        self.add_widget(inv_table)
        inv_table.bind(on_row_press=self.row_press)

    # Grabs information from a selected row
    def row_press(self, instance_table, instance_row):
        global row_info
        global inv_dialog
        row_info = []
        inv_dialog = None
        start_index, end_index = instance_row.table.recycle_data[instance_row.index]["range"]
        for i in range(start_index, end_index + 1):
            row_info.append(instance_row.table.recycle_data[i]["text"])

        self.manager.current = 'update_inv_qty'
        return row_info

    # Modifies a quantity to add a new quantity with the existing quantity in the database
    def modify_quantity(self, text):
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(
            f"update inventory_db set quantity = {int(inv_dialog.content_cls.text) + int(row_info[3])} where product_id = {row_info[0]}")

        self.addInvTable()
        cur.close()
        conn.close()
        inv_dialog.dismiss()

    ########################### INVENTORY SCREEN ###########################


############### Update Inventory Screen ###############################
class UpdateInvItemScreen(Screen):
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(UpdateInvItemScreen, self).__init__(**kwargs)
        self.created = False
        self.no_input_dialog = None
        # This function adds a keypad by creating a KeyManager object and calling the keypad function

    def add_keypad(self):
        if not self.created:
            self.keys.keypad()
            self.keys.modify_keypad_row4()
            self.keys.ids.searchbar.hint_text = "Update Item Quantity:"
            self.add_widget(self.keys)
            self.created = True

    def modify_quantity(self):
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(
            f"update inventory_db set quantity = {int(self.keys.ids.searchbar.text) + int(row_info[3])} where product_id = {row_info[0]}")
        cur.close()
        conn.close()
        addTable = InventoryScreen()
        addTable.addInvTable()

    def store_new_item(self, text):
        self.keys.new_item.clear()
        self.keys.new_item.append(str(text))
        self.modify_quantity()

    def close_error_popup(self, inst):
        no_input_dialog.dismiss()

    def close_update_price_popup(self, inst):
        query_dialog.dismiss()
        self.manager.current = 'inventory'

    def updatePriceQuery(self, text):
        input = str(text)
        global query_dialog
        query_dialog = None
        query_dialog = MDDialog(
            title="",
            type="custom",
            text="Would you like to update the price for this item?",
            buttons=[MDFlatButton(text="Yes", text_color="#000000", on_press=self.callUpdateInvPriceScreen),
                     MDFlatButton(text="No", text_color="#000000", on_release=self.close_update_price_popup)]
        )
        if input:
            query_dialog.open()

    def callUpdateInvPriceScreen(self, inst):
        query_dialog.dismiss()
        self.manager.current = 'updateInvPrice'

    def check_user_error(self, text):
        input = str(text)
        global no_input_dialog
        no_input_dialog = None
        no_input_dialog = MDDialog(
            title="",
            type="custom",
            text="Must enter a valid quantity for this item",
            buttons=[MDFlatButton(text="CLOSE", text_color="#000000", on_release=self.close_error_popup)]
        )
        if not input:
            no_input_dialog.open()
        elif input == '-':
            no_input_dialog.open()
        else:
            self.store_new_item(input)


############### Update Inventory Price Screen ###############################
class UpdateInvPriceScreen(Screen):
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(UpdateInvPriceScreen, self).__init__(**kwargs)
        self.created = False
        self.no_input_dialog = None
        # This function adds a keypad by creating a KeyManager object and calling the keypad function

    def add_keypad(self):
        if not self.created:
            self.keys.keypad()
            self.keys.ids.searchbar.hint_text = "Update Item Price:"
            self.add_widget(self.keys)
            self.created = True

    def modify_price(self):
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(
            f"update inventory_db set price = {float(self.keys.ids.searchbar.text)} where product_id = {row_info[0]}")
        cur.close()
        conn.close()
        addTable = InventoryScreen()
        addTable.addInvTable()

    def store_new_price(self, text):
        self.keys.new_item.append(str(text))
        self.modify_price()
        self.manager.current = 'inventory'

    def close_error_popup(self, inst):
        no_input_dialog.dismiss()

    def check_user_error(self, text):
        input = str(text)
        global no_input_dialog
        no_input_dialog = None
        no_input_dialog = MDDialog(
            title="",
            type="custom",
            text="Must enter a valid price for this item",
            buttons=[MDFlatButton(text="CLOSE", text_color="#000000", on_release=self.close_error_popup)]
        )
        if not input:
            no_input_dialog.open()
        if input == '.':
            no_input_dialog.open()
        else:
            self.store_new_price(input)
    ########################### INVENTORY SCREEN ###########################


class AddItemNameScreen(Screen):
    # Variable keys for KeyManager object

    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(AddItemNameScreen, self).__init__(**kwargs)
        self.created = False

    def add_keyboard(self):
        if not self.created:
            self.keys.keyboard()
            self.add_widget(self.keys)
            self.keys.ids.searchbar.hint_text = "Enter Item Name"

            self.created = True

    # This function starts to build the list that will be used to insert a new item to the inventory DB
    def store_new_item(self, text):
        self.keys.new_item.clear()

        self.keys.new_item.append(str(text))

        self.manager.current = 'additemprice'

    # Checks the user input to ensure the text input is populated and the item does not already exist in inventory DB
    def check_user_error(self, text):
        input = str(text)
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(f"SELECT item_name FROM inventory_db WHERE item_name=\'{input}\'")
        inv_list = cur.fetchall()

        if not input:
            no_input = MessagePopup("Must enter item to add")
            no_input.open()
        elif len(inv_list) > 0:
            already_exists = MessagePopup(f"{input} already exists in the inventory")
            already_exists.open()
        else:
            self.store_new_item(input)
        cur.close()
        conn.close()
    ########################### CHECKOUT SCREEN ###########################


class RemoveItemScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        self.invTable = InventoryScreen()
        super(RemoveItemScreen, self).__init__(**kwargs)
        self.created = False

    # This function adds a KeyManager object which contains creates the keyboard
    def add_keyboard(self):
        if not self.created:
            self.keys.keyboard()
            self.add_widget(self.keys)
            self.keys.ids.searchbar.hint_text = "Enter Item Name"

            self.created = True

    def remove_item(self, text):
        removed_item = str(text)

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM inventory_db WHERE item_name = \'{removed_item}\';")
        cur.close()
        conn.close()
        self.manager.current = 'inventory'

    # Checks the user input to ensure the text input is populated and the item desired for removal exists in inventory DB
    def check_user_error(self, text):
        input = str(text)
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()
        cur.execute(f"SELECT item_name FROM inventory_db WHERE item_name=\'{input}\'")
        inv_list = cur.fetchall()

        if not input:
            no_input = MessagePopup("Must enter an item to remove")
            no_input.open()
        elif len(inv_list) == 0:
            does_not_exist = MessagePopup(f"{input} does not exist in the inventory")
            does_not_exist.open()
        else:
            self.remove_item(input)
        cur.close()
        conn.close()


class AddItemPriceScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(AddItemPriceScreen, self).__init__(**kwargs)
        self.created = False

    # This function adds a keymanager object which contains creates the keypad
    def add_keypad(self):
        if not self.created:
            self.keys.keypad()
            self.add_widget(self.keys)
            self.keys.ids.searchbar.hint_text = "Enter Item Price"
            self.created = True

    # This function continues building the list that is used to store new items in inventory DB
    def store_new_item(self, text):
        self.keys.new_item.append(str(text))

        self.manager.current = 'additemquantity'

    # Checks to make sure the text input is populated
    def check_user_error(self, text):
        input = str(text)
        no_input = MessagePopup("Must a price for this item")
        if not input:
            no_input.open()
        else:
            self.store_new_item(input)


class AddItemQuantityScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(AddItemQuantityScreen, self).__init__(**kwargs)
        self.created = False

    # This function adds a KeyManager object which contains creates the keypad
    def add_keypad(self):
        if not self.created:
            self.keys.keypad()
            self.add_widget(self.keys)
            self.keys.ids.searchbar.hint_text = "Enter Item Quantity"

            self.created = True

    # This function inserts the built list (new_item) into the inventory DB
    def store_new_item(self, text):
        self.keys.new_item.append(str(text))

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()

        cur.execute(
            f"INSERT INTO inventory_db (item_name, price, quantity) VALUES ('{self.keys.new_item[0]}', {self.keys.new_item[1]}, {self.keys.new_item[2]});")
        cur.close()
        conn.close()
        self.keys.new_item.clear()
        self.manager.current = 'inventory'

    # Checks to make sure the text input is populated
    def check_user_error(self, text):
        input = str(text)
        if not input:
            no_input = MessagePopup("Must a quantity for this item")
            no_input.open()
        else:
            self.store_new_item(input)


class ReturnScreen(Screen):
    # Variable keys for KeyManager object
    def __init__(self, **kwargs):
        self.keys = KeyManager()
        super(ReturnScreen, self).__init__(**kwargs)
        self.created = False
        self.no_input_dialog = None

    # This function adds a keypad by creating a KeyManager object and calling the keypad function
    def add_keypad(self):
        if not self.created:
            self.keys.keypad()

            self.keys.ids.searchbar.hint_text = "Enter Receipt Number"

            self.add_widget(self.keys)
            self.created = True

    # This function performs input validation o receipt number of returns
    def inputvalidation(self):
        # Message for popup window
        message = "Invalid Entry, Try Again"
        try:
            if '.' in self.keys.ids.searchbar.text:
                raise ValueError
            else:
                connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
                conn = psycopg2.connect(connection_string)
                conn.set_session(autocommit=True)
                cur = conn.cursor()
                # Query returns all receipt numbers in database
                query1 = "SELECT receipt_number FROM customer_orders_db"
                cur.execute(query1)
                receipt_nums = cur.fetchall()
                foundreceipt = False
                for i in receipt_nums:
                    # Extracting contents from list of tuples of receipt numbers
                    if int(*i) == int(self.keys.ids.searchbar.text):
                        foundreceipt = True
                        break
                if not foundreceipt:
                    raise ValueError

        except ValueError as er:
            MessagePopup(message).startup()
            self.keys.delete_search()
            return
        conn.close()
        cur.close()
        self.manager.current = 'return_cart'
    ########################### RETURN SCREEN ###########################


class ReturnCartScreen(Screen):
    def __init__(self, **kwargs):
        # receipt_num is the value entered in the text field in ReturnScreen
        self.receipt_num = ""
        self.date = ""
        self.row_info = []
        self.item_index = None
        self.cost = None
        self.refund_label = None
        self.total_label = None
        super(ReturnCartScreen, self).__init__(**kwargs)

    # This function connects to customer_orders_db and displays all items in customer order
    def temp_connection(self):
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        self.receipt_num = self.manager.return_screen.keys.ids.searchbar.text

        try:
            query = "select unnest(ARRAY_AGG(DISTINCT list_of_items_bought)), unnest(ARRAY_AGG(DISTINCT quantity_of_each_item_bought)) from customer_orders_db where receipt_number = " + self.receipt_num + "group by receipt_number"
            cur.execute(query)
            inv = cur.fetchall()

            table = MDDataTable(
                check=False,
                use_pagination=False,
                rows_num=3,
                column_data=[("List of Items Bought", dp(27)),
                             ("Quantity of Each Item Bought", dp(27))
                             ],
                row_data=inv
            )
            table.bind(on_row_press=self.remove_item)
            self.add_widget(table)
            self.display_info(cur, self.receipt_num)
        except psycopg2.Error as er:
            pass
        conn.close()
        cur.close()

    # This function will display Date of purchase and total cost in right hand side of Return cart
    def display_info(self, cur, rec_num):
        query = "SELECT date_of_purchase,total_cost from customer_orders_db where receipt_number = " + rec_num + ";"
        cur.execute(query)
        res = cur.fetchall()
        self.date = str(res[0][0])
        self.cost = str(res[0][1])
        self.add_widget(MDLabel(text=("Date of Purchase: " + self.date), pos_hint={'center_x': 1.13, 'center_y': 0.95}))
        self.total_label = MDLabel(text=("Total Cost: $" + "{:.2f}".format(float(self.cost))),
                                   pos_hint={'center_x': 1.13, 'center_y': 0.85})
        self.add_widget(self.total_label)
        self.refund_label = MDLabel(text="Refund Total: $0.00", pos_hint={'center_x': 1.13, 'center_y': 0.75})
        self.add_widget(self.refund_label)
        finish_button = Button(text="Done", pos_hint={'center_x': .8, 'center_y': 0.2}, size_hint=(0.15, 0.15))
        self.add_widget(finish_button)
        finish_button.bind(on_press=self.go_menu)

    # This function switches to menu screen and reinitializes variables in ReturnAmountScreen
    def go_menu(self, obj):
        self.manager.current = 'menu'
        self.manager.return_amount_screen.prevrefund = 0
        self.manager.return_amount_screen.refund_total = 0

    # This function updates the MDDatatable with updated quantity after refund
    def remove_item(self, instance_table, instance_row):
        self.row_info = []
        start_index, end_index = instance_row.table.recycle_data[instance_row.index]["range"]
        for i in range(start_index, end_index + 1):
            self.row_info.append(instance_row.table.recycle_data[i]["text"])
        self.refund_amount()
        for i in range(len(instance_table.row_data)):
            if instance_table.row_data[i][0] == self.row_info[0]:
                self.item_index = i + 1

    # This function switches to refund amount screen to enter refund quantity
    def refund_amount(self):
        self.manager.return_amount_screen.keys.ids.searchbar.hint_text = "Enter Refund Quantity for " + \
                                                                         self.manager.return_cart_screen.row_info[0]
        self.manager.current = 'return_amount'


class ReturnAmountScreen(Screen):
    def __init__(self, **kwargs):
        self.amount = ""
        self.item = ""
        self.item_p = None
        self.keys = KeyManager()
        self.prevrefund = 0
        self.refund_total = 0
        self.created = False
        super(ReturnAmountScreen, self).__init__(**kwargs)

    # This function adds a keypad in screen to input refund amount
    def add_keypad(self):
        if not self.created:
            self.keys.keypad()
            # Modifying hint text to match item selected
            self.keys.ids.searchbar.hint_text = "Enter Refund Quantity for " + self.manager.return_cart_screen.row_info[
                0]
            self.add_widget(self.keys)
            self.created = True

    # This function updates the customer_orders_db after selecting refund amount
    def update_db(self):
        self.amount = self.keys.ids.searchbar.text
        self.item = self.manager.return_cart_screen.row_info[0]
        if not self.inputvalidation():
            return

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)

        conn.set_session(autocommit=True)
        cur = conn.cursor()
        receipt = self.manager.return_cart_screen.receipt_num
        index = self.manager.return_cart_screen.item_index
        # query to subtract amount from amount in customer order
        query = "update customer_orders_db set quantity_of_each_item_bought[" + str(
            index) + "] = quantity_of_each_item_bought[" + str(
            index) + "]- " + self.amount + " where receipt_number=" + receipt + ";"
        cur.execute(query)
        # query to add returned value to inventory
        query2 = "update inventory_db set quantity = quantity + " + self.amount + " where item_name = '" + self.item.lower() + "';"
        cur.execute(query2)

        query3 = "SELECT price from inventory_db where item_name = '" + self.item.lower() + "';"
        cur.execute(query3)
        item_price = cur.fetchall()
        self.item_p = (float(*item_price[0]))

        refund = float(self.amount) * float(self.item_p)
        self.manager.return_cart_screen.cost = round(float(self.manager.return_cart_screen.cost) - float(refund), 2)

        newtotal = self.manager.return_cart_screen.cost
        query4 = f"update customer_orders_db set total_cost = {newtotal} where receipt_number = {receipt};"
        cur.execute(query4)
        conn.close()
        cur.close()
        self.manager.current = 'return_cart'

        self.refund_total += refund
        self.manager.return_cart_screen.refund_label.text = (
                "Refund total: $" + str("{:.2f}".format(self.refund_total)))
        self.manager.return_cart_screen.total_label.text = ("Total cost: $" + str("{:.2f}".format(newtotal)))

        self.prevrefund = refund

    # This function performs input validation for return amount
    def inputvalidation(self):
        # Message for popup window
        message = "Refund quantity exceeds purchase quantity of item, Try Again"
        try:
            if '.' in self.keys.ids.searchbar.text:
                message = "Invalid entry, Try Again"
                raise ValueError
            else:
                connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
                conn = psycopg2.connect(connection_string)
                conn.set_session(autocommit=True)
                cur = conn.cursor()
                index = self.manager.return_cart_screen.item_index
                receipt = self.manager.return_cart_screen.receipt_num

                query = "SELECT quantity_of_each_item_bought[" + str(
                    index) + "] FROM customer_orders_db where receipt_number = " + str(receipt) + ";"
                cur.execute(query)
                qamount = cur.fetchall()
                if (int(*qamount[0]) - int(self.amount)) < 0:
                    raise ValueError
        except ValueError as er:
            MessagePopup(message).startup()
            self.keys.delete_search()
            return 0
        conn.close()
        cur.close()
        return 1


# Class for StatisticsScreen, formatting and buttons specified in the KV builder string
# The functions by_year, and by_month can be copied and modified to enter any other graphs we may want.
class StatisticsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__()
        box = self.ids.box
        box.add_widget(FigureCanvas(plt.gcf()))

    def last_thirty(self):
        plt.clf()
        currentTime = datetime.date.today()
        filter = currentTime - timedelta(days=30)
        # Connect to database and get customer order information from customer_orders_db        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        query = "SELECT total_cost, date_of_purchase FROM customer_orders_db"
        cur.execute(query)
        result = cur.fetchall()
        df = pd.DataFrame(result, columns=['total_cost', 'date_of_purchase'])
        df = df[df['date_of_purchase'] >= filter]
        df = (df.groupby(['date_of_purchase'])['total_cost'].apply(np.mean).reset_index())
        plt.title("Orders in the last thirty days")
        plt.ylabel("Total Cost in Dollars($)", fontsize=11)
        plt.xticks(rotation=90)
        plt.xlabel("Date of Purchase", fontsize=11)
        plt.plot(df['date_of_purchase'], df['total_cost'])
        # fig = plt.gcf()
        # fig.set_tight_layout(tight=True)
        # fig.rcParams()
        # fig.set_layout_engine(layout='tight')

        self.ids.box.add_widget(FigureCanvas(plt.gcf()))
        conn.close()
        cur.close()

    def top_sellers(self):
        plt.clf()
        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        query = "SELECT total_cost, date_of_purchase, list_of_items_bought FROM customer_orders_db"
        cur.execute(query)
        result = cur.fetchall()
        df = pd.DataFrame(result, columns=['total_cost', 'date_of_purchase', 'list_of_items_bought'])
        newSeries = df['list_of_items_bought'].explode()
        dict = newSeries.value_counts().to_dict()
        plt.plot(dict.keys(), dict.values())
        plt.xticks(rotation=90)
        plt.title("Top Sellers")
        plt.xlabel("Products", fontsize=11)
        plt.ylabel("QuantitySold", fontsize=11)
        fig = plt.gcf()
        # fig = TightLayoutEngine()
        # fig.set_tight_layout(tight=True)
        # fig.set_tight_layout(tight=True)
        # plt.autoscale(enable=False, axis='both', tight=True)
        # fig.set_layout_engine(layout='tight')
        # plt.tight_layout()
        # plt.savefig("foo")
        self.ids.box.add_widget(FigureCanvas(plt.gcf()))
        # self.ids.box.add_widget(FigureCanvas(plt.show()))

        conn.close()
        cur.close()

    def by_week(self):
        plt.clf()

        currentTime = datetime.date.today()
        filter = currentTime - timedelta(days=7)

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        query = "SELECT total_cost, date_of_purchase FROM customer_orders_db"
        cur.execute(query)
        result = cur.fetchall()
        df = pd.DataFrame(result, columns=['total_cost', 'date_of_purchase'])
        df = df[df['date_of_purchase'] >= filter]
        df = (df.groupby(['date_of_purchase'])['total_cost'].apply(np.mean).reset_index())
        # Group by movie title
        plt.title("Orders in the last seven days")
        plt.ylabel("Total Cost in Dollars($)", fontsize=11)
        plt.xticks(rotation=90)
        plt.xlabel("Date of Purchase", fontsize=11)
        plt.plot(df['date_of_purchase'], df['total_cost'])

        # fig = plt.gcf()
        # fig.set_tight_layout(tight=True)
        # fig.set_layout_engine(layout='tight')
        self.ids.box.add_widget(FigureCanvas(plt.gcf()))

        conn.close()
        cur.close()

    def by_year(self):
        plt.clf()

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        query = "SELECT total_cost, date_of_purchase FROM customer_orders_db"
        cur.execute(query)
        result = cur.fetchall()
        df = pd.DataFrame(result, columns=['total_cost', 'date_of_purchase'])

        df['date_of_purchase'] = pd.DatetimeIndex(df['date_of_purchase']).year
        df = (df.groupby(['date_of_purchase'])['total_cost'].apply(np.mean).reset_index())
        plt.title("Timeline of Sales")
        plt.ylabel("Average Order Price in Dollars($)", fontsize=11)
        plt.xlabel("Date of Purchase", horizontalalignment='right', position=(1, 30), fontsize=11)
        plt.plot(df['date_of_purchase'], df['total_cost'])

        # fig = plt.gcf()
        # fig.set_tight_layout(tight=True)
        # fig.set_layout_engine(layout='tight')
        self.ids.box.add_widget(FigureCanvas(plt.gcf()))

        conn.close()
        cur.close()

    def by_month(self):
        plt.clf()

        connection_string = "postgres://zxtsblsy:9ycG2N28tOZoH-uiLpZTRBbZ_HqKueaX@heffalump.db.elephantsql.com/zxtsblsy"
        conn = psycopg2.connect(connection_string)
        conn.set_session(autocommit=True)
        cur = conn.cursor()
        query = "SELECT total_cost, date_of_purchase FROM customer_orders_db"
        cur.execute(query)
        result = cur.fetchall()
        df = pd.DataFrame(result, columns=['total_cost', 'date_of_purchase'])

        df['date_of_purchase'] = pd.DatetimeIndex(df['date_of_purchase']).month
        df = (df.groupby(['date_of_purchase'])['total_cost'].apply(np.mean).reset_index())
        plt.title("Monthly Trends")
        plt.ylabel("Average Order Amount in Dollars($)", fontsize=11)
        plt.xlabel("Months", fontsize=11)
        plt.plot(df['date_of_purchase'], df['total_cost'])
        # fig = plt.gcf()
        # fig.set_tight_layout(tight=True)
        # fig.set_layout_engine(layout='tight')
        self.ids.box.add_widget(FigureCanvas(plt.gcf()))

        conn.close()
        cur.close()

    ########################### STATISTICS SCREEN ###########################


class CustomizationScreen(Screen):
    pass
    ########################### CUSTOMIZATION SCREEN ###########################


class BackgroundColorScreen(Screen):
    def __init__(self, **kwargs):
        super(BackgroundColorScreen, self).__init__(**kwargs)
        self.instVal = []
        self.background_color_values = []

    def on_color(self, instance, value):
        self.instVal = instance.color

    def on_press(self):
        value = self.instVal
        self.background_color_values = [str(value[0]), str(value[1]), str(value[2]), str(value[3])]
        with open("background_color.txt", "w") as c:
            c.write(", ".join(self.background_color_values))


class ButtonColorScreen(Screen):
    def __init__(self, **kwargs):
        super(ButtonColorScreen, self).__init__(**kwargs)
        self.instVal = []
        self.button_color_values = []

    def on_color(self, instance, value):
        self.instVal = instance.color

    def on_press(self):
        value = self.instVal
        self.button_color_values = [str(value[0]), str(value[1]), str(value[2]), str(value[3])]
        with open("button_color.txt", "w") as c:
            c.write(", ".join(self.button_color_values))


# This class creates a generic pop up window
class MessagePopup(MDDialog):
    # Constructor accepts 1 parameter for message in popup body
    def __init__(self, msg, **kwargs):
        self.no_input_dialog = None
        self.title = ""
        self.type = "custom"
        self.text = msg
        self.buttons = [MDFlatButton(text="CLOSE", text_color="#000000", on_release=self.close_error_popup)]
        super().__init__(**kwargs)
        # receipt_num is the value entered in the text field in ReturnScreen

    def startup(self):
        self.open()
        # self.keys.delete_search()

    def close_error_popup(self, inst):
        self.dismiss()


# This class is for the ScreenManager which contains all screens used in the app
class Manager(ScreenManager):
    menu_screen = ObjectProperty(None)
    checkout_screen = ObjectProperty(None)
    checkout_table_screen = ObjectProperty(None)
    checkout_keypad_screen = ObjectProperty(None)
    checkout_cart_screen = ObjectProperty(None)
    send_receipt_screen = ObjectProperty(None)
    camera_screen = ObjectProperty(None)
    inventory_screen = ObjectProperty(None)
    update_inv = ObjectProperty(None)
    update_inv_price = ObjectProperty(None)
    add_item_name_screen = ObjectProperty(None)
    remove_item_screen = ObjectProperty(None)
    add_item_price_screen = ObjectProperty(None)
    add_item_quantity_screen = ObjectProperty(None)
    return_screen = ObjectProperty(None)
    return_cart_screen = ObjectProperty(None)
    return_amount_screen = ObjectProperty(None)
    statistics_screen = ObjectProperty(None)
    customization_screen = ObjectProperty(None)
    background_color_screen = ObjectProperty(None)
    button_color_screen = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(Manager, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.android_back_click)

    def android_back_click(self, window, key, scancode, codepoint, modifier):
        transition = {"checkout": 'menu', "statistics": "menu", "inventory": "menu", "return": "menu",
                      "customization": "menu",
                      "background_color": "customization", "button_color": "customization",
                      "send_receipt": "checkout", "camera": "checkout", "checkout_cart": "checkout",
                      "checkout_keypad": "checkout", "checkout_table": "checkout",
                      "return_cart": "return", "return_amount": "return_cart",
                      "update_inv_qty": "inventory", "updateInvPrice": "update_inv_qty", "additemname": "inventory",
                      "additemprice": "additemname", "additemquantity": "additemprice"}
        if key == 27:
            # menu
            if self.current == 'menu':
                sys.exit(0)
            else:
                self.current = transition[self.current]
                return True
    ########################### MANAGER ###########################


# Class definition for MDApp in which builder string is loaded and screen manager is called
class POS(MDApp):
    def build(self):
        self.kv = Builder.load_string(screen_helper)
        m = Manager()
        return m

    def change_background_color(self):
        with open("background_color.txt") as c:
            contents = c.read()
        r_color = contents.split(',')[0]
        g_color = contents.split(',')[1]
        b_color = contents.split(',')[2]
        a_color = contents.split(',')[3]

        rgba_background = (float(r_color), float(g_color), float(b_color), float(a_color))
        c.close()
        return rgba_background

    def change_button_color(self):
        with open("button_color.txt") as c:
            contents = c.read()
        r_color = contents.split(',')[0]
        g_color = contents.split(',')[1]
        b_color = contents.split(',')[2]
        a_color = contents.split(',')[3]

        rgba_button = (float(r_color), float(g_color), float(b_color), float(a_color))
        c.close()
        return rgba_button
    ########################### POS ###########################


POS().run()
