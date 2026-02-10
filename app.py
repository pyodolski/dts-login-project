from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, LoginHistory
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = '로그인이 필요합니다.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        try:
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('아이디와 비밀번호를 입력해주세요.', 'danger')
                return render_template('login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                user.last_login = datetime.utcnow()
                
                # 로그인 기록 저장
                login_record = LoginHistory(
                    user_id=user.id,
                    ip_address=request.remote_addr,
                    user_agent=request.headers.get('User-Agent')
                )
                db.session.add(login_record)
                db.session.commit()
                
                flash('로그인에 성공했습니다!', 'success')
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('로그인 중 오류가 발생했습니다.', 'danger')
            print(f"Login error: {e}")
    
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
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if not username or not email or not password:
                flash('모든 필드를 입력해주세요.', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('이미 존재하는 사용자명입니다.', 'danger')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('이미 존재하는 이메일입니다.', 'danger')
                return redirect(url_for('register'))
            
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            
            flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'회원가입 중 오류가 발생했습니다. 관리자에게 문의하세요.', 'danger')
            print(f"Registration error: {e}")
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
