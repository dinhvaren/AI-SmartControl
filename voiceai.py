"""
Module xử lý nhận diện và thực thi lệnh giọng nói
Sử dụng thư viện speech_recognition để nhận diện giọng nói
và gTTS để chuyển văn bản thành giọng nói
"""

import cv2  # Xử lý hình ảnh
import pyautogui  # Điều khiển chuột và bàn phím
import speech_recognition as sr  # Nhận diện giọng nói
from gtts import gTTS  # Chuyển văn bản thành giọng nói
import os  # Thao tác với hệ thống file
import tempfile  # Tạo file tạm
import re  # Xử lý biểu thức chính quy
import time  # Thời gian
import pygame  # Phát âm thanh
import webbrowser
import subprocess
from typing import Optional
import openai
from dotenv import load_dotenv

import hand
from hand_gesture import HandGesture
from hidden_window import WindowControl
from scroll import AutoScroll
from shutdown import Shutdown
from tab_window import TabWindow
from volume import Volume

# Load biến môi trường từ file .env
load_dotenv()

# Cấu hình OpenAI API key từ biến môi trường
openai.api_key = os.getenv('OPENAI_API_KEY')

# Kiểm tra API key
if not openai.api_key:
    raise ValueError("Không tìm thấy OPENAI_API_KEY trong file .env")

# Các hằng số cấu hình
DEFAULT_VOLUME_STEP = 5  # Bước tăng/giảm âm lượng mặc định
LANGUAGE_CODE = 'vi-VN'  # Mã ngôn ngữ cho nhận diện giọng nói
LISTENING_TIMEOUT = 15  # Thời gian lắng nghe tối đa (giây)

class ChromeControl:
    def __init__(self):
        self.chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        self.chrome_process = None

    def open_chrome(self):
        """Mở Chrome nếu chưa mở"""
        try:
            subprocess.Popen([self.chrome_path])
            time.sleep(1)  # Đợi Chrome mở
            return True
        except Exception as e:
            print(f"Lỗi khi mở Chrome: {e}")
            return False

    def new_tab(self):
        """Mở tab mới"""
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.5)

    def close_tab(self):
        """Đóng tab hiện tại"""
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(0.5)

    def reopen_tab(self):
        """Mở lại tab đã đóng"""
        pyautogui.hotkey('ctrl', 'shift', 't')
        time.sleep(0.5)

    def switch_tab(self, tab_number: int):
        """Chuyển đến tab số [tab_number]"""
        pyautogui.hotkey('ctrl', str(tab_number))
        time.sleep(0.5)

    def move_tab_right(self):
        """Di chuyển tab sang phải"""
        pyautogui.hotkey('ctrl', 'shift', 'pgdn')
        time.sleep(0.5)

    def move_tab_left(self):
        """Di chuyển tab sang trái"""
        pyautogui.hotkey('ctrl', 'shift', 'pgup')
        time.sleep(0.5)

    def pin_tab(self):
        """Ghim tab hiện tại"""
        pyautogui.hotkey('ctrl', 'shift', 'p')
        time.sleep(0.5)

    def unpin_tab(self):
        """Bỏ ghim tab"""
        pyautogui.hotkey('ctrl', 'shift', 'p')
        time.sleep(0.5)

    def new_incognito(self):
        """Mở tab ẩn danh"""
        pyautogui.hotkey('ctrl', 'shift', 'n')
        time.sleep(0.5)

    def close_all_tabs(self):
        """Đóng tất cả các tab"""
        pyautogui.hotkey('ctrl', 'shift', 'w')
        time.sleep(0.5)

    def refresh_page(self):
        """Làm mới trang"""
        pyautogui.hotkey('ctrl', 'r')
        time.sleep(0.5)

    def stop_loading(self):
        """Dừng tải trang"""
        pyautogui.press('esc')
        time.sleep(0.5)

    def zoom_in(self):
        """Phóng to trang"""
        pyautogui.hotkey('ctrl', '+')
        time.sleep(0.5)

    def zoom_out(self):
        """Thu nhỏ trang"""
        pyautogui.hotkey('ctrl', '-')
        time.sleep(0.5)

    def reset_zoom(self):
        """Đặt lại tỷ lệ zoom"""
        pyautogui.hotkey('ctrl', '0')
        time.sleep(0.5)

    def open_history(self):
        """Mở lịch sử"""
        pyautogui.hotkey('ctrl', 'h')
        time.sleep(0.5)

    def open_bookmarks(self):
        """Mở dấu trang"""
        pyautogui.hotkey('ctrl', 'shift', 'o')
        time.sleep(0.5)

    def bookmark_page(self):
        """Đánh dấu trang hiện tại"""
        pyautogui.hotkey('ctrl', 'd')
        time.sleep(0.5)

    def open_downloads(self):
        """Mở trang tải xuống"""
        pyautogui.hotkey('ctrl', 'j')
        time.sleep(0.5)

    def open_settings(self):
        """Mở cài đặt"""
        pyautogui.hotkey('alt', 'f')
        time.sleep(0.5)
        pyautogui.press('s')
        time.sleep(0.5)

    def open_extensions(self):
        """Mở trang tiện ích"""
        pyautogui.hotkey('alt', 'f')
        time.sleep(0.5)
        pyautogui.press('e')
        time.sleep(0.5)

    def open_dev_tools(self):
        """Mở công cụ nhà phát triển"""
        pyautogui.hotkey('ctrl', 'shift', 'i')
        time.sleep(0.5)

    def inspect_element(self):
        """Kiểm tra phần tử"""
        pyautogui.hotkey('ctrl', 'shift', 'c')
        time.sleep(0.5)

    def view_source(self):
        """Xem mã nguồn"""
        pyautogui.hotkey('ctrl', 'u')
        time.sleep(0.5)

    def clear_browsing_data(self):
        """Xóa dữ liệu duyệt web"""
        pyautogui.hotkey('ctrl', 'shift', 'delete')
        time.sleep(0.5)

    def open_chrome_store(self):
        """Mở cửa hàng tiện ích"""
        webbrowser.open('https://chrome.google.com/webstore')
        time.sleep(0.5)

    def search_in_page(self, text: str):
        """Tìm kiếm trong trang"""
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        pyautogui.write(text)
        time.sleep(0.5)

    def translate_page(self):
        """Dịch trang"""
        pyautogui.hotkey('alt', 'f')
        time.sleep(0.5)
        pyautogui.press('t')
        time.sleep(0.5)

    def save_page(self):
        """Lưu trang"""
        pyautogui.hotkey('ctrl', 's')
        time.sleep(0.5)

    def print_page(self):
        """In trang"""
        pyautogui.hotkey('ctrl', 'p')
        time.sleep(0.5)

    def open_new_window(self):
        """Mở cửa sổ mới"""
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(0.5)

    def close_window(self):
        """Đóng cửa sổ"""
        pyautogui.hotkey('alt', 'f4')
        time.sleep(0.5)

    def minimize_window(self):
        """Thu nhỏ cửa sổ"""
        pyautogui.hotkey('win', 'down')
        time.sleep(0.5)

    def maximize_window(self):
        """Phóng to cửa sổ"""
        pyautogui.hotkey('win', 'up')
        time.sleep(0.5)

    def restore_window(self):
        """Khôi phục cửa sổ"""
        pyautogui.hotkey('win', 'down')
        time.sleep(0.5)
        pyautogui.hotkey('win', 'up')
        time.sleep(0.5)

