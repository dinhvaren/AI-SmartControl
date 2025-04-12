"""
Module xử lý điều khiển âm lượng hệ thống
Sử dụng thư viện pycaw để điều khiển âm lượng Windows
và OpenCV để xử lý hình ảnh từ camera
"""

import math  # Tính toán khoảng cách
import cv2  # Xử lý hình ảnh
import numpy  # Xử lý số học
from comtypes import CLSCTX_ALL  # Truy cập COM interface
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume  # Điều khiển âm lượng Windows
import pyautogui  # Điều khiển chuột và bàn phím
import time  # Xử lý thời gian

# Các hằng số cấu hình giao diện
CIRCLE_RADIUS = 7  # Bán kính vòng tròn vẽ điểm
CIRCLE_COLOR = (255, 0, 0)  # Màu vòng tròn (BGR)
LINE_COLOR = (255, 0, 0)  # Màu đường kẻ (BGR)
LINE_THICKNESS = 2  # Độ dày đường kẻ

# Các hằng số điều khiển âm lượng
MIN_HAND_LENGTH = 15  # Khoảng cách tối thiểu giữa các ngón tay
MAX_HAND_LENGTH = 150  # Khoảng cách tối đa giữa các ngón tay
DEFAULT_VOLUME_STEP = 5  # Bước tăng/giảm âm lượng mặc định

# Thiết lập điều khiển âm lượng Windows
devices = AudioUtilities.GetSpeakers()  # Lấy thiết bị âm thanh
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)  # Kích hoạt interface
volume = interface.QueryInterface(IAudioEndpointVolume)  # Lấy interface điều khiển âm lượng
minVolume, maxVolume = volume.GetVolumeRange()[:2]  # Lấy phạm vi âm lượng

