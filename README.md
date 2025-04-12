# AI SmartControl - Hệ Thống Điều Khiển Đa Phương Thức Cho Máy Tính

AI SmartControl là một hệ thống điều khiển máy tính thông minh thông qua giọng nói và cử chỉ tay, được phát triển bằng Python. Hệ thống được thiết kế để giúp người dùng điều khiển máy tính một cách tiện lợi và hiệu quả mà không cần sử dụng bàn phím và chuột truyền thống, đặc biệt hữu ích cho người khuyết tật và người dùng muốn trải nghiệm phương thức điều khiển mới.

## Mục Đích Dự Án

- Tạo ra một giải pháp điều khiển máy tính thông minh và tiện lợi
- Hỗ trợ người khuyết tật trong việc sử dụng máy tính
- Cải thiện trải nghiệm người dùng với các phương thức điều khiển mới
- Tích hợp công nghệ AI trong việc nhận diện giọng nói và cử chỉ
- Cung cấp giải pháp điều khiển đa phương thức cho máy tính

## Thông Tin Phiên Bản

- Phiên bản hiện tại: 1.0.0
- Ngày phát hành: 12/04/2024
- Tác giả: Đình Wage
- Facebook: [https://www.facebook.com/dvr.official.2203](https://www.facebook.com/dvr.official.2203)

## Tính Năng Chính

- **Điều khiển bằng giọng nói**: Sử dụng thư viện voiceai.py để nhận diện và xử lý lệnh thoại
- **Điều khiển bằng cử chỉ tay**: Sử dụng camera để nhận diện cử chỉ tay (hand_gesture.py, hand.py)
- **Điều khiển âm lượng**: Chức năng điều chỉnh âm lượng hệ thống (volume.py)
- **Điều khiển cửa sổ**: Quản lý và điều khiển các cửa sổ ứng dụng (tab_window.py, hidden_window.py)
- **Cuộn trang**: Điều khiển cuộn trang web hoặc tài liệu (scroll.py)
- **Tắt máy**: Chức năng tắt máy tính (shutdown.py)
- **Nhập văn bản bằng giọng nói**: Chuyển đổi giọng nói thành văn bản
- **Điều khiển chuột**: Di chuyển và thao tác chuột thông qua giọng nói

## Yêu Cầu Hệ Thống

### Phần Cứng
- Webcam (độ phân giải tối thiểu 720p)
- Microphone (chất lượng tốt, có khả năng lọc tiếng ồn)
- CPU: Intel Core i3 trở lên hoặc tương đương
- RAM: Tối thiểu 4GB
- GPU: Không bắt buộc, nhưng có thể cải thiện hiệu suất

### Phần Mềm
- Python 3.8 trở lên
- Các thư viện được liệt kê trong requirements.txt
- Hệ điều hành: Windows 10/11, Linux, macOS

## Cài Đặt

1. Clone repository này về máy local
2. Cài đặt các thư viện cần thiết:
   ```
   pip install -r requirements.txt
   ```
3. Chạy chương trình chính:
   ```
   python main.py
   ```

## Hướng Dẫn Sử Dụng

Chi tiết hướng dẫn sử dụng có thể xem trong file `Huongdan.txt`

### Lưu Ý Quan Trọng

1. Đảm bảo microphone và webcam hoạt động bình thường trước khi sử dụng
2. Sử dụng trong môi trường có ánh sáng đầy đủ để nhận diện cử chỉ tay tốt hơn
3. Tránh tiếng ồn xung quanh khi sử dụng tính năng nhận diện giọng nói
4. Đảm bảo đã cấp quyền truy cập microphone và camera cho ứng dụng

## Cấu Trúc Dự Án

### Core Components
- `main.py`: File chính chạy chương trình, quản lý luồng điều khiển
- `voiceai.py`: Xử lý nhận diện giọng nói và chuyển đổi thành lệnh
- `hand.py`: Xử lý nhận diện cử chỉ tay cơ bản
- `hand_gesture.py`: Phân tích và xử lý các cử chỉ tay phức tạp

### Control Modules
- `volume.py`: Điều khiển âm lượng hệ thống
- `tab_window.py`: Quản lý và điều khiển các cửa sổ ứng dụng
- `scroll.py`: Điều khiển cuộn trang web và tài liệu
- `shutdown.py`: Xử lý các lệnh tắt máy và khởi động lại
- `hidden_window.py`: Quản lý cửa sổ ẩn và chế độ nền

### Configuration
- `requirements.txt`: Danh sách các thư viện cần thiết
- `config.json`: Cấu hình hệ thống (nếu có)

## Đóng Góp

Mọi đóng góp cho dự án đều được hoan nghênh. Vui lòng tạo pull request hoặc issue để thảo luận về các thay đổi.

### Quy Tắc Đóng Góp

1. Tuân thủ quy tắc viết code của dự án
2. Thêm comment rõ ràng cho các thay đổi
3. Kiểm tra kỹ trước khi tạo pull request
4. Cập nhật tài liệu khi cần thiết

## Giấy Phép

Dự án này được phân phối dưới giấy phép MIT. Xem file [LICENSE](LICENSE) để biết thêm chi tiết.

## Liên Hệ

- Email: hqhuyzzzz@gmail.com
- GitHub: [https://github.com/dinhvaren](https://github.com/dinhvaren)
- Website: [https://dinhvaren.github.io](https://dinhvaren.github.io)

## Cảm Ơn

Cảm ơn tất cả những người đã đóng góp và hỗ trợ cho dự án này. Đặc biệt cảm ơn các thư viện mã nguồn mở đã được sử dụng trong dự án.