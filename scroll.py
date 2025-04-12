"""
Module xử lý điều khiển cuộn trang
Sử dụng cử chỉ tay để cuộn lên/xuống trang
"""

import cv2  # Xử lý hình ảnh
import pyautogui  # Điều khiển chuột và bàn phím
import numpy as np  # Xử lý mảng
import time  # Xử lý thời gian
import threading  # Xử lý đa luồng

class AutoScroll:
    def __init__(self, screen_height):
        """
        Khởi tạo đối tượng AutoScroll
        Args:
            screen_height: Chiều cao màn hình
        """
        self.screen_height = screen_height  # Chiều cao màn hình
        self.scroll = False  # Trạng thái cuộn
        self.prev_y = 0  # Vị trí Y trước đó
        self.scroll_speed = 0  # Tốc độ cuộn
        self.last_update_time = time.time()  # Thời gian cập nhật cuối cùng
        self.pointList = None  # Danh sách điểm đặc trưng trên bàn tay
        self.scroll_thread = None  # Thread xử lý cuộn

    def __set__(self, pointList):
        """
        Cập nhật danh sách điểm đặc trưng trên bàn tay
        Args:
            pointList: Danh sách các điểm trên bàn tay
        """
        self.pointList = pointList

    def _scroll_loop(self, direction=1):
        """
        Vòng lặp cuộn trang
        Args:
            direction: 1 để cuộn lên, -1 để cuộn xuống
        """
        while self.scroll:
            try:
                pyautogui.scroll(direction * self.scroll_speed)
                print(f"Đang cuộn {'lên' if direction > 0 else 'xuống'} với tốc độ {self.scroll_speed}")
                time.sleep(0.1)
            except Exception as e:
                print(f"Lỗi khi cuộn: {e}")
                break

    def start_scroll(self):
        """
        Bắt đầu cuộn xuống từ lệnh giọng nói
        """
        print("Bắt đầu cuộn xuống...")
        self.stop_scroll()  # Dừng thread cũ nếu có
        self.scroll = True
        self.scroll_speed = 20
        self.scroll_thread = threading.Thread(target=self._scroll_loop, args=(-1,))
        self.scroll_thread.daemon = True
        self.scroll_thread.start()

    def start_scroll_up(self):
        """
        Bắt đầu cuộn lên từ lệnh giọng nói
        """
        print("Bắt đầu cuộn lên...")
        self.stop_scroll()  # Dừng thread cũ nếu có
        self.scroll = True
        self.scroll_speed = 20
        self.scroll_thread = threading.Thread(target=self._scroll_loop, args=(1,))
        self.scroll_thread.daemon = True
        self.scroll_thread.start()

    def stop_scroll(self):
        """
        Dừng cuộn trang
        """
        print("Dừng cuộn...")
        self.scroll = False
        self.scroll_speed = 0
        if self.scroll_thread and self.scroll_thread.is_alive():
            self.scroll_thread.join(timeout=1.0)  # Chờ thread kết thúc tối đa 1 giây

    def update(self, pointList, fingers):
        """
        Cập nhật trạng thái cuộn trang
        Args:
            pointList: Danh sách các điểm trên bàn tay
            fingers: Trạng thái các ngón tay
        """
        if not self.scroll:
            return

        current_time = time.time()
        time_diff = current_time - self.last_update_time

        # Nếu có pointList, cập nhật tốc độ cuộn dựa trên cử chỉ tay
        if pointList:
            self.pointList = pointList
            current_y = pointList[8][2]  # Vị trí Y của ngón trỏ
            y_diff = current_y - self.prev_y

            # Tính tốc độ cuộn dựa trên khoảng cách di chuyển
            if time_diff > 0:
                self.scroll_speed = y_diff / time_diff
            self.prev_y = current_y

        # Cuộn trang với tốc độ hiện tại
        if abs(self.scroll_speed) > 1:  # Chỉ cuộn khi tốc độ đủ lớn
            pyautogui.scroll(int(-self.scroll_speed * 2))  # Nhân 2 để tăng tốc độ

        self.last_update_time = current_time

        # Dừng cuộn nếu tất cả ngón tay đều gập xuống
        if fingers == [0, 0, 0, 0, 0]:
            self.stop_scroll()





