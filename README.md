# Mission 2 — 나만의 Python 퀴즈 게임

Python 클래스, 데이터 검증, 예외 처리, JSON 파일 영속성, 테스트, Git 협업 흐름을 연습하는 콘솔 프로그램입니다. Python 3.10 이상, 외부 패키지 없이 실행합니다.

## 핵심 기능
- `Quiz` 데이터 클래스: 질문, 선택지 4개, 정답, 선택 힌트 검증
- `QuizGame`: 문제 추가/목록/무작위 출제/채점/점수 기록
- 최고 점수, 누적 게임 수, 평균 점수 표시
- 퀴즈 삭제(보너스): 번호 선택 후 삭제하고 즉시 `state.json`에 반영
- JSON 자동 저장과 재실행 후 복원
- JSON 손상, 잘못된 구조, 잘못된 필드 값 복구
- 빈 입력, 숫자 형식, 범위 오류, EOF/Ctrl+C 처리
- 원자적 저장: 임시 파일 작성 후 `replace()`로 교체

## 실행
```bash
python main.py
```

## 자동 테스트
```bash
python -m py_compile main.py test_main.py
python -m unittest -v
```
테스트는 임시 디렉터리를 사용하므로 실제 `state.json`을 오염시키지 않습니다.

## 파일
```text
ai-codyssey_mission2/
├── main.py
├── test_main.py
├── README.md
├── .gitignore
└── state.json       # 첫 실행 시 생성, Git에는 올리지 않음
```

## JSON 구조
```json
{
  "quizzes": [
    {"question": "질문", "choices": ["A", "B", "C", "D"], "answer": 2, "hint": "힌트"}
  ],
  "best_score": 100,
  "history": [{"total": 5, "correct": 5, "score": 100}]
}
```
정답은 1~4 정수이며 점수는 0~100 정수입니다. 잘못된 저장 구조는 기본 퀴즈로 복구합니다.

## 클래스를 나눈 이유
- `Quiz`는 문제 하나의 데이터와 검증(선택지 4개, 정답 1~4)만 책임집니다. 검증이 한곳에 있어 어디서 만들든 잘못된 퀴즈가 생기지 않고(추상화), 파일 복원·퀴즈 추가에서 그대로 재사용합니다(재사용성).
- `QuizGame`은 메뉴 진행, 점수, 저장/불러오기를 책임집니다. 화면 흐름이 바뀌어도 `Quiz`는 수정하지 않습니다.
- 테스트가 `QuizGame(임시경로)`로 실제 파일을 건드리지 않고 동작을 검증할 수 있는 것도 역할 분리 덕분입니다.

## 주요 진입점(메서드)
| 역할 | 메서드 |
|---|---|
| 입력 검증 | `parse_int`, `ask_int`, `ask_text` |
| 게임 진행 | `run`, `play`, `add_quiz`, `delete_quiz`, `list_quizzes`, `show_score` |
| 데이터 입출력 | `load_state`, `save_state`, `validate_state`, `backup_corrupt_state` |
흐름: 생성자 → `load_state`(없으면 기본값 저장) → 메뉴 반복 → 변경 때마다 `save_state` → 종료 시 저장.

## 요구사항이 바뀌면 수정할 곳
| 변경 | 수정 대상 |
|---|---|
| 점수 계산 방식 | `QuizGame.play`의 `score` 계산, `show_score`, 관련 테스트 |
| 선택지 개수 변경 | `Quiz.__post_init__`, `Quiz.from_dict`, `add_quiz`, 기본 퀴즈 데이터, 테스트 |
| 저장 형식 변경 | `save_state`, `validate_state`(이전 형식도 읽도록 버전 필드 권장), README의 JSON 구조 |
| 새 메뉴 추가 | `MENU_TEXT`, `MENU_MAX`, `run`의 분기, 새 메서드와 테스트 |
저장 형식을 바꿀 때는 `state.json`에 `version` 필드를 두고 `validate_state`가 이전 버전을 변환하게 하면 호환성이 유지됩니다.

## 손상 파일 백업과 복구 절차
1. `state.json`을 읽다가 JSON 오류나 잘못된 구조를 만나면 안내 메시지를 출력합니다.
2. 덮어쓰기 전에 원본을 `state.json.corrupt.bak`으로 복사해 보존합니다(Git에는 올리지 않음).
3. 기본 퀴즈와 점수 0으로 새 `state.json`을 만들어 프로그램을 계속 실행합니다.
4. 이전 데이터를 살리려면 `.corrupt.bak`을 열어 깨진 부분을 고친 뒤 `state.json`으로 이름을 바꿉니다.
저장은 임시 파일에 쓴 뒤 `replace()`로 교체해서, 저장 중 중단되어도 기존 파일이 반쯤 깨지지 않게 합니다. Ctrl+C와 EOF는 입력 예외로 처리해 저장 후 종료합니다. SIGTERM 같은 프로세스 시그널은 별도로 처리하지 않으므로, 강제 종료 시 마지막 변경은 이미 저장된 시점까지만 남습니다(변경 때마다 저장).

