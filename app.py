import streamlit as st
import qrcode
from PIL import Image
import requests
from pyzbar.pyzbar import decode

# Hàm kiểm tra URL có an toàn không
def check_url_safety(url):
    # Danh sách giả lập các URL nguy hiểm
    blacklist = ["phishing.com", "malware-site.net", "dangerous-site.org"]

    for site in blacklist:
        if site in url:
            return "❌ Cảnh báo: URL này có thể nguy hiểm!"
    
    return "✅ URL an toàn!"

# Giao diện Streamlit
st.title("🔍 Kiểm tra độ an toàn của mã QR")

# Tải lên ảnh QR Code
uploaded_file = st.file_uploader("📂 Tải lên ảnh mã QR", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Hiển thị ảnh
    image = Image.open(uploaded_file)
    st.image(image, caption="📷 Mã QR đã tải lên", use_column_width=True)

    # Giải mã mã QR
    decoded_objects = decode(image)
    if decoded_objects:
        decoded_url = decoded_objects[0].data.decode("utf-8")
        st.write(f"🔗 **URL giải mã từ QR:** {decoded_url}")

        # Kiểm tra độ an toàn
        safety_result = check_url_safety(decoded_url)
        st.write(safety_result)
    else:
        st.write("⚠ Không phát hiện được mã QR hợp lệ trong ảnh!")

import streamlit as st
import qrcode
from PIL import Image
import requests
from pyzbar.pyzbar import decode

# Hàm kiểm tra URL an toàn
def check_url_safety(url):
    blacklist = ["phishing.com", "malware-site.net", "dangerous-site.org"]
    for site in blacklist:
        if site in url:
            return "❌ Cảnh báo: URL này có thể nguy hiểm!"
    return "✅ URL an toàn!"

# Hàm lấy tiêu đề trang web để xem trước nội dung URL
def get_url_preview(url):
    try:
        response = requests.get(url, timeout=3)  # Giới hạn thời gian để tránh treo ứng dụng
        if response.status_code == 200:
            return response.text[:500]  # Hiển thị 500 ký tự đầu tiên của HTML trang
    except:
        return "⚠ Không thể xem trước nội dung trang này!"
    return "⚠ URL không hợp lệ hoặc không thể truy cập."

# Giao diện Streamlit
st.title("🔍 Kiểm tra độ an toàn của mã QR & Xem trước URL")

# Tải lên ảnh QR Code
uploaded_file = st.file_uploader("📂 Tải lên ảnh mã QR", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Hiển thị ảnh
    image = Image.open(uploaded_file)
    st.image(image, caption="📷 Mã QR đã tải lên", use_column_width=True)

    # Giải mã mã QR
    decoded_objects = decode(image)
    if decoded_objects:
        decoded_url = decoded_objects[0].data.decode("utf-8")
        st.write(f"🔗 **URL giải mã từ QR:** [{decoded_url}]({decoded_url})")

        # Kiểm tra độ an toàn
        safety_result = check_url_safety(decoded_url)
        st.write(safety_result)

        # Xem trước nội dung trang web
        with st.expander("🔍 Xem trước nội dung trang web"):
            preview_content = get_url_preview(decoded_url)
            st.text(preview_content)
    else:
        st.write("⚠ Không phát hiện được mã QR hợp lệ trong ảnh!")
