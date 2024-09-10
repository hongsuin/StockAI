import kis_auth as ka
import kis_domstk as kb
import pandas as pd
import time

# 토큰 발급
ka.auth()

# 사용자 입력 받기
start_date = input("조회 시작일을 입력하세요 (YYYYMMDD 형식): ")
end_date = input("조회 종료일을 입력하세요 (YYYYMMDD 형식): ")

# kospi_code.xlsx 파일을 읽어서 종목코드 리스트를 추출
kospi_codes_df = pd.read_excel("C:/Users/홍수인/Documents/newkis/kospi_code.xlsx")  
print("kospi Codes DataFrame Columns:")
print(kospi_codes_df.columns)

# 종목 코드 리스트를 추출 ('단축코드' 열을 사용)
kospi_codes_list = kospi_codes_df['단축코드'].astype(str).tolist()

# 결과를 저장할 리스트
all_rt_data = []

# 성공적인 호출 수를 기록할 변수
success_count = 0

# 한 파일에 저장할 종목 수를 설정 (예: 100 종목)
codes_per_file = 150  
file_count = 7

# API 호출 함수 정의
def fetch_data(code, start_date, end_date):
    try:
        rt_data = kb.get_inquire_daily_itemchartprice(
            div_code="J",
            itm_no_list=[code],
            inqr_strt_dt=start_date,
            inqr_end_dt=end_date,
            output_dv="2"
        )
        
        if rt_data is not None and not rt_data.empty:
            return rt_data
        else:
            print(f"No data returned for code: {code}")
            return None
    except Exception as e:
        print(f"Failed to fetch data for code: {code}. Error: {e}")
        return None

# 1초당 20건의 API 호출 제약조건을 고려하여 API 호출
for index, code in enumerate(kospi_codes_list[900:], start=901):  # 901번째 종목부터 시작
    temp_data = []
    current_end_date = end_date
    last_date = None  # last_date 초기화
    
    while True:
        rt_data = fetch_data(code, start_date, current_end_date)
        if rt_data is not None and not rt_data.empty:
            temp_data.append(rt_data)
            if 'date' in rt_data.columns:
                rt_data['date'] = rt_data['date'].astype(str)  # Ensure 'date' column is string type
                last_date = rt_data['date'].min()  # 가장 오래된 날짜
                
                if pd.isna(last_date) or last_date <= start_date:
                    break
                try:
                    current_end_date = (pd.to_datetime(last_date) - pd.DateOffset(days=1)).strftime('%Y%m%d')
                except ValueError as e:
                    print(f"Error converting date: {e}")
                    break
            else:
                print(f"Column 'date' not found in the data for code: {code}")
                break
        else:
            break

        time.sleep(0.5)  # API 요청 제한을 피하기 위해 잠시 대기
    
    # start_date에 도달하지 못했을 때, 호출을 다시 해줌
    if temp_data and last_date and not pd.isna(last_date) and last_date > start_date:
        while last_date > start_date:
            rt_data = fetch_data(code, start_date, current_end_date)
            if rt_data is not None and not rt_data.empty:
                temp_data.append(rt_data)
                if 'date' in rt_data.columns:
                    rt_data['date'] = rt_data['date'].astype(str)  # Ensure 'date' column is string type
                    last_date = rt_data['date'].min()
                    if pd.isna(last_date) or last_date <= start_date:
                        break
                    try:
                        last_date = str(last_date)
                        current_end_date = (pd.to_datetime(last_date) - pd.DateOffset(days=1)).strftime('%Y%m%d')
                    except ValueError as e:
                        print(f"Error converting date: {e}")
                        break
                else:
                    break
            else:
                break
            time.sleep(0.5)  # API 요청 제한을 피하기 위해 잠시 대기

    if temp_data:
        combined_temp_data = pd.concat(temp_data, ignore_index=True)
        if not combined_temp_data.empty:
            all_rt_data.append(combined_temp_data)
            success_count += 1
            print(f"Fetched data for code: {code}")

    # 일정 수의 종목 데이터를 수집했으면 파일로 저장
    if index % codes_per_file == 0 or index == len(kospi_codes_list[900:]):
        if all_rt_data:
            combined_df = pd.concat(all_rt_data, ignore_index=True)
            file_name = f"C:/Users/홍수인/Documents/newkis/part{file_count}.xlsx"
            combined_df.to_excel(file_name, index=False)
            print(f"Data saved to {file_name}")
            file_count += 1
            all_rt_data = []  # 리스트 초기화

# 남아있는 데이터를 마지막 파일로 저장
if all_rt_data:
    combined_df = pd.concat(all_rt_data, ignore_index=True)
    file_name = f"C:/Users/홍수인/Documents/newkis/part{file_count}.xlsx"  
    combined_df.to_excel(file_name, index=False)
    print(f"Data saved to {file_name}")

# 코스피 종목 수
total_stocks = len(kospi_codes_list)
print(f"총 코스피 종목의 수: {total_stocks}")

#014990->part4에서 토큰만료. 580번째 종목. 
#119650->part6에서 vs종료. 900번째 종목.