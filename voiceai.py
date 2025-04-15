"""
Module xử lý nhận diện và thực thi lệnh giọng nói
Sử dụng thư viện speech_recognition để nhận diện giọng nói
và pyttsx3 để chuyển văn bản thành giọng nói
"""

import cv2  # Xử lý hình ảnh
import pyautogui  # Điều khiển chuột và bàn phím
import speech_recognition as sr  # Nhận diện giọng nói
import pyttsx3  # Chuyển văn bản thành giọng nói
import os  # Thao tác với hệ thống file
import tempfile  # Tạo file tạm
import re  # Xử lý biểu thức chính quy
import time  # Thời gian

import hand
from hand_gesture import HandGesture
from hidden_window import WindowControl
from scroll import AutoScroll
from shutdown import Shutdown
from tab_window import TabWindow
from volume import Volume

# Các hằng số cấu hình
DEFAULT_VOLUME_STEP = 5  # Bước tăng/giảm âm lượng mặc định
LANGUAGE_CODE = 'vi-VN'  # Mã ngôn ngữ cho nhận diện giọng nói
LISTENING_TIMEOUT = 15  # Thời gian lắng nghe tối đa (giây)

class VoiceAI:
    # Lớp xử lý nhận diện và thực thi lệnh giọng nói.
    def __init__(self):
        # Khởi tạo đối tượng VoiceAI với các thành phần điều khiển cần thiết.
        self.recognizer = sr.Recognizer()
        self.volume = Volume()
        self.auto_scroll = AutoScroll(screen_height=pyautogui.size()[1])
        self.shutdown = Shutdown()
        self.tab_window = TabWindow()
        
        # Cấu hình recognizer
        self.recognizer.energy_threshold = 4000  # Ngưỡng năng lượng âm thanh
        self.recognizer.dynamic_energy_threshold = True  # Tự động điều chỉnh ngưỡng
        self.recognizer.pause_threshold = 0.8  # Thời gian chờ giữa các từ
        self.recognizer.phrase_threshold = 0.3  # Ngưỡng cho cụm từ
        
        # Khởi tạo engine text-to-speech
        self.engine = pyttsx3.init()
        
        # Cấu hình giọng nói tiếng Việt
        voices = self.engine.getProperty('voices')
        for voice in voices:
            if 'vietnamese' in voice.name.lower():
                self.engine.setProperty('voice', voice.id)
                break
        
        # Cấu hình tốc độ và âm lượng
        self.engine.setProperty('rate', 150)  # Tốc độ nói
        self.engine.setProperty('volume', 1.0)  # Âm lượng

    def listen(self):
        try:
            with sr.Microphone() as source:
                print("Đang lắng nghe...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = self.recognizer.listen(source, timeout=3, phrase_time_limit=5)
                print("Đã thu âm xong, đang xử lý...")

                try:
                    command = self.recognizer.recognize_google(audio, language=LANGUAGE_CODE)
                    print(f"Bạn đã nói: {command}")
                    return command.lower()
                except sr.UnknownValueError:
                    print("Không thể nhận diện giọng nói.")
                except sr.RequestError as e:
                    print(f"Không thể kết nối đến dịch vụ nhận diện giọng nói: {e}")
                except sr.WaitTimeoutError:
                    print("Hết thời gian chờ giọng nói.")
        except sr.WaitTimeoutError:
            print("Timeout khi chờ microphone.")
        except Exception as e:
            print(f"Lỗi khi lắng nghe (bên ngoài): {e}")
        return None

    def speak(self, text):
        # Chuyển văn bản thành giọng nói và phát ra.
        # Args:
            # text (str): Văn bản cần chuyển thành giọng nói
        self.engine.say(text)
        self.engine.runAndWait()

    def _extract_number_from_command(self, command):
        # Trích xuất số từ lệnh giọng nói.
        # Args:
            # command (str): Lệnh giọng nói
        # Returns:
            # int: Số được trích xuất hoặc giá trị mặc định

        numbers = re.findall(r'\d+', command)
        return int(numbers[0]) if numbers else DEFAULT_VOLUME_STEP

    def _handle_volume_command(self, command, is_increase=True):
        """
        Xử lý lệnh điều chỉnh âm lượng
        """
        # Mở Quick Settings trước khi điều chỉnh âm lượng
        pyautogui.hotkey('win', 'a')
        # Đợi Quick Settings mở
        time.sleep(0.5)
        
        amount = self._extract_number_from_command(command)
        if is_increase:
            new_percent = self.volume.increase(amount)
            # self.speak(f"Âm lượng đã được tăng lên {new_percent} phần trăm.")
        else:
            new_percent = self.volume.decrease(amount)
            # self.speak(f"Âm lượng đã được giảm xuống {new_percent} phần trăm.")
        
        # Đợi một chút để người dùng thấy thanh âm lượng thay đổi
        time.sleep(1)
        # Đóng Quick Settings
        pyautogui.hotkey('win', 'a')

    def _handle_mouse_commands(self, command):
        """
        Xử lý các lệnh điều khiển chuột
        """
        try:
            if "nhấp đôi" in command or "double click" in command:
                pyautogui.doubleClick()
                # self.speak("Đã nhấp đôi.")
                return True
            elif "nhấp chuột" in command or "click chuột" in command:
                pyautogui.click()
                # self.speak("Đã nhấp chuột.")
                return True
            elif "chuột phải" in command or "right click" in command:
                pyautogui.rightClick()
                # self.speak("Đã nhấp chuột phải.")
                return True
            elif "chuột trái" in command or "left click" in command:
                pyautogui.leftClick()
                # self.speak("Đã nhấp chuột trái.")
                return True
            elif "chuột qua phải" in command:
                current_x, current_y = pyautogui.position()
                pyautogui.moveTo(current_x + 25, current_y, duration=0.5)
                # self.speak("Đã di chuột qua phải.")
                return True
            elif "chuột qua trái" in command:
                current_x, current_y = pyautogui.position()
                pyautogui.moveTo(current_x - 25, current_y, duration=0.5)
                # self.speak("Đã di chuột qua trái.")
                return True
            elif "chuột lên" in command:
                current_x, current_y = pyautogui.position()
                pyautogui.moveTo(current_x, current_y - 25, duration=0.5)
                # self.speak("Đã di chuột lên.")
                return True
            elif "chuột xuống" in command:
                current_x, current_y = pyautogui.position()
                pyautogui.moveTo(current_x, current_y + 25, duration=0.5)
                # self.speak("Đã di chuột xuống.")
                return True
            elif "nhập chữ" in command:
                print("=== Bắt đầu chế độ nhập văn bản ===")
                self.speak("Vui lòng nói nội dung cần nhập. Nói 'dừng nhập' để kết thúc.")
                is_typing = True
                
                while is_typing:
                    try:
                        print("Đang chờ nội dung cần nhập...")
                        text = self.listen()
                        
                        if not text:
                            print("Không nhận diện được giọng nói, vui lòng thử lại.")
                            continue
                            
                        print(f"Nhận diện được: {text}")
                        
                        if "dừng nhập" in text.lower():
                            print("=== Đã nhận lệnh dừng nhập ===")
                            self.speak("Đã dừng nhập.")
                            is_typing = False
                            break
                            
                        # Xóa khoảng trắng thừa và chuẩn hóa văn bản
                        text = ' '.join(text.split())
                        print(f"Văn bản đã chuẩn hóa: {text}")
                        
                        try:
                            # Tạm thời tắt độ trễ của pyautogui
                            pyautogui.PAUSE = 0
                            print("Bắt đầu nhập ký tự...")
                            
                            # Nhập từng ký tự với độ trễ nhỏ hơn
                            for char in text:
                                print(f"Đang nhập ký tự: {char}")
                                pyautogui.write(char)
                                time.sleep(0.1)
                            
                            # Thêm khoảng trắng sau mỗi từ
                            pyautogui.write(' ')
                            time.sleep(0.1)
                            print("Đã nhập xong một từ.")
                            
                        except Exception as e:
                            print(f"Lỗi khi nhập ký tự: {e}")
                            continue
                        finally:
                            # Reset lại độ trễ mặc định
                            pyautogui.PAUSE = 0.1
                            
                        self.speak(f"Đã nhập: {text}")
                        print(f"Đã hoàn thành nhập: {text}")
                        
                    except Exception as e:
                        print(f"Lỗi trong quá trình nhập văn bản: {e}")
                        continue
                
                print("=== Kết thúc chế độ nhập văn bản ===")
                return True
            elif "xóa chữ" in command:
                # Trích xuất số lượng chữ cần xóa từ lệnh
                numbers = re.findall(r'\d+', command)
                if numbers:
                    count = int(numbers[0])
                    print(f"Đang xóa {count} ký tự...")
                    # Tạm thời tắt độ trễ của pyautogui
                    pyautogui.PAUSE = 0
                    try:
                        for _ in range(count):
                            pyautogui.press('backspace')
                            time.sleep(0.05)  # Giảm độ trễ xuống 0.05 giây
                        print(f"Đã xóa {count} ký tự.")
                    except Exception as e:
                        print(f"Lỗi khi xóa ký tự: {e}")
                    finally:
                        # Reset lại độ trễ mặc định
                        pyautogui.PAUSE = 0.1
                else:
                    # Nếu không có số lượng cụ thể, xóa một ký tự
                    pyautogui.press('backspace')
                    print("Đã xóa một ký tự.")
                return True
            elif "xóa từ" in command:
                # Trích xuất số lượng từ cần xóa từ lệnh
                numbers = re.findall(r'\d+', command)
                if numbers:
                    count = int(numbers[0])
                    for _ in range(count):
                        pyautogui.hotkey('ctrl', 'backspace')
                    # self.speak(f"Đã xóa {count} từ.")
                else:
                    pyautogui.hotkey('ctrl', 'backspace')
                    # self.speak("Đã xóa một từ.")
                return True
            elif "bôi đen" in command:
                # Trích xuất số lượng từ cần bôi đen từ lệnh
                numbers = re.findall(r'\d+', command)
                if numbers:
                    count = int(numbers[0])
                    for _ in range(count):
                        pyautogui.hotkey('shift', 'right')
                        time.sleep(0.1)  # Thêm độ trễ giữa các lần bôi đen
                    print(f"Đã bôi đen {count} từ.")  # Thêm log để kiểm tra
                else:
                    pyautogui.hotkey('shift', 'right')
                    print("Đã bôi đen một từ.")  # Thêm log để kiểm tra
                return True
            elif "copy" in command or "sao chép" in command:
                pyautogui.hotkey('ctrl', 'c')
                print("Đã sao chép.")  # Thêm log để kiểm tra
                return True
            elif "dán chữ" in command or "paste" in command:
                pyautogui.hotkey('ctrl', 'v')
                print("Đã dán.")  # Thêm log để kiểm tra
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi xử lý lệnh chuột: {e}")
            # self.speak("Không thể thực hiện lệnh chuột.")
            return False

    def _handle_text_commands(self, command):
        """
        Xử lý các lệnh nhập và xóa văn bản
        """
        try:
            if "nhập chữ" in command:
                print("=== Bắt đầu chế độ nhập văn bản ===")
                self.speak("Vui lòng nói nội dung cần nhập. Nói 'dừng nhập' để kết thúc.")
                is_typing = True
                
                while is_typing:
                    try:
                        print("Đang chờ nội dung cần nhập...")
                        text = self.listen()
                        
                        if not text:
                            print("Không nhận diện được giọng nói, vui lòng thử lại.")
                            continue
                            
                        print(f"Nhận diện được: {text}")
                        
                        if "dừng nhập" in text.lower():
                            print("=== Đã nhận lệnh dừng nhập ===")
                            self.speak("Đã dừng nhập.")
                            is_typing = False
                            break
                            
                        # Xóa khoảng trắng thừa và chuẩn hóa văn bản
                        text = ' '.join(text.split())
                        print(f"Văn bản đã chuẩn hóa: {text}")
                        
                        try:
                            # Tạm thời tắt độ trễ của pyautogui
                            pyautogui.PAUSE = 0
                            print("Bắt đầu nhập ký tự...")
                            
                            # Nhập từng ký tự với độ trễ nhỏ hơn
                            for char in text:
                                print(f"Đang nhập ký tự: {char}")
                                pyautogui.write(char)
                                time.sleep(0.1)
                            
                            # Thêm khoảng trắng sau mỗi từ
                            pyautogui.write(' ')
                            time.sleep(0.1)
                            print("Đã nhập xong một từ.")
                            
                        except Exception as e:
                            print(f"Lỗi khi nhập ký tự: {e}")
                            continue
                        finally:
                            # Reset lại độ trễ mặc định
                            pyautogui.PAUSE = 0.1
                            
                        self.speak(f"Đã nhập: {text}")
                        print(f"Đã hoàn thành nhập: {text}")
                        
                    except Exception as e:
                        print(f"Lỗi trong quá trình nhập văn bản: {e}")
                        continue
                
                print("=== Kết thúc chế độ nhập văn bản ===")
                return True
            elif "xóa chữ" in command:
                # Trích xuất số lượng chữ cần xóa từ lệnh
                numbers = re.findall(r'\d+', command)
                if numbers:
                    count = int(numbers[0])
                    print(f"Đang xóa {count} ký tự...")
                    # Tạm thời tắt độ trễ của pyautogui
                    pyautogui.PAUSE = 0
                    try:
                        for _ in range(count):
                            pyautogui.press('backspace')
                            time.sleep(0.05)  # Giảm độ trễ xuống 0.05 giây
                        print(f"Đã xóa {count} ký tự.")
                    except Exception as e:
                        print(f"Lỗi khi xóa ký tự: {e}")
                    finally:
                        # Reset lại độ trễ mặc định
                        pyautogui.PAUSE = 0.1
                else:
                    # Nếu không có số lượng cụ thể, xóa một ký tự
                    pyautogui.press('backspace')
                    print("Đã xóa một ký tự.")
                return True
            elif "xóa từ" in command:
                # Trích xuất số lượng từ cần xóa từ lệnh
                numbers = re.findall(r'\d+', command)
                if numbers:
                    count = int(numbers[0])
                    for _ in range(count):
                        pyautogui.hotkey('ctrl', 'backspace')
                    # self.speak(f"Đã xóa {count} từ.")
                else:
                    pyautogui.hotkey('ctrl', 'backspace')
                    # self.speak("Đã xóa một từ.")
                return True
            elif "bôi đen" in command:
                # Trích xuất số lượng từ cần bôi đen từ lệnh
                numbers = re.findall(r'\d+', command)
                if numbers:
                    count = int(numbers[0])
                    for _ in range(count):
                        pyautogui.hotkey('shift', 'right')
                        time.sleep(0.1)  # Thêm độ trễ giữa các lần bôi đen
                    print(f"Đã bôi đen {count} từ.")  # Thêm log để kiểm tra
                else:
                    pyautogui.hotkey('shift', 'right')
                    print("Đã bôi đen một từ.")  # Thêm log để kiểm tra
                return True
            elif "copy" in command or "sao chép" in command:
                pyautogui.hotkey('ctrl', 'c')
                print("Đã sao chép.")  # Thêm log để kiểm tra
                return True
            elif "dán chữ" in command or "paste" in command:
                pyautogui.hotkey('ctrl', 'v')
                print("Đã dán.")  # Thêm log để kiểm tra
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi xử lý lệnh văn bản: {e}")
            return False

    def _handle_app_commands(self, command):
        """
        Xử lý các lệnh mở và đóng ứng dụng
        """
        try:
            if "đóng cửa sổ" in command:
                pyautogui.hotkey('alt', 'f4')
                # self.speak("Đã đóng cửa sổ.")
                return True
            elif "cài đặt" in command or "setting" in command:
                pyautogui.hotkey('win', 'i')
                print("Đã mở cài đặt Windows.")  # Thêm log để kiểm tra
                return True
            elif "mở" in command:
                # Trích xuất tên ứng dụng từ lệnh
                app_name = command.replace("mở", "").strip()
                if app_name:
                    # Mở ứng dụng bằng cách nhấn phím Windows và nhập tên ứng dụng
                    pyautogui.hotkey('win')
                    time.sleep(0.5)  # Đợi menu Start mở
                    pyautogui.write(app_name)
                    time.sleep(0.5)  # Đợi kết quả tìm kiếm
                    pyautogui.press('enter')
                    print(f"Đang mở {app_name}...")  # Thêm log để kiểm tra
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi xử lý lệnh ứng dụng: {e}")
            return False

    def process_command(self, command):
        # Xử lý lệnh giọng nói
        # Args:
            # command (str): Lệnh cần xử lý
        if not command:
            return

        # Xử lý các lệnh chuột
        if self._handle_mouse_commands(command):
            return

        # Xử lý các lệnh văn bản
        if self._handle_text_commands(command):
            return

        # Xử lý các lệnh ứng dụng
        if self._handle_app_commands(command):
            return

        if "tăng âm lượng" in command or "tăng âm" in command:
            self._handle_volume_command(command, is_increase=True)
        elif "giảm âm lượng" in command or "giảm âm" in command:
            self._handle_volume_command(command, is_increase=False)
        elif "lướt xuống" in command:
            self.auto_scroll.start_scroll()
            # self.speak("Đang lướt xuống.")
        elif "lướt lên" in command:
            self.auto_scroll.start_scroll_up()
            # self.speak("Đang lướt lên.")
        elif "dừng lại" in command:
            self.auto_scroll.stop_scroll()
            # self.speak("Đã dừng lướt.")
        elif "tắt máy" in command:
            self.shutdown.shutdown_computer()
            # self.speak("Máy tính sẽ tắt.")
        elif "mở trang" in command:
            self.tab_window.open_tab()
            # self.speak("Đang mở trang.")
        elif "chuyển trang" in command:
            self.tab_window.open_tab()  # Sử dụng cùng hàm với mở tab
            # self.speak("Đang chuyển trang.")
        elif "cửa sổ" in command:
            self.tab_window.open_tab()  # Sử dụng cùng hàm với mở tab
            # self.speak("Đang mở chế độ chuyển cửa sổ.")
        elif "qua phải" in command:
            if self.tab_window.alt_tab_active:
                self.tab_window.switch_tab_right()
                # self.speak("Chuyển qua phải.")
            else:
                # self.speak("Vui lòng mở chế độ chuyển cửa sổ trước.")
                pass
        elif "qua trái" in command:
            if self.tab_window.alt_tab_active:
                self.tab_window.switch_tab_left()
                # self.speak("Chuyển qua trái.")
            else:
                # self.speak("Vui lòng mở chế độ chuyển cửa sổ trước.")
                pass
        elif "chọn trang" in command:
            if self.tab_window.alt_tab_active:
                self.tab_window.select_tab()
                # self.speak("Đã chọn.")
            else:
                # self.speak("Vui lòng mở chế độ chuyển cửa sổ trước.")
                pass
        else:
            print("Lệnh không được nhận diện.")
            # self.speak("Xin lỗi, lệnh không được nhận diện.")

def main():
    # Hàm chính để chạy ứng dụng VoiceAI.
    voice_ai = VoiceAI()
    print("Trợ lý ảo đã sẵn sàng.")
    while True:
        command = voice_ai.listen()
        voice_ai.process_command(command)

if __name__ == "__main__":
    main()   