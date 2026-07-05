import streamlit as st
import google.generativeai as genai

# Cấu hình trang web của Bot
st.set_page_config(page_title="PC Builder AI", page_icon="💻")
st.title("💻 Trợ Lý Tư Vấn Build PC Theo Nhu Cầu")

# Khởi tạo API Key trong session nếu chưa có
if "GEMINI_API_KEY" not in st.session_state:
    st.session_state.GEMINI_API_KEY = ""

# Giao diện phụ để nhập API Key
if not st.session_state.GEMINI_API_KEY:
    api_key_input = st.text_input("Nhập Gemini API Key của bạn để bắt đầu:", type="password")
    if api_key_input:
        st.session_state.GEMINI_API_KEY = api_key_input
        st.rerun()
    st.warning("Vui lòng nhập API Key để kích hoạt não bộ cho AI.")
    st.stop()

# Cấu hình thư viện AI của Google
genai.configure(api_key=st.session_state.GEMINI_API_KEY)

# Định hình tính cách cho Bot (System Instruction)
system_prompt = """
Bạn là một chuyên gia tư vấn Build PC và phần cứng máy tính chuyên nghiệp, am hiểu sâu sắc về phần cứng (CPU, GPU, RAM, SSD, Mainboard, Nguồn, Tản nhiệt) tại thị trường Việt Nam.
Nhiệm vụ của bạn:
1. Lắng nghe nhu cầu của người dùng (Ngân sách bao nhiêu, chơi game gì, làm đồ họa hay lập trình ứng dụng như Android Studio...).
2. Đưa ra cấu hình tối ưu nhất trong tầm giá. Giải thích rõ ràng tại sao lại chọn linh kiện đó (Ví dụ: chọn Nvidia vì hỗ trợ AI/CUDA tốt, chọn CPU Intel dòng K hay AMD Ryzen...).
3. Cách xưng hô: Hãy xưng hô thân thiện, cởi mở, gọi người dùng là 'Đạt' hoặc 'bạn' và xưng 'tôi'. Hãy nói chuyện như một người anh em đam mê công nghệ tư vấn cho nhau, ngắn gọn, súc tích, đi thẳng vào vấn đề, không dài dòng văn tự.
"""

# Khởi tạo model Gemini 1.5 Flash bản nâng cấp ổn định nhất
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    system_instruction=system_prompt
)

# Khởi tạo lịch sử chat nếu chưa có
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào Đạt! Tôi là AI chuyên gia build PC đây. Đạt đang có ngân sách khoảng bao nhiêu và nhu cầu dùng làm gì (chơi game gì, code phần mềm gì...) để tôi lên cấu hình tối ưu nhất?"}
    ]

# Hiển thị các tin nhắn cũ
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Ô nhập liệu của người dùng
if user_input := st.chat_input("Nhập nhu cầu của bạn ở đây..."):
    # Hiển thị tin nhắn người dùng vừa nhập
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
        
    # Gọi API Gemini để lấy câu trả lời thực tế
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            # Chuyển đổi lịch sử chat sang định dạng Gemini hiểu
            formatted_history = []
            for m in st.session_state.messages[:-1]:
                role = "user" if m["role"] == "user" else "model"
                formatted_history.append({"role": role, "parts": [m["content"]]})
            
            chat = model.start_chat(history=formatted_history)
            response = chat.send_message(user_input, stream=True)
            
            full_response = ""
            for chunk in response:
                full_response += chunk.text
                response_placeholder.write(full_response + "▌")
                
            response_placeholder.write(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Có lỗi xảy ra khi gọi AI: {str(e)}")