class YouTubeControl:
    def __init__(self):
        self.chrome = ChromeControl()
        self.youtube_url = "https://www.youtube.com"

    def open_youtube(self):
        """Mở YouTube"""
        webbrowser.open(self.youtube_url)
        time.sleep(1)

    def play_pause(self):
        """Phát/Tạm dừng video"""
        pyautogui.press('k')
        time.sleep(0.5)

    def next_video(self):
        """Chuyển sang video tiếp theo"""
        pyautogui.hotkey('shift', 'n')
        time.sleep(0.5)

    def previous_video(self):
        """Quay lại video trước"""
        pyautogui.hotkey('shift', 'p')
        time.sleep(0.5)

    def volume_up(self):
        """Tăng âm lượng"""
        pyautogui.press('up')
        time.sleep(0.5)

    def volume_down(self):
        """Giảm âm lượng"""
        pyautogui.press('down')
        time.sleep(0.5)

    def mute(self):
        """Tắt tiếng"""
        pyautogui.press('m')
        time.sleep(0.5)

    def fullscreen(self):
        """Bật/tắt chế độ toàn màn hình"""
        pyautogui.press('f')
        time.sleep(0.5)

    def theater_mode(self):
        """Bật/tắt chế độ rạp hát"""
        pyautogui.press('t')
        time.sleep(0.5)

    def forward(self):
        """Tua nhanh 5 giây"""
        pyautogui.press('right')
        time.sleep(0.5)

    def backward(self):
        """Tua lùi 5 giây"""
        pyautogui.press('left')
        time.sleep(0.5)

    def speed_up(self):
        """Tăng tốc độ phát"""
        pyautogui.hotkey('shift', '.')
        time.sleep(0.5)

    def speed_down(self):
        """Giảm tốc độ phát"""
        pyautogui.hotkey('shift', ',')
        time.sleep(0.5)

    def reset_speed(self):
        """Đặt lại tốc độ phát"""
        pyautogui.hotkey('shift', '0')
        time.sleep(0.5)

    def like_video(self):
        """Thích video"""
        pyautogui.hotkey('shift', 'l')
        time.sleep(0.5)

    def dislike_video(self):
        """Không thích video"""
        pyautogui.hotkey('shift', 'd')
        time.sleep(0.5)

    def subscribe(self):
        """Đăng ký kênh"""
        pyautogui.hotkey('shift', 's')
        time.sleep(0.5)

    def search(self, query):
        """Tìm kiếm trên YouTube"""
        pyautogui.hotkey('ctrl', 'l')  # Chọn thanh địa chỉ
        time.sleep(0.5)
        pyautogui.write(f"{self.youtube_url}/results?search_query={query}")
        pyautogui.press('enter')
        time.sleep(1)

