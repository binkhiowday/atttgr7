import streamlit as st
import qrcode
from PIL import Image
import requests
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 🖥️ Cấu hình trang (Giao diện rộng, tiêu đề)
st.set_page_config(page_title="QR Security Check", layout="wide")

# 🎨 CSS tùy chỉnh để tạo giao diện giống ChatGPT
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: auto; }
    .title { text-align: center; font-size: 28px; font-weight: bold; }
    .chat-box { padding: 15px; border-radius: 10px; margin: 10px 0; font-size: 16px; }
    .safe { background-color: #dff0d8; color: #3c763d; } /* Màu xanh lá */
    .danger { background-color: #f2dede; color: #a94442; } /* Màu đỏ */
    .info { background-color: #d9edf7; color: #31708f; } /* Màu xanh dương */
    .warn { background-color: #fcf8e3; color: #8a6d3b; } /* Màu vàng */
    .stButton>button:hover { border: 2px solid #0A74DA; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# 🏆 Tiêu đề ứng dụng
st.markdown("<p class='title'>🔍 Kiểm tra độ an toàn của mã QR & Xem trước URL</p>", unsafe_allow_html=True)

# 🛡️ Hàm kiểm tra độ an toàn của URL
def check_url_safety(url):
    blacklist = ["phishing.com", "malware-site.net", "dangerous-site.org"]
    for site in blacklist:
        if site in url:
            return "❌ Cảnh báo: URL này có thể nguy hiểm!", "danger"
    return "✅ URL an toàn!", "safe"

# 🌐 Hàm lấy tiêu đề trang & ảnh xem trước
def get_url_preview(url):
    try:
        response = requests.get(url, timeout=5, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        # Lấy ảnh từ thẻ meta Open Graph (og:image)
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else None

        # Nếu không có ảnh, lấy favicon
        if not image_url:
            icon_link = soup.find("link", rel=lambda x: x and "icon" in x)
            image_url = icon_link["href"] if icon_link else None

        # Xử lý URL ảnh nếu là đường dẫn tương đối
        if image_url and not image_url.startswith("http"):
            image_url = urljoin(url, image_url)

        # Lấy tiêu đề trang
        page_title = soup.title.string if soup.title else "Không tìm thấy tiêu đề trang"

        return image_url, page_title
    except:
        return None, "⚠ Không thể xem trước nội dung trang này!"

# 📂 Tải lên ảnh QR Code
uploaded_file = st.file_uploader("📂 Tải lên ảnh mã QR", type=["png", "jpg", "jpeg"], key="file_uploader_main")

if uploaded_file:
    # 📷 Hiển thị ảnh QR
    image = Image.open(uploaded_file)
    st.image(image, caption="📷 Mã QR đã tải lên", use_column_width=True)

    # 🔍 Giải mã mã QR
    decoded_objects = decode(image)
    if decoded_objects:
        decoded_url = decoded_objects[0].data.decode("utf-8")
        st.markdown(f"<div class='chat-box info'>🔗 <strong>URL giải mã từ QR:</strong> <a href='{decoded_url}' target='_blank'>{decoded_url}</a></div>", unsafe_allow_html=True)

        # 🛡️ Kiểm tra độ an toàn của URL
        safety_result, safety_class = check_url_safety(decoded_url)
        st.markdown(f"<div class='chat-box {safety_class}'>{safety_result}</div>", unsafe_allow_html=True)

        # 🌐 Xem trước nội dung trang web
        with st.expander("🔍 Xem trước nội dung trang web"):
            image_url, preview_text = get_url_preview(decoded_url)

            if image_url:
                st.image(image_url, caption="Ảnh xem trước", use_column_width=True)
            st.markdown(f"<div class='chat-box info'><strong>{preview_text}</strong></div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='chat-box warn'>⚠ Không phát hiện được mã QR hợp lệ trong ảnh!</div>", unsafe_allow_html=True)

import streamlit as st

# 🖥️ Cấu hình trang rộng
st.set_page_config(page_title="QR Security Check", layout="wide")

# 🎨 CSS để căn chỉnh logo về bên trái
st.markdown("""
    <style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
    }
    .header-container img {
        width: 120px; /* Điều chỉnh kích thước logo */
        margin-right: 15px;
    }
    .header-title {
        font-size: 26px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# 🔹 Hiển thị logo và tiêu đề
logo_path = "logo_ENG_positive_full-color-10.width-500.png"  # Thay bằng đường dẫn file logo
st.markdown(f"""
    <div class="header-container">
        <img src="{logo_path}">
        <span class="header-title">🔍 Kiểm tra độ an toàn của mã QR & Xem trước URL</span>
    </div>
""", unsafe_allow_html=True)

# 🔹 Hiển thị nội dung tiếp theo
st.write("## Hệ thống kiểm tra mã QR thông minh")

# 📂 File uploader
uploaded_file = st.file_uploader("📂 Tải lên ảnh mã QR", type=["png", "jpg", "jpeg"])
