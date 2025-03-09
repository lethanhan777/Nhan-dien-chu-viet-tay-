import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter
import easyocr
import numpy as np
import threading  # Để chạy nhận dạng văn bản trong một luồng riêng, tránh làm đơ giao diện

# Khởi tạo đối tượng OCR sử dụng easyocr
reader = easyocr.Reader(['vi', 'en'])  # Hỗ trợ tiếng Việt và tiếng Anh

def upload_image():
    """Cho phép người dùng tải lên ảnh và hiển thị nó."""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.jpeg;*.png")])
    if file_path:
        try:
            img = Image.open(file_path)
            img.thumbnail((400, 400))  # Thay đổi kích thước ảnh để hiển thị
            img_display = ImageTk.PhotoImage(img)

            # Hiển thị ảnh trên khung bên trái
            image_label.config(image=img_display)
            image_label.image = img_display  # Lưu tham chiếu để tránh bị garbage collected

            global current_image_path
            current_image_path = file_path
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể mở ảnh: {e}")

def recognize_text():
    """Nhận dạng văn bản từ ảnh đã tải lên."""
    if not current_image_path:
        messagebox.showwarning("Cảnh báo", "Hãy tải lên một ảnh trước!")
        return

    # Đặt một trạng thái "Đang nhận dạng" khi bắt đầu nhận dạng văn bản
    status_label.config(text="Đang nhận dạng...")

    # Chạy nhận dạng văn bản trong một luồng riêng để tránh làm đơ giao diện
    threading.Thread(target=perform_ocr).start()

def perform_ocr():
    """Thực hiện nhận dạng văn bản từ ảnh."""
    try:
        # Mở ảnh và chuyển thành ảnh xám (Grayscale) để tiền xử lý
        img = Image.open(current_image_path)
        img = img.convert('L')  # Chuyển ảnh sang ảnh xám (Grayscale)

        # Tiền xử lý ảnh
        img = preprocess_image(img)

        # Chuyển đổi ảnh PIL sang numpy array
        img_array = np.array(img)

        # Sử dụng easyocr để nhận dạng văn bản
        result = reader.readtext(img_array, detail=0, paragraph=True)

        # Tạo chuỗi văn bản nhận diện được (bao gồm chữ và số)
        text = '\n'.join(result)

        # Chuyển tất cả chữ cái thành chữ thường
        text = text.lower()

        # Hiển thị văn bản đã nhận dạng trên khung bên phải
        text_display.delete(1.0, tk.END)  # Xóa văn bản cũ
        text_display.insert(tk.END, text)

        # Cập nhật trạng thái
        status_label.config(text="Nhận dạng hoàn tất.")
    except Exception as e:
        messagebox.showerror("Lỗi", f"Không thể nhận dạng văn bản: {e}")
        status_label.config(text="Có lỗi xảy ra.")

def preprocess_image(img):
    """Tiền xử lý ảnh để cải thiện độ chính xác nhận dạng."""
    # Cân bằng độ sáng
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(1.5)  # Tăng độ sáng ảnh để rõ nét hơn

    # Cân bằng độ tương phản
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2.0)  # Tăng độ tương phản

    # Làm mịn ảnh (Giảm nhiễu)
    img = img.filter(ImageFilter.MedianFilter(3))  # Dùng MedianFilter để giảm nhiễu

    # Áp dụng phân ngưỡng để chuyển ảnh thành ảnh đen trắng rõ ràng
    img = img.point(lambda p: p > 128 and 255)  # Phân ngưỡng (binarization)

    return img

# Tạo cửa sổ chính
window = tk.Tk()
window.title("Ứng dụng nhận dạng chữ viết tay")

# Khung bên trái để hiển thị ảnh
image_frame = tk.Frame(window, padx=10, pady=10)
image_frame.pack(side=tk.LEFT)

image_label = tk.Label(image_frame)
image_label.pack()

# Khung bên phải để hiển thị văn bản đã nhận dạng
text_frame = tk.Frame(window, padx=10, pady=10)
text_frame.pack(side=tk.RIGHT)

text_display = tk.Text(text_frame, height=20, width=50)
text_display.pack()

# Trạng thái
status_label = tk.Label(window, text="", fg="blue")
status_label.pack()

# Nút "Tải ảnh lên"
upload_button = tk.Button(window, text="Tải ảnh lên", command=upload_image)
upload_button.pack()

# Nút "Chuyển đổi"
convert_button = tk.Button(window, text="Chuyển đổi", command=recognize_text)
convert_button.pack()

# Biến toàn cục để lưu đường dẫn ảnh hiện tại
current_image_path = None

window.mainloop()
