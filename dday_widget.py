import tkinter as tk
from datetime import datetime, date
import json
import os
import sys
from tkinter import messagebox, scrolledtext
import pystray
from PIL import Image, ImageDraw
import threading
import random
import math
import time
import uuid
import requests
from threading import Thread
import queue
import winsound
import win32gui
import win32api
import win32con

class DdayWidget:
    def __init__(self):
        # 저장 경로 설정
        self.app_data_dir = r'C:\DdayWidget'
        self.ensure_app_directory()
        
        self.root = tk.Tk()
        self.root.title("D-DAY Counter")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.7)
        self.notification_active = False
        self.gradient_step = 0
        self.gradient_direction = 1
        self.current_bg_color = '#2d2d3d'

        self.firebase_url = "YOUR_FIREBASE_REALTIME_DATABASE_URL"
        
        # 파일 경로를 C:\안녕지쓰 폴더로 변경
        self.config_file = os.path.join(self.app_data_dir, 'dday_config.json')
        self.read_messages_file = os.path.join(self.app_data_dir, 'read_messages.json')
        self.user_info_file = os.path.join(self.app_data_dir, 'user_info.json')
        
        self.start_date = date(2024, 1, 1)
        
        self.message_queue = queue.Queue()
        
        self.read_message_ids = set()
        self.load_read_messages()
        
        if not self.authenticate_user():
            self.root.destroy()
            return
            
        self.load_position()
        
        self.messages = []
        self.last_message_id = None
        
        self.heart_scale = 1.0
        self.heart_growing = True
        self.sparkle_positions = []
        self.color_index = 0
        self.gradient_colors = ['#ff6b6b', '#ff8e8e', '#ffb3b3', '#ff8e8e', '#ff6b6b']
        
        self.processing_double_click = False
        
        self.chat_expanded = False
        
        self.setup_ui()
        self.current_bg_color = self.get_desktop_color_at_position()
        self.set_background_color(self.current_bg_color)
        self.update_dday()
        self.setup_drag()
        self.setup_tray()
        
        self.animate_sparkles()
        self.animate_heart()
        
        self.start_firebase_listener()
        
        self.process_message_queue()
        
        self.root.after(100, self.update_background_color)
    
    def ensure_app_directory(self):
        """C:\안녕지쓰 폴더가 없으면 생성"""
        try:
            if not os.path.exists(self.app_data_dir):
                os.makedirs(self.app_data_dir)
        except Exception as e:
            messagebox.showerror("Folder Creation Error", f"Cannot create C:\\DdayWidget folder:\n{str(e)}")
            sys.exit(1)
        
    def get_desktop_color_at_position(self):
        try:
            center_x = self.root.winfo_x() + 75
            center_y = self.root.winfo_y() + 50
            
            offsets = [(-5, -5), (5, -5), (-5, 5), (5, 5)]
            
            hwnd = win32gui.GetDesktopWindow()
            hdc = win32gui.GetWindowDC(hwnd)
            
            colors = []
            for offset_x, offset_y in offsets:
                x = center_x + offset_x
                y = center_y + offset_y
                
                color = win32gui.GetPixel(hdc, x, y)
                
                r = color & 0xff
                g = (color >> 8) & 0xff
                b = (color >> 16) & 0xff
                
                colors.append((r, g, b))
            
            win32gui.ReleaseDC(hwnd, hdc)
            
            avg_r = sum(c[0] for c in colors) // 4
            avg_g = sum(c[1] for c in colors) // 4
            avg_b = sum(c[2] for c in colors) // 4
            
            return f"#{avg_r:02x}{avg_g:02x}{avg_b:02x}"
        except:
            return '#2d2d3d'
    
    def update_background_color(self):
        if not self.chat_expanded and not self.notification_active:
            color = self.get_desktop_color_at_position()
            self.current_bg_color = color
            self.set_background_color(color)
        
        self.root.after(40, self.update_background_color)
    
    def get_complementary_color(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        comp_r = 255 - r
        comp_g = 255 - g
        comp_b = 255 - b
        
        return f"#{comp_r:02x}{comp_g:02x}{comp_b:02x}"
    
    def set_background_color(self, color):
        self.root.configure(bg=color)
        self.main_frame.configure(bg=color)
        self.dday_frame.configure(bg=color)
        self.sparkle_frame.configure(bg=color)
        self.content_frame.configure(bg=color)
        self.label_title.configure(bg=color)
        self.inner_frame.configure(bg=color)
        
        complementary_color = self.get_complementary_color(color)
        self.label_days.configure(bg=color, fg=complementary_color)
        
        self.heart_canvas.configure(bg=color)
        
    def authenticate_user(self):
        SECRET_PASSWORD = "1234"
        
        if os.path.exists(self.user_info_file):
            try:
                with open(self.user_info_file, 'r', encoding='utf-8') as f:
                    user_info = json.load(f)
                    self.user_name = user_info['name']
                    self.user_id = user_info['id']
                    return True
            except:
                pass
        
        auth_window = tk.Toplevel(self.root)
        auth_window.title("User Authentication")
        auth_window.geometry("300x200")
        auth_window.attributes('-topmost', True)
        
        auth_window.update_idletasks()
        x = (auth_window.winfo_screenwidth() // 2) - (300 // 2)
        y = (auth_window.winfo_screenheight() // 2) - (200 // 2)
        auth_window.geometry(f"300x200+{x}+{y}")
        
        authenticated = False
        
        def verify():
            nonlocal authenticated
            password = password_entry.get()
            name = name_var.get()
            
            if password != SECRET_PASSWORD:
                messagebox.showerror("Authentication Failed", "Invalid password.")
                return
            
            if not name or (name != "User1" and name != "User2"):
                messagebox.showerror("Name Verification", "Please select a valid user.")
                return
            
            user_info = {
                'name': name,
                'id': str(uuid.uuid4()),
                'created': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            with open(self.user_info_file, 'w', encoding='utf-8') as f:
                json.dump(user_info, f, ensure_ascii=False, indent=2)
            
            self.user_name = name
            self.user_id = user_info['id']
            authenticated = True
            auth_window.destroy()
        
        tk.Label(auth_window, text="Welcome", font=('Arial', 14, 'bold')).pack(pady=10)
        
        tk.Label(auth_window, text="Password:", font=('Arial', 10)).pack()
        password_entry = tk.Entry(auth_window, show="*", font=('Arial', 10))
        password_entry.pack(pady=5)
        
        tk.Label(auth_window, text="Select User:", font=('Arial', 10)).pack(pady=(10, 5))
        
        name_var = tk.StringVar()
        tk.Radiobutton(auth_window, text="User2", variable=name_var, value="User2", 
                      font=('Arial', 10)).pack()
        tk.Radiobutton(auth_window, text="User1", variable=name_var, value="User1", 
                      font=('Arial', 10)).pack()
        
        tk.Button(auth_window, text="확인", command=verify, bg='#ff6b6b', fg='white',
                 font=('Arial', 10, 'bold')).pack(pady=10)
        
        password_entry.bind('<Return>', lambda e: verify())
        
        self.root.wait_window(auth_window)
        
        return authenticated
        
    def load_position(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.x = config.get('x', 100)
                    self.y = config.get('y', 100)
            except:
                self.x = 100
                self.y = 100
        else:
            self.x = 100
            self.y = 100
    
    def load_read_messages(self):
        if os.path.exists(self.read_messages_file):
            try:
                with open(self.read_messages_file, 'r') as f:
                    data = json.load(f)
                    user_key = f"{self.user_name}_{self.user_id}" if hasattr(self, 'user_name') else ""
                    if user_key:
                        self.read_message_ids = set(data.get(user_key, []))
            except:
                self.read_message_ids = set()
        else:
            self.read_message_ids = set()
    
    def save_read_messages(self):
        try:
            if os.path.exists(self.read_messages_file):
                with open(self.read_messages_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            user_key = f"{self.user_name}_{self.user_id}"
            data[user_key] = list(self.read_message_ids)
            
            with open(self.read_messages_file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def save_position(self):
        config = {
            'x': self.x,
            'y': self.y
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except:
            pass
    
    def start_firebase_listener(self):
        def listen():
            first_load = True
            
            while True:
                try:
                    response = requests.get(f"{self.firebase_url}/messages.json")
                    if response.status_code == 200:
                        data = response.json()
                        if data:
                            messages = []
                            for key, value in data.items():
                                value['firebase_id'] = key
                                messages.append(value)
                            
                            messages.sort(key=lambda x: x.get('timestamp', ''))
                            
                            if len(messages) > 5:
                                messages = messages[-5:]
                            
                            if messages and (not self.messages or messages != self.messages):
                                old_messages = self.messages.copy()
                                self.messages = messages
                                
                                if first_load:
                                    has_unread_other_message = False
                                    for msg in messages:
                                        msg_id = msg.get('firebase_id')
                                        
                                        is_mine = False
                                        msg_user = msg.get('user', '').strip()
                                        msg_user_id = msg.get('user_id', '').strip() if msg.get('user_id') else ''
                                        
                                        if msg_user_id and msg_user_id == self.user_id:
                                            is_mine = True
                                        elif msg_user.lower() == self.user_name.lower():
                                            is_mine = True
                                        
                                        if not is_mine and msg_id not in self.read_message_ids:
                                            has_unread_other_message = True
                                            break
                                    
                                    if has_unread_other_message:
                                        self.message_queue.put(('new_other_message', None))
                                    else:
                                        self.message_queue.put(('update', None))
                                    first_load = False
                                else:
                                    new_other_message = False
                                    for msg in messages:
                                        msg_id = msg.get('firebase_id')
                                        
                                        is_mine = False
                                        msg_user = msg.get('user', '').strip()
                                        msg_user_id = msg.get('user_id', '').strip() if msg.get('user_id') else ''
                                        
                                        if msg_user_id and msg_user_id == self.user_id:
                                            is_mine = True
                                        elif msg_user.lower() == self.user_name.lower():
                                            is_mine = True
                                        
                                        if (msg_id not in [m.get('firebase_id') for m in old_messages] and 
                                            not is_mine and 
                                            msg_id not in self.read_message_ids):
                                            new_other_message = True
                                            break
                                    
                                    if new_other_message:
                                        self.message_queue.put(('new_other_message', None))
                                    else:
                                        self.message_queue.put(('update', None))
                        else:
                            self.messages = []
                            self.message_queue.put(('update', None))
                            first_load = False
                except Exception as e:
                    print(f"Firebase 오류: {e}")
                
                time.sleep(2)
        
        listener_thread = Thread(target=listen, daemon=True)
        listener_thread.start()
    
    def process_message_queue(self):
        try:
            while True:
                action, data = self.message_queue.get_nowait()
                if action == 'new_other_message':
                    if not self.chat_expanded:
                        self.toggle_btn.config(text="💬 Chat ✨")
                        self.start_notification_gradient()
                    self.play_notification_sound()
                    self.update_message_display()
                elif action == 'update':
                    self.update_message_display()
        except queue.Empty:
            pass
        
        self.root.after(100, self.process_message_queue)

    def play_notification_sound(self):
        try:
            def play_beeps():
                for i in range(3):
                    winsound.Beep(1000 + i * 300, 50)
                    time.sleep(0.05)
            
            Thread(target=play_beeps, daemon=True).start()
        except:
            self.root.bell()

    def start_notification_gradient(self):
        if not self.notification_active:
            self.notification_active = True
            self.gradient_step = 0
            self.gradient_direction = 1
            self.animate_notification_gradient()

    def stop_notification_gradient(self):
        self.notification_active = False
        if not self.chat_expanded:
            self.current_bg_color = self.get_desktop_color_at_position()
        self.set_background_color(self.current_bg_color)

    def animate_notification_gradient(self):
        if not self.notification_active:
            return
            
        base_color = 0x2d2d3d
        accent_color = 0xff6b6b
        
        progress = (self.gradient_step / 30.0)
        if self.gradient_direction == -1:
            progress = 1.0 - progress
            
        r1, g1, b1 = (base_color >> 16) & 0xff, (base_color >> 8) & 0xff, base_color & 0xff
        r2, g2, b2 = (accent_color >> 16) & 0xff, (accent_color >> 8) & 0xff, accent_color & 0xff
        
        r = int(r1 + (r2 - r1) * progress * 0.3)
        g = int(g1 + (g2 - g1) * progress * 0.3)
        b = int(b1 + (b2 - b1) * progress * 0.3)
        
        color = f"#{r:02x}{g:02x}{b:02x}"
        
        self.root.configure(bg=color)
        self.main_frame.configure(bg=color)
        self.dday_frame.configure(bg=color)
        self.sparkle_frame.configure(bg=color)
        self.content_frame.configure(bg=color)
        self.label_title.configure(bg=color)
        self.inner_frame.configure(bg=color)
        self.heart_canvas.configure(bg=color)
        
        complementary_color = self.get_complementary_color(color)
        self.label_days.configure(bg=color, fg=complementary_color)
        
        self.gradient_step += self.gradient_direction
        
        if self.gradient_step >= 30:
            self.gradient_direction = -1
        elif self.gradient_step <= 0:
            self.gradient_direction = 1
        
        self.root.after(50, self.animate_notification_gradient)

    def send_message_to_firebase(self, message):
        try:
            response = requests.post(
                f"{self.firebase_url}/messages.json",
                json=message
            )
            if response.status_code == 200:
                self.messages.append(message)
                
                self.cleanup_old_messages()
                
                self.update_message_display()
                return True
        except Exception as e:
            print(f"메시지 전송 오류: {e}")
            messagebox.showerror("Send Error", "Failed to send message. Please check your internet connection.")
        return False

    def cleanup_old_messages(self):
        try:
            if len(self.messages) > 5:
                messages_to_delete = self.messages[:-5]
                
                for msg in messages_to_delete:
                    firebase_id = msg.get('firebase_id')
                    if firebase_id:
                        delete_response = requests.delete(f"{self.firebase_url}/messages/{firebase_id}.json")
                        if delete_response.status_code == 200:
                            print(f"메시지 삭제됨: {firebase_id}")
                
                self.messages = self.messages[-5:]
                
        except Exception as e:
            print(f"메시지 정리 오류: {e}")    

    def setup_ui(self):
        self.root.geometry(f"150x100+{self.x}+{self.y}")
        self.root.configure(bg=self.current_bg_color)
        
        self.main_frame = tk.Frame(self.root, bg=self.current_bg_color)
        self.main_frame.pack(fill='both', expand=True)
        
        self.dday_frame = tk.Frame(self.main_frame, bg=self.current_bg_color, height=65)
        self.dday_frame.pack(fill='x')
        self.dday_frame.pack_propagate(False)
        
        self.sparkle_frame = tk.Frame(self.dday_frame, bg=self.current_bg_color)
        self.sparkle_frame.place(relwidth=1, relheight=1)
        
        self.content_frame = tk.Frame(self.dday_frame, bg=self.current_bg_color)
        self.content_frame.pack(expand=True)
        
        self.label_title = tk.Label(self.content_frame, text="D-Day Counter", font=('Arial', 9), 
                                   fg='#ffb3b3', bg=self.current_bg_color)
        self.label_title.pack()
        
        self.inner_frame = tk.Frame(self.content_frame, bg=self.current_bg_color)
        self.inner_frame.pack()
        
        self.label_days = tk.Label(self.inner_frame, font=('Arial', 24, 'bold'), 
                                  fg='white', bg=self.current_bg_color)
        self.label_days.pack(side='left', padx=(10, 0))
        
        self.heart_canvas = tk.Canvas(self.inner_frame, width=90, height=50, 
                                     bg=self.current_bg_color, highlightthickness=0)
        self.heart_canvas.pack(side='left', padx=(10, 0))
        
        self.toggle_btn = tk.Button(self.main_frame, text="💬 Chat", font=('Arial', 10, 'bold'),
                                   bg='#ff6b6b', fg='white', bd=0, cursor='hand2',
                                   command=self.toggle_chat, padx=10, pady=3)
        self.toggle_btn.pack(pady=5)
        
        self.chat_frame = tk.Frame(self.main_frame, bg='#3d3d4d')
        
        self.msg_display_frame = tk.Frame(self.chat_frame, bg='#3d3d4d')
        self.msg_display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.recent_msg_labels = []
        
        self.input_frame = tk.Frame(self.chat_frame, bg='#3d3d4d')
        self.input_frame.pack(fill='x', padx=5, pady=(0, 5))
        
        self.msg_entry = tk.Entry(self.input_frame, font=('Arial', 10),
                                 bg='#2d2d3d', fg='white', insertbackground='white')
        self.msg_entry.pack(side='left', fill='x', expand=True)
        self.msg_entry.bind('<Return>', self.send_message)
        
        self.send_btn = tk.Button(self.input_frame, text="❤️", font=('Arial', 12),
                                 bg='#ff6b6b', fg='white', bd=0, cursor='hand2',
                                 command=self.send_message)
        self.send_btn.pack(side='right', padx=(5, 0))
        
        self.menu = tk.Menu(self.root, tearoff=0)
        self.menu.add_command(label="About", command=self.quit_app)
        self.menu.add_separator()
        self.menu.add_command(label="Exit", command=self.quit_app)
        
        self.bind_events()
        
    def toggle_chat(self):
        if self.chat_expanded:
            self.chat_frame.pack_forget()
            self.root.geometry(f"150x100+{self.x}+{self.y}")
            self.toggle_btn.config(text="💬 Chat")
            self.chat_expanded = False
            self.current_bg_color = self.get_desktop_color_at_position()
            self.set_background_color(self.current_bg_color)
        else:
            self.chat_frame.pack(fill='both', expand=True)
            self.root.geometry(f"300x500+{self.x}+{self.y}")
            self.toggle_btn.config(text="🔼 Close")
            self.chat_expanded = True
            self.update_message_display()
            self.msg_entry.focus_set()
            
            for msg in self.messages:
                msg_id = msg.get('firebase_id')
                if msg_id:
                    self.read_message_ids.add(msg_id)
            
            self.save_read_messages()
            
            self.stop_notification_gradient()
    
    def send_message(self, event=None):
        msg_text = self.msg_entry.get().strip()
        if msg_text:
            message = {
                'user': self.user_name,
                'user_id': self.user_id,
                'text': msg_text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if self.send_message_to_firebase(message):
                self.msg_entry.delete(0, tk.END)
                self.create_message_heart_effect()
    
    def update_message_display(self):
        for label in self.recent_msg_labels:
            label.destroy()
        self.recent_msg_labels.clear()
        
        display_messages = self.messages[-5:] if len(self.messages) > 5 else self.messages
        
        for msg in display_messages:
            msg_frame = tk.Frame(self.msg_display_frame, bg='#3d3d4d')
            msg_frame.pack(fill='x', pady=2)
            
            msg_user = msg.get('user', '').strip()
            msg_user_id = msg.get('user_id', '').strip() if msg.get('user_id') else ''
            
            is_mine = False
            
            if msg_user_id and msg_user_id == self.user_id:
                is_mine = True
            elif msg_user.lower() == self.user_name.lower():
                is_mine = True
            
            if is_mine:
                inner_frame = tk.Frame(msg_frame, bg='#ff6b6b', relief='solid', bd=1)
                inner_frame.pack(side='right', padx=(30, 0))
                text_color = 'white'
                name_text = "Me"
            else:
                inner_frame = tk.Frame(msg_frame, bg='#4d4d5d', relief='solid', bd=1)
                inner_frame.pack(side='left', padx=(0, 30))
                text_color = '#ffb3b3'
                partner_name = msg.get('user', '❤️')
                if partner_name == "User1":
                    name_text = "💙 User1"
                elif partner_name == "User2":
                    name_text = "💕 User2"
                else:
                    name_text = "❤️"
            
            info_frame = tk.Frame(inner_frame, bg=inner_frame['bg'])
            info_frame.pack(fill='x', padx=5, pady=(2, 0))
            
            name_label = tk.Label(info_frame, text=name_text, font=('Arial', 8),
                                 fg=text_color, bg=inner_frame['bg'])
            name_label.pack(side='left')
            
            try:
                time_text = datetime.strptime(msg['timestamp'], '%Y-%m-%d %H:%M:%S').strftime('%H:%M')
            except:
                time_text = "00:00"
                
            time_label = tk.Label(info_frame, text=time_text, font=('Arial', 7),
                                 fg=text_color, bg=inner_frame['bg'])
            time_label.pack(side='right')
            
            msg_label = tk.Label(inner_frame, text=msg['text'], font=('Arial', 9),
                               fg=text_color, bg=inner_frame['bg'], wraplength=130,
                               justify='left' if not is_mine else 'right')
            msg_label.pack(padx=5, pady=(0, 2))
            
            self.recent_msg_labels.append(msg_frame)
    
    def create_message_heart_effect(self):
        for _ in range(3):
            x = random.randint(0, 300)
            y = random.randint(0, 60)
            heart = tk.Label(self.sparkle_frame, text='❤️', font=('Arial', 20),
                           fg='#ff1744', bg=self.current_bg_color)
            heart.place(x=x, y=y)
            
            def animate_heart(h=heart, start_y=y, start_x=x):
                def update(i):
                    if i < 30:
                        new_y = start_y - i * 2
                        new_x = start_x + int(5 * math.sin(i * 0.5))
                        h.place(x=new_x, y=new_y)
                        
                        current_bg = self.sparkle_frame.cget('bg')
                        h.config(bg=current_bg)
                        
                        alpha = 1.0 - (i / 30.0)
                        new_size = int(20 - i // 3)
                        if new_size > 8:
                            h.config(font=('Arial', new_size))
                        
                        self.root.after(40, lambda: update(i + 1))
                    else:
                        h.destroy()
                update(0)
            
            self.root.after(random.randint(0, 300), animate_heart)
    
    def bind_events(self):
        widgets = [self.root, self.main_frame, self.dday_frame, self.sparkle_frame, 
                  self.content_frame, self.label_title, self.inner_frame, 
                  self.label_days, self.heart_canvas]
        
        for widget in widgets:
            widget.bind("<Button-3>", self.show_menu)
            widget.bind("<Double-Button-1>", self.on_double_click)
            widget.bind("<Button-1>", self.start_drag)
            widget.bind("<B1-Motion>", self.drag)
            widget.bind("<ButtonRelease-1>", self.stop_drag)
        
    def setup_drag(self):
        pass
        
    def start_drag(self, event):
        self.drag_x = event.x_root - self.root.winfo_x()
        self.drag_y = event.y_root - self.root.winfo_y()
        
    def drag(self, event):
        x = event.x_root - self.drag_x
        y = event.y_root - self.drag_y
        self.root.geometry(f"+{x}+{y}")
        
    def stop_drag(self, event):
        self.x = self.root.winfo_x()
        self.y = self.root.winfo_y()
        self.save_position()
        
    def show_menu(self, event):
        self.menu.post(event.x_root, event.y_root)
    
    def on_double_click(self, event):
        if self.processing_double_click:
            return
            
        self.processing_double_click = True
        result = messagebox.askyesno("Exit Application", "Are you sure you want to exit?", 
                                   icon='question')
        if result:
            self.quit_app()
        self.processing_double_click = False
        return "break"
        
    def update_dday(self):
        today = date.today()
        days = (today - self.start_date).days + 1
        self.label_days.config(text=f"Day {days}")
        
        if days % 100 == 0:
            self.label_title.config(text=f"🎉 Milestone!")
            self.create_celebration_effect()
        else:
            self.label_title.config(text="D-Day Counter")
            
        self.root.after(60000, self.update_dday)
    
    def create_celebration_effect(self):
        for _ in range(10):
            x = random.randint(10, 140)
            y = random.randint(10, 55)
            emoji = random.choice(['🎉', '🎊', '✨', '🌟', '💕'])
            current_bg = self.sparkle_frame.cget('bg')
            celebration = tk.Label(self.sparkle_frame, text=emoji, 
                                 font=('Arial', random.randint(12, 20)),
                                 fg='gold', bg=current_bg)
            celebration.place(x=x, y=y)
            
            def remove_celebration(c=celebration):
                self.root.after(random.randint(1000, 3000), c.destroy)
            
            remove_celebration()
    
    def draw_heart(self, size, color):
        self.heart_canvas.delete("heart")
        
        cx, cy = 25, 25
        
        points = []
        for angle in range(0, 360, 5):
            rad = math.radians(angle)
            
            x = 16 * (math.sin(rad) ** 3)
            y = -(13 * math.cos(rad) - 5 * math.cos(2*rad) - 2 * math.cos(3*rad) - math.cos(4*rad))
            
            x = cx + (x * size * 0.7)
            y = cy + (y * size * 0.7)
            
            points.append(x)
            points.append(y)
        
        if len(points) > 6:
            self.heart_canvas.create_polygon(points, fill=color, outline='', 
                                           tags="heart", smooth=True)
    
    def animate_heart(self):
        if self.heart_growing:
            self.heart_scale += 0.02
            if self.heart_scale >= 1.2:
                self.heart_growing = False
        else:
            self.heart_scale -= 0.02
            if self.heart_scale <= 0.8:
                self.heart_growing = True
        
        self.color_index = (self.color_index + 1) % len(self.gradient_colors)
        color = self.gradient_colors[self.color_index]
        
        self.draw_heart(self.heart_scale * 1.0, color)
        
        self.root.after(50, self.animate_heart)
    
    def create_sparkle(self, x, y, parent):
        colors = ['#ffffff', '#ffcccc', '#ffeeee', '#ffdddd', '#ffd4d4']
        color = random.choice(colors)
        size = random.randint(8, 14)
        emoji = random.choice(['✨', '⭐', '💫', '✦', '✧'])
        
        current_bg = parent.cget('bg')
        sparkle = tk.Label(parent, text=emoji, font=('Arial', size), 
                          fg=color, bg=current_bg)
        sparkle.place(x=x, y=y)
        
        alpha = 1.0
        
        def fade_sparkle():
            nonlocal alpha
            try:
                if alpha > 0:
                    alpha -= 0.1
                    new_size = int(size * alpha)
                    if new_size > 0:
                        sparkle.config(font=('Arial', new_size))
                    self.root.after(100, fade_sparkle)
                else:
                    sparkle.destroy()
            except:
                pass
        
        self.root.after(random.randint(800, 2000), fade_sparkle)
    
    def animate_sparkles(self):
        if random.random() < 0.5:
            x = random.randint(0, 300)
            y = random.randint(0, 60)
            self.create_sparkle(x, y, self.sparkle_frame)
        
        self.root.after(3000, self.animate_sparkles)
                
    def create_tray_icon(self):
        image = Image.new('RGB', (64, 64), color='#2d2d3d')
        draw = ImageDraw.Draw(image)
        draw.ellipse([16, 20, 32, 36], fill='#ff6b6b')
        draw.ellipse([32, 20, 48, 36], fill='#ff6b6b')
        draw.polygon([(32, 32), (16, 40), (32, 52), (48, 40)], fill='#ff6b6b')
        return image
        
    def setup_tray(self):
        self.icon = pystray.Icon("dday")
        self.icon.icon = self.create_tray_icon()
        self.icon.menu = pystray.Menu(
            pystray.MenuItem("Show", self.show_window),
            pystray.MenuItem("Exit", self.quit_app)
        )
        
        threading.Thread(target=self.icon.run, daemon=True).start()
        
    def hide_window(self):
        self.root.withdraw()
        
    def show_window(self):
        self.root.deiconify()
        
    def quit_app(self):
        self.save_read_messages()
        try:
            self.icon.stop()
        except:
            pass
        self.root.quit()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    try:
        app = DdayWidget()
        app.run()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while running the program:\n{str(e)}")