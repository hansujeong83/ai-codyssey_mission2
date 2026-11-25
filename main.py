"""Codyssey Mission 2: a JSON-persistent terminal quiz game."""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

STATE_FILE = Path(__file__).with_name("state.json")


@dataclass
class Quiz:
    question: str
    choices: list[str]
    answer: int
    hint: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.question, str) or not self.question.strip():
            raise ValueError("문제는 비어 있을 수 없습니다.")
        if not isinstance(self.choices, list) or len(self.choices) != 4:
            raise ValueError("선택지는 정확히 4개여야 합니다.")
        if any(not isinstance(item, str) or not item.strip() for item in self.choices):
            raise ValueError("선택지는 빈 문자열일 수 없습니다.")
        if isinstance(self.answer, bool) or not isinstance(self.answer, int) or self.answer not in range(1, 5):
            raise ValueError("정답 번호는 1~4의 정수여야 합니다.")
        if not isinstance(self.hint, str):
            raise ValueError("힌트는 문자열이어야 합니다.")

    def is_correct(self, answer: int) -> bool:
        return answer == self.answer

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Quiz":
        if not isinstance(data, dict):
            raise ValueError("퀴즈 데이터는 객체여야 합니다.")
        return cls(
            question=data["question"],
            choices=data["choices"],
            answer=data["answer"],
            hint=data.get("hint", ""),
        )


DEFAULT_QUIZZES = [
    Quiz("Python에서 화면에 글자를 출력하는 함수는?", ["input()", "print()", "len()", "type()"], 2, "출력이라는 뜻의 영어 단어입니다."),
    Quiz("리스트(list)를 만드는 괄호는?", ["{}", "()", "[]", "<>"], 3),
    Quiz("딕셔너리(dict)는 무엇을 저장하나요?", ["키와 값", "숫자만", "문자 하나", "파일 경로만"], 1),
    Quiz("반복 횟수가 정해진 경우 자주 사용하는 반복문은?", ["if", "for", "class", "return"], 2),
    Quiz("JSON 파일을 읽고 쓰는 표준 라이브러리는?", ["random", "time", "json", "math"], 3),
    Quiz("클래스에서 객체 자신을 가리키는 관례적 매개변수는?", ["this", "self", "me", "object"], 2),
    Quiz("Git에서 변경사항을 기록하는 명령은?", ["git status", "git commit", "git clone", "git log"], 2),
]


