# 🤖 AI SmartControl - Hệ Thống Điều Khiển Thông Minh Thế Hệ Mới

<div align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version"/>
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"/>
  <img src="https://img.shields.io/badge/Status-Active-success.svg" alt="Status"/>
</div>

## 🚀 Giới Thiệu

AI SmartControl là một hệ thống điều khiển máy tính thông minh được thiết kế đặc biệt để hỗ trợ người khuyết tật, thông qua giọng nói và cử chỉ tay. Hệ thống được phát triển bằng Python với mục tiêu tạo ra một giải pháp điều khiển máy tính dễ tiếp cận và thân thiện với người dùng, giúp họ có thể sử dụng máy tính một cách độc lập mà không phụ thuộc vào bàn phím và chuột truyền thống.

### ✨ Điểm Nổi Bật

- 🎯 Điều khiển đa phương thức: Giọng nói và cử chỉ tay
- 🎨 Giao diện thân thiện, dễ sử dụng
- ⚡ Tốc độ xử lý nhanh chóng
- 🔒 Bảo mật cao
- 🎁 Hoàn toàn miễn phí và mã nguồn mở
- ♿ Tối ưu hóa cho người khuyết tật

## 🎯 Mục Đích Dự Án

- Tạo ra một giải pháp điều khiển máy tính thông minh và tiện lợi dành riêng cho người khuyết tật
- Hỗ trợ người khuyết tật vận động trong việc sử dụng máy tính
- Cải thiện khả năng tiếp cận công nghệ cho người khuyết tật
- Tích hợp công nghệ AI tiên tiến trong việc nhận diện giọng nói và cử chỉ
- Cung cấp giải pháp điều khiển đa phương thức, phù hợp với nhiều dạng khuyết tật khác nhau
- Tạo ra một cộng đồng hỗ trợ và chia sẻ kinh nghiệm
- Phát triển một hệ thống mã nguồn mở, miễn phí

## 📦 Thông Tin Phiên Bản

| Phiên bản | Ngày phát hành | Trạng thái |
|-----------|---------------|------------|
| 1.0.0     | 12/04/2024    | ✅ Active  |

## 💡 Tính Năng Chính

| Tính Năng | Mô Tả | Trạng Thái |
|-----------|-------|------------|
| 🎤 Điều khiển bằng giọng nói | Nhận diện và xử lý lệnh thoại tiếng Việt | ✅ Hoạt động |
| ✋ Điều khiển bằng cử chỉ tay | Nhận diện cử chỉ tay qua camera | ✅ Hoạt động |
| 🤖 Trợ lý ảo ChatGPT | Tích hợp ChatGPT để hỗ trợ người dùng | ✅ Hoạt động |
| 🔊 Điều khiển âm lượng | Điều chỉnh âm lượng hệ thống | ✅ Hoạt động |
| 🖥️ Điều khiển cửa sổ | Quản lý và điều khiển cửa sổ | ✅ Hoạt động |
| 📜 Cuộn trang | Điều khiển cuộn trang web/tài liệu | ✅ Hoạt động |
| ⏻ Tắt máy | Chức năng tắt máy tính | ✅ Hoạt động |
| ⌨️ Nhập văn bản bằng giọng nói | Chuyển đổi giọng nói thành văn bản | ✅ Hoạt động |
| 🖱️ Điều khiển chuột | Di chuyển và thao tác chuột | ✅ Hoạt động |
| 🎯 Chế độ điều khiển thông minh | Tự động chuyển đổi chế độ | ✅ Hoạt động |
| 🔍 Phóng to thu nhỏ | Điều khiển zoom | ✅ Hoạt động |
| 📱 Điều khiển đa màn hình | Hỗ trợ nhiều màn hình | ✅ Hoạt động |
| 🎨 Giao diện thân thiện | Thiết kế dễ sử dụng | ✅ Hoạt động |
| 🔄 Tùy chỉnh lệnh | Cho phép tùy chỉnh lệnh | ✅ Hoạt động |
| 📊 Báo cáo trạng thái | Hiển thị trạng thái hệ thống | ✅ Hoạt động |
| 🔒 Bảo mật | Bảo vệ thông tin người dùng | ✅ Hoạt động |

## 🛠️ Yêu Cầu Hệ Thống

