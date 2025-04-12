"""
Module xử lý điều khiển tab và cửa sổ
Sử dụng cử chỉ tay để chuyển đổi giữa các tab và cửa sổ
"""

import cv2  # Xử lý hình ảnh
import pyautogui  # Điều khiển chuột và bàn phím
import hand  # Xử lý nhận diện tay
import time  # Xử lý thời gian

class TabWindow:
    def __init__(self):
        """
        Khởi tạo đối tượng TabWindow
        """
        self.alt_tab_active = False  # Trạng thái Alt+Tab
        self.prev_x = None  # Lưu vị trí X trước đó để kiểm tra vuốt
        self.threshold_x = 200  # Vị trí đường dọc (giữa màn hình)
        self.gesture_handled = False  # Đánh dấu đã xử lý cử chỉ
        self.last_alt_time = 0  # Thời gian nhấn Alt lần cuối

    def __set__(self, pointList):
        """
        Cập nhật danh sách điểm đặc trưng trên bàn tay
        Args:
            pointList: Danh sách các điểm trên bàn tay
        """
        self.pointList = pointList 

    def detect_gesture(self):
        """
        Nhận diện cử chỉ tay (mở/nắm)
        Returns:
            "open" nếu bàn tay mở
            "closed" nếu bàn tay nắm
            "four_fingers" nếu mở 4 ngón tay
            "three_fingers" nếu mở 3 ngón tay
            None nếu không nhận diện được
        """
        if not self.pointList:
            print("Không phát hiện bàn tay")
            return None

        # Kiểm tra bàn tay mở 5 ngón tay
        is_hand_open = (
            self.pointList[8][2] < self.pointList[6][2] and  # Ngón trỏ
            self.pointList[12][2] < self.pointList[10][2] and  # Ngón giữa
            self.pointList[16][2] < self.pointList[14][2] and  # Ngón nhẫn
            self.pointList[20][2] < self.pointList[18][2]  # Ngón út
        )

        # Kiểm tra bàn tay mở 4 ngón tay (ngón út gập)
        is_four_fingers = (
            self.pointList[8][2] < self.pointList[6][2] and  # Ngón trỏ
            self.pointList[12][2] < self.pointList[10][2] and  # Ngón giữa
            self.pointList[16][2] < self.pointList[14][2] and  # Ngón nhẫn
            self.pointList[20][2] > self.pointList[18][2]  # Ngón út gập
        )

        # Kiểm tra bàn tay mở 3 ngón tay (ngón út và nhẫn gập)
        is_three_fingers = (
            self.pointList[8][2] < self.pointList[6][2] and  # Ngón trỏ
            self.pointList[12][2] < self.pointList[10][2] and  # Ngón giữa
            self.pointList[16][2] > self.pointList[14][2] and  # Ngón nhẫn gập
            self.pointList[20][2] > self.pointList[18][2]  # Ngón út gập
        )

        # Kiểm tra bàn tay nắm (các ngón tay gập xuống)
        is_hand_closed = (
            self.pointList[8][2] > self.pointList[6][2] and  # Ngón trỏ
            self.pointList[12][2] > self.pointList[10][2] and  # Ngón giữa
            self.pointList[16][2] > self.pointList[14][2] and  # Ngón nhẫn
            self.pointList[20][2] > self.pointList[18][2]  # Ngón út
        )

        if is_hand_open:
            print("Phát hiện cử chỉ: Bàn tay mở 5 ngón")
            return "open"
        elif is_four_fingers:
            print("Phát hiện cử chỉ: Bàn tay mở 4 ngón")
            return "four_fingers"
        elif is_three_fingers:
            print("Phát hiện cử chỉ: Bàn tay mở 3 ngón")
            return "three_fingers"
        elif is_hand_closed:
            print("Phát hiện cử chỉ: Bàn tay nắm")
            return "closed"
        print("Không phát hiện cử chỉ nào")
        return None
        
    def execute(self, frame):
        """
        Thực thi điều khiển tab dựa trên cử chỉ tay
        Args:
            frame: Khung hình camera
        """
        if not self.pointList:
            return

        gesture = self.detect_gesture()
        x_index_finger = self.pointList[8][1]  # Vị trí X của ngón trỏ

        # Vẽ đường phân cách trên màn hình
        cv2.line(frame, (self.threshold_x, 0), (self.threshold_x, 480), (0, 255, 0), 2)  

        # Xử lý cử chỉ tay
        if gesture == "open" and not self.alt_tab_active and len(self.pointList) == 21:  # Kiểm tra có đủ 5 ngón tay
            print("Thực hiện: Giữ Alt + Tab")
            pyautogui.keyDown("alt")
            pyautogui.press("tab")
            self.alt_tab_active = True
            self.gesture_handled = False
            self.last_alt_time = time.time()

        elif gesture == "closed" and self.alt_tab_active and not self.gesture_handled:
            print("Thực hiện: Chọn ứng dụng")
            # Đợi một chút trước khi nhấn Enter
            time.sleep(0.1)
            pyautogui.press("enter")
            # Đợi một chút trước khi thả Alt
            time.sleep(0.1)
            pyautogui.keyUp("alt")
            self.alt_tab_active = False
            self.gesture_handled = True

        # Xử lý vuốt tay để chuyển tab
        if self.prev_x is not None and self.alt_tab_active:
            # Vuốt sang phải để chuyển sang tab tiếp theo
            if self.prev_x < self.threshold_x and x_index_finger >= self.threshold_x:
                print("Thực hiện: Vuốt sang phải -> Chuyển tab tiếp theo")
                pyautogui.press("tab")
            # Vuốt sang trái để chuyển về tab trước đó
            elif self.prev_x > self.threshold_x and x_index_finger <= self.threshold_x:
                print("Thực hiện: Vuốt sang trái -> Chuyển tab trước đó")
                pyautogui.keyDown("shift")
                pyautogui.press("tab")
                pyautogui.keyUp("shift")

        # Xử lý đóng tab/cửa sổ
        if gesture == "four_fingers":
            print("Thực hiện: Đóng tab hiện tại")
            pyautogui.hotkey('ctrl', 'w')  # Đóng tab hiện tại

        elif gesture == "three_fingers":
            print("Thực hiện: Đóng cửa sổ hiện tại")
            pyautogui.hotkey('alt', 'f4')  # Đóng cửa sổ hiện tại

        # Reset trạng thái khi thay đổi cử chỉ
        if gesture != "closed":
            self.gesture_handled = False

        # Kiểm tra và thả phím Alt nếu quá lâu
        if self.alt_tab_active and time.time() - self.last_alt_time > 5:
            print("Tự động thả phím Alt do quá thời gian")
            pyautogui.keyUp("alt")
            self.alt_tab_active = False

        self.prev_x = x_index_finger  

    def select_tab(self):
        """
        Chọn trang/cửa sổ hiện tại trong chế độ Alt+Tab
        """
        if self.alt_tab_active:
            print("Thực hiện: Chọn trang/cửa sổ")
            # Đợi một chút trước khi nhấn Enter
            time.sleep(0.1)
            pyautogui.press("enter")
            # Đợi một chút trước khi thả Alt
            time.sleep(0.1)
            pyautogui.keyUp("alt")
            self.alt_tab_active = False
            self.gesture_handled = True

    def switch_tab_right(self):
        """
        Chuyển sang tab bên phải trong chế độ Alt+Tab
        """
        if self.alt_tab_active:
            print("Thực hiện: Chuyển qua phải")
            pyautogui.press("tab")
            self.last_alt_time = time.time()  # Cập nhật thời gian để không tự động thả Alt

    def switch_tab_left(self):
        """
        Chuyển sang tab bên trái trong chế độ Alt+Tab
        """
        if self.alt_tab_active:
            print("Thực hiện: Chuyển qua trái")
            pyautogui.keyDown("shift")
            pyautogui.press("tab")
            pyautogui.keyUp("shift")
            self.last_alt_time = time.time()  # Cập nhật thời gian để không tự động thả Alt

    def open_tab(self):
        """
        Mở tab mới từ lệnh giọng nói
        """
        print("Thực hiện: Mở chế độ Alt + Tab")
        pyautogui.keyDown("alt")
        pyautogui.press("tab")
        self.alt_tab_active = True
        self.gesture_handled = False
        self.last_alt_time = time.time()  # Cập nhật thời gian nhấn Alt