class QuizGame:
    def __init__(self, state_path: Path = STATE_FILE, rng: Any = None):
        self.state_path = Path(state_path)
        self.rng = rng or random
        self.quizzes = list(DEFAULT_QUIZZES)
        self.best_score = 0
        self.history: list[dict[str, int]] = []
        self.load_state()

    @staticmethod
    def parse_int(raw: str, minimum: int, maximum: int) -> int:
        try:
            value = int(raw.strip())
        except (AttributeError, TypeError, ValueError) as exc:
            raise ValueError("숫자로 입력해 주세요.") from exc
        if not minimum <= value <= maximum:
            raise ValueError(f"{minimum}~{maximum} 사이의 숫자를 입력해 주세요.")
        return value

    @staticmethod
    def validate_state(data: Any) -> tuple[list[Quiz], int, list[dict[str, int]]]:
        if not isinstance(data, dict):
            raise ValueError("저장 데이터의 최상위 구조는 객체여야 합니다.")
        raw_quizzes = data.get("quizzes", [])
        if not isinstance(raw_quizzes, list):
            raise ValueError("quizzes는 배열이어야 합니다.")
        quizzes = [Quiz.from_dict(item) for item in raw_quizzes]
        if not quizzes:
            quizzes = list(DEFAULT_QUIZZES)

        best_score = data.get("best_score", 0)
        if isinstance(best_score, bool) or not isinstance(best_score, int) or not 0 <= best_score <= 100:
            raise ValueError("best_score는 0~100 정수여야 합니다.")

        history = data.get("history", [])
        if not isinstance(history, list):
            raise ValueError("history는 배열이어야 합니다.")
        clean_history = []
        for item in history:
            if not isinstance(item, dict):
                raise ValueError("history 항목은 객체여야 합니다.")
            total, correct, score = item.get("total"), item.get("correct"), item.get("score")
            if any(isinstance(v, bool) or not isinstance(v, int) for v in (total, correct, score)):
                raise ValueError("history 값은 정수여야 합니다.")
            if total < 1 or not 0 <= correct <= total or not 0 <= score <= 100:
                raise ValueError("history 값의 범위가 올바르지 않습니다.")
            clean_history.append({"total": total, "correct": correct, "score": score})
        return quizzes, best_score, clean_history

    def load_state(self) -> None:
        if not self.state_path.exists():
            self.save_state()
            return
        try:
            raw = self.state_path.read_text(encoding="utf-8")
            data = json.loads(raw)
            self.quizzes, self.best_score, self.history = self.validate_state(data)
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            print(f"저장 파일 복구: {exc}")
            self.quizzes = list(DEFAULT_QUIZZES)
            self.best_score = 0
            self.history = []
            self.save_state()

    def save_state(self) -> None:
        payload = {
            "quizzes": [asdict(quiz) for quiz in self.quizzes],
            "best_score": self.best_score,
            "history": self.history,
        }
        temp_path = self.state_path.with_name(self.state_path.name + ".tmp")
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            temp_path.replace(self.state_path)
        except OSError as exc:
            print(f"저장 오류: {exc}")
            try:
                temp_path.unlink(missing_ok=True)
            except OSError:
                pass

    @staticmethod
    def ask_text(prompt: str, allow_empty: bool = False) -> str | None:
        while True:
            try:
                value = input(prompt).strip()
            except (EOFError, KeyboardInterrupt):
                print("\n입력이 종료되어 현재 작업을 취소합니다.")
                return None
            if value or allow_empty:
                return value
            print("빈 입력은 사용할 수 없습니다.")

    @staticmethod
    def ask_int(prompt: str, minimum: int, maximum: int) -> int | None:
        while True:
            try:
                raw = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print("\n입력이 종료되어 현재 작업을 취소합니다.")
                return None
            try:
                return QuizGame.parse_int(raw, minimum, maximum)
            except ValueError as exc:
                print(exc)

    def add_quiz(self) -> bool:
        print("\n새 퀴즈 등록")
        question = self.ask_text("문제: ")
        if question is None:
            return False
        choices = []
        for index in range(1, 5):
            choice = self.ask_text(f"선택지 {index}: ")
            if choice is None:
                return False
            choices.append(choice)
        answer = self.ask_int("정답 번호 (1~4): ", 1, 4)
        if answer is None:
            return False
        hint = self.ask_text("힌트(선택): ", allow_empty=True)
        if hint is None:
            return False
        self.quizzes.append(Quiz(question, choices, answer, hint))
        self.save_state()
        print("퀴즈를 저장했습니다.")
        return True

    def play(self, count: int | None = None) -> int | None:
        if not self.quizzes:
            print("등록된 퀴즈가 없습니다.")
            return None
        if count is None:
            count = self.ask_int(f"몇 문제를 풀까요? (1~{len(self.quizzes)}): ", 1, len(self.quizzes))
        if count is None:
            return None
        if not 1 <= count <= len(self.quizzes):
            raise ValueError("출제 문제 수가 등록된 퀴즈 범위를 벗어났습니다.")

        selected = self.rng.sample(self.quizzes, count)
        correct = 0
        for index, quiz in enumerate(selected, 1):
            print(f"\n[문제 {index}] {quiz.question}")
            for option, choice in enumerate(quiz.choices, 1):
                print(f"  {option}. {choice}")
            while True:
                try:
                    raw = input("정답 번호 (1~4, 힌트 h): ").strip().lower()
                except (EOFError, KeyboardInterrupt):
                    print("\n게임을 중단하고 기록하지 않습니다.")
                    return None
                if raw == "h" and quiz.hint:
                    print("힌트:", quiz.hint)
                    continue
                try:
                    answer = self.parse_int(raw, 1, 4)
                except ValueError as exc:
                    print(exc)
                    continue
                if quiz.is_correct(answer):
                    print("정답입니다!")
                    correct += 1
                else:
                    print(f"아쉽습니다. 정답은 {quiz.answer}번입니다.")
                break

        score = round(correct / count * 100)
        print(f"\n결과: {count}문제 중 {correct}문제 정답 ({score}점)")
        self.best_score = max(self.best_score, score)
        self.history.append({"total": count, "correct": correct, "score": score})
        self.save_state()
        return score

    def list_quizzes(self) -> None:
        print(f"\n등록된 퀴즈 ({len(self.quizzes)}개)")
        for index, quiz in enumerate(self.quizzes, 1):
            print(f"{index}. {quiz.question}")

    def show_score(self) -> None:
        print(f"최고 점수: {self.best_score}점")
        print(f"누적 게임: {len(self.history)}회")
        if self.history:
            average = sum(item["score"] for item in self.history) / len(self.history)
            print(f"평균 점수: {average:.1f}점")

    def run(self) -> None:
        while True:
            print("\n" + "=" * 42)
            print("       나만의 Python 퀴즈 게임")
            print("=" * 42)
            print("1. 퀴즈 풀기\n2. 퀴즈 추가\n3. 퀴즈 목록\n4. 점수 확인\n5. 종료")
            choice = self.ask_int("선택: ", 1, 5)
            if choice is None:
                self.save_state()
                print("저장하고 종료합니다.")
                return
            if choice == 1:
                self.play()
            elif choice == 2:
                self.add_quiz()
            elif choice == 3:
                self.list_quizzes()
            elif choice == 4:
                self.show_score()
            else:
                self.save_state()
                print("저장하고 종료합니다.")
                return


if __name__ == "__main__":
    QuizGame().run()