class TextControl:
    def __init__(self):
        pass

    def select_all(self):
        """Chọn toàn bộ văn bản"""
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)

    def cut(self):
        """Cắt văn bản đã chọn"""
        pyautogui.hotkey('ctrl', 'x')
        time.sleep(0.5)

    def delete_line(self):
        """Xóa dòng hiện tại"""
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

    def delete_paragraph(self):
        """Xóa đoạn văn bản hiện tại"""
        pyautogui.hotkey('ctrl', 'd')
        time.sleep(0.5)

    def delete_to_line_start(self):
        """Xóa từ vị trí con trỏ đến đầu dòng"""
        pyautogui.hotkey('ctrl', 'backspace')
        time.sleep(0.5)

    def delete_to_line_end(self):
        """Xóa từ vị trí con trỏ đến cuối dòng"""
        pyautogui.hotkey('ctrl', 'delete')
        time.sleep(0.5)

    def bold(self):
        """Bật/tắt in đậm"""
        pyautogui.hotkey('ctrl', 'b')
        time.sleep(0.5)

    def italic(self):
        """Bật/tắt in nghiêng"""
        pyautogui.hotkey('ctrl', 'i')
        time.sleep(0.5)

    def underline(self):
        """Bật/tắt gạch chân"""
        pyautogui.hotkey('ctrl', 'u')
        time.sleep(0.5)

    def strikethrough(self):
        """Bật/tắt gạch ngang"""
        pyautogui.hotkey('ctrl', 'shift', 'x')
        time.sleep(0.5)

    def increase_font_size(self):
        """Tăng cỡ chữ"""
        pyautogui.hotkey('ctrl', 'shift', '>')
        time.sleep(0.5)

    def decrease_font_size(self):
        """Giảm cỡ chữ"""
        pyautogui.hotkey('ctrl', 'shift', '<')
        time.sleep(0.5)

    def align_left(self):
        """Căn lề trái"""
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.5)

    def align_right(self):
        """Căn lề phải"""
        pyautogui.hotkey('ctrl', 'r')
        time.sleep(0.5)

    def align_center(self):
        """Căn lề giữa"""
        pyautogui.hotkey('ctrl', 'e')
        time.sleep(0.5)

    def align_justify(self):
        """Căn đều hai bên"""
        pyautogui.hotkey('ctrl', 'j')
        time.sleep(0.5)

    def move_up(self):
        """Di chuyển con trỏ lên dòng"""
        pyautogui.press('up')
        time.sleep(0.5)

    def move_down(self):
        """Di chuyển con trỏ xuống dòng"""
        pyautogui.press('down')
        time.sleep(0.5)

    def move_to_line_start(self):
        """Di chuyển con trỏ về đầu dòng"""
        pyautogui.hotkey('home')
        time.sleep(0.5)

    def move_to_line_end(self):
        """Di chuyển con trỏ đến cuối dòng"""
        pyautogui.hotkey('end')
        time.sleep(0.5)

    def move_to_page_start(self):
        """Di chuyển con trỏ lên đầu trang"""
        pyautogui.hotkey('ctrl', 'home')
        time.sleep(0.5)

    def move_to_page_end(self):
        """Di chuyển con trỏ xuống cuối trang"""
        pyautogui.hotkey('ctrl', 'end')
        time.sleep(0.5)

    def move_to_doc_start(self):
        """Di chuyển con trỏ lên đầu tài liệu"""
        pyautogui.hotkey('ctrl', 'home')
        time.sleep(0.5)

    def move_to_doc_end(self):
        """Di chuyển con trỏ xuống cuối tài liệu"""
        pyautogui.hotkey('ctrl', 'end')
        time.sleep(0.5)

    def indent(self):
        """Thụt lề đoạn văn"""
        pyautogui.hotkey('tab')
        time.sleep(0.5)

    def unindent(self):
        """Bỏ thụt lề đoạn văn"""
        pyautogui.hotkey('shift', 'tab')
        time.sleep(0.5)

    def create_numbered_list(self):
        """Tạo danh sách đánh số"""
        pyautogui.hotkey('ctrl', 'shift', 'l')
        time.sleep(0.5)

    def create_bullet_list(self):
        """Tạo danh sách gạch đầu dòng"""
        pyautogui.hotkey('ctrl', 'shift', 'l')
        time.sleep(0.5)

    def increase_line_spacing(self):
        """Tăng khoảng cách giữa các dòng"""
        pyautogui.hotkey('ctrl', '2')
        time.sleep(0.5)

    def decrease_line_spacing(self):
        """Giảm khoảng cách giữa các dòng"""
        pyautogui.hotkey('ctrl', '1')
        time.sleep(0.5)

    def find_text(self, text: str):
        """Tìm kiếm từ khóa trong văn bản"""
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        pyautogui.write(text)
        time.sleep(0.5)

    def find_next(self):
        """Tìm kiếm từ khóa tiếp theo"""
        pyautogui.hotkey('f3')
        time.sleep(0.5)

    def replace_text(self, old_text: str, new_text: str):
        """Thay thế từ cũ bằng từ mới"""
        pyautogui.hotkey('ctrl', 'h')
        time.sleep(0.5)
        pyautogui.write(old_text)
        pyautogui.press('tab')
        pyautogui.write(new_text)
        pyautogui.press('enter')
        time.sleep(0.5)

    def replace_all(self, old_text: str, new_text: str):
        """Thay thế tất cả từ cũ bằng từ mới"""
        pyautogui.hotkey('ctrl', 'h')
        time.sleep(0.5)
        pyautogui.write(old_text)
        pyautogui.press('tab')
        pyautogui.write(new_text)
        pyautogui.hotkey('alt', 'a')
        time.sleep(0.5)

    def undo(self):
        """Hoàn tác thao tác vừa thực hiện"""
        pyautogui.hotkey('ctrl', 'z')
        time.sleep(0.5)

    def redo(self):
        """Làm lại thao tác vừa hoàn tác"""
        pyautogui.hotkey('ctrl', 'y')
        time.sleep(0.5)

