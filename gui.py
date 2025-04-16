import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import threading
import queue
import pyautogui

# Import các module điều khiển
import hand
from hand_gesture import HandGesture
from hidden_window import WindowControl
from scroll import AutoScroll
from shutdown import Shutdown
from tab_window import TabWindow
from volume import Volume
from voiceai import VoiceAI

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Cấu hình cửa sổ
        self.title("Cài Đặt")
        self.geometry("400x250")
        self.configure(bg="#f8f9fa")
        
        # Làm cho cửa sổ không thể resize
        self.resizable(False, False)
        
        # Tạo style
        self.style = ttk.Style()
        
        # Cấu hình style cho nút Lưu
        self.style.configure("Save.TButton",
                           background="#0d6efd",
                           foreground="white",
                           padding=10,
                           font=("Segoe UI", 10, "bold"))
        self.style.map("Save.TButton",
                      background=[("active", "#0b5ed7")])
                           
        # Frame chính
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo các biến cho các tùy chọn
        self.startup_var = tk.BooleanVar(value=False)
        self.voice_only_var = tk.BooleanVar(value=False)
        self.gesture_only_var = tk.BooleanVar(value=False)
        
        # Tạo các checkbox
        startup_check = ttk.Checkbutton(main_frame,
                                      text="Khởi động cùng Windows",
                                      variable=self.startup_var,
                                      style="Settings.TCheckbutton")
        startup_check.pack(anchor=tk.W, pady=10)
        
        voice_only_check = ttk.Checkbutton(main_frame,
                                         text="Chỉ sử dụng giọng nói",
                                         variable=self.voice_only_var,
                                         style="Settings.TCheckbutton")
        voice_only_check.pack(anchor=tk.W, pady=10)
        
        gesture_only_check = ttk.Checkbutton(main_frame,
                                           text="Chỉ sử dụng cử chỉ",
                                           variable=self.gesture_only_var,
                                           style="Settings.TCheckbutton")
        gesture_only_check.pack(anchor=tk.W, pady=10)
        
        # Frame cho nút Lưu
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        # Nút lưu
        save_button = ttk.Button(button_frame,
                               text="LƯU",
                               command=self.save_settings,
                               style="Save.TButton",
                               width=15)
        save_button.pack(anchor=tk.CENTER)
        
        # Thiết lập modal window và căn giữa cửa sổ
        self.transient(parent)
        self.grab_set()
        
        # Căn giữa cửa sổ
        self.center_window()
        
    def center_window(self):
        """Căn giữa cửa sổ cài đặt so với cửa sổ chính"""
        self.update_idletasks()
        
        # Lấy kích thước và vị trí của cửa sổ chính
        parent = self.master
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()
        
        # Tính toán vị trí để căn giữa
        width = self.winfo_width()
        height = self.winfo_height()
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # Đặt vị trí cửa sổ
        self.geometry(f"{width}x{height}+{x}+{y}")
        
    def save_settings(self):
        # TODO: Lưu cài đặt
        self.destroy()

class ControlApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Khởi tạo các biến điều khiển
        self.running = False
        self.command_queue = queue.Queue()
        self.current_mode = ''  # Mode hiện tại (volume/scroll/tab/shutdown)
        
        # Khởi tạo các đối tượng điều khiển
        self.screen_width, self.screen_height = pyautogui.size()
        self.detector = hand.handDetector(detectionCon=0.7)
        self.auto_scroll = AutoScroll(self.screen_height)
        self.volume = Volume()
        self.window_control = WindowControl()
        self.hand_gesture = HandGesture()
        self.tab_window = TabWindow()
        self.shutdown = Shutdown()
        self.voice_ai = VoiceAI()
        
        # Cấu hình cửa sổ chính
        self.title("AI Control - Điều Khiển Máy Tính Bằng Tay & Giọng Nói")
        self.geometry("1200x800")
        self.configure(bg="#f8f9fa")
        
        # Tạo style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Cấu hình style
        self.style.configure("TFrame", background="#f8f9fa")
        self.style.configure("TLabel", 
                           background="#f8f9fa", 
                           foreground="#212529", 
                           font=("Segoe UI", 10))

        # Style cho nút chính (Bắt đầu/Dừng)
        self.style.configure("Primary.TButton",
                           background="#0d6efd",
                           foreground="white",
                           padding=(20, 10),
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           relief="flat")
        self.style.map("Primary.TButton",
                      background=[("active", "#0b5ed7")],
                      relief=[("pressed", "flat")],
                      borderwidth=[("pressed", 0)])

        # Style cho nút Dừng
        self.style.configure("Stop.TButton",
                           background="#dc3545",
                           foreground="white",
                           padding=(20, 10),
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           relief="flat")
        self.style.map("Stop.TButton",
                      background=[("active", "#bb2d3b")],
                      relief=[("pressed", "flat")],
                      borderwidth=[("pressed", 0)])

        # Style cho nút cài đặt
        self.style.configure("Settings.TButton",
                           background="#6c757d",
                           foreground="white",
                           padding=(20, 10),
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           relief="flat")
        self.style.map("Settings.TButton",
                      background=[("active", "#5c636a")],
                      relief=[("pressed", "flat")],
                      borderwidth=[("pressed", 0)])

        # Style cho các frame
        self.style.configure("TLabelframe", 
                           background="white", 
                           foreground="#212529",
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=1,
                           relief="solid")
        self.style.configure("TLabelframe.Label", 
                           background="white", 
                           foreground="#212529",
                           font=("Segoe UI", 10, "bold"))
        
        # Tạo các widget
        self.create_widgets()
        
        # Khởi tạo camera
        self.cap = cv2.VideoCapture(0)
        
        # Khởi tạo luồng voice
        self.voice_thread = None
        
        # Bắt đầu hiển thị camera mặc định
        self.show_default_frame()
        
    def create_widgets(self):
        # Frame chính
        main_frame = ttk.Frame(self, padding="30")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tiêu đề
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 30))
        
        title_label = ttk.Label(title_frame, 
                              text="AI CONTROL", 
                              font=("Segoe UI", 28, "bold"),
                              foreground="#0d6efd")
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Điều Khiển Máy Tính Bằng Tay & Giọng Nói AI",
                                 font=("Segoe UI", 14),
                                 foreground="#6c757d")
        subtitle_label.pack(pady=(5, 0))
        
        # Frame chứa camera và thông tin
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Cấu hình trọng số cho các cột để chia đều
        content_frame.columnconfigure(0, weight=1)  # Cột cho camera
        content_frame.columnconfigure(1, weight=1)  # Cột cho thông tin
        
        # Frame camera
        camera_frame = ttk.LabelFrame(content_frame, text="Camera & Nhận Diện Cử Chỉ", padding="15")
        camera_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Mode indicator frame
        mode_frame = tk.Frame(camera_frame, bg="#f8f9fa")
        mode_frame.pack(side=tk.BOTTOM, pady=10, anchor=tk.W)
        
        # Voice indicator
        voice_frame = tk.Frame(mode_frame, bg="#f8f9fa", padx=10, pady=5)
        voice_frame.pack(side=tk.LEFT, padx=5)
        
        self.voice_dot = tk.Canvas(voice_frame, width=14, height=14, bg="#f8f9fa", 
                                 highlightthickness=0)
        self.voice_dot.pack(side=tk.LEFT, padx=(0, 5), pady=(2, 0))
        self.voice_circle = self.voice_dot.create_oval(2, 2, 12, 12, 
                                                     fill="#f8f9fa",
                                                     outline="black",
                                                     width=1)
        
        voice_label = tk.Label(voice_frame, text="Voice", fg="black", bg="#f8f9fa", font=("Segoe UI", 10))
        voice_label.pack(side=tk.LEFT)
        
        # Gesture indicator
        gesture_frame = tk.Frame(mode_frame, bg="#f8f9fa", padx=10, pady=5)
        gesture_frame.pack(side=tk.LEFT, padx=5)
        
        self.gesture_dot = tk.Canvas(gesture_frame, width=14, height=14, bg="#f8f9fa",
                                   highlightthickness=0)
        self.gesture_dot.pack(side=tk.LEFT, padx=(0, 5), pady=(2, 0))
        self.gesture_circle = self.gesture_dot.create_oval(2, 2, 12, 12,
                                                         fill="#f8f9fa",
                                                         outline="black",
                                                         width=1)
        
        gesture_label = tk.Label(gesture_frame, text="Gesture", fg="black", bg="#f8f9fa", font=("Segoe UI", 10))
        gesture_label.pack(side=tk.LEFT)
        
        # Frame thông tin
        info_frame = ttk.LabelFrame(content_frame, text="Thông Tin & Điều Khiển", padding="25")
        info_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        # Hiển thị trạng thái
        status_frame = ttk.Frame(info_frame)
        status_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(status_frame, 
                text="Trạng thái:", 
                font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        self.status_label = ttk.Label(status_frame, 
                                    text="Đang chờ...", 
                                    font=("Segoe UI", 12))
        self.status_label.pack(side=tk.LEFT, padx=15)
        
        # Hiển thị chế độ
        mode_frame = ttk.Frame(info_frame)
        mode_frame.pack(fill=tk.X, pady=15)
        
        ttk.Label(mode_frame, 
                text="Chế độ:", 
                font=("Segoe UI", 12, "bold")).pack(side=tk.LEFT)
        self.mode_label = ttk.Label(mode_frame, 
                                  text="Đang chờ...", 
                                  font=("Segoe UI", 12))
        self.mode_label.pack(side=tk.LEFT, padx=15)
        
        # Frame chứa tất cả các nút
        buttons_container = ttk.Frame(info_frame)
        buttons_container.pack(fill=tk.X, pady=25)
        
        # Frame cho nút điều khiển (bên trái)
        control_frame = ttk.Frame(buttons_container)
        control_frame.pack(side=tk.LEFT)
        
        self.start_button = ttk.Button(control_frame, 
                                     text="BẮT ĐẦU", 
                                     command=self.start_control,
                                     style="Primary.TButton",
                                     width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, 
                                    text="DỪNG", 
                                    command=self.stop_control,
                                    style="Stop.TButton",
                                    width=15)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.state(['disabled'])

        # Frame cho nút cài đặt (bên phải)
        settings_frame = ttk.Frame(buttons_container)
        settings_frame.pack(side=tk.RIGHT)

        self.settings_button = ttk.Button(settings_frame,
                                        text="CÀI ĐẶT",
                                        command=self.open_settings,
                                        style="Settings.TButton",
                                        width=15)
        self.settings_button.pack(padx=5)
        
        # Thêm hướng dẫn sử dụng
        guide_frame = ttk.LabelFrame(info_frame, text="Hướng Dẫn Sử Dụng", padding="15")
        guide_frame.pack(fill=tk.BOTH, expand=True, pady=15)

        # Tạo canvas và scrollbar
        canvas = tk.Canvas(guide_frame, bg="#f8f9fa", highlightthickness=0)
        scrollbar = ttk.Scrollbar(guide_frame, orient="vertical", command=canvas.yview)
        
        # Frame chứa nội dung hướng dẫn
        guide_content = ttk.Frame(canvas, style="TFrame")
        
        # Cấu hình canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar và canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        guide_text = """
    ĐIỀU KHIỂN BẰNG TAY:
    1. Điều khiển âm lượng:
        • Giơ ngón cái và ngón trỏ
        • Di chuyển lên/xuống để tăng/giảm âm lượng
        • Khoảng cách giữa 2 ngón tay thể hiện mức âm lượng

    2. Cuộn trang:
        • Giơ ngón trỏ và ngón giữa
        • Di chuyển lên/xuống để cuộn trang
        • Tốc độ cuộn phụ thuộc vào khoảng cách di chuyển

    3. Điều khiển cửa sổ/tab:
        • Giơ 4 ngón tay (trừ ngón cái) để mở Alt+Tab
        • Di chuyển trái/phải để chọn cửa sổ
        • Nắm tay lại để chọn cửa sổ hiện tại
        • Giơ 3 ngón để đóng cửa sổ hiện tại
        • Giơ 4 ngón để đóng tab hiện tại

    4. Tắt máy:
        • Giơ ngón út để kích hoạt
        • Giữ 3 giây để xác nhận tắt máy

    ĐIỀU KHIỂN BẰNG GIỌNG NÓI:
    1. Mở ứng dụng:
        • "Mở [tên ứng dụng]"
        • "Khởi động [tên ứng dụng]"

    2. Tìm kiếm:
        • "Tìm kiếm [nội dung]"
        • "Search [nội dung]"

    3. Điều khiển âm lượng:
        • "Tăng âm lượng"
        • "Giảm âm lượng"
        • "Tắt tiếng"
        • "Bật tiếng"

    4. Điều khiển hệ thống:
        • "Tắt máy"
        • "Khởi động lại"
        • "Đăng xuất"
        • "Ngủ đông"

    5. Điều khiển cửa sổ:
        • "Mở cửa sổ"
        • "Chuyển cửa sổ"
        • "Đóng cửa sổ"
        • "Thu nhỏ cửa sổ"
        • "Phóng to cửa sổ"
        """
        
        # Label chứa nội dung
        self.guide_label = ttk.Label(guide_content,
                                   text=guide_text,
                                   justify=tk.LEFT,
                                   font=("Segoe UI", 11),
                                   background="#f8f9fa",
                                   wraplength=500)  # Giới hạn độ rộng văn bản
        self.guide_label.pack(anchor=tk.W, padx=10, pady=5, fill=tk.BOTH, expand=True)

        # Tạo cửa sổ trong canvas để chứa frame nội dung
        canvas.create_window((0, 0), window=guide_content, anchor=tk.NW)

        # Cập nhật kích thước scrollregion khi frame thay đổi
        def on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Đặt độ rộng của frame nội dung bằng với độ rộng của canvas
            canvas.itemconfig(canvas.find_withtag("all")[0], width=event.width)
        
        guide_content.bind("<Configure>", on_configure)
        canvas.bind("<Configure>", lambda e: guide_content.configure(width=e.width))

        # Thêm khả năng cuộn bằng chuột
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", on_mousewheel)

    def start_control(self):
        self.running = True
        self.status_label.config(text="Đang chạy")
        self.start_button.state(['disabled'])
        self.stop_button.state(['!disabled'])
        
        # Bắt đầu luồng voice
        self.voice_thread = threading.Thread(target=self.voice_control, daemon=True)
        self.voice_thread.start()
        
        # Bắt đầu xử lý camera
        self.process_camera()
        
    def stop_control(self):
        self.running = False
        self.status_label.config(text="Đã dừng")
        self.start_button.state(['!disabled'])
        self.stop_button.state(['disabled'])
        
        # Reset indicators
        self.voice_dot.itemconfig(self.voice_circle, fill="#f8f9fa")
        self.gesture_dot.itemconfig(self.gesture_circle, fill="#f8f9fa")
        self.mode_label.config(text="Đang chờ...")
        
    def voice_control(self):
        """Hàm xử lý nhận diện giọng nói trong một luồng riêng"""
        while self.running:
            try:
                command = self.voice_ai.listen()
                if command:
                    self.command_queue.put(command)
                    # Hiển thị đèn voice active
                    self.voice_dot.itemconfig(self.voice_circle, fill="#28a745")
                    self.gesture_dot.itemconfig(self.gesture_circle, fill="#f8f9fa")
                    self.after(1000, lambda: self.voice_dot.itemconfig(self.voice_circle, fill="#f8f9fa"))
            except Exception as e:
                print(f"Lỗi trong luồng giọng nói: {e}")
                
    def process_camera(self):
        """Hàm xử lý frame từ camera và nhận diện cử chỉ"""
        if not self.running:
            return
            
        ret, frame = self.cap.read()
        if ret:
            # Xử lý frame
            frame = cv2.flip(frame, 1)  # Lật ngang để dễ thao tác
            
            # Xử lý nhận diện cử chỉ
            frame = self.detector.findHands(frame)
            point_list = self.detector.findPosition(frame, draw=False)
            fingers = self.hand_gesture.detect_fingers(point_list)
            
            # Xác định chế độ điều khiển
            if fingers:
                self.gesture_dot.itemconfig(self.gesture_circle, fill="#28a745")
                self.voice_dot.itemconfig(self.voice_circle, fill="#f8f9fa")
                
                if fingers == [1, 1, 0, 0, 0]:  # Giơ ngón cái và ngón trỏ
                    if self.current_mode != 'volume':
                        self.current_mode = 'volume'
                        self.mode_label.config(text="Điều khiển âm lượng")
                    self.volume.__set__(point_list, frame, fingers)
                    self.volume.run()
                    
                elif fingers == [0, 1, 1, 0, 0]:  # Giơ ngón trỏ và ngón giữa
                    if self.current_mode != 'scroll':
                        self.current_mode = 'scroll'
                        self.mode_label.config(text="Cuộn trang")
                    if not self.auto_scroll.scroll:
                        self.auto_scroll.start(point_list)
                    self.auto_scroll.update(point_list, fingers)
                    
                elif fingers == [0, 1, 1, 1, 1]:  # Giơ 4 ngón tay
                    if self.current_mode != 'tab':
                        self.current_mode = 'tab'
                        self.mode_label.config(text="Điều khiển tab")
                    self.tab_window.__set__(point_list)
                    self.tab_window.execute(frame)
                    
                elif fingers == [0, 0, 0, 0, 1]:  # Giơ ngón út
                    if self.current_mode != 'shutdown':
                        self.current_mode = 'shutdown'
                        self.mode_label.config(text="Tắt máy")
                    self.shutdown.execute(fingers)
                
                # Kiểm tra cửa sổ
                self.window_control.minimize_window(fingers)
            else:
                # Không phát hiện cử chỉ
                self.gesture_dot.itemconfig(self.gesture_circle, fill="#f8f9fa")
            
            # Xử lý lệnh giọng nói
            try:
                while not self.command_queue.empty():
                    command = self.command_queue.get_nowait()
                    self.voice_ai.process_command(command)
                    self.status_label.config(text=f"Thực thi lệnh: {command}")
            except queue.Empty:
                pass
            
            # Hiển thị frame lên GUI
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (600, 450))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        
        # Lặp lại sau 10ms
        self.after(10, self.process_camera)
        
    def open_settings(self):
        """Mở cửa sổ cài đặt"""
        settings_window = SettingsWindow(self)
        self.wait_window(settings_window)
        
    def show_default_frame(self):
        """Hiển thị frame mặc định khi khởi động"""
        if self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame = cv2.resize(frame, (600, 450))
                img = Image.fromarray(frame)
                imgtk = ImageTk.PhotoImage(image=img)
                self.camera_label.imgtk = imgtk
                self.camera_label.configure(image=imgtk)
            
            # Lặp lại sau 10ms nếu chưa bắt đầu điều khiển
            if not self.running:
                self.after(10, self.show_default_frame)
        
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()

if __name__ == "__main__":
    app = ControlApp()
    app.mainloop() 