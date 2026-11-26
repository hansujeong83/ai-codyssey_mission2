"""입력을 자동으로 흘려 보내 실행 화면(프롬프트+입력+출력)을 텍스트로 기록한다.

사용: python scripts/record_demo.py > docs/evidence/run-log.txt
실제 main.py 코드를 임시 폴더의 state.json으로 실행하며, 사람이 입력한 화면 캡처를 대체하지 않는다.
"""
import builtins
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from main import QuizGame  # noqa: E402


def session(path, inputs, title):
    print("=" * 60)
    print(title)
    print("=" * 60)
    feed = iter(inputs)

    def fake_input(prompt=""):
        value = next(feed)
        print(f"{prompt}{value}")
        return value

    with patch.object(builtins, "input", fake_input):
        QuizGame(path, rng=__import__("random").Random(1)).run()


def main():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "state.json"
        session(path, [
            "abc", "", "9", "3",                      # 잘못된 메뉴 입력과 목록
            "2", "영화 '기생충'의 감독은?", "박찬욱", "봉준호", "김기덕", "이창동", "2", "",  # 퀴즈 추가
            "4",                                        # 점수(아직 없음)
            "1", "0", "abc", "3", "1", "1", "1",         # 퀴즈 풀기(3문제, 입력 오류 포함)
            "4",                                        # 점수 확인
            "5", "8",                                   # 삭제(범위 오류)
            "5", "1",                                   # 1번 삭제
            "6",
        ], "[세션 1] 입력 검증 → 추가 → 풀기 → 점수 → 삭제 → 종료")
        session(path, ["3", "4", "6"], "[세션 2] 재실행 후 저장된 퀴즈와 점수 유지 확인")


if __name__ == "__main__":
    main()
