"""
Module chính của ứng dụng điều khiển bằng tay và giọng nói
Kết hợp xử lý hình ảnh từ camera và nhận diện giọng nói
để điều khiển các chức năng của máy tính
"""

import cv2  # Xử lý hình ảnh từ camera
import pyautogui  # Điều khiển chuột và bàn phím
import speech_recognition as sr  # Nhận diện giọng nói
import threading  # Xử lý đa luồng
import queue  # Hàng đợi để đồng bộ giữa các luồng

# Import các module điều khiển
import hand
from hand_gesture import HandGesture
from hidden_window import WindowControl
from scroll import AutoScroll
from shutdown import Shutdown
from tab_window import TabWindow
from volume import Volume
from voiceai import VoiceAI

# Thiết lập camera và detector
cap = cv2.VideoCapture(0)  # Mở camera mặc định
detector = hand.handDetector(detectionCon=0.7)  # Khởi tạo detector với độ tin cậy 70%

# Biến trạng thái để theo dõi chế độ điều khiển hiện tại
mode = ''

# Hàng đợi để đồng bộ giữa các luồng
command_queue = queue.Queue()

# Lấy kích thước màn hình và khởi tạo các đối tượng điều khiển
screen_width, screen_height = pyautogui.size()
auto_scroll = AutoScroll(screen_height)  # Điều khiển cuộn trang
volume = Volume()  # Điều khiển âm lượng
window_control = WindowControl()  # Điều khiển cửa sổ
hand_gesture = HandGesture()  # Nhận diện cử chỉ tay
tab_window = TabWindow()  # Điều khiển tab trình duyệt
shutdown = Shutdown()  # Điều khiển tắt máy
voice_ai = VoiceAI()  # Xử lý giọng nói

def voice_thread():
    """
    Hàm xử lý nhận diện giọng nói trong một luồng riêng
    Liên tục lắng nghe và thực thi các lệnh giọng nói
    """
    while True:
        try:
            command = voice_ai.listen()
            if command:
                command_queue.put(command)  # Đưa lệnh vào hàng đợi
        except Exception as e:
            print(f"Lỗi trong luồng giọng nói: {e}")

# Khởi tạo và chạy luồng nhận diện giọng nói
voice_thread = threading.Thread(target=voice_thread, daemon=True)
voice_thread.start()

# Vòng lặp chính xử lý hình ảnh từ camera
while True:
    ret, frame = cap.read()  # Đọc frame từ camera

    # Xử lý hình ảnh và nhận diện bàn tay
    frame = detector.findHands(frame)
    pointList = detector.findPosition(frame, draw=False)
    fingers = hand_gesture.detect_fingers(pointList)
    
    # Xác định chế độ điều khiển dựa trên cử chỉ tay
    if fingers == [1, 1, 0, 0, 0]:  # Giơ ngón cái và ngón trỏ
        mode = 'volume'  # Chế độ điều khiển âm lượng
    elif fingers == [0, 1, 1, 0, 0]:  # Giơ ngón trỏ và ngón giữa
        mode = 'scroll'  # Chế độ cuộn trang
    elif fingers == [0, 1, 1, 1, 1]:  # Giơ 4 ngón tay
        mode = 'tab'  # Chế độ điều khiển tab
    elif fingers == [0, 0, 0, 0, 1]:  # Giơ ngón út
        mode = 'shutdown'  # Chế độ tắt máy

    # Xử lý các chế độ điều khiển
    if mode == 'volume':
        volume.__set__(pointList, frame, fingers)
        volume.run()
        if fingers.count(1) == 3:  # Kết thúc điều khiển âm lượng
            volume.adjusting = False
            mode = ''
            
    if mode == 'scroll' and not auto_scroll.scroll:
        auto_scroll.start(pointList)
    if auto_scroll.scroll:
        auto_scroll.update(pointList, fingers)

    if mode == 'tab':
        tab_window.__set__(pointList)
        tab_window.execute(frame)

    if mode == 'shutdown':
        shutdown.execute(fingers)

    # Kiểm tra và xử lý cửa sổ
    window_control.minimize_window(fingers)
    
    # Xử lý lệnh giọng nói từ hàng đợi
    try:
        while not command_queue.empty():
            command = command_queue.get_nowait()
            voice_ai.execute_command(command)
    except queue.Empty:
        pass
    
    # Hiển thị hình ảnh
    cv2.imshow('Vision Control', frame)
    
    # Thoát chương trình khi nhấn phím 'x'
    if cv2.waitKey(1) == ord('x'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()