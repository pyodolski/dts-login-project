import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Supabase 연결 설정
    db_url = os.environ.get('SUPABASE_DB_URL') or 'sqlite:///app.db'
    
    # SSL 모드 추가 (Supabase Pooler 사용 시 필요)
    if 'supabase.com' in db_url and '?' not in db_url:
        db_url += '?sslmode=require'
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10,
        'connect_args': {
            'connect_timeout': 10,
            'sslmode': 'require'
        }
    }
    # 세션 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
