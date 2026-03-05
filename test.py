import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# --- 0. 웹페이지 설정 ---
st.set_page_config(page_title="피닉스 펌프 잇 업 아카이브", page_icon="💃", layout="centered", initial_sidebar_state="collapsed")

# --- 🎨 아예 '모바일 앱'처럼 보이게 고정하는 CSS ---
st.markdown("""
<style>
    /* 1. PC 모니터로 봐도 앱 화면처럼 폭을 좁게 고정! */
    [data-testid="stAppViewBlockContainer"] {
        max-width: 450px !important; 
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 2. 프로필 박스는 무조건 세로 정렬(모바일 뷰)로 고정 */
    .profile-box {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 25px 15px;
        background-color: white;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        text-align: center; /* 텍스트 무조건 가운데 정렬 */
    }
    .profile-content {
        display: flex;
        flex-direction: column; /* 가로가 아닌 무조건 세로 배열 */
        align-items: center;
    }
    .profile-img-wrap {
        margin-bottom: 15px; /* 사진과 이름 사이 간격 */
    }
    .stat-row {
        display: flex;
        flex-direction: column; /* 시각, 장소, PP도 세로로 깔끔하게 정리 */
        gap: 6px;
        color: #555;
        font-size: 0.9em;
        margin-top: 15px;
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- 🎯 내 링크 설정 (여기에 링크를 적어주세요!) ---
MY_LINKS = [
    {"title": "유튜브 채널", "url": "https://youtube.com"},
    {"title": "인스타그램", "url": "https://instagram.com"}
]

# --- 1. 기억 상자 (Session State) 세팅 ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'my_id' not in st.session_state:
    st.session_state['my_id'] = ""
if 'my_pw' not in st.session_state:
    st.session_state['my_pw'] = ""
if 'nickname' not in st.session_state:
    st.session_state['nickname'] = "아직 데이터를 불러오지 않았습니다."
if 'profile_img' not in st.session_state:
    st.session_state['profile_img'] = None
if 'title' not in st.session_state:
    st.session_state['title'] = "없음"
if 'last_time' not in st.session_state:
    st.session_state['last_time'] = "-"
if 'last_place' not in st.session_state:
    st.session_state['last_place'] = "-"
if 'pp' not in st.session_state:
    st.session_state['pp'] = "0"

# --- 2. 로봇(크롤러) 함수 만들기 ---
def run_crawler(user_id, user_pw):
    options = webdriver.ChromeOptions()
     options.add_argument('--headless') 
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://piugame.com/") 
        time.sleep(1)
        
        driver.find_element(By.XPATH, '//*[@id="login_fs"]/ul/li[1]/input').send_keys(user_id)
        driver.find_element(By.XPATH, '//*[@id="login_fs"]/ul/li[2]/input').send_keys(user_pw)
        driver.find_element(By.XPATH, '//*[@id="login_fs"]/ul/li[4]/button').click()
        time.sleep(2)
        
        driver.get("https://piugame.com/my_page/play_data.php")
        time.sleep(2)
        
        fetched_nickname = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div/div[1]/div[2]/div[1]/p[2]').text
        style_text = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div/div[1]/div[1]/div/div').get_attribute("style")
        fetched_img = style_text.split("url(")[1].split(")")[0].replace("'", "").replace('"', "")
        
        title_element = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div/div[1]/div[2]/div[1]/p[1]')
        fetched_title = title_element.text
        
        fetched_time = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div/div[1]/div[2]/div[2]/ul/li[1]/i').text
        fetched_place = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div/div[1]/div[2]/div[2]/ul/li[2]/i').text
        fetched_pp = driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/div/div/div[1]/div[3]/p/i[2]').text
        
        return fetched_nickname, fetched_img, fetched_title, fetched_time, fetched_place, fetched_pp
        
    except Exception as e:
        st.error("크롤링 중 문제가 발생했어요! XPath나 인터넷 연결을 확인해주세요.")
        return None, None, None, None, None, None
    finally:
        driver.quit()

# --- 3. 웹사이트 화면 그리기 ---

# [화면 A] 로그인 전
if not st.session_state['logged_in']:
    st.markdown("""
    <div style='text-align: center; margin-bottom: 20px;'>
        <h2 style='margin: 0;'>피닉스 펌프 잇 업</h2>
        <span style='color: gray; font-size: 0.9rem; font-weight: bold;'>아카이브 by Zerong</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.info("펌프 잇 업 공식 홈페이지의 아이디와 비밀번호를 입력해주세요.")
    
    input_id = st.text_input("아이디 (이메일)")
    input_pw = st.text_input("비밀번호", type="password")
    
    if st.button("내 계정 연동 시작", use_container_width=True):
        if input_id and input_pw:
            st.session_state['my_id'] = input_id
            st.session_state['my_pw'] = input_pw
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.warning("아이디와 비밀번호를 모두 입력해주세요.")

# [화면 B] 로그인 후
else:
    # --- 좌측 3줄 메뉴 (사이드바) ---
    st.sidebar.title("메뉴")
    st.sidebar.success(f"현재 연동된 아이디:\n{st.session_state['my_id']}")
    
    # [수정] 메인에 있던 링크를 사이드바로 옮겼습니다!
    st.sidebar.markdown("### 🔗 내 링크")
    for link in MY_LINKS:
        if link["title"] and link["url"]:
            # 사이드바 안에서 꽉 차는 버튼 모양의 링크를 만들어줍니다.
            st.sidebar.markdown(
                f"<a href='{link['url']}' target='_blank' style='display: block; text-align: center; text-decoration: none; background-color: #f1f2f6; padding: 10px; margin-bottom: 10px; border-radius: 8px; color: #2c3e50; font-weight: bold;'>{link['title']}</a>", 
                unsafe_allow_html=True
            )
            
    st.sidebar.divider() # 가로줄 긋기
    
    if st.sidebar.button("연동 해제 (로그아웃)", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['my_id'] = ""
        st.session_state['my_pw'] = ""
        st.session_state['nickname'] = "아직 데이터를 불러오지 않았습니다."
        st.session_state['profile_img'] = None
        st.session_state['title'] = "없음"
        st.session_state['last_time'] = "-"
        st.session_state['last_place'] = "-"
        st.session_state['pp'] = "0"
        st.rerun()

    # --- 메인 프로필 화면 ---
    st.markdown("""
    <div style='text-align: center; margin-bottom: 10px;'>
        <h3 style='margin: 0;'>피닉스 펌프 잇 업 아카이브</h3>
        <span style='color: gray; font-size: 0.8rem; font-weight: bold;'>by Zerong</span>
    </div>
    """, unsafe_allow_html=True)
        
    if st.button("🔄 새로고침", use_container_width=True):
        with st.spinner('가져오는 중...'):
            new_nick, new_img, new_title, new_time, new_place, new_pp = run_crawler(st.session_state['my_id'], st.session_state['my_pw'])
            if new_nick:
                st.session_state['nickname'] = new_nick
                st.session_state['profile_img'] = new_img
                st.session_state['title'] = new_title
                st.session_state['last_time'] = new_time
                st.session_state['last_place'] = new_place
                st.session_state['pp'] = new_pp
                st.success("데이터 새로고침 완료!")
                time.sleep(1)
                st.rerun()
    
    if st.session_state['profile_img']:
        
        # [수정] 메인 화면에서는 링크 관련 HTML을 완전히 삭제했습니다.
        profile_box_html = f"""
        <div class="profile-box">
            <div class="profile-content">
                <div class="profile-img-wrap">
                    <img src="{st.session_state['profile_img']}" style="width: 120px; height: 120px; border-radius: 30%; object-fit: cover; display: block; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                </div>
                <div class="profile-details">
                    <p style="margin: 0; color: #7f8c8d; font-size: 0.9em; font-weight: bold;">🏅 {st.session_state['title']}</p>
                    <p style="margin: 5px 0 0 0; font-size: 1.8em; font-weight: 900; color: #2c3e50;">{st.session_state['nickname']}</p>
                    <div class="stat-row">
                        <span>🕒 <b>접속일:</b> {st.session_state['last_time']}</span>
                        <span>📍 <b>장소:</b> {st.session_state['last_place']}</span>
                        <span style="color: #e74c3c;">💰 <b>PP:</b> {st.session_state['pp']}</span>
                    </div>
                </div>
            </div>
        </div>
        """
        st.markdown(profile_box_html, unsafe_allow_html=True)
    else:
        st.markdown("👻 **데이터를 불러와주세요! 상단의 [새로고침] 버튼을 누르면 시작됩니다.**")