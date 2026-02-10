# Vercel 배포 가이드

## 배포 전 준비사항

### 1. GitHub 저장소 생성

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### 2. Vercel 계정 준비

- https://vercel.com 에서 GitHub 계정으로 로그인

## Vercel 배포 단계

### 방법 1: Vercel 웹사이트에서 배포

1. **Vercel 대시보드 접속**
   - https://vercel.com/dashboard

2. **New Project 클릭**
   - Import Git Repository 선택
   - GitHub 저장소 연결

3. **프로젝트 설정**
   - Framework Preset: `Other`
   - Root Directory: `./`
   - Build Command: (비워두기)
   - Output Directory: (비워두기)

4. **환경 변수 설정**
   Environment Variables 섹션에서 추가:

   ```
   SUPABASE_DB_URL = postgresql://postgres:66FtX3GFgW363Zhp@db.icfduytlkfhoyksfmazc.supabase.co:5432/postgres
   SECRET_KEY = your-production-secret-key-here
   ```

5. **Deploy 클릭**

### 방법 2: Vercel CLI로 배포

```bash
# Vercel CLI 설치
npm i -g vercel

# 로그인
vercel login

# 배포
vercel

# 프로덕션 배포
vercel --prod
```

## 환경 변수 설정 (중요!)

Vercel 프로젝트 설정에서 다음 환경 변수를 추가하세요:

```
SUPABASE_DB_URL = postgresql://postgres:66FtX3GFgW363Zhp@db.icfduytlkfhoyksfmazc.supabase.co:5432/postgres
SECRET_KEY = [강력한 랜덤 키 생성]
```

**SECRET_KEY 생성 방법:**

```python
import secrets
print(secrets.token_hex(32))
```

## 데이터베이스 초기화

배포 후 Supabase에서 직접 테이블을 생성해야 합니다.

### Supabase SQL Editor에서 실행:

```sql
-- users 테이블 생성
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);

-- login_history 테이블 생성
CREATE TABLE login_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    user_agent VARCHAR(255)
);

CREATE INDEX idx_login_history_user_id ON login_history(user_id);
```

## 배포 후 확인사항

1. **배포 URL 확인**
   - Vercel이 제공하는 URL (예: `your-app.vercel.app`)

2. **데이터베이스 연결 테스트**
   - 회원가입 페이지에서 테스트 계정 생성
   - 로그인 테스트

3. **환경 변수 확인**
   - Vercel 대시보드 → Settings → Environment Variables

## 문제 해결

### 배포 실패 시

- Vercel 대시보드에서 Deployment Logs 확인
- `requirements.txt`의 패키지 버전 확인

### 데이터베이스 연결 오류

- Supabase 연결 문자열 확인
- Supabase 프로젝트가 활성화되어 있는지 확인
- IP 화이트리스트 설정 (Supabase는 기본적으로 모든 IP 허용)

### 500 에러

- Vercel Function Logs 확인
- 환경 변수가 올바르게 설정되었는지 확인

## 커스텀 도메인 연결 (선택사항)

1. Vercel 프로젝트 → Settings → Domains
2. 도메인 추가 및 DNS 설정
3. SSL 자동 적용

## 주의사항

- `.env` 파일은 Git에 커밋하지 마세요 (`.gitignore`에 포함됨)
- 프로덕션 환경에서는 강력한 SECRET_KEY 사용
- Supabase 비밀번호는 환경 변수로만 관리
- 정기적으로 보안 업데이트 확인
