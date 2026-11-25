# Mission 2 — 나만의 Python 퀴즈 게임

Python 클래스, 데이터 검증, 예외 처리, JSON 파일 영속성, 테스트, Git 협업 흐름을 연습하는 콘솔 프로그램입니다. Python 3.10 이상, 외부 패키지 없이 실행합니다.

## 핵심 기능
- `Quiz` 데이터 클래스: 질문, 선택지 4개, 정답, 선택 힌트 검증
- `QuizGame`: 문제 추가/목록/무작위 출제/채점/점수 기록
- 최고 점수, 누적 게임 수, 평균 점수 표시
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
