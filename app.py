import streamlit as st
import qrcode
from PIL import Image
import requests
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import sqlite3

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
st.markdown("<p class='title'>🔍 Kiểm tra độ an toàn của mã QR & Lưu trữ lịch sử</p>", unsafe_allow_html=True)

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

    # 🛡️ API Key Google Safe Browsing (Thay bằng API Key của bạn)
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

            # Lưu vào lịch sử kiểm tra
            cursor.execute("INSERT INTO qr_history (username, qr_url, status) VALUES (?, ?, ?)", (st.session_state["username"], decoded_url, safety_class))
            conn.commit()

    # 📜 Hiển thị lịch sử kiểm tra
    st.subheader("📜 Lịch sử kiểm tra của bạn:")
    cursor.execute("SELECT qr_url, status, checked_at FROM qr_history WHERE username=? ORDER BY checked_at DESC", (st.session_state["username"],))
    history = cursor.fetchall()

    if history:
        for entry in history:
            url, status, timestamp = entry
            color_class = "safe" if status == "safe" else "danger" if status == "danger" else "warn"
            st.markdown(f"<div class='chat-box {color_class}'>📅 {timestamp} - 🔗 <a href='{url}' target='_blank'>{url}</a></div>", unsafe_allow_html=True)
    else:
        st.info("Bạn chưa có lịch sử kiểm tra nào!")

