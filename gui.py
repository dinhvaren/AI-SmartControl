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

# Màu sắc chủ đạo
PRIMARY_COLOR = "#2c3e50"
SECONDARY_COLOR = "#3498db"
ACCENT_COLOR = "#e74c3c"
BACKGROUND_COLOR = "#ecf0f1"
TEXT_COLOR = "#2c3e50"
SUCCESS_COLOR = "#2ecc71"
WARNING_COLOR = "#f39c12"

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Cấu hình cửa sổ
        self.title("Cài Đặt")
        self.geometry("400x300")
        self.configure(bg=BACKGROUND_COLOR)
        
        # Làm cho cửa sổ không thể resize
        self.resizable(False, False)
        
        # Tạo style
        self.style = ttk.Style()
        
        # Cấu hình style cho nút Lưu
        self.style.configure("Save.TButton",
                           background=SECONDARY_COLOR,
                           foreground="white",
                           padding=10,
                           font=("Segoe UI", 10, "bold"))
        self.style.map("Save.TButton",
                      background=[("active", "#2980b9")])
                           
        # Frame chính
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tạo các biến cho các tùy chọn
        self.startup_var = tk.BooleanVar(value=False)
        self.voice_only_var = tk.BooleanVar(value=False)
        self.gesture_only_var = tk.BooleanVar(value=False)
        self.disable_ai_var = tk.BooleanVar(value=False)
        
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
        
        disable_ai_check = ttk.Checkbutton(main_frame,
                                         text="Tắt trợ lý ảo",
                                         variable=self.disable_ai_var,
                                         style="Settings.TCheckbutton")
        disable_ai_check.pack(anchor=tk.W, pady=10)
        
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

    def show_voice_commands(self):
        """Hiển thị hướng dẫn các lệnh giọng nói"""
        commands = """
ĐIỀU KHIỂN BẰNG GIỌNG NÓI:

1. Điều khiển âm lượng:
    • "tăng âm lượng" hoặc "tăng âm" - Tăng âm lượng
    • "giảm âm lượng" hoặc "giảm âm" - Giảm âm lượng
    • "tăng âm 10" - Tăng âm lượng 10 đơn vị
    • "giảm âm 10" - Giảm âm lượng 10 đơn vị
    • "tắt âm" - Tắt âm
    • "bật âm" - Bật âm
    • "âm lượng tối đa" - Đặt âm lượng tối đa
    • "âm lượng tối thiểu" - Đặt âm lượng tối thiểu

2. Điều khiển cuộn trang:
    • "lướt xuống" - Cuộn trang xuống
    • "lướt lên" - Cuộn trang lên
    • "dừng lại" - Dừng cuộn trang
    • "cuộn nhanh" - Tăng tốc độ cuộn
    • "cuộn chậm" - Giảm tốc độ cuộn
    • "cuộn đến đầu" - Cuộn lên đầu trang
    • "cuộn đến cuối" - Cuộn xuống cuối trang

3. Điều khiển cửa sổ:
    • "mở trang" - Mở tab mới
    • "chuyển trang" - Chuyển tab
    • "cửa sổ" - Mở chế độ chuyển cửa sổ
    • "qua phải" - Chuyển sang tab/cửa sổ bên phải
    • "qua trái" - Chuyển sang tab/cửa sổ bên trái
    • "chọn trang" - Chọn cửa sổ hiện tại
    • "đóng cửa sổ" - Đóng cửa sổ hiện tại
    • "thu nhỏ" - Thu nhỏ cửa sổ hiện tại
    • "phóng to" - Phóng to cửa sổ hiện tại

4. Điều khiển chuột:
    • "nhấp đôi" hoặc "double click" - Nhấp đôi chuột
    • "nhấp chuột" hoặc "click chuột" - Nhấp chuột trái
    • "chuột phải" hoặc "right click" - Nhấp chuột phải
    • "chuột trái" hoặc "left click" - Nhấp chuột trái
    • "chuột qua phải" - Di chuột sang phải
    • "chuột qua trái" - Di chuột sang trái
    • "chuột lên" - Di chuột lên trên
    • "chuột xuống" - Di chuột xuống dưới
    • "kéo chuột" - Bắt đầu kéo chuột
    • "thả chuột" - Thả chuột
    • "di chuột" - Di chuyển chuột theo hướng chỉ định
    • "giữ chuột" - Giữ chuột
    • "nhả chuột" - Nhả chuột

5. Nhập văn bản:
    • "nhập chữ" - Bắt đầu nhập văn bản
    • "xóa chữ [số]" - Xóa số ký tự
    • "xóa từ [số]" - Xóa số từ
    • "bôi đen [số] [phải/trái]" - Bôi đen số từ
    • "copy" hoặc "sao chép" - Sao chép văn bản
    • "dán chữ" hoặc "paste" - Dán văn bản
    • "xuống dòng" - Xuống dòng mới
    • "tab" - Nhấn phím Tab
    • "enter" - Nhấn phím Enter
    • "space" - Nhấn phím Space
    • "backspace" - Xóa ký tự trước đó
    • "delete" - Xóa ký tự sau đó

6. Điều khiển Google:
    • "google mở tab mới" - Mở tab mới
    • "google đóng tab" - Đóng tab hiện tại
    • "google mở lại tab" - Mở lại tab đã đóng
    • "google chuyển tab [số]" - Chuyển đến tab số
    • "google di chuyển tab phải" - Di chuyển tab sang phải
    • "google di chuyển tab trái" - Di chuyển tab sang trái
    • "google ghim tab" - Ghim tab hiện tại
    • "google bỏ ghim tab" - Bỏ ghim tab
    • "google ẩn danh" - Mở tab ẩn danh
    • "google đóng tất cả tab" - Đóng tất cả tab
    • "google làm mới trang" - Làm mới trang
    • "google dừng tải" - Dừng tải trang
    • "google phóng to" - Phóng to trang
    • "google thu nhỏ" - Thu nhỏ trang
    • "google đặt lại zoom" - Đặt lại tỷ lệ zoom
    • "google lịch sử" - Mở lịch sử
    • "google dấu trang" - Mở dấu trang
    • "google đánh dấu trang" - Đánh dấu trang hiện tại
    • "google tìm trong trang [từ khóa]" - Tìm kiếm trong trang
    • "google dịch trang" - Mở dịch trang

7. Điều khiển YouTube:
    • "youtube mở youtube" - Mở YouTube
    • "youtube phát" hoặc "youtube tạm dừng" - Phát/tạm dừng video
    • "youtube video tiếp theo" - Chuyển sang video tiếp theo
    • "youtube video trước" - Quay lại video trước
    • "youtube tăng âm" - Tăng âm lượng
    • "youtube giảm âm" - Giảm âm lượng
    • "youtube tắt tiếng" - Tắt tiếng
    • "youtube toàn màn hình" - Bật/tắt chế độ toàn màn hình
    • "youtube rạp hát" - Bật/tắt chế độ rạp hát
    • "youtube tua nhanh" - Tua nhanh 5 giây
    • "youtube tua lùi" - Tua lùi 5 giây
    • "youtube tăng tốc độ" - Tăng tốc độ phát
    • "youtube giảm tốc độ" - Giảm tốc độ phát
    • "youtube đặt lại tốc độ" - Đặt lại tốc độ phát
    • "youtube thích video" - Thích video
    • "youtube không thích video" - Không thích video
    • "youtube đăng ký" - Đăng ký kênh
    • "youtube tìm kiếm [từ khóa]" - Tìm kiếm trên YouTube

8. Lệnh hệ thống:
    • "tắt máy" - Tắt máy tính
    • "khởi động lại" - Khởi động lại máy tính
    • "chế độ ngủ" - Đưa máy vào chế độ ngủ
    • "đăng xuất" - Đăng xuất khỏi tài khoản
    • "khóa màn hình" - Khóa màn hình
    • "mở task manager" - Mở Task Manager
    • "mở control panel" - Mở Control Panel
    • "mở settings" - Mở Settings Windows
    • "mở [tên ứng dụng]" - Mở ứng dụng được chỉ định
    • "điều khiển" - Bắt đầu lắng nghe lệnh
    • "dừng lại" - Dừng lắng nghe lệnh
"""
        messagebox.showinfo("Hướng dẫn lệnh giọng nói", commands)

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
        self.configure(bg=BACKGROUND_COLOR)
        
        # Tạo style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Cấu hình style
        self.style.configure("TFrame", background=BACKGROUND_COLOR)
        self.style.configure("TLabel", 
                           background=BACKGROUND_COLOR, 
                           foreground=TEXT_COLOR, 
                           font=("Segoe UI", 10))

        # Style cho nút chính (Bắt đầu/Dừng)
        self.style.configure("Primary.TButton",
                           background=SECONDARY_COLOR,
                           foreground="white",
                           padding=(20, 10),
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           relief="flat")
        self.style.map("Primary.TButton",
                      background=[("active", "#2980b9")],
                      relief=[("pressed", "flat")],
                      borderwidth=[("pressed", 0)])

        # Style cho nút Dừng
        self.style.configure("Stop.TButton",
                           background=ACCENT_COLOR,
                           foreground="white",
                           padding=(20, 10),
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           relief="flat")
        self.style.map("Stop.TButton",
                      background=[("active", "#c0392b")],
                      relief=[("pressed", "flat")],
                      borderwidth=[("pressed", 0)])

        # Style cho nút cài đặt
        self.style.configure("Settings.TButton",
                           background=PRIMARY_COLOR,
                           foreground="white",
                           padding=(20, 10),
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=0,
                           relief="flat")
        self.style.map("Settings.TButton",
                      background=[("active", "#34495e")],
                      relief=[("pressed", "flat")],
                      borderwidth=[("pressed", 0)])

        # Style cho các frame
        self.style.configure("TLabelframe", 
                           background="white", 
                           foreground=TEXT_COLOR,
                           font=("Segoe UI", 10, "bold"),
                           borderwidth=1,
                           relief="solid")
        self.style.configure("TLabelframe.Label", 
                           background="white", 
                           foreground=TEXT_COLOR,
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
                              font=("Segoe UI", 32, "bold"),
                              foreground=PRIMARY_COLOR)
        title_label.pack()
        
        subtitle_label = ttk.Label(title_frame,
                                 text="Điều Khiển Máy Tính Bằng Tay & Giọng Nói AI",
                                 font=("Segoe UI", 14),
                                 foreground=SECONDARY_COLOR)
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
        mode_frame = tk.Frame(camera_frame, bg=BACKGROUND_COLOR)
        mode_frame.pack(side=tk.BOTTOM, pady=10, anchor=tk.W)
        
        # Voice indicator
        voice_frame = tk.Frame(mode_frame, bg=BACKGROUND_COLOR, padx=10, pady=5)
        voice_frame.pack(side=tk.LEFT, padx=5)
        
        self.voice_dot = tk.Canvas(voice_frame, width=14, height=14, bg=BACKGROUND_COLOR, 
                                 highlightthickness=0)
        self.voice_dot.pack(side=tk.LEFT, padx=(0, 5), pady=(2, 0))
        self.voice_circle = self.voice_dot.create_oval(2, 2, 12, 12, 
                                                     fill=BACKGROUND_COLOR,
                                                     outline=PRIMARY_COLOR,
                                                     width=1)
        
        voice_label = tk.Label(voice_frame, text="Voice", fg=TEXT_COLOR, bg=BACKGROUND_COLOR, font=("Segoe UI", 10))
        voice_label.pack(side=tk.LEFT)
        
        # Gesture indicator
        gesture_frame = tk.Frame(mode_frame, bg=BACKGROUND_COLOR, padx=10, pady=5)
        gesture_frame.pack(side=tk.LEFT, padx=5)
        
        self.gesture_dot = tk.Canvas(gesture_frame, width=14, height=14, bg=BACKGROUND_COLOR,
                                   highlightthickness=0)
        self.gesture_dot.pack(side=tk.LEFT, padx=(0, 5), pady=(2, 0))
        self.gesture_circle = self.gesture_dot.create_oval(2, 2, 12, 12,
                                                         fill=BACKGROUND_COLOR,
                                                         outline=PRIMARY_COLOR,
                                                         width=1)
        
        gesture_label = tk.Label(gesture_frame, text="Gesture", fg=TEXT_COLOR, bg=BACKGROUND_COLOR, font=("Segoe UI", 10))
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
        canvas = tk.Canvas(guide_frame, bg=BACKGROUND_COLOR, highlightthickness=0)
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
        • Nắm tay lại để kết thúc điều khiển âm lượng

    2. Cuộn trang:
        • Giơ ngón trỏ và ngón giữa
        • Di chuyển lên/xuống để cuộn trang
        • Tốc độ cuộn phụ thuộc vào khoảng cách di chuyển
        • Nắm tay lại để dừng cuộn trang

    3. Điều khiển tab/cửa sổ:
        • Giơ 4 ngón tay (trừ ngón cái) để mở Alt+Tab
        • Di chuyển trái/phải để chọn cửa sổ
        • Nắm tay lại để chọn cửa sổ hiện tại (đóng menu Alt+Tab)
        • Giơ 3 ngón để đóng cửa sổ hiện tại
        • Giơ 4 ngón để đóng tab hiện tại

    4. Tắt máy:
        • Giơ ngón út để kích hoạt
        • Giữ 3 giây để xác nhận tắt máy

    5. Thu nhỏ cửa sổ:
        • Gập tất cả các ngón tay xuống để thu nhỏ cửa sổ hiện tại

    6. Điều khiển âm thanh:
        • Giơ ngón cái và ngón trỏ
        • Vuốt lên để tăng âm lượng
        • Vuốt xuống để giảm âm lượng
        • Nắm tay lại để kết thúc điều khiển

    7. Chuyển đổi giữa các cửa sổ:
        • Giơ tay phải
        • Vuốt sang phải để chuyển sang cửa sổ tiếp theo
        • Vuốt sang trái để chuyển về cửa sổ trước đó

    8. Điều khiển hai tay:
        • Giơ cả hai tay để reset trạng thái điều khiển
        • Giơ tay trái để điều khiển âm lượng
        • Giơ tay phải để điều khiển cửa sổ
        """
        
        # Label chứa nội dung
        self.guide_label = ttk.Label(guide_content,
                                   text=guide_text,
                                   justify=tk.LEFT,
                                   font=("Segoe UI", 11),
                                   background=BACKGROUND_COLOR,
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
        self.voice_dot.itemconfig(self.voice_circle, fill=BACKGROUND_COLOR)
        self.gesture_dot.itemconfig(self.gesture_circle, fill=BACKGROUND_COLOR)
        self.mode_label.config(text="Đang chờ...")
        
        # Dừng luồng voice
        if self.voice_thread and self.voice_thread.is_alive():
            self.voice_thread.join(timeout=1.0)  # Chờ thread kết thúc tối đa 1 giây
            self.voice_thread = None
            
        # Xóa tất cả lệnh trong hàng đợi
        while not self.command_queue.empty():
            try:
                self.command_queue.get_nowait()
            except queue.Empty:
                break
            
    def voice_control(self):
        """Hàm xử lý nhận diện giọng nói trong một luồng riêng"""
        while self.running:
            try:
                command = self.voice_ai.listen()
                if not self.running:  # Kiểm tra lại trạng thái running
                    break
                    
                if command:
                    self.command_queue.put(command)
                    # Hiển thị đèn voice active
                    self.voice_dot.itemconfig(self.voice_circle, fill=SUCCESS_COLOR)
                    self.gesture_dot.itemconfig(self.gesture_circle, fill=BACKGROUND_COLOR)
                    self.after(1000, lambda: self.voice_dot.itemconfig(self.voice_circle, fill=BACKGROUND_COLOR))
            except Exception as e:
                print(f"Lỗi trong luồng giọng nói: {e}")
                if not self.running:  # Kiểm tra lại trạng thái running
                    break
                
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
                self.gesture_dot.itemconfig(self.gesture_circle, fill=SUCCESS_COLOR)
                self.voice_dot.itemconfig(self.voice_circle, fill=BACKGROUND_COLOR)
                
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
                self.gesture_dot.itemconfig(self.gesture_circle, fill=BACKGROUND_COLOR)
            
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
        
    def show_voice_commands(self):
        """Hiển thị hướng dẫn các lệnh giọng nói"""
        commands = """
