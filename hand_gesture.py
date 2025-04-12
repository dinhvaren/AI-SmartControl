"""
Module xử lý nhận diện cử chỉ tay
Sử dụng các điểm đặc trưng trên bàn tay để xác định trạng thái của các ngón tay
"""

class HandGesture:
    def __init__(self):
        """
        Khởi tạo các ID của các điểm đặc trưng trên bàn tay
        Tương ứng với các ngón tay: cái, trỏ, giữa, nhẫn, út
        """
        self.fingerId = [4, 8, 12, 16, 20]

    def detect_fingers(self, pointList):
        """
        Xác định trạng thái của các ngón tay (giơ lên hay không)
        Args:
            pointList: Danh sách các điểm đặc trưng trên bàn tay
        Returns:
            List các giá trị 0/1 tương ứng với trạng thái của các ngón tay
        """
        fingers = []
        if len(pointList) == 0:
            return fingers

        # Xác định bên tay (trái/phải) dựa vào vị trí ngón cái
        wrist_x = pointList[0][1]  # Tọa độ x của cổ tay
        thumb_x = pointList[4][1]  # Tọa độ x của ngón cái
        hand_side = "left" if thumb_x < wrist_x else "right"

        # Xác định trạng thái ngón cái
        if hand_side == "left":
            # Ngón cái giơ lên nếu điểm 4 nằm bên trái điểm 3
            fingers.append(1 if pointList[4][1] < pointList[3][1] else 0)
        else:
            # Ngón cái giơ lên nếu điểm 4 nằm bên phải điểm 3
            fingers.append(1 if pointList[4][1] > pointList[3][1] else 0)

        # Xác định trạng thái các ngón tay còn lại
        for i in range(1, 5):
            # Ngón tay giơ lên nếu điểm đỉnh nằm trên điểm gốc
            fingers.append(1 if pointList[self.fingerId[i]][2] < pointList[self.fingerId[i] - 2][2] else 0)

        return fingers