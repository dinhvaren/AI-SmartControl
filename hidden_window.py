"""
Module xử lý điều khiển cửa sổ
Sử dụng cử chỉ tay để thu nhỏ cửa sổ
"""

import pygetwindow  # Thư viện điều khiển cửa sổ Windows


class WindowControl:
    def __init__(self):
        """
        Khởi tạo đối tượng WindowControl
        """
        self.window_hidden = False  # Trạng thái cửa sổ

    def minimize_window(self, fingers):
        """
        Thu nhỏ cửa sổ dựa trên cử chỉ tay
        Args:
            fingers: Trạng thái các ngón tay
        """
        # Nếu tất cả ngón tay đều gập xuống và cửa sổ chưa bị thu nhỏ
        if fingers == [0, 0, 0, 0, 0] and not self.window_hidden:
            active_window = pygetwindow.getActiveWindow()  # Lấy cửa sổ đang active
            if active_window:
                active_window.minimize()  # Thu nhỏ cửa sổ
                self.window_hidden = True  # Đánh dấu cửa sổ đã bị thu nhỏ
        # Nếu có ngón tay giơ lên thì reset trạng thái
        elif fingers != [0, 0, 0, 0, 0]:
            self.window_hidden = False