ĐIỀU KHIỂN BẰNG GIỌNG NÓI:

1. Điều khiển âm lượng:
    • "tăng âm lượng" hoặc "tăng âm" - Tăng âm lượng
    • "giảm âm lượng" hoặc "giảm âm" - Giảm âm lượng
    • "tăng âm 10" - Tăng âm lượng 10 đơn vị
    • "giảm âm 10" - Giảm âm lượng 10 đơn vị
    • "tắt âm" - Tắt âm
    • "bật âm" - Bật âm
    • "âm lượng tối đa" - Đặt âm lượng tối đa
    • "âm lượng tối thiểu" - Đặt âm lượng tối thiểu

2. Điều khiển cuộn trang:
    • "lướt xuống" - Cuộn trang xuống
    • "lướt lên" - Cuộn trang lên
    • "dừng lại" - Dừng cuộn trang
    • "cuộn nhanh" - Tăng tốc độ cuộn
    • "cuộn chậm" - Giảm tốc độ cuộn
    • "cuộn đến đầu" - Cuộn lên đầu trang
    • "cuộn đến cuối" - Cuộn xuống cuối trang

3. Điều khiển cửa sổ:
    • "mở trang" - Mở tab mới
    • "chuyển trang" - Chuyển tab
    • "cửa sổ" - Mở chế độ chuyển cửa sổ
    • "qua phải" - Chuyển sang tab/cửa sổ bên phải
    • "qua trái" - Chuyển sang tab/cửa sổ bên trái
    • "chọn trang" - Chọn cửa sổ hiện tại
    • "đóng cửa sổ" - Đóng cửa sổ hiện tại
    • "thu nhỏ" - Thu nhỏ cửa sổ hiện tại
    • "phóng to" - Phóng to cửa sổ hiện tại