## 대량 퀴즈(1,000개 이상) 성능
`python benchmark_quizzes.py`로 측정했습니다(이 세션 환경 값이며 PC마다 다릅니다).

| 퀴즈 수 | 저장(ms) | 불러오기(ms) | 10문제 추출(ms) | 파일 크기(KB) | 피크 메모리(KB) |
|---|---:|---:|---:|---:|---:|
| 1,000 | 4.37 | 12.36 | 0.026 | 156 | 760 |
| 5,000 | 15.79 | 66.07 | 0.016 | 785 | 3,801 |
| 10,000 | 32.41 | 118.24 | 0.017 | 1,571 | 7,606 |
저장·불러오기는 퀴즈 수에 비례해 늘고(선형), 문제 추출은 개수와 거의 무관합니다. 퀴즈 10,000개도 불러오기가 0.12초 수준이라 이 규모에서 병목은 아닙니다. 현재 구조는 변경 때마다 전체 파일을 다시 저장하므로 수만 개 이상이면 SQLite 같은 저장소를 고려해야 합니다.

## 입력 검증 테스트 요약
- 빈 입력, 숫자 변환 실패, 범위 밖 숫자: `parse_int` 테스트
- 입력 중단(EOF): 추가·삭제 취소 테스트
- 파일 손상, 구조 오류, 이력 값 오류, 손상 파일 백업: 영속성 테스트
`python -m unittest -v`로 전체 테스트(23개)를 확인합니다.

## Git 과제 수행 — 10개 이상 의미 있는 커밋
아래 순서는 예시 메시지입니다. 각 단계에서 파일을 실제로 수정하고, `git diff`로 변경을 확인한 뒤 커밋합니다. 동일한 변경을 반복 커밋하거나 커밋 날짜를 조작하지 않습니다.

```bash
git init
git branch -M main
git add README.md .gitignore
git commit -m "docs: 프로젝트 목적과 실행 방법 작성"

# Quiz 모델을 작성한 뒤
git add main.py
git commit -m "feat: Quiz 데이터 모델과 입력 검증 구현"

# 기본 문제 목록을 추가한 뒤
git add main.py
git commit -m "feat: 기본 퀴즈 데이터 7개 추가"

# feature 브랜치에서 진행
git switch -c feature/quiz-flow
# 출제·채점 기능을 구현하고 테스트
git add main.py
git commit -m "feat: 무작위 퀴즈 출제와 채점 구현"

# 목록·문제 추가 기능을 구현
git add main.py
git commit -m "feat: 퀴즈 등록과 목록 기능 구현"

# JSON 저장/복원을 구현
git add main.py
git commit -m "feat: JSON 상태 저장과 복원 구현"

# 오류 처리와 데이터 검증을 보강
git add main.py
git commit -m "fix: 손상된 JSON과 잘못된 입력 복구"

# 점수 통계 기능 구현
git add main.py
git commit -m "feat: 최고 점수와 게임 통계 추가"

# 브랜치 병합
git switch main
git merge --no-ff feature/quiz-flow -m "merge: 퀴즈 기능 브랜치 병합"

# 테스트 추가
git add test_main.py
git commit -m "test: 모델과 저장 기능 단위 테스트 추가"

# 문서와 ignore 정리
git add README.md .gitignore
git commit -m "docs: 테스트와 Git 워크플로우 문서화"

# 실제 저장소 연결 및 push
git remote add origin https://github.com/hansujeong83/ai-codyssey_mission2.git
git push -u origin main
```
위 예시는 10개 이상의 커밋을 만들기 위한 **단계별 작업 기록 예시**입니다. 각 커밋 전에 해당 기능을 실제로 구현하고 테스트해야 합니다. 최종 제출 증거로 다음을 저장합니다.
```bash
git log --oneline --graph --decorate --all
git branch -avv
git remote -v
```

## clone / pull 실습
원격에 push한 뒤 별도 폴더에서:
```bash
cd ..
git clone https://github.com/hansujeong83/ai-codyssey_mission2.git mission2-clone-check
cd mission2-clone-check
git status
```
원본 작업 폴더에서 README에 실제 실행 결과를 추가하고 commit/push한 다음, clone 폴더에서:
```bash
git pull origin main
git log -1 --oneline
```
`git pull` 전후의 변경을 터미널 캡처로 남깁니다. 원격 인증 토큰은 절대 문서에 기록하지 않습니다.