class VoiceAI:
    def __init__(self):
        # Khởi tạo đối tượng VoiceAI với các thành phần điều khiển cần thiết
        self.recognizer = sr.Recognizer()
        self.volume = Volume()
        self.auto_scroll = AutoScroll(screen_height=pyautogui.size()[1])
        self.shutdown = Shutdown()
        self.tab_window = TabWindow()
        self.chrome = ChromeControl()
        self.youtube = YouTubeControl()
        self.mouse_dragging = False
        self.is_listening = False
        self.text_control = TextControl()
        
        # Khởi tạo các thành phần cho trợ lý ảo
        self.conversation_history = []
        self.max_turns = 30
        self.is_assistant_mode = False
        
        # Cấu hình recognizer
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.recognizer.phrase_threshold = 0.3
        self.recognizer.non_speaking_duration = 0.5
        
        # Khởi tạo pygame mixer
        pygame.mixer.init()
        
        # Tạo thư mục tạm để lưu file âm thanh
        self.temp_dir = tempfile.mkdtemp()

    def add_to_history(self, role, content):
        """Thêm một lượt vào lịch sử hội thoại"""
        self.conversation_history.append({"role": role, "content": content})
        if len(self.conversation_history) > self.max_turns:
            system_message = next((msg for msg in self.conversation_history if msg["role"] == "system"), None)
            self.conversation_history = self.conversation_history[-self.max_turns:]
            if system_message and system_message not in self.conversation_history:
                self.conversation_history.insert(0, system_message)

    def get_chatgpt_response(self, prompt):
        """Lấy phản hồi từ ChatGPT"""
        try:
            self.add_to_history("user", prompt)
            
            messages = [
                {"role": "system", "content": "Bạn là một trợ lý ảo thông minh và hữu ích, có khả năng hiểu và trả lời bằng tiếng Việt một cách tự nhiên."}
            ] + self.conversation_history
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            assistant_response = response.choices[0].message.content
            self.add_to_history("assistant", assistant_response)
            
            return assistant_response
        except openai.error.RateLimitError:
            print("Lỗi: Đã vượt quá giới hạn sử dụng API. Vui lòng kiểm tra tài khoản OpenAI của bạn.")
            return None
        except openai.error.AuthenticationError:
            print("Lỗi: API key không hợp lệ hoặc đã hết hạn. Vui lòng kiểm tra lại API key.")
            return None
        except Exception as e:
            print(f"Lỗi không xác định khi gọi OpenAI API: {str(e)}")
            return None

    def listen(self):
        try:
            with sr.Microphone() as source:
                print("Đang chờ lệnh 'Điều Khiển' hoặc 'Trợ Lý Ảo'...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                max_attempts = 3
                for attempt in range(max_attempts):
                    try:
                        audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                        print("Đã thu âm xong, đang xử lý...")

                        command = self.recognizer.recognize_google(audio, language=LANGUAGE_CODE)
                        print(f"Bạn đã nói: {command}")
                        
                        # Kiểm tra nếu người dùng nói "Trợ Lý Ảo"
                        if "trợ lý ảo" in command.lower():
                            print("Đã nhận lệnh 'Trợ Lý Ảo', chuyển sang chế độ trợ lý...")
                            self.speak("Đã chuyển sang chế độ trợ lý ảo, vui lòng nói câu hỏi của bạn.")
                            self.is_assistant_mode = True
                            self.is_listening = True
                            
                            # Lắng nghe câu hỏi
                            for cmd_attempt in range(max_attempts):
                                try:
                                    audio = self.recognizer.listen(source, timeout=10)
                                    question = self.recognizer.recognize_google(audio, language=LANGUAGE_CODE)
                                    print(f"Câu hỏi: {question}")
                                    
                                    # Nếu lệnh là "dừng trợ lý" thì tắt chế độ trợ lý
                                    if "dừng trợ lý" in question.lower():
                                        print("Đã nhận lệnh 'Dừng trợ lý'")
                                        self.is_assistant_mode = False
                                        self.is_listening = False
                                        self.speak("Đã tắt chế độ trợ lý ảo. Để tiếp tục, vui lòng nói 'điều khiển' hoặc 'trợ lý ảo'.")
                                        return None
                                        
                                    # Xử lý câu hỏi với ChatGPT
                                    response = self.get_chatgpt_response(question)
                                    if response:
                                        self.speak(response)
                                    return None
                                    
                                except sr.UnknownValueError:
                                    if cmd_attempt < max_attempts - 1:
                                        print("Không nghe rõ, vui lòng nói lại...")
                                        continue
                                    else:
                                        print("Không thể nhận diện giọng nói sau nhiều lần thử.")
                                        return None
                        
                        # Kiểm tra nếu người dùng nói "Điều Khiển" hoặc đang trong chế độ lắng nghe
                        elif "điều khiển" in command.lower() or self.is_listening:
                            if "điều khiển" in command.lower():
                                print("Đã nhận lệnh 'Điều Khiển', đang lắng nghe trong 5 giây...")
                                self.speak("Đã nhận lệnh điều khiển, vui lòng nói lệnh tiếp theo.")
                                self.is_listening = True
                                self.is_assistant_mode = False
                                
                            # Lắng nghe lệnh thực sự
                            for cmd_attempt in range(max_attempts):
                                try:
                                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                                    command = self.recognizer.recognize_google(audio, language=LANGUAGE_CODE)
                                    print(f"Lệnh thực hiện: {command}")
                                    
                                    # Nếu lệnh là "dừng điều khiển" thì tắt chế độ lắng nghe
                                    if "dừng điều khiển" in command.lower():
                                        print("Đã nhận lệnh 'Dừng điều khiển'")
                                        self.is_listening = False
                                        self.speak("Hệ thống đã dừng lắng nghe lệnh. Để tiếp tục, vui lòng nói 'điều khiển' hoặc 'trợ lý ảo'.")
                                        return None
                                        
                                    return command.lower()
                                except sr.UnknownValueError:
                                    if cmd_attempt < max_attempts - 1:
                                        print("Không nghe rõ, vui lòng nói lại...")
                                        continue
                                    else:
                                        print("Không thể nhận diện giọng nói sau nhiều lần thử.")
                                        return None
                                        
                        else:
                            print("Không nhận được lệnh 'Điều Khiển' hoặc 'Trợ Lý Ảo'")
                            return None
                            
                    except sr.UnknownValueError:
                        if attempt < max_attempts - 1:
                            print("Không nghe rõ, vui lòng nói lại...")
                            self.speak("Xin lỗi, tôi không nghe rõ. Vui lòng nói lại.")
                            continue
                        else:
                            print("Không thể nhận diện giọng nói sau nhiều lần thử.")
                            return None
                            
        except sr.RequestError as e:
            print(f"Không thể kết nối đến dịch vụ nhận diện giọng nói: {e}")
        except sr.WaitTimeoutError:
            print("Hết thời gian chờ giọng nói.")
            self.is_listening = False
            self.speak("Đã hết thời gian chờ lệnh. Để tiếp tục, vui lòng nói 'điều khiển' hoặc 'trợ lý ảo'.")
        except Exception as e:
            print(f"Lỗi khi lắng nghe (bên ngoài): {e}")
            self.is_listening = False
        return None

    def speak(self, text):
        try:
            # Tạo file âm thanh tạm
            temp_file = os.path.join(self.temp_dir, "temp.mp3")
            
            # Chuyển văn bản thành giọng nói
            tts = gTTS(text=text, lang='vi', slow=False)
            tts.save(temp_file)
            
            # Phát âm thanh trực tiếp bằng pygame
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Đợi cho đến khi phát xong
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Dừng phát nhạc và giải phóng tài nguyên
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            # Đợi một chút để đảm bảo file được giải phóng
            time.sleep(0.5)
            
            # Xóa file tạm sau khi phát xong
            try:
                os.remove(temp_file)
            except PermissionError:
                # Nếu không thể xóa ngay lập tức, thử lại sau 1 giây
                time.sleep(1)
                try:
                    os.remove(temp_file)
                except PermissionError:
                    print("Không thể xóa file tạm, sẽ được xóa trong lần chạy tiếp theo")
            
        except Exception as e:
            print(f"Lỗi khi phát âm thanh: {e}")

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
            self.speak(f"Âm lượng đã được tăng lên {new_percent} phần trăm.")
        else:
            new_percent = self.volume.decrease(amount)
            self.speak(f"Âm lượng đã được giảm xuống {new_percent} phần trăm.")
        
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
                self.speak("Đã nhấp đôi.")
                return True
            elif "nhấp chuột" in command or "click chuột" in command:
                pyautogui.click()
                self.speak("Đã nhấp chuột.")
                return True
            elif "chuột phải" in command or "right click" in command:
                pyautogui.rightClick()
                self.speak("Đã nhấp chuột phải.")
                return True
            elif "chuột trái" in command or "left click" in command:
                pyautogui.leftClick()
                self.speak("Đã nhấp chuột trái.")
                return True
            elif "chuột qua phải" in command:
                current_x, current_y = pyautogui.position()
                if self.mouse_dragging:
                    pyautogui.dragTo(current_x + 25, current_y, duration=0.5)
                else:
                    pyautogui.moveTo(current_x + 25, current_y, duration=0.5)
                self.speak("Đã di chuột qua phải.")
                return True
            elif "chuột qua trái" in command:
                current_x, current_y = pyautogui.position()
                if self.mouse_dragging:
                    pyautogui.dragTo(current_x - 25, current_y, duration=0.5)
                else:
                    pyautogui.moveTo(current_x - 25, current_y, duration=0.5)
                self.speak("Đã di chuột qua trái.")
                return True
            elif "chuột lên" in command:
                current_x, current_y = pyautogui.position()
                if self.mouse_dragging:
                    pyautogui.dragTo(current_x, current_y - 25, duration=0.5)
                else:
                    pyautogui.moveTo(current_x, current_y - 25, duration=0.5)
                self.speak("Đã di chuột lên.")
                return True
            elif "chuột xuống" in command:
                current_x, current_y = pyautogui.position()
                if self.mouse_dragging:
                    pyautogui.dragTo(current_x, current_y + 25, duration=0.5)
                else:
                    pyautogui.moveTo(current_x, current_y + 25, duration=0.5)
                self.speak("Đã di chuột xuống.")
                return True
            elif "kéo chuột" in command:
                pyautogui.mouseDown()
                self.mouse_dragging = True
                self.speak("Đã kéo chuột.")
                return True
            elif "thả chuột" in command:
                pyautogui.mouseUp()
                self.mouse_dragging = False
                self.speak("Đã thả chuột.")
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
                            # Tắt chế độ lắng nghe sau khi dừng nhập
                            self.is_listening = False
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
                    self.speak(f"Đã xóa {count} từ.")
                else:
                    pyautogui.hotkey('ctrl', 'backspace')
                    self.speak("Đã xóa một từ.")
                return True
            elif "bôi đen" in command:
                # Trích xuất số lượng từ cần bôi đen từ lệnh
                numbers = re.findall(r'\d+', command)
                count = int(numbers[0]) if numbers else 1
                
                # Xác định hướng bôi đen
                if "phải" in command:
                    for _ in range(count):
                        pyautogui.hotkey('shift', 'right')
                        time.sleep(0.1)
                elif "trái" in command:
                    for _ in range(count):
                        pyautogui.hotkey('shift', 'left')
                        time.sleep(0.1)
                else:
                    # Mặc định bôi đen sang phải
                    for _ in range(count):
                        pyautogui.hotkey('shift', 'right')
                        time.sleep(0.1)
                
                print(f"Đã bôi đen {count} từ.")
                self.speak(f"Đã bôi đen {count} từ.")
                return True
            elif "copy" in command or "sao chép" in command:
                pyautogui.hotkey('ctrl', 'c')
                self.speak("Đã sao chép.")
                return True
            elif "dán chữ" in command or "paste" in command:
                pyautogui.hotkey('ctrl', 'v')
                self.speak("Đã dán.")
                return True
            elif "xuống dòng" in command:
                pyautogui.press('enter')
                self.speak("Đã xuống dòng.")
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi xử lý lệnh chuột: {e}")
            self.speak("Không thể thực hiện lệnh chuột.")
            return False

    def _handle_text_commands(self, command):
        """Xử lý các lệnh liên quan đến văn bản"""
        if "chọn tất cả" in command:
            self.text_control.select_all()
        elif "cắt" in command:
            self.text_control.cut()
        elif "xóa dòng" in command:
            self.text_control.delete_line()
        elif "xóa đoạn" in command:
            self.text_control.delete_paragraph()
        elif "xóa từ đầu dòng" in command:
            self.text_control.delete_to_line_start()
        elif "xóa đến cuối dòng" in command:
            self.text_control.delete_to_line_end()
        elif "in đậm" in command:
            self.text_control.bold()
        elif "in nghiêng" in command:
            self.text_control.italic()
        elif "gạch chân" in command:
            self.text_control.underline()
        elif "gạch ngang" in command:
            self.text_control.strikethrough()
        elif "cỡ chữ lớn" in command:
            self.text_control.increase_font_size()
        elif "cỡ chữ nhỏ" in command:
            self.text_control.decrease_font_size()
        elif "căn trái" in command:
            self.text_control.align_left()
        elif "căn phải" in command:
            self.text_control.align_right()
        elif "căn giữa" in command:
            self.text_control.align_center()
        elif "căn đều" in command:
            self.text_control.align_justify()
        elif "lên dòng" in command:
            self.text_control.move_up()
        elif "xuống dòng" in command:
            self.text_control.move_down()
        elif "đầu dòng" in command:
            self.text_control.move_to_line_start()
        elif "cuối dòng" in command:
            self.text_control.move_to_line_end()
        elif "đầu trang" in command:
            self.text_control.move_to_page_start()
        elif "cuối trang" in command:
            self.text_control.move_to_page_end()
        elif "đầu tài liệu" in command:
            self.text_control.move_to_doc_start()
        elif "cuối tài liệu" in command:
            self.text_control.move_to_doc_end()
        elif "thụt lề" in command:
            self.text_control.indent()
        elif "bỏ thụt lề" in command:
            self.text_control.unindent()
        elif "tạo danh sách" in command:
            self.text_control.create_numbered_list()
        elif "tạo gạch đầu dòng" in command:
            self.text_control.create_bullet_list()
        elif "tăng khoảng cách dòng" in command:
            self.text_control.increase_line_spacing()
        elif "giảm khoảng cách dòng" in command:
            self.text_control.decrease_line_spacing()
        elif "tìm" in command:
            text = command.replace("tìm", "").strip()
            self.text_control.find_text(text)
        elif "tìm tiếp" in command:
            self.text_control.find_next()
        elif "thay thế" in command:
            parts = command.split()
            if len(parts) >= 4:
                old_text = parts[2]
                new_text = parts[3]
                if "tất cả" in command:
                    self.text_control.replace_all(old_text, new_text)
                else:
                    self.text_control.replace_text(old_text, new_text)
        elif "hoàn tác" in command:
            self.text_control.undo()
        elif "làm lại" in command:
            self.text_control.redo()
        else:
            return False
        self.speak("Đã xử lý xong lệnh")
        time.sleep(0.5)
        self.speak("Đang lắng nghe lệnh tiếp theo...")
        time.sleep(0.5)
        return True

    def _handle_app_commands(self, command):
        """
        Xử lý các lệnh mở và đóng ứng dụng
        """
        try:
            if "đóng cửa sổ" in command:
                pyautogui.hotkey('alt', 'f4')
                self.speak("Đã đóng cửa sổ.")
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
            elif "khởi động lại" in command:
                print("Đang khởi động lại máy tính...")
                self.speak("Máy tính sẽ khởi động lại sau 1 giây.")
                os.system("shutdown /r /t 1")  # Khởi động lại sau 1 giây
                return True
            elif "chế độ ngủ" in command:
                print("Đang đưa máy vào chế độ ngủ...")
                self.speak("Máy tính sẽ chuyển sang chế độ ngủ.")
                os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")  # Đưa máy vào chế độ ngủ
                return True
            return False
        except Exception as e:
            print(f"Lỗi khi xử lý lệnh ứng dụng: {e}")
            return False

    def process_command(self, command):
        # Xử lý lệnh giọng nói
        if not command:
            return

        # Thông báo đang xử lý lệnh
        print(f"\n=== Đang xử lý lệnh: {command} ===")
        self.speak("Đang xử lý lệnh...")
        time.sleep(0.5)

        # Xử lý các lệnh chuột
        if self._handle_mouse_commands(command):
            print(f"=== Đã thực hiện xong lệnh: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return

        # Xử lý các lệnh văn bản
        if self._handle_text_commands(command):
            print(f"=== Đã thực hiện xong lệnh: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return

        # Xử lý các lệnh ứng dụng
        if self._handle_app_commands(command):
            print(f"=== Đã thực hiện xong lệnh: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return

        # Xử lý các lệnh YouTube
        if "youtube" in command.lower():
            if "mở youtube" in command:
                self.youtube.open_youtube()
                self.speak("Đã mở YouTube.")
            elif "phát" in command or "tạm dừng" in command:
                self.youtube.play_pause()
                self.speak("Đã phát/tạm dừng video.")
            elif "video tiếp theo" in command:
                self.youtube.next_video()
                self.speak("Đã chuyển sang video tiếp theo.")
            elif "video trước" in command:
                self.youtube.previous_video()
                self.speak("Đã quay lại video trước.")
            elif "tăng âm" in command:
                self.youtube.volume_up()
                self.speak("Đã tăng âm lượng.")
            elif "giảm âm" in command:
                self.youtube.volume_down()
                self.speak("Đã giảm âm lượng.")
            elif "tắt tiếng" in command:
                self.youtube.mute()
                self.speak("Đã tắt tiếng.")
            elif "toàn màn hình" in command:
                self.youtube.fullscreen()
                self.speak("Đã bật/tắt chế độ toàn màn hình.")
            elif "rạp hát" in command:
                self.youtube.theater_mode()
                self.speak("Đã bật/tắt chế độ rạp hát.")
            elif "tua nhanh" in command:
                self.youtube.forward()
                self.speak("Đã tua nhanh 5 giây.")
            elif "tua lùi" in command:
                self.youtube.backward()
                self.speak("Đã tua lùi 5 giây.")
            elif "tăng tốc độ" in command:
                self.youtube.speed_up()
                self.speak("Đã tăng tốc độ phát.")
            elif "giảm tốc độ" in command:
                self.youtube.speed_down()
                self.speak("Đã giảm tốc độ phát.")
            elif "đặt lại tốc độ" in command:
                self.youtube.reset_speed()
                self.speak("Đã đặt lại tốc độ phát.")
            elif "thích video" in command:
                self.youtube.like_video()
                self.speak("Đã thích video.")
            elif "không thích video" in command:
                self.youtube.dislike_video()
                self.speak("Đã không thích video.")
            elif "đăng ký" in command:
                self.youtube.subscribe()
                self.speak("Đã đăng ký kênh.")
            elif "tìm kiếm" in command:
                # Trích xuất từ khóa tìm kiếm
                search_text = command.replace("youtube tìm kiếm", "").strip()
                if search_text:
                    self.youtube.search(search_text)
                    self.speak(f"Đã tìm kiếm '{search_text}' trên YouTube.")
            print(f"=== Đã thực hiện xong lệnh YouTube: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return

        # Xử lý các lệnh Chrome
        if "google" in command.lower():
            if "mở tab mới" in command:
                self.chrome.new_tab()
                self.speak("Đã mở tab mới.")
            elif "đóng tab" in command:
                self.chrome.close_tab()
                self.speak("Đã đóng tab.")
            elif "mở lại tab" in command:
                self.chrome.reopen_tab()
                self.speak("Đã mở lại tab.")
            elif "chuyển tab" in command:
                # Trích xuất số tab từ lệnh
                numbers = re.findall(r'\d+', command)
                if numbers:
                    tab_number = int(numbers[0])
                    self.chrome.switch_tab(tab_number)
                    self.speak(f"Đã chuyển đến tab {tab_number}.")
            elif "di chuyển tab phải" in command:
                self.chrome.move_tab_right()
                self.speak("Đã di chuyển tab sang phải.")
            elif "di chuyển tab trái" in command:
                self.chrome.move_tab_left()
                self.speak("Đã di chuyển tab sang trái.")
            elif "ghim tab" in command:
                self.chrome.pin_tab()
                self.speak("Đã ghim tab.")
            elif "bỏ ghim tab" in command:
                self.chrome.unpin_tab()
                self.speak("Đã bỏ ghim tab.")
            elif "ẩn danh" in command:
                self.chrome.new_incognito()
                self.speak("Đã mở tab ẩn danh.")
            elif "đóng tất cả tab" in command:
                self.chrome.close_all_tabs()
                self.speak("Đã đóng tất cả tab.")
            elif "làm mới trang" in command:
                self.chrome.refresh_page()
                self.speak("Đã làm mới trang.")
            elif "dừng tải" in command:
                self.chrome.stop_loading()
                self.speak("Đã dừng tải trang.")
            elif "phóng to" in command:
                self.chrome.zoom_in()
                self.speak("Đã phóng to trang.")
            elif "thu nhỏ" in command:
                self.chrome.zoom_out()
                self.speak("Đã thu nhỏ trang.")
            elif "đặt lại zoom" in command:
                self.chrome.reset_zoom()
                self.speak("Đã đặt lại tỷ lệ zoom.")
            elif "lịch sử" in command:
                self.chrome.open_history()
                self.speak("Đã mở lịch sử.")
            elif "dấu trang" in command:
                self.chrome.open_bookmarks()
                self.speak("Đã mở dấu trang.")
            elif "đánh dấu trang" in command:
                self.chrome.bookmark_page()
                self.speak("Đã đánh dấu trang.")
            elif "tải xuống" in command:
                self.chrome.open_downloads()
                self.speak("Đã mở trang tải xuống.")
            elif "cài đặt google" in command:
                self.chrome.open_settings()
                self.speak("Đã mở cài đặt Google.")
            elif "tiện ích" in command:
                self.chrome.open_extensions()
                self.speak("Đã mở trang tiện ích.")
            elif "công cụ nhà phát triển" in command:
                self.chrome.open_dev_tools()
                self.speak("Đã mở công cụ nhà phát triển.")
            elif "kiểm tra phần tử" in command:
                self.chrome.inspect_element()
                self.speak("Đã mở kiểm tra phần tử.")
            elif "mã nguồn" in command:
                self.chrome.view_source()
                self.speak("Đã mở mã nguồn trang.")
            elif "xóa dữ liệu" in command:
                self.chrome.clear_browsing_data()
                self.speak("Đã mở trang xóa dữ liệu.")
            elif "cửa hàng google" in command:
                self.chrome.open_chrome_store()
                self.speak("Đã mở cửa hàng tiện ích.")
            elif "tìm trong trang" in command:
                # Trích xuất từ khóa tìm kiếm
                search_text = command.replace("tìm trong trang", "").strip()
                if search_text:
                    self.chrome.search_in_page(search_text)
                    self.speak(f"Đã tìm kiếm '{search_text}' trong trang.")
            elif "dịch trang" in command:
                self.chrome.translate_page()
                self.speak("Đã mở dịch trang.")
            elif "lưu trang" in command:
                self.chrome.save_page()
                self.speak("Đã mở lưu trang.")
            elif "in trang" in command:
                self.chrome.print_page()
                self.speak("Đã mở in trang.")
            elif "cửa sổ mới" in command:
                self.chrome.open_new_window()
                self.speak("Đã mở cửa sổ mới.")
            elif "đóng cửa sổ" in command:
                self.chrome.close_window()
                self.speak("Đã đóng cửa sổ.")
            elif "thu nhỏ cửa sổ" in command:
                self.chrome.minimize_window()
                self.speak("Đã thu nhỏ cửa sổ.")
            elif "phóng to cửa sổ" in command:
                self.chrome.maximize_window()
                self.speak("Đã phóng to cửa sổ.")
            elif "khôi phục cửa sổ" in command:
                self.chrome.restore_window()
                self.speak("Đã khôi phục cửa sổ.")
            print(f"=== Đã thực hiện xong lệnh Chrome: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return

        if "tăng âm lượng" in command or "tăng âm" in command:
            self._handle_volume_command(command, is_increase=True)
            print(f"=== Đã thực hiện xong lệnh âm lượng: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "giảm âm lượng" in command or "giảm âm" in command:
            self._handle_volume_command(command, is_increase=False)
            print(f"=== Đã thực hiện xong lệnh âm lượng: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "lướt xuống" in command:
            self.auto_scroll.scroll_speed = 10  # Đặt tốc độ lướt mặc định là 10
            self.auto_scroll.start_scroll()
            self.speak("Đang lướt xuống.")
            print(f"=== Đã thực hiện xong lệnh lướt: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "lướt lên" in command:
            self.auto_scroll.scroll_speed = 10  # Đặt tốc độ lướt mặc định là 10
            self.auto_scroll.start_scroll_up()
            self.speak("Đang lướt lên.")
            print(f"=== Đã thực hiện xong lệnh lướt: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "lướt chậm" in command:
            self.auto_scroll.scroll_speed = 10  # Giảm tốc độ cuộn
            self.speak("Đã giảm tốc độ lướt.")
            print(f"=== Đã thực hiện xong lệnh lướt: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "lướt nhanh" in command:
            self.auto_scroll.scroll_speed = 30  # Tăng tốc độ cuộn
            self.speak("Đã tăng tốc độ lướt.")
            print(f"=== Đã thực hiện xong lệnh lướt: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "dừng điều khiển" in command:
            self.auto_scroll.stop_scroll()
            self.speak("Đã dừng lướt.")
            print(f"=== Đã thực hiện xong lệnh dừng: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "tắt máy" in command:
            self.shutdown.shutdown_computer()
            self.speak("Máy tính sẽ tắt.")
            print(f"=== Đã thực hiện xong lệnh tắt máy: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "mở trang" in command:
            self.tab_window.open_tab()
            self.speak("Đang mở trang.")
            print(f"=== Đã thực hiện xong lệnh mở trang: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "chuyển trang" in command:
            self.tab_window.open_tab()  # Sử dụng cùng hàm với mở tab
            self.speak("Đang chuyển trang.")
            print(f"=== Đã thực hiện xong lệnh chuyển trang: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "cửa sổ" in command:
            self.tab_window.open_tab()  # Sử dụng cùng hàm với mở tab
            self.speak("Đang mở chế độ chuyển cửa sổ.")
            print(f"=== Đã thực hiện xong lệnh cửa sổ: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "qua phải" in command:
            if self.tab_window.alt_tab_active:
                self.tab_window.switch_tab_right()
                self.speak("Chuyển qua phải.")
            else:
                self.speak("Vui lòng mở chế độ chuyển cửa sổ trước.")
            print(f"=== Đã thực hiện xong lệnh chuyển tab: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "qua trái" in command:
            if self.tab_window.alt_tab_active:
                self.tab_window.switch_tab_left()
                self.speak("Chuyển qua trái.")
            else:
                self.speak("Vui lòng mở chế độ chuyển cửa sổ trước.")
            print(f"=== Đã thực hiện xong lệnh chuyển tab: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        elif "chọn trang" in command:
            if self.tab_window.alt_tab_active:
                self.tab_window.select_tab()
                self.speak("Đã chọn.")
            else:
                self.speak("Vui lòng mở chế độ chuyển cửa sổ trước.")
            print(f"=== Đã thực hiện xong lệnh chọn trang: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return
        else:
            print("Lệnh không được nhận diện.")
            self.speak("Xin lỗi, lệnh không được nhận diện.")
            print(f"=== Lệnh không được nhận diện: {command} ===")
            self.speak("Đã xử lý xong lệnh")
            time.sleep(0.5)
            self.speak("Đang lắng nghe lệnh tiếp theo...")
            time.sleep(0.5)
            return

def main():
    # Hàm chính để chạy ứng dụng VoiceAI
    voice_ai = VoiceAI()
    print("Trợ lý ảo đã sẵn sàng.")
    print("Nói 'Điều Khiển' để sử dụng các lệnh điều khiển.")
    print("Nói 'Trợ Lý Ảo' để trò chuyện với trợ lý ảo.")
    while True:
        command = voice_ai.listen()
        if command:
            voice_ai.process_command(command)

if __name__ == "__main__":
    main()   