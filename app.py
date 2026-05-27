import streamlit as st
from google import genai
from google.genai import types
from google.genai.errors import APIError

# 1. 페이지 설정 및 디자인
st.set_page_config(page_title="달콤살벌 연애상담소", page_icon="💌", layout="centered")
st.title("💌 달콤살벌 연애상담소")
st.caption("gemini-2.5-flash-lite 모델이 당신의 연애 고민을 들어 드립니다.")

# 2. Secrets에서 API 키 불러오기 및 클라이언트 초기화
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    client = genai.Client(api_key=api_key)
except KeyError:
    st.error(".streamlit/secrets.toml 파일에 'GEMINI_API_KEY'가 설정되지 않았습니다.")
    st.stop()

# 3. 세션 상태(Session State) 초기화 - 채팅 기록 및 대화 객체 유지
if "messages" not in st.session_state:
    st.session_state.messages = []

if "chat_session" not in st.session_state:
    # 챗봇에게 연애 상담사 페르소나 부여 (시스템 프롬프트)
    system_instruction = (
        "당신은 공감 능력이 뛰어나면서도 때로는 뼈 때리는 조언을 해주는 전문 연애 상담사입니다. "
        "사용자의 고민을 경청하고, 다정하지만 현실적인 해결책을 제시해 주세요. "
        "답변은 친근한 말투(반말과 존댓말 중 친근한 어조 선호)를 사용하고, 이모지를 적절히 섞어주세요."
    )
    
    try:
        # gemini-2.5-flash-lite 모델로 멀티턴 대화 세션 시작
        st.session_state.chat_session = client.chats.create(
            model="gemini-2.5-flash-lite",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.7, # 적당히 창의적이고 공감대 있는 답변 유도
            )
        )
    except Exception as e:
        st.error(f"채팅 세션을 초기화하는 중 오류가 발생했습니다: {e}")
        st.stop()

# 4. 기존 채팅 기록 UI에 렌더링
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 5. 사용자 입력 처리
if user_input := st.chat_input("연애 고민을 편하게 털어놓으세요..."):
    
    # 사용자 메시지 UI 표시 및 기록 저장
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # 챗봇 답변 생성 및 오류 처리
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            with st.spinner("당신의 고민을 읽고 생각하는 중... ☕"):
                # 이전 기록이 누적된 대화 세션에 메시지 전송
                response = st.session_state.chat_session.send_message(user_input)
                ai_response = response.text
                
            # 결과 출력 및 기록 저장
            message_placeholder.markdown(ai_response)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})
            
        except APIError as e:
            # 구글 API 측 에러 처리 (할당량 초과, 인증 오류 등)
            message_placeholder.error(f"⚠️ Gemini API 오류가 발생했습니다: {e.message}")
        except Exception as e:
            # 기타 예외 처리
            message_placeholder.error(f"⚠️ 예상치 못한 오류가 발생했습니다: {str(e)}")

# 6. 대화 초기화 버튼 (사이드바)
if st.sidebar.button("대화 기록 초기화 🔄"):
    st.session_state.messages = []
    # 대화 세션도 새로 리셋
    st.session_state.chat_session = client.chats.create(
        model="gemini-2.5-flash-lite",
        config=types.GenerateContentConfig(
            system_instruction="당신은 공감 능력이 뛰어나면서도 때로는 뼈 때리는 조언을 해주는 전문 연애 상담사입니다."
        )
    )
    st.rerun()
