import pymysql
from sshtunnel import SSHTunnelForwarder
import pandas as pd

# --- (1. 접속 정보 설정) ---
ssh_host = '175.45.194.216'
ssh_port = 22
ssh_user = 'root'
ssh_password = 'M6bdM*Tc!H5?h'

mysql_host = '192.168.6.6'
mysql_port = 3306
mysql_user = 'addd'
mysql_password = '!@addd1004'
mysql_db = 'bus_operation_logs'
target_table_name = 'bus_operation_logs'
# 날짜 컬럼의 실제 이름을 확인 후 수정해주세요. (예: 'operation_date', 'date', 'created_at')
date_column_name = 'created_at' 

# --- (2. 사용자로부터 날짜 입력받기) ---
input_date = input("조회할 날짜를 입력하세요 (예: 2025-08-20): ")

try:
    # --- (3. SSH 터널 및 DB 연결) ---
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        remote_bind_address=(mysql_host, mysql_port)
    ) as tunnel:
        print("\n✅ SSH 터널이 성공적으로 생성되었습니다!")
        
        conn = pymysql.connect(
            host='127.0.0.1', 
            port=tunnel.local_bind_port,
            user=mysql_user,
            password=mysql_password,
            db=mysql_db,
            charset='utf8',
            # 딕셔너리 형태로 결과를 받기 위해 cursorclass 설정
            cursorclass=pymysql.cursors.DictCursor 
        )
        print("✅ 데이터베이스에 성공적으로 접속했습니다!")

        # --- (4. SQL 쿼리 실행) ---
        # DictCursor를 사용하므로, 결과를 다루기 편리합니다.
        with conn.cursor() as curs:
            # SQL Injection 방지를 위해 파라미터 바인딩 방식 사용 (?)
            # 날짜 형식과 3개 컬럼이 모두 0인 조건을 WHERE 절에 추가
            sql_query = f"""
                SELECT 
                    * FROM 
                    {target_table_name} 
                WHERE 
                    DATE({date_column_name}) = %s 
                    AND is_morning_operating = 0
                    AND is_lunch_operating = 0
                    AND is_dinner_operating = 0;
            """
            
            # 쿼리 실행
            curs.execute(sql_query, (input_date,))
            
            results = curs.fetchall()

        # --- (5. 결과 출력) ---
        if not results:
            print(f"\n❌ {input_date} 날짜에 모든 시간대(아침/점심/저녁)에 미운행한 데이터가 없습니다.")
        else:
            # pandas DataFrame으로 변환하여 출력
            df_result = pd.DataFrame(results)
            
            print(f"\n--- 📊 {input_date}에 모든 시간대 미운행 데이터 ---")
            print(df_result)


finally:
    # --- (6. 연결 종료) ---
    if 'conn' in locals() and conn.open:
        conn.close()
        print("\n⏹️ 데이터베이스 연결이 종료되었습니다.")