### Phần Cứng
- 📷 Webcam (720p trở lên)
- 🎤 Microphone chất lượng cao
- 💻 CPU: Intel Core i3 trở lên
- 🧠 RAM: 4GB trở lên
- 🎮 GPU: Khuyến nghị (không bắt buộc)

### Phần Mềm
- 🐍 Python 3.8+
- 📚 Các thư viện trong requirements.txt
- 💻 Windows 10/11, Linux, macOS

## 🚀 Cài Đặt

1. Clone repository:
```bash
git clone https://github.com/dinhvaren/AI-SmartControl.git
cd AI-SmartControl
```

2. Cài đặt thư viện:
```bash
pip install -r requirements.txt
```

3. Chạy chương trình:
```bash
python main.py
```

## 📚 Cấu Trúc Dự Án

```
.
├── 📄 main.py                # File chính chạy chương trình
├── 📄 gui.py                 # Giao diện người dùng
├── 📄 hand.py                # Xử lý cử chỉ tay
├── 📄 hand_gesture.py        # Controller cử chỉ tay
├── 📄 voiceai.py             # Controller giọng nói
├── 📄 volume.py              # Controller âm lượng
├── 📄 tab_window.py          # Controller cửa sổ
├── 📄 scroll.py              # Controller cuộn trang
├── 📄 shutdown.py            # Controller tắt máy
├── 📄 hidden_window.py       # Controller cửa sổ ẩn
├── 📄 requirements.txt       # Danh sách thư viện cần thiết
├── 📄 .gitignore            # File cấu hình Git
├── 📄 README.md             # Tài liệu hướng dẫn
├── 📄 Huongdan.txt          # Hướng dẫn sử dụng chi tiết
├── 📄 icon.png              # Biểu tượng ứng dụng
└── 📄 abc                   # File cấu hình bổ sung
```

### Giải Thích Cấu Trúc

- **Các file chính**:
  - `main.py`: File chính để chạy chương trình
  - `gui.py`: Xử lý giao diện người dùng
  - `hand.py`: Xử lý cử chỉ tay
  - `voiceai.py`: Xử lý giọng nói

- **Các controller**:
  - `hand_gesture.py`: Điều khiển cử chỉ tay
  - `volume.py`: Điều khiển âm lượng
  - `tab_window.py`: Điều khiển cửa sổ
  - `scroll.py`: Điều khiển cuộn trang
  - `shutdown.py`: Điều khiển tắt máy
  - `hidden_window.py`: Điều khiển cửa sổ ẩn

- **Cấu hình và tài liệu**:
  - `requirements.txt`: Danh sách thư viện
  - `.gitignore`: Cấu hình Git
  - `README.md`: Tài liệu hướng dẫn
  - `Huongdan.txt`: Hướng dẫn chi tiết
  - `icon.png`: Biểu tượng ứng dụng
  - `abc`: File cấu hình bổ sung

## 🤝 Đóng Góp

Chúng tôi rất hoan nghênh mọi đóng góp từ cộng đồng! Nếu bạn muốn đóng góp cho dự án, vui lòng:

1. Fork repository
2. Tạo branch mới cho tính năng của bạn (`git checkout -b feature/AmazingFeature`)
3. Commit những thay đổi của bạn (`git commit -m 'Add some AmazingFeature'`)
4. Push lên branch (`git push origin feature/AmazingFeature`)
5. Mở một Pull Request

## 📄 Giấy Phép

Dự án được phân phối dưới giấy phép MIT. Xem [LICENSE](LICENSE) để biết thêm chi tiết.

## 📞 Liên Hệ

- 📧 Email: dinhlnng2003@gmail.com
- 💻 GitHub: [dinhvaren](https://github.com/dinhvaren)
- 🌐 Website: [dinhvaren.github.io](https://dinhvaren.github.io)
- 📱 Facebook: [Đình Wage](https://www.facebook.com/dvr.official.2203)

## 🙏 Cảm Ơn

Cảm ơn tất cả những người đã đóng góp và hỗ trợ cho dự án này. Đặc biệt cảm ơn các thư viện mã nguồn mở đã được sử dụng trong dự án.

---

<div align="center">
  <sub>Built with ❤️ by Đình Wage</sub>
</div>