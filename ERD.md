# 데이터베이스 ERD (Entity Relationship Diagram)

## 프로젝트 개요

- **프로젝트명**: DTS 직무과제 - 로그인/로그아웃 시스템
- **데이터베이스**: PostgreSQL (Supabase)
- **ORM**: SQLAlchemy (Flask-SQLAlchemy)

---

## ERD 다이어그램

```
┌─────────────────────────────────────┐
│            users                    │
├─────────────────────────────────────┤
│ PK  id              INTEGER         │
│ UK  username        VARCHAR(80)     │
│ UK  email           VARCHAR(120)    │
│     password_hash   VARCHAR(255)    │
│     created_at      DATETIME        │
│     last_login      DATETIME        │
└─────────────────────────────────────┘
              │
              │ 1:N
              │
              ▼
┌─────────────────────────────────────┐
│        login_history                │
├─────────────────────────────────────┤
│ PK  id              INTEGER         │
│ FK  user_id         INTEGER         │
│     login_time      DATETIME        │
│     ip_address      VARCHAR(45)     │
│     user_agent      VARCHAR(255)    │
└─────────────────────────────────────┘
```

---

## 테이블 상세 설명

### 1. users (사용자 테이블)

사용자 계정 정보를 저장하는 메인 테이블입니다.

| 컬럼명        | 데이터 타입  | 제약조건                    | 설명                              |
| ------------- | ------------ | --------------------------- | --------------------------------- |
| id            | INTEGER      | PRIMARY KEY, AUTO_INCREMENT | 사용자 고유 ID                    |
| username      | VARCHAR(80)  | UNIQUE, NOT NULL, INDEX     | 사용자명 (로그인 ID)              |
| email         | VARCHAR(120) | UNIQUE, NOT NULL, INDEX     | 이메일 주소                       |
| password_hash | VARCHAR(255) | NOT NULL                    | 암호화된 비밀번호 (Werkzeug 해시) |
| created_at    | DATETIME     | DEFAULT CURRENT_TIMESTAMP   | 계정 생성 일시                    |
| last_login    | DATETIME     | NULLABLE                    | 마지막 로그인 일시                |

**인덱스**:

- `username` (UNIQUE INDEX) - 로그인 시 빠른 조회
- `email` (UNIQUE INDEX) - 이메일 중복 체크

**보안**:

- 비밀번호는 `werkzeug.security.generate_password_hash`로 암호화
- 평문 비밀번호는 저장하지 않음

---

### 2. login_history (로그인 기록 테이블)

사용자의 로그인 이력을 추적하는 테이블입니다.

| 컬럼명     | 데이터 타입  | 제약조건                         | 설명                     |
| ---------- | ------------ | -------------------------------- | ------------------------ |
| id         | INTEGER      | PRIMARY KEY, AUTO_INCREMENT      | 기록 고유 ID             |
| user_id    | INTEGER      | FOREIGN KEY (users.id), NOT NULL | 사용자 ID (외래키)       |
| login_time | DATETIME     | DEFAULT CURRENT_TIMESTAMP        | 로그인 시간              |
| ip_address | VARCHAR(45)  | NULLABLE                         | 접속 IP 주소 (IPv6 지원) |
| user_agent | VARCHAR(255) | NULLABLE                         | 브라우저 User-Agent 정보 |

**외래키 관계**:

- `user_id` → `users.id` (CASCADE DELETE)
  - 사용자 삭제 시 관련 로그인 기록도 함께 삭제

---

## 관계 (Relationships)

### users ↔ login_history (1:N)

- **관계 유형**: One-to-Many (일대다)
- **설명**: 한 명의 사용자는 여러 개의 로그인 기록을 가질 수 있음
- **구현**:
  ```python
  # User 모델
  login_history = db.relationship('LoginHistory',
                                  backref='user',
                                  lazy=True,
                                  cascade='all, delete-orphan')
  ```
- **Cascade 옵션**:
  - `all, delete-orphan`: 사용자 삭제 시 모든 로그인 기록 자동 삭제

---

## 데이터베이스 설정

### 연결 정보

```python
# PostgreSQL (Supabase)
SQLALCHEMY_DATABASE_URI = os.environ.get('SUPABASE_DB_URL')

# Connection Pool 설정
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,      # 연결 유효성 검사
    'pool_recycle': 60,         # 60초마다 연결 재생성
    'pool_size': 1,             # 최소 연결 수
    'max_overflow': 0,          # 추가 연결 허용 안함
    'pool_timeout': 10,         # 연결 대기 시간 10초
}
```

### 초기화 명령어

```bash
# 데이터베이스 테이블 생성
flask init-db

# 테스트 사용자 생성
flask create-test-user
```

---

## 샘플 데이터

### users 테이블

```sql
INSERT INTO users (username, email, password_hash, created_at) VALUES
('testuser', 'test@example.com', 'pbkdf2:sha256:...', '2026-02-10 10:00:00');
```

### login_history 테이블

```sql
INSERT INTO login_history (user_id, login_time, ip_address, user_agent) VALUES
(1, '2026-02-10 10:05:00', '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...');
```

---

## 보안 고려사항

1. **비밀번호 암호화**: Werkzeug의 PBKDF2 SHA256 해시 사용
2. **SQL Injection 방지**: SQLAlchemy ORM 사용으로 자동 방지
3. **세션 보안**:
   - `SESSION_COOKIE_SECURE = True` (HTTPS only)
   - `SESSION_COOKIE_HTTPONLY = True` (JavaScript 접근 차단)
4. **인덱스 최적화**: username, email에 인덱스 적용으로 조회 성능 향상

---

## 확장 가능성

향후 추가 가능한 테이블:

- `user_roles`: 사용자 권한 관리
- `password_reset_tokens`: 비밀번호 재설정 토큰
- `user_sessions`: 세션 관리
- `audit_logs`: 시스템 감사 로그