4. Điều khiển chuột:
    • "nhấp đôi" hoặc "double click" - Nhấp đôi chuột
    • "nhấp chuột" hoặc "click chuột" - Nhấp chuột trái
    • "chuột phải" hoặc "right click" - Nhấp chuột phải
    • "chuột trái" hoặc "left click" - Nhấp chuột trái
    • "chuột qua phải" - Di chuột sang phải
    • "chuột qua trái" - Di chuột sang trái
    • "chuột lên" - Di chuột lên trên
    • "chuột xuống" - Di chuột xuống dưới
    • "kéo chuột" - Bắt đầu kéo chuột
    • "thả chuột" - Thả chuột
    • "di chuột" - Di chuyển chuột theo hướng chỉ định
    • "giữ chuột" - Giữ chuột
    • "nhả chuột" - Nhả chuột

5. Nhập văn bản:
    • "nhập chữ" - Bắt đầu nhập văn bản
    • "xóa chữ [số]" - Xóa số ký tự
    • "xóa từ [số]" - Xóa số từ
    • "bôi đen [số] [phải/trái]" - Bôi đen số từ
    • "copy" hoặc "sao chép" - Sao chép văn bản
    • "dán chữ" hoặc "paste" - Dán văn bản
    • "xuống dòng" - Xuống dòng mới
    • "tab" - Nhấn phím Tab
    • "enter" - Nhấn phím Enter
    • "space" - Nhấn phím Space
    • "backspace" - Xóa ký tự trước đó
    • "delete" - Xóa ký tự sau đó

