import kis_auth as ka
import kis_domstk as kb
import pandas as pd
import time

# 토큰 발급
ka.auth()

# 엑셀 파일 읽기
kosdaq_codes_df = pd.read_excel("C:/Users/홍수인/Documents/newkis/kosdaq_code.xlsx")

# 사용자 입력 받기
start_date = input("조회 시작일을 입력하세요 (YYYYMMDD 형식): ")
end_date = input("조회 종료일을 입력하세요 (YYYYMMDD 형식): ")

# 단축코드 열에서 1053번째 항목부터 모든 코드를 리스트로 추출
codes_list = kosdaq_codes_df['단축코드'].tolist()[1052:]  # 1053번째 항목부터 시작

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

# 각 코드에 대해 API 호출 수행 및 데이터 저장
batch_size = 20  # 한 번에 처리할 API 호출 수
file_batch_size = 150  # 한 파일에 저장할 종목 수
file_counter = 1
all_data = []

for index, code in enumerate(codes_list):
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

                # 날짜 범위가 시작 날짜에 도달했거나 더 오래된 경우 루프 종료
                if pd.isna(last_date) or last_date <= start_date:
                    break

                # 다음 반복을 위해 current_end_date 업데이트
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

    if temp_data:
        combined_temp_data = pd.concat(temp_data, ignore_index=True)
        if not combined_temp_data.empty:
            all_data.append(combined_temp_data)
            print(f"Fetched data for code: {code}")

    # 일정 수의 종목 데이터를 수집했으면 파일로 저장
    if (index + 1) % file_batch_size == 0 or index + 1 == len(codes_list):
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            file_name = f"C:/Users/홍수인/Documents/newkis/kosdaq_data_result_part_{file_counter}.xlsx"
            combined_df.to_excel(file_name, index=False)
            print(f"파일 저장 완료: {file_name}")
            file_counter += 1
            all_data = []  # 데이터 초기화

# 남아있는 데이터를 마지막 파일로 저장
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    file_name = f"C:/Users/홍수인/Documents/newkis/kosdaq_data_result_part_{file_counter}.xlsx"
    combined_df.to_excel(file_name, index=False)
    print(f"파일 저장 완료: {file_name}")
