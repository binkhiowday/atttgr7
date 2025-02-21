import streamlit as st
import qrcode
from PIL import Image
import requests
from pyzbar.pyzbar import decode
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# 🔹 Thay API key của bạn vào đây
VIRUSTOTAL_API_KEY = "YOUR_VIRUSTOTAL_API_KEY"
GOOGLE_SAFE_BROWSING_API_KEY = "YOUR_GOOGLE_SAFE_BROWSING_API_KEY"

# 🛡️ Kiểm tra URL bằng VirusTotal
def check_url_with_virustotal(url):
    headers = {"x-apikey": VIRUSTOTAL_API_KEY}
    params = {"url": url}
    scan_url = "https://www.virustotal.com/api/v3/urls"

    try:
        response = requests.post(scan_url, headers=headers, data=params)
        if response.status_code == 200:
            result = response.json()
            url_id = result["data"]["id"]

            # Lấy kết quả phân tích
            report_url = f"https://www.virustotal.com/api/v3/analyses/{url_id}"
            report_response = requests.get(report_url, headers=headers)
            report_data = report_response.json()

            # Kiểm tra số lượng công cụ đánh giá URL là nguy hiểm
            malicious_count = report_data["data"]["attributes"]["stats"]["malicious"]
            if malicious_count > 0:
                return f"❌ Cảnh báo: URL này bị đánh giá nguy hiểm bởi {malicious_count} nguồn!"
            else:
                return "✅ URL an toàn!"
        else:
            return "⚠ Không thể kiểm tra URL (Lỗi API)."
    except Exception as e:
        return f"⚠ Lỗi khi kiểm tra URL trên VirusTotal: {str(e)}"

# 🛡️ Kiểm tra URL bằng Google Safe Browsing
def check_url_with_google_safe_browsing(url):
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
            return "❌ Cảnh báo: URL này bị Google đánh dấu là không an toàn!"
        else:
            return "✅ URL an toàn!"
    except Exception as e:
        return f"⚠ Lỗi khi kiểm tra URL trên Google Safe Browsing: {str(e)}"

# 🔹 Tích hợp kiểm tra từ nhiều nguồn
def check_url_safety(url):
    vt_result = check_url_with_virustotal(url)
    google_result = check_url_with_google_safe_browsing(url)

    if "Cảnh báo" in vt_result or "Cảnh báo" in google_result:
        return f"⚠ {vt_result}\n⚠ {google_result}"
    
    return "✅ URL an toàn!"

# 🌐 Lấy tiêu đề trang web & ảnh xem trước
def get_url_preview(url):
    try:
        response = requests.get(url, timeout=5, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        # Lấy ảnh từ thẻ meta Open Graph (og:image)
        og_image = soup.find("meta", property="og:image")
        image_url = og_image["content"] if og_image else None

        # Nếu không có og:image, thử lấy favicon hoặc apple-touch-icon
        if not image_url:
            icon_link = soup.find("link", rel=lambda x: x and "icon" in x)
            image_url = icon_link["href"] if icon_link else None

        # Xử lý URL ảnh nếu nó là đường dẫn tương đối
        if image_url and not image_url.startswith("http"):
            image_url = urljoin(url, image_url)

        # Lấy tiêu đề trang
        page_title = soup.title.string if soup.title else "Không tìm thấy tiêu đề trang"

        return image_url, page_title
    except:
        return None, "⚠ Không thể xem trước nội dung trang này!"

# 🎨 Giao diện Streamlit
st.title("🔍 Kiểm tra độ an toàn của mã QR & Xem trước URL")

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
        st.write(f"🔗 **URL giải mã từ QR:** [{decoded_url}]({decoded_url})")

        # 🛡️ Kiểm tra độ an toàn của URL
        safety_result = check_url_safety(decoded_url)
        st.write(safety_result)

        # 🌐 Xem trước nội dung trang web
        with st.expander("🔍 Xem trước nội dung trang web"):
            image_url, preview_text = get_url_preview(decoded_url)

            if image_url:
                st.image(image_url, caption="Ảnh xem trước", use_column_width=True)
            st.write(f"**{preview_text}**")
    else:
        st.write("⚠ Không phát hiện được mã QR hợp lệ trong ảnh!")
