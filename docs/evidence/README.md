# 실행 증거

| 파일 | 내용 | 만든 방법 |
|---|---|---|
| `run-log.txt` | 메뉴 입력 검증, 퀴즈 추가·풀기·점수·삭제·종료, 재실행 후 데이터 유지 | `python scripts/record_demo.py` (입력을 자동으로 흘려 보낸 실제 실행 출력) |
| `test-log.txt` | 단위 테스트 23개 전체 출력 | `python -m unittest -v` |
| `benchmark-log.txt` | 퀴즈 1,000~10,000개 성능 측정 | `python benchmark_quizzes.py` |
| `git-log.txt` | `git remote -v`, 브랜치, 그래프 로그 | 본인 PC에서 `bash scripts/collect_git_evidence.sh` |
| `clone-pull-log.txt` | clone → 수정 → push → pull | 본인 PC에서 `bash scripts/clone_pull_practice.sh` |

- `run-log.txt`는 자동 입력으로 만든 로그라서 사람이 직접 입력한 화면 캡처를 대체하지 않습니다. 제출용 스크린샷은 `python main.py`를 직접 실행해서 따로 찍으세요.
- `git-log.txt`와 `clone-pull-log.txt`는 GitHub에 push한 뒤 본인 PC에서 실행해야 의미가 있어, 이 저장소에는 아직 들어 있지 않습니다.
