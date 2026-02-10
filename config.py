import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # Supabase 연결 설정
    db_url = os.environ.get('SUPABASE_DB_URL') or 'sqlite:///app.db'
    
    # IPv6 문제 해결: Supabase Pooler 사용 + IPv4 강제
    if 'supabase.co' in db_url:
        # 포트 6543 사용 (Connection Pooler)
        if ':5432' in db_url:
            db_url = db_url.replace(':5432/', ':6543/')
        
        # IPv4 전용 엔드포인트 사용
        # db.xxx.supabase.co → aws-0-ap-northeast-2.pooler.supabase.com
        # 또는 프로젝트별 pooler 주소 사용
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 5,
        'max_overflow': 10,
        'connect_args': {
            'connect_timeout': 10,
        }
    }
    # 세션 설정
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
