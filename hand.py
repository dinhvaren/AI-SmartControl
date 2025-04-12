"""
Module xử lý nhận diện cử chỉ tay sử dụng thư viện MediaPipe
Cung cấp các chức năng:
- Nhận diện bàn tay trong hình ảnh
- Xác định vị trí các điểm đặc trưng trên bàn tay
- Vẽ các điểm đặc trưng và đường nối giữa chúng
"""

import cv2
import mediapipe as mp
import time


class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        """
        Khởi tạo detector với các tham số:
        - mode: Chế độ xử lý ảnh tĩnh (False) hoặc video (True)
        - maxHands: Số lượng bàn tay tối đa cần nhận diện
        - detectionCon: Ngưỡng tin cậy cho phát hiện bàn tay
        - trackCon: Ngưỡng tin cậy cho theo dõi bàn tay
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # Khởi tạo MediaPipe Hands
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        """
        Tìm và vẽ các điểm đặc trưng trên bàn tay trong ảnh
        Args:
            img: Ảnh đầu vào
            draw: Có vẽ các điểm đặc trưng hay không
        Returns:
            Ảnh đã được xử lý
        """
        # Chuyển đổi ảnh BGR sang RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        # Nếu tìm thấy bàn tay, vẽ các điểm đặc trưng
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
        return img
    # def findTwoHandsPosition(self, img, draw=True):
    #     img = self.findHands(img, draw)
    #     hands = []
    #     imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     self.results = self.hands.process(imgRGB)
    #     if self.results.multi_hand_landmarks and self.results.multi_handedness:
    #         for idx, handLms in enumerate(self.results.multi_hand_landmarks):
    #             lmList = []
    #             h, w, _ = img.shape
    #             for id, lm in enumerate(handLms.landmark):
    #                 cx, cy = int(lm.x * w), int(lm.y * h)
    #                 lmList.append([id, cx, cy])

    #             # Xác định tay trái hoặc phải
    #             hand_label = self.results.multi_handedness[idx].classification[0].label  # "Left" hoặc "Right"

    #             hands.append((hand_label, lmList))  # Trả về tuple chứa nhãn và danh sách tọa độ

    #     return hands

    def findPosition(self, img, handNo=0, draw=True):
        """
        Tìm vị trí các điểm đặc trưng trên bàn tay
        Args:
            img: Ảnh đầu vào
            handNo: Số thứ tự bàn tay cần xử lý
            draw: Có vẽ các điểm đặc trưng hay không
        Returns:
            Danh sách các điểm đặc trưng với tọa độ (id, x, y)
        """
        lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                # Chuyển đổi tọa độ tỷ lệ sang tọa độ pixel
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])
                if draw:
                    # Vẽ điểm đặc trưng
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmList


# def main():
#     pTime = 0
#     cTime = 0
#     cap = cv2.VideoCapture(1)
#     detector = handDetector()
#     while True:
#         success, img = cap.read()
#         img = detector.findHands(img)
#         lmList = detector.findPosition(img)
#         if len(lmList) != 0:
#             print(lmList[4])
#
#         cTime = time.time()
#         fps = 1 / (cTime - pTime)
#         pTime = cTime
#
#         cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
#                     (255, 0, 255), 3)
#
#         cv2.imshow("Image", img)
#         cv2.waitKey(1)
#
#
# if __name__ == "__main__":
#     main()