6. Điều khiển Google:
    • "google mở tab mới" - Mở tab mới
    • "google đóng tab" - Đóng tab hiện tại
    • "google mở lại tab" - Mở lại tab đã đóng
    • "google chuyển tab [số]" - Chuyển đến tab số
    • "google di chuyển tab phải" - Di chuyển tab sang phải
    • "google di chuyển tab trái" - Di chuyển tab sang trái
    • "google ghim tab" - Ghim tab hiện tại
    • "google bỏ ghim tab" - Bỏ ghim tab
    • "google ẩn danh" - Mở tab ẩn danh
    • "google đóng tất cả tab" - Đóng tất cả tab
    • "google làm mới trang" - Làm mới trang
    • "google dừng tải" - Dừng tải trang
    • "google phóng to" - Phóng to trang
    • "google thu nhỏ" - Thu nhỏ trang
    • "google đặt lại zoom" - Đặt lại tỷ lệ zoom
    • "google lịch sử" - Mở lịch sử
    • "google dấu trang" - Mở dấu trang
    • "google đánh dấu trang" - Đánh dấu trang hiện tại
    • "google tìm trong trang [từ khóa]" - Tìm kiếm trong trang
    • "google dịch trang" - Mở dịch trang

7. Điều khiển YouTube:
    • "youtube mở youtube" - Mở YouTube
    • "youtube phát" hoặc "youtube tạm dừng" - Phát/tạm dừng video
    • "youtube video tiếp theo" - Chuyển sang video tiếp theo
    • "youtube video trước" - Quay lại video trước
    • "youtube tăng âm" - Tăng âm lượng
    • "youtube giảm âm" - Giảm âm lượng
    • "youtube tắt tiếng" - Tắt tiếng
    • "youtube toàn màn hình" - Bật/tắt chế độ toàn màn hình
    • "youtube rạp hát" - Bật/tắt chế độ rạp hát
    • "youtube tua nhanh" - Tua nhanh 5 giây
    • "youtube tua lùi" - Tua lùi 5 giây
    • "youtube tăng tốc độ" - Tăng tốc độ phát
    • "youtube giảm tốc độ" - Giảm tốc độ phát
    • "youtube đặt lại tốc độ" - Đặt lại tốc độ phát
    • "youtube thích video" - Thích video
    • "youtube không thích video" - Không thích video
    • "youtube đăng ký" - Đăng ký kênh
    • "youtube tìm kiếm [từ khóa]" - Tìm kiếm trên YouTube

8. Lệnh hệ thống:
    • "tắt máy" - Tắt máy tính
    • "khởi động lại" - Khởi động lại máy tính
    • "chế độ ngủ" - Đưa máy vào chế độ ngủ
    • "đăng xuất" - Đăng xuất khỏi tài khoản
    • "khóa màn hình" - Khóa màn hình
    • "mở task manager" - Mở Task Manager
    • "mở control panel" - Mở Control Panel
    • "mở settings" - Mở Settings Windows
    • "mở [tên ứng dụng]" - Mở ứng dụng được chỉ định
    • "điều khiển" - Bắt đầu lắng nghe lệnh
    • "dừng lại" - Dừng lắng nghe lệnh
"""
        messagebox.showinfo("Hướng dẫn lệnh giọng nói", commands)
        
    def __del__(self):
        if hasattr(self, 'cap'):
            self.cap.release()

if __name__ == "__main__":
    app = ControlApp()
    app.mainloop() 