class Volume:

    # Lớp xử lý điều khiển âm lượng hệ thống thông qua cử chỉ tay và lệnh giọng nói.
    
    def __init__(self, pointList=None, frame=None, fingers=None):
 
        # Khởi tạo đối tượng Volume.
        
        # Args:
            # pointList: Danh sách các điểm trên bàn tay
            # frame: Khung hình camera
            # fingers: Trạng thái các ngón tay

        self.pointList = pointList
        self.frame = frame
        self.fingers = fingers
        self.adjusting = False
        self.prev_y = None  # Lưu vị trí Y trước đó để kiểm tra vuốt
        self.threshold_y = 240  # Vị trí đường ngang (giữa màn hình)
        self.volume_active = False  # Trạng thái điều khiển âm lượng
        self.last_gesture_time = 0  # Thời gian cử chỉ cuối cùng
        self.gesture_handled = False  # Đánh dấu đã xử lý cử chỉ

    def __set__(self, pointList, frame, fingers):
        # Cập nhật thông tin về bàn tay và khung hình.
        # Args:
        #     pointList: Danh sách các điểm trên bàn tay
        #     frame: Khung hình camera
        #     fingers: Trạng thái các ngón tay

        self.pointList = pointList
        self.frame = frame
        self.fingers = fingers

    def run(self):
        # Xử lý điều khiển âm lượng bằng cử chỉ tay.
        if not self.pointList:
            return

        self.adjusting = True
        index_x, index_y = self.pointList[4][1], self.pointList[4][2]
        middle_x, middle_y = self.pointList[8][1], self.pointList[8][2]

        # Vẽ điểm và đường kết nối
        self._draw_hand_points(index_x, index_y, middle_x, middle_y)

        if self.adjusting:
            self._adjust_volume(index_x, index_y, middle_x, middle_y)

    def _draw_hand_points(self, index_x, index_y, middle_x, middle_y):
       # Vẽ các điểm và đường kết nối trên bàn tay.
        cv2.circle(self.frame, (index_x, index_y), CIRCLE_RADIUS, CIRCLE_COLOR, -1)
        cv2.circle(self.frame, (middle_x, middle_y), CIRCLE_RADIUS, CIRCLE_COLOR, -1)
        cv2.line(self.frame, (index_x, index_y), (middle_x, middle_y), LINE_COLOR, LINE_THICKNESS)

    def _adjust_volume(self, index_x, index_y, middle_x, middle_y):
        # Điều chỉnh âm lượng dựa trên khoảng cách giữa các ngón tay.
        length = math.hypot(middle_x - index_x, middle_y - index_y)
        vol = numpy.interp(length, [MIN_HAND_LENGTH, MAX_HAND_LENGTH], (minVolume, maxVolume))
        
        # Lấy âm lượng hiện tại để so sánh
        current_vol = volume.GetMasterVolumeLevel()
        
        # In ra console khi tăng/giảm âm lượng
        if vol > current_vol:
            print(f"Phát hiện cử chỉ: Tăng âm lượng (từ {int(numpy.interp(current_vol, [minVolume, maxVolume], [0, 100]))}% lên {int(numpy.interp(vol, [minVolume, maxVolume], [0, 100]))}%)")
        elif vol < current_vol:
            print(f"Phát hiện cử chỉ: Giảm âm lượng (từ {int(numpy.interp(current_vol, [minVolume, maxVolume], [0, 100]))}% xuống {int(numpy.interp(vol, [minVolume, maxVolume], [0, 100]))}%)")
            
        volume.SetMasterVolumeLevel(vol, None)

    def get_current_volume_percent(self):
       # Lấy mức âm lượng hiện tại theo phần trăm.
        
       # Returns:
           # int: Mức âm lượng từ 0-100
        current_volume = volume.GetMasterVolumeLevel()
        return int(numpy.interp(current_volume, [minVolume, maxVolume], [0, 100]))

    def set_volume_percent(self, percent):
        # Đặt mức âm lượng theo phần trăm.
        # Args:
            # percent (int): Mức âm lượng từ 0-100
        # Returns:
            # int: Mức âm lượng thực tế được đặt

        percent = max(0, min(100, percent))
        db_value = numpy.interp(percent, [0, 100], [minVolume, maxVolume])
        volume.SetMasterVolumeLevel(db_value, None)
        return percent

    def increase(self, amount=DEFAULT_VOLUME_STEP):
        # Tăng âm lượng theo số phần trăm chỉ định.
        # Args:
            # amount (int): Số phần trăm cần tăng      
        # Returns:
            # int: Mức âm lượng mới
        current_percent = self.get_current_volume_percent()
        new_percent = min(100, current_percent + amount)
        self.set_volume_percent(new_percent)
        print(f"Âm lượng đã được tăng lên {new_percent}%")
        return new_percent

    def decrease(self, amount=DEFAULT_VOLUME_STEP):
        # Giảm âm lượng theo số phần trăm chỉ định.
        # Args:
            # amount (int): Số phần trăm cần giảm     
        # Returns:
            # int: Mức âm lượng mới

        current_percent = self.get_current_volume_percent()
        new_percent = max(0, current_percent - amount)
        self.set_volume_percent(new_percent)
        print(f"Âm lượng đã được giảm xuống {new_percent}%")
        return new_percent

    def detect_gesture(self):
        """
        Nhận diện cử chỉ tay (mở/nắm)
        Returns:
            "open" nếu bàn tay mở
            "closed" nếu bàn tay nắm
            None nếu không nhận diện được
        """
        if not self.pointList:
            print("Không phát hiện bàn tay")
            return None

        # Kiểm tra bàn tay mở (các ngón tay duỗi thẳng)
        is_hand_open = (
            self.pointList[8][2] < self.pointList[6][2] and  # Ngón trỏ
            self.pointList[12][2] < self.pointList[10][2] and  # Ngón giữa
            self.pointList[16][2] < self.pointList[14][2] and  # Ngón nhẫn
            self.pointList[20][2] < self.pointList[18][2]  # Ngón út
        )

        # Kiểm tra bàn tay nắm (các ngón tay gập xuống)
        is_hand_closed = (
            self.pointList[8][2] > self.pointList[6][2] and  # Ngón trỏ
            self.pointList[12][2] > self.pointList[10][2] and  # Ngón giữa
            self.pointList[16][2] > self.pointList[14][2] and  # Ngón nhẫn
            self.pointList[20][2] > self.pointList[18][2]  # Ngón út
        )

        if is_hand_open:
            print("Phát hiện cử chỉ: Bàn tay mở")
            return "open"
        elif is_hand_closed:
            print("Phát hiện cử chỉ: Bàn tay nắm")
            return "closed"
        print("Không phát hiện cử chỉ nào")
        return None

    def execute(self, frame):
        """
        Thực thi điều khiển âm lượng dựa trên cử chỉ tay
        Args:
            frame: Khung hình camera
        """
        if not self.pointList:
            return

        gesture = self.detect_gesture()
        y_index_finger = self.pointList[8][2]  # Vị trí Y của ngón trỏ

        # Vẽ đường phân cách trên màn hình
        cv2.line(frame, (0, self.threshold_y), (640, self.threshold_y), (0, 255, 0), 2)

        # Xử lý cử chỉ tay
        if gesture == "open" and not self.volume_active:
            print("Thực hiện: Bắt đầu điều khiển âm lượng")
            self.volume_active = True
            self.gesture_handled = False
            self.last_gesture_time = time.time()

        elif gesture == "closed" and self.volume_active and not self.gesture_handled:
            print("Thực hiện: Kết thúc điều khiển âm lượng")
            self.volume_active = False
            self.gesture_handled = True

        # Xử lý vuốt tay để điều chỉnh âm lượng
        if self.prev_y is not None and self.volume_active:
            # Vuốt lên để tăng âm lượng
            if self.prev_y > self.threshold_y and y_index_finger <= self.threshold_y:
                print("Thực hiện: Vuốt lên -> Tăng âm lượng")
                pyautogui.press("volumeup")
            # Vuốt xuống để giảm âm lượng
            elif self.prev_y < self.threshold_y and y_index_finger >= self.threshold_y:
                print("Thực hiện: Vuốt xuống -> Giảm âm lượng")
                pyautogui.press("volumedown")

        # Reset trạng thái khi thay đổi cử chỉ
        if gesture != "closed":
            self.gesture_handled = False

        # Kiểm tra và tắt điều khiển âm lượng nếu quá lâu
        if self.volume_active and time.time() - self.last_gesture_time > 5:
            print("Tự động tắt điều khiển âm lượng do quá thời gian")
            self.volume_active = False

        self.prev_y = y_index_finger

    def volume_up(self):
        """
        Tăng âm lượng từ lệnh giọng nói
        """
        print("Thực hiện: Tăng âm lượng")
        pyautogui.press("volumeup")

    def volume_down(self):
        """
        Giảm âm lượng từ lệnh giọng nói
        """
        print("Thực hiện: Giảm âm lượng")
        pyautogui.press("volumedown")
