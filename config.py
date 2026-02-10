import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Supabase Connection Pooler 사용 (IPv6 문제 해결)
    # 직접 연결 대신 pgbouncer를 통한 연결 사용
    db_url = os.environ.get('SUPABASE_DB_URL') or 'sqlite:///app.db'
    
    # 포트 5432를 6543으로 변경 (connection pooler)
    if 'supabase.co:5432' in db_url:
        db_url = db_url.replace(':5432/', ':6543/')
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20,
    }
    # 세션 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
