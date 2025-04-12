"""
Module xử lý tắt máy tính
Sử dụng cử chỉ tay hoặc lệnh giọng nói để tắt máy
"""

import time  # Xử lý thời gian
import os  # Thao tác hệ thống

class Shutdown:
    def __init__(self):
        """
        Khởi tạo đối tượng Shutdown
        """
        self.start_time = None  # Biến lưu thời điểm bắt đầu đếm ngược
        self.hold_time = 3  # Thời gian cần giữ ngón tay (giây)

    def execute(self, fingers):
        """
        Xử lý tắt máy bằng cử chỉ tay
        Args:
            fingers: Trạng thái các ngón tay
        """
        # Kiểm tra nếu chỉ giơ ngón út
        if fingers == [0, 0, 0, 0, 1]: 
            if self.start_time is None:
                self.start_time = time.time()  # Bắt đầu đếm ngược

            elapsed_time = time.time() - self.start_time
            print(f"Giữ ngón út trong {elapsed_time:.1f}s")

            # Nếu giữ đủ thời gian thì tắt máy
            if elapsed_time >= self.hold_time:
                print("Tắt máy...")
                os.system("shutdown /s /t 1")  # Tắt máy sau 1 giây
        else:
            self.start_time = None  # Reset thời gian nếu không giơ ngón út

    def shutdown_computer(self):
        """
        Tắt máy từ lệnh giọng nói
        """
        print("Tắt máy...")
        try:
            # Thử lệnh tắt máy mới
            os.system("shutdown /s /f /t 0")
        except Exception as e:
            print(f"Lỗi khi tắt máy: {e}")
            # Thử lệnh tắt máy khác nếu lệnh đầu tiên thất bại
            os.system("shutdown.exe /s /f /t 0")