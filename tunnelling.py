import pymysql
from sshtunnel import SSHTunnelForwarder
import pandas as pd

# 1. 팀원에게 받은 정보 변수화
ssh_host = '175.45.194.216'
ssh_port = 22
ssh_user = 'root'
ssh_password = 'M6bdM*Tc!H5?h'

mysql_host = '192.168.6.6'
mysql_port = 3306  # MySQL 기본 포트
mysql_user = 'addd'
mysql_password = '!@addd1004'
mysql_db = 'bus_operation_logs' # 데이터베이스 이름 확인 필요 (bus_operation_logs는 테이블일 수 있습니다)
try:
    with SSHTunnelForwarder(
        (ssh_host, ssh_port),
        ssh_username=ssh_user,
        ssh_password=ssh_password,
        remote_bind_address=(mysql_host, mysql_port)
    ) as tunnel:
        conn = pymysql.connect(
            host='127.0.0.1', 
            port=tunnel.local_bind_port,
            user=mysql_user,
            password=mysql_password,
            db=mysql_db,
            charset='utf8'
        )
        print("데이터베이스에 성공적으로 접속했습니다!")

        # 1. SQL 쿼리를 DESCRIBE로 변경
        sql_query = "DESCRIBE bus_operation_logs;"
        
        # 2. Pandas를 이용해 바로 DataFrame으로 읽어오기
        # read_sql_query를 사용하면 컬럼명까지 한번에 깔끔하게 가져옵니다.
        schema_df = pd.read_sql_query(sql_query, conn)

        print("\n--- bus_operation_logs 테이블 스키마 정보 ---")
        print(schema_df)

finally:
    if 'conn' in locals() and conn.open:
        conn.close()
        print("\n데이터베이스 연결이 종료되었습니다.")