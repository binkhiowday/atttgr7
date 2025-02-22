import streamlit as st
import qrcode
from PIL import Image
import requests
import cv2
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3
import os

# 🖥️ Cấu hình trang rộng
st.set_page_config(page_title="QR Security Check", layout="wide")

# 🎨 CSS để tạo giao diện đẹp hơn
st.markdown("""
    <style>
    .stApp { max-width: 800px; margin: auto; }
    .title { text-align: center; font-size: 26px; font-weight: bold; }
    .chat-box { padding: 15px; border-radius: 10px; margin: 10px 0; font-size: 16px; }
    .safe { background-color: #dff0d8; color: #3c763d; } /* Xanh lá */
    .danger { background-color: #f2dede; color: #a94442; } /* Đỏ */
    .info { background-color: #d9edf7; color: #31708f; } /* Xanh dương */
    .warn { background-color: #fcf8e3; color: #8a6d3b; } /* Vàng */
    .stButton>button:hover { border: 2px solid #0A74DA; transform: scale(1.02); }
    </style>
""", unsafe_allow_html=True)

# 🏆 Tiêu đề ứng dụng
st.markdown("<p class='title'>🔍 Kiểm tra độ an toàn của mã QR & Xem trước website</p>", unsafe_allow_html=True)

# 🔹 Kết nối với SQLite để lưu tài khoản và lịch sử quét QR
conn = sqlite3.connect("qr_scanner.db", check_same_thread=False)
cursor = conn.cursor()

# 🔹 Tạo bảng nếu chưa tồn tại
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS qr_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    qr_url TEXT,
    status TEXT,
    checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")
conn.commit()

# 🏆 Đăng nhập / Đăng ký tài khoản
st.sidebar.header("🔑 Đăng nhập / Đăng ký")

# Chọn giữa đăng nhập hoặc đăng ký
auth_choice = st.sidebar.radio("Chọn:", ["🔓 Đăng nhập", "📝 Đăng ký"])

if auth_choice == "📝 Đăng ký":
    new_username = st.sidebar.text_input("Tạo tài khoản")
    new_password = st.sidebar.text_input("Mật khẩu", type="password")
    if st.sidebar.button("Đăng ký"):
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (new_username, new_password))
            conn.commit()
            st.sidebar.success("✅ Đăng ký thành công! Vui lòng đăng nhập.")
        except sqlite3.IntegrityError:
            st.sidebar.error("❌ Tài khoản đã tồn tại!")

if auth_choice == "🔓 Đăng nhập":
    username = st.sidebar.text_input("Tài khoản")
    password = st.sidebar.text_input("Mật khẩu", type="password")
    if st.sidebar.button("Đăng nhập"):
        cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = cursor.fetchone()
        if user:
            st.sidebar.success(f"✅ Đăng nhập thành công! Xin chào {username}")
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
        else:
            st.sidebar.error("❌ Sai tài khoản hoặc mật khẩu!")

# Chỉ tiếp tục nếu đã đăng nhập
if "logged_in" in st.session_state and st.session_state["logged_in"]:

    # 🛡️ Cấu hình API Key của Google Safe Browsing (Thay bằng API Key của bạn)
    GOOGLE_SAFE_BROWSING_API_KEY = "YOUR_GOOGLE_SAFE_BROWSING_API_KEY"

    # 🛡️ Kiểm tra độ an toàn của URL qua Google Safe Browsing API
    def check_url_safety(url):
        google_api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GOOGLE_SAFE_BROWSING_API_KEY}"
        request_body = {
            "client": {"clientId": "streamlit-app", "clientVersion": "1.0"},
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [{"url": url}]
            }
        }

        try:
            response = requests.post(google_api_url, json=request_body)
            result = response.json()
            if "matches" in result:
                return "❌ Cảnh báo: URL này bị Google đánh dấu là không an toàn!", "danger"
            else:
                return "✅ URL an toàn!", "safe"
        except Exception as e:
            return f"⚠ Lỗi khi kiểm tra URL: {str(e)}", "warn"

    # 🌐 Xem trước hình ảnh của website
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

            return image_url
        except:
            return None

    # 📂 Tải lên ảnh QR Code
    uploaded_file = st.file_uploader("📂 Tải lên ảnh mã QR", type=["png", "jpg", "jpeg"], key="file_uploader_main")

    if uploaded_file:
        # 📷 Hiển thị ảnh QR
        image = Image.open(uploaded_file)
        st.image(image, caption="📷 Mã QR đã tải lên", use_column_width=True)

        # 🔍 Giải mã mã QR
        temp_image_path = "temp_qr.png"
        image.save(temp_image_path)
        img = cv2.imread(temp_image_path)
        detector = cv2.QRCodeDetector()
        decoded_url, _, _ = detector.detectAndDecode(img)

        if decoded_url:
            st.markdown(f"<div class='chat-box info'>🔗 <strong>URL giải mã từ QR:</strong> <a href='{decoded_url}' target='_blank'>{decoded_url}</a></div>", unsafe_allow_html=True)

            # 🛡️ Kiểm tra độ an toàn của URL
            safety_result, safety_class = check_url_safety(decoded_url)
            st.markdown(f"<div class='chat-box {safety_class}'>{safety_result}</div>", unsafe_allow_html=True)

            # 🌐 Xem trước hình ảnh của website
            image_url = get_url_preview(decoded_url)
            if image_url:
                st.image(image_url, caption="Ảnh xem trước website", use_column_width=True)
