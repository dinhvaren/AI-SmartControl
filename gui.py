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
        self.style.configure("TButton", 
                           background="#0d6efd", 
                           foreground="white",
                           padding=12,
                           font=("Segoe UI", 10, "bold"))
        self.style.map("TButton",
                      background=[("active", "#0b5ed7")])
        self.style.configure("TLabelframe", 
                           background="white", 
                           foreground="#212529",
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=2,
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
        
        # Frame camera
        camera_frame = ttk.LabelFrame(content_frame, text="Camera & Nhận Diện Cử Chỉ", padding="15")
        camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
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
        info_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)
        
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
        
        # Nút điều khiển
        control_frame = ttk.Frame(info_frame)
        control_frame.pack(fill=tk.X, pady=25)
        
        self.start_button = ttk.Button(control_frame, 
                                     text="BẮT ĐẦU", 
                                     command=self.start_control,
                                     width=20)
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        self.stop_button = ttk.Button(control_frame, 
                                    text="DỪNG", 
                                    command=self.stop_control,
                                    width=20)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        self.stop_button.state(['disabled'])
        
        # Thêm hướng dẫn sử dụng
        guide_frame = ttk.LabelFrame(info_frame, text="Hướng Dẫn Sử Dụng", padding="15")
        guide_frame.pack(fill=tk.BOTH, expand=True, pady=15)
        
        guide_text = """
        Điều Khiển Bằng Tay:
        • Giơ ngón cái và ngón trỏ: Điều khiển âm lượng
        • Giơ ngón trỏ và ngón giữa: Cuộn trang
        • Giơ 4 ngón tay: Điều khiển tab
        • Giơ ngón út: Tắt máy

        Điều Khiển Bằng Giọng Nói:
        • "Mở ứng dụng [tên]": Mở ứng dụng
        • "Tìm kiếm [nội dung]": Tìm kiếm trên web
        • "Tắt máy": Tắt máy tính
        • "Tăng/Giảm âm lượng": Điều chỉnh âm thanh
        """
        
        self.guide_label = ttk.Label(guide_frame,
                                   text=guide_text,
                                   justify=tk.LEFT,
                                   font=("Segoe UI", 11))
        self.guide_label.pack(anchor=tk.W, padx=10)
        
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
        
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()

if __name__ == "__main__":
    app = ControlApp()
    app.mainloop() 