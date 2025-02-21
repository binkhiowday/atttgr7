import streamlit as st
import qrcode
from PIL import Image
import requests
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup

# Hàm kiểm tra URL có an toàn không
def check_url_safety(url):
    # Danh sách giả lập các URL nguy hiểm
    blacklist = ["phishing.com", "malware-site.net", "dangerous-site.org"]
    for site in blacklist:
        if site in url:
            return "❌ Cảnh báo: URL này có thể nguy hiểm!"
    return "✅ URL an toàn!"

# Hàm lấy tiêu đề trang web & ảnh xem trước
def get_url_preview(url):
    try:
        response = requests.get(url, timeout=5, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        # Lấy ảnh từ thẻ meta Open Graph (og:image)
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else None

        # Nếu không có og:image, thử lấy favicon
        if not image_url:
            favicon = soup.find("link", rel="icon")
            image_url = favicon["href"] if favicon else None

        # Nếu không có favicon, thử lấy apple-touch-icon
        if not image_url:
            apple_icon = soup.find("link", rel="apple-touch-icon")
            image_url = apple_icon["href"] if apple_icon else None

        # Lấy tiêu đề trang
        page_title = soup.title.string if soup.title else "Không tìm thấy tiêu đề trang"

        # Xử lý URL ảnh nếu nó là đường dẫn tương đối
        if image_url and not image_url.startswith("http"):
            from urllib.parse import urljoin
            image_url = urljoin(url, image_url)

        return image_url, page_title
    except:
        return None, "⚠ Không thể xem trước nội dung trang này!"

# Giao diện Streamlit
st.title("🔍 Kiểm tra độ an toàn của mã QR & Xem trước URL")

# Tải lên ảnh QR Code
uploaded_file = st.file_uploader("📂 Tải lên ảnh mã QR", type=["png", "jpg", "jpeg"], key="file_uploader_main")

if uploaded_file:
    # Hiển thị ảnh QR
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
            image_url, preview_text = get_url_preview(decoded_url)

            if image_url:
                st.image(image_url, caption="Ảnh xem trước", use_column_width=True)
            st.write(f"**{preview_text}**")
    else:
        st.write("⚠ Không phát hiện được mã QR hợp lệ trong ảnh!")
