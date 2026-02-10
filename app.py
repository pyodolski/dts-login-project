from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, LoginHistory
from datetime import datetime
import sys
import traceback

app = Flask(__name__)
app.config.from_object(Config)

# 로깅 설정
import logging
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '로그인이 필요합니다.'

# Jinja2 필터: UTC를 KST로 변환
@app.template_filter('kst')
def to_kst(dt):
    if dt is None:
        return None
    from datetime import timedelta
    return dt + timedelta(hours=9)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/health')
def health():
    """헬스체크 및 DB 연결 확인"""
    try:
        # DB 연결 테스트
        user_count = User.query.count()
        db_status = f"OK - {user_count} users"
    except Exception as e:
        db_status = f"ERROR - {str(e)}"
    
    return {
        'status': 'running',
        'database': db_status,
        'db_url': app.config['SQLALCHEMY_DATABASE_URI'][:30] + '...' if app.config['SQLALCHEMY_DATABASE_URI'] else 'Not set'
    }

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            app.logger.info("=== 로그인 시도 ===")
            username = request.form.get('username')
            password = request.form.get('password')
            
            app.logger.info(f"Username: {username}")
            
            if not username or not password:
                app.logger.warning("아이디/비밀번호 누락")
                flash('아이디와 비밀번호를 입력해주세요.', 'danger')
                return render_template('login.html')
            
            app.logger.info("사용자 조회 시작")
            user = User.query.filter_by(username=username).first()
            
            if not user:
                app.logger.warning(f"사용자 없음: {username}")
                flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
                return render_template('login.html')
            
            app.logger.info(f"사용자 찾음: {user.username}")
            
            if not user.check_password(password):
                app.logger.warning("비밀번호 불일치")
                flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
                return render_template('login.html')
            
            app.logger.info("비밀번호 확인 완료, 로그인 처리")
            login_user(user, remember=True)
            
            # 마지막 로그인 시간 업데이트
            user.last_login = datetime.utcnow()
            
            # 로그인 기록 저장
            login_record = LoginHistory(
                user_id=user.id,
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent', '')[:255]
            )
            db.session.add(login_record)
            db.session.commit()
            
            app.logger.info(f"로그인 성공: {username}")
            flash('로그인에 성공했습니다!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"로그인 에러: {str(e)}")
            app.logger.error(traceback.format_exc())
            flash('로그인 중 오류가 발생했습니다.', 'danger')
            return render_template('login.html')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    return render_template('logout.html')

@app.route('/logout/confirm', methods=['POST'])
@login_required
def logout_confirm():
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    login_history = LoginHistory.query.filter_by(user_id=current_user.id).order_by(LoginHistory.login_time.desc()).limit(5).all()
    return render_template('dashboard.html', login_history=login_history)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            app.logger.info("=== 회원가입 시작 ===")
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            app.logger.info(f"Username: {username}, Email: {email}")
            
            if not username or not email or not password:
                app.logger.warning("필수 필드 누락")
                flash('모든 필드를 입력해주세요.', 'danger')
                return redirect(url_for('register'))
            
            app.logger.info("중복 체크 시작")
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                app.logger.warning(f"중복 사용자명: {username}")
                flash('이미 존재하는 사용자명입니다.', 'danger')
                return redirect(url_for('register'))
            
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                app.logger.warning(f"중복 이메일: {email}")
                flash('이미 존재하는 이메일입니다.', 'danger')
                return redirect(url_for('register'))
            
            app.logger.info("사용자 생성 시작")
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            app.logger.info(f"회원가입 성공: {username}")
            flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"회원가입 에러: {str(e)}")
            app.logger.error(traceback.format_exc())
            flash(f'회원가입 중 오류가 발생했습니다.', 'danger')
            return redirect(url_for('register'))
    
    return render_template('register.html')

@app.cli.command()
def init_db():
    """데이터베이스 초기화"""
    db.create_all()
    print('데이터베이스가 초기화되었습니다.')

@app.cli.command()
def create_test_user():
    """테스트 사용자 생성"""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    print('테스트 사용자가 생성되었습니다. (username: testuser, password: password123)')

# 요청 후 DB 연결 정리
@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

# Vercel serverless 환경에서 테이블 자동 생성
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Database initialization error: {e}")

# Vercel serverless function handler
app = app

if __name__ == '__main__':
    app.run(debug=True)
