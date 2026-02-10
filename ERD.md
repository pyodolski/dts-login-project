# 데이터베이스 ERD (Entity Relationship Diagram)

## 데이터베이스 구조

```
┌─────────────────────────────────────┐
│            users                    │
├─────────────────────────────────────┤
│ PK  id              INTEGER         │
│     username        VARCHAR(80)     │ UNIQUE, INDEX
│     email           VARCHAR(120)    │ UNIQUE, INDEX
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
│ FK  user_id         INTEGER         │ → users.id
│     login_time      DATETIME        │
│     ip_address      VARCHAR(45)     │
│     user_agent      VARCHAR(255)    │
└─────────────────────────────────────┘
```

## 테이블 설명

### 1. users (사용자 테이블)

사용자 계정 정보를 저장하는 메인 테이블

**컬럼:**

- `id`: 기본 키 (Primary Key)
- `username`: 사용자명 (고유값, 인덱스)
- `email`: 이메일 주소 (고유값, 인덱스)
- `password_hash`: 암호화된 비밀번호 (Werkzeug 사용)
- `created_at`: 계정 생성 시간
- `last_login`: 마지막 로그인 시간

**제약 조건:**

- username: UNIQUE, NOT NULL
- email: UNIQUE, NOT NULL
- password_hash: NOT NULL

### 2. login_history (로그인 기록 테이블)

사용자의 로그인 이력을 추적하는 테이블

**컬럼:**

- `id`: 기본 키 (Primary Key)
- `user_id`: 사용자 ID (Foreign Key → users.id)
- `login_time`: 로그인 시간
- `ip_address`: 접속 IP 주소 (IPv4/IPv6 지원)
- `user_agent`: 브라우저 정보

**관계:**

- users와 1:N 관계 (한 사용자는 여러 로그인 기록을 가질 수 있음)
- CASCADE DELETE: 사용자 삭제 시 관련 로그인 기록도 함께 삭제

## 인덱스 전략

1. **users.username**: 로그인 시 빠른 조회를 위한 인덱스
2. **users.email**: 이메일 기반 조회 최적화
3. **login_history.user_id**: 외래 키 인덱스 (자동 생성)

## 보안 고려사항

- 비밀번호는 Werkzeug의 `generate_password_hash`를 사용하여 암호화
- 평문 비밀번호는 데이터베이스에 저장되지 않음
- 로그인 기록을 통한 보안 감사 추적 가능
