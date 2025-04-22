import speech_recognition as sr
import openai
import time
import os
import pygame
from gtts import gTTS
import tempfile
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()

# Cấu hình OpenAI API key từ biến môi trường
openai.api_key = os.getenv('OPENAI_API_KEY')

# Kiểm tra API key
if not openai.api_key:
    raise ValueError("Không tìm thấy OPENAI_API_KEY trong file .env")

class VoiceAssistant:
    def __init__(self):
        # Khởi tạo pygame mixer cho phát âm thanh
        pygame.mixer.init()
        # Tạo thư mục tạm để lưu file âm thanh
        self.temp_dir = tempfile.mkdtemp()
        # Khởi tạo lịch sử hội thoại
        self.conversation_history = []
        # Giới hạn số lượt hội thoại
        self.max_turns = 30
        
    def add_to_history(self, role, content):
        """Thêm một lượt vào lịch sử hội thoại"""
        self.conversation_history.append({"role": role, "content": content})
        # Giữ lại max_turns lượt gần nhất
        if len(self.conversation_history) > self.max_turns:
            # Giữ lại tin nhắn system đầu tiên
            system_message = next((msg for msg in self.conversation_history if msg["role"] == "system"), None)
            # Lấy các tin nhắn gần nhất
            self.conversation_history = self.conversation_history[-self.max_turns:]
            # Thêm lại tin nhắn system vào đầu nếu có
            if system_message and system_message not in self.conversation_history:
                self.conversation_history.insert(0, system_message)

    def speak(self, text):
        """Phát âm văn bản thành giọng nói tiếng Việt"""
        try:
            # Tạo file âm thanh tạm
            temp_file = os.path.join(self.temp_dir, "temp.mp3")
            
            # Chuyển văn bản thành giọng nói
            tts = gTTS(text=text, lang='vi', slow=False)
            tts.save(temp_file)
            
            # Phát âm thanh
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Đợi cho đến khi phát xong
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            
            # Dừng phát nhạc và giải phóng tài nguyên
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            
            # Xóa file tạm
            try:
                os.remove(temp_file)
            except:
                pass
                
        except Exception as e:
            print(f"Lỗi khi phát âm thanh: {str(e)}")
            print(f"Phản hồi dạng văn bản: {text}")

def check_microphone():
    """Kiểm tra và hiển thị danh sách microphone có sẵn"""
    try:
        print("\nDanh sách microphone đã phát hiện:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"Microphone {index}: {name}")
        return True
    except Exception as e:
        print(f"\nLỗi khi kiểm tra microphone: {str(e)}")
        return False

def listen_for_wake_word():
    """Lắng nghe từ khóa kích hoạt 'trợ lý ảo'"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Đang lắng nghe từ khóa kích hoạt 'trợ lý ảo'...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
        
        try:
            text = recognizer.recognize_google(audio, language='vi-VN').lower()
            if "trợ lý ảo" in text:
                print("Đã phát hiện từ khóa kích hoạt!")
                return True
        except sr.UnknownValueError:
            pass
        except sr.RequestError:
            print("Không thể kết nối đến dịch vụ nhận dạng giọng nói")
    
    return False

def listen_for_command():
    """Lắng nghe lệnh từ người dùng trong 10 giây"""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("Đang lắng nghe lệnh của bạn...")
        recognizer.adjust_for_ambient_noise(source)
        
        try:
            audio = recognizer.listen(source, timeout=10)  # Tăng thời gian chờ lên 10 giây
            text = recognizer.recognize_google(audio, language='vi-VN')
            print(f"Bạn nói: {text}")
            return text
        except sr.WaitTimeoutError:
            print("Không nghe thấy lệnh nào sau 10 giây")
            return None
        except sr.UnknownValueError:
            print("Không thể nhận dạng giọng nói")
            return None
        except sr.RequestError:
            print("Không thể kết nối đến dịch vụ nhận dạng giọng nói")
            return None

def get_chatgpt_response(prompt, assistant):
    """Lấy phản hồi từ ChatGPT"""
    try:
        # Thêm câu hỏi mới vào lịch sử
        assistant.add_to_history("user", prompt)
        
        # Tạo messages từ lịch sử hội thoại
        messages = [
            {"role": "system", "content": "Bạn là một trợ lý ảo thông minh và hữu ích, có khả năng hiểu và trả lời bằng tiếng Việt một cách tự nhiên."}
        ] + assistant.conversation_history
        
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        
        # Thêm câu trả lời vào lịch sử
        assistant_response = response.choices[0].message.content
        assistant.add_to_history("assistant", assistant_response)
        
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

def process_commands(assistant):
    """Xử lý chuỗi lệnh từ người dùng"""
    while True:
        # Lắng nghe lệnh
        command = listen_for_command()
        if not command:
            break
            
        # Xử lý lệnh và phát âm phản hồi
        response = get_chatgpt_response(command, assistant)
        if response:
            print(f"ChatGPT: {response}")
            assistant.speak(response)
            print("\nĐang lắng nghe câu hỏi tiếp theo (10 giây)...")
        
        # Lắng nghe câu hỏi tiếp theo
        try:
            with sr.Microphone() as source:
                recognizer = sr.Recognizer()
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=10)
                text = recognizer.recognize_google(audio, language='vi-VN')
                if text:
                    command = text  # Tiếp tục vòng lặp với câu hỏi mới
                    continue
        except sr.WaitTimeoutError:
            print("Không có câu hỏi mới, kết thúc phiên lắng nghe.")
            break
        except sr.UnknownValueError:
            print("Không thể nhận dạng giọng nói")
            break
        except sr.RequestError:
            print("Không thể kết nối đến dịch vụ nhận dạng giọng nói")
            break
        except Exception as e:
            print(f"Lỗi khi lắng nghe: {str(e)}")
            break
    
    print("\nĐang chờ từ khóa kích hoạt tiếp theo...")

def main():
    print("Trợ lý ảo đã được khởi động.")
    
    # Khởi tạo trợ lý ảo
    assistant = VoiceAssistant()
    
    # Kiểm tra API key
    if not openai.api_key:
        print("Lỗi: Không tìm thấy OpenAI API key. Vui lòng kiểm tra file .env")
        return
    
    # Kiểm tra microphone trước khi bắt đầu
    if not check_microphone():
        print("Không tìm thấy microphone hoặc có lỗi. Vui lòng kiểm tra lại thiết bị.")
        return
        
    print("Nói 'trợ lý ảo' để bắt đầu.")
    
    while True:
        try:
            if listen_for_wake_word():
                assistant.speak("Trợ lý ảo, đã sẵn sàng lắng nghe lệnh của bạn")
                process_commands(assistant)
        except KeyboardInterrupt:
            print("\nĐã dừng chương trình.")
            break
        except Exception as e:
            print(f"\nLỗi không xác định: {str(e)}")
            print("Đang thử lại...")
            time.sleep(1)

if __name__ == "__main__":
    main() 