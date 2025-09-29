import streamlit as st
import pandas as pd
from supabase import create_client, Client
from datetime import date

# 1. Supabase 접속 정보 설정 및 연결 초기화
#SUPABASE_URL: str = "https://uuvpiutfdayziretlsfl.supabase.co"
#SUPABASE_KEY: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1dnBpdXRmZGF5emlyZXRsc2ZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3NjY4NzksImV4cCI6MjA3NDM0Mjg3OX0.IabxaqaJewI6-7o2YWWh_u7wiI6vjGhfUo7TiHZz9kg"
TABLE_NAME: str = "서울시생활인구"

SUPABASE_URL = "https://uuvpiutfdayziretlsfl.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InV1dnBpdXRmZGF5emlyZXRsc2ZsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3NjY4NzksImV4cCI6MjA3NDM0Mjg3OX0.IabxaqaJewI6-7o2YWWh_u7wiI6vjGhfUo7TiHZz9kg"  # Supabase 대시보드에서 anon 키를 입력하세요



@st.cache_resource
def init_connection() -> Client | None:
    """Supabase 클라이언트 연결을 초기화하고 상태를 반환합니다."""
    try:
        client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception:
        return None

supabase = init_connection()

# 2. 데이터 조회 함수 (이전과 동일)
def fetch_population_data(admin_code: str, query_date: date, limit: int = None) -> pd.DataFrame:
    """Supabase에서 행정동코드와 날짜에 해당하는 시간대별 인구 데이터를 조회합니다."""
    if supabase is None:
        return pd.DataFrame()

    date_str = query_date.strftime('%Y-%m-%d')
    
    try:
        admin_code_int = int(admin_code)
        
        query = supabase.table(TABLE_NAME)\
                        .select('날짜, 시간대, 행정동코드, 총생활인구수')\
                        .eq('행정동코드', admin_code_int)\
                        .eq('날짜', date_str)\
                        .order('시간대', desc=False)
        
        # limit 파라미터가 있으면 적용 (테스트용)
        if limit is not None:
            query = query.limit(limit)

        response = query.execute()
        
        data = response.data
        if not data:
            st.warning("🚨 해당 조건에 맞는 데이터가 없습니다. (코드 또는 날짜 확인)")
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        # 시각화를 위해 인덱스 설정
        if '시간대' in df.columns:
            df.rename(columns={'시간대': '시간대(Time)', '총생활인구수': '총 생활 인구수'}, inplace=True)
            df.set_index('시간대(Time)', inplace=True)
        
        return df
        
    except ValueError:
        st.error("❌ '행정동코드'는 유효한 숫자여야 합니다.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"❌ 데이터 조회 중 오류가 발생했습니다: {e}")
        return pd.DataFrame()

# 3. Streamlit 앱 실행 메인 함수
def main():
    st.set_page_config(page_title="생활인구 시간대별 추이 분석", layout="wide")
    st.title("🏙️ 생활인구 시간대별 추이 분석 Web App")

    # 사이드바에 DB 연결 상태 표시 (추가된 부분)
    with st.sidebar:
        st.header("⚙️ DB 연결 상태")
        if supabase:
            st.success("✅ Supabase에 성공적으로 연결되었습니다.")
            # 연결 테스트 버튼 추가
            if st.button("📊 연결 테스트 데이터 조회"):
                test_code = "1111061500"
                test_date = date(2023, 8, 26) # 데이터셋에 있을 법한 날짜
                
                with st.spinner(f"테스트 데이터 조회 중..."):
                    df_test = fetch_population_data(str(test_code), test_date, limit=5)

                if not df_test.empty:
                    st.success(f"🔍 조회 성공! (코드: {test_code}, 날짜: {test_date})")
                    st.dataframe(df_test)
                else:
                    st.error("❌ 테스트 데이터 조회에 실패했거나 데이터가 없습니다.")

        else:
            st.error("❌ Supabase 연결 실패. 키와 URL을 확인해주세요.")
            return

    st.markdown("---")

    # 사용자 입력 섹션 (이전과 동일)
    st.header("🔍 조회 조건 입력")
    default_date = date(2023, 1, 1)
    
    col1, col2, col3 = st.columns([1, 1, 0.5])
    
    with col1:
        admin_code_input = st.text_input(
            "행정동코드 입력 (예: 1111061500)", 
            value="1111061500",
            placeholder="10자리 숫자 입력"
        )
    
    with col2:
        date_input = st.date_input(
            "조회 날짜 선택", 
            value=default_date, 
            min_value=date(2023, 1, 1), 
            max_value=date(2023, 12, 31)
        )
    
    with col3:
        st.write("") 
        st.write("")
        search_button = st.button("📈 데이터 조회 및 시각화", type="primary")

    st.markdown("---")

    # 4. 조회 버튼 클릭 시 로직 처리 (이전과 동일)
    if search_button:
        if not admin_code_input or not date_input:
            st.error("🚨 올바른 값을 입력해주세요. (행정동코드와 날짜 모두 필수)")
            return

        try:
            int(admin_code_input) 
        except ValueError:
            st.error("🚨 올바른 값을 입력해주세요. 행정동코드는 숫자여야 합니다.")
            return

        with st.spinner("⏳ Supabase에서 데이터를 조회 중입니다..."):
            df_result = fetch_population_data(admin_code_input, date_input)

        if not df_result.empty:
            st.success(f"✅ 데이터 조회 완료: {date_input.strftime('%Y년 %m월 %d일')} - 행정동코드 {admin_code_input}")
            
            st.header(f"시간대별 총 생활 인구수 추이")
            st.line_chart(df_result, height=400)
            
            st.subheader("Raw Data")
            st.dataframe(df_result)
        
if __name__ == "__main__":
    main()