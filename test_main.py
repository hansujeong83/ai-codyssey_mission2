import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from main import DEFAULT_QUIZZES, Quiz, QuizGame


class QuizModelTests(unittest.TestCase):
    def test_default_quiz_count_at_least_five(self):
        self.assertGreaterEqual(len(DEFAULT_QUIZZES), 5)

    def test_quiz_accepts_valid_values(self):
        quiz = Quiz("Q?", ["a", "b", "c", "d"], 2, "hint")
        self.assertTrue(quiz.is_correct(2))
        self.assertFalse(quiz.is_correct(1))

    def test_rejects_blank_question(self):
        with self.assertRaises(ValueError):
            Quiz(" ", ["a", "b", "c", "d"], 1)

    def test_rejects_wrong_choice_count(self):
        with self.assertRaises(ValueError):
            Quiz("Q", ["a", "b", "c"], 1)

    def test_rejects_blank_choice(self):
        with self.assertRaises(ValueError):
            Quiz("Q", ["a", "", "c", "d"], 1)

    def test_from_dict_rejects_string_answer(self):
        with self.assertRaises(ValueError):
            Quiz.from_dict({"question": "Q", "choices": ["a", "b", "c", "d"], "answer": "2"})

    def test_rejects_answer_out_of_range(self):
        for answer in (0, 5, True, 1.5):
            with self.subTest(answer=answer), self.assertRaises(ValueError):
                Quiz("Q", ["a", "b", "c", "d"], answer)


class QuizGamePersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "nested" / "state.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_first_run_creates_state(self):
        game = QuizGame(self.path)
        self.assertTrue(self.path.exists())
        self.assertEqual(len(game.quizzes), len(DEFAULT_QUIZZES))

    def test_json_round_trip(self):
        game = QuizGame(self.path)
        game.quizzes.append(Quiz("New?", ["a", "b", "c", "d"], 4))
        game.best_score = 80
        game.history.append({"total": 5, "correct": 4, "score": 80})
        game.save_state()
        restored = QuizGame(self.path)
        self.assertEqual(len(restored.quizzes), len(DEFAULT_QUIZZES) + 1)
        self.assertEqual(restored.best_score, 80)
        self.assertEqual(restored.history[0]["correct"], 4)

    def test_corrupt_json_recovers_defaults(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("{broken", encoding="utf-8")
        game = QuizGame(self.path)
        self.assertEqual(len(game.quizzes), len(DEFAULT_QUIZZES))
        self.assertEqual(json.loads(self.path.read_text())["best_score"], 0)

    def test_corrupt_json_is_backed_up(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("{broken", encoding="utf-8")
        with patch("builtins.print"):
            QuizGame(self.path)
        backup = self.path.with_name(self.path.name + ".corrupt.bak")
        self.assertEqual(backup.read_text(encoding="utf-8"), "{broken")

    def test_non_object_json_recovers_defaults(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[]", encoding="utf-8")
        game = QuizGame(self.path)
        self.assertEqual(len(game.quizzes), len(DEFAULT_QUIZZES))

    def test_invalid_history_recovers_defaults(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text(json.dumps({"quizzes": [], "best_score": 0, "history": ["bad"]}), encoding="utf-8")
        game = QuizGame(self.path)
        self.assertEqual(game.history, [])

    def test_temp_file_name_matches_gitignore(self):
        game = QuizGame(self.path)
        game.save_state()
        self.assertFalse(self.path.with_name(self.path.name + ".tmp").exists())

    def test_parse_int_validates_range(self):
        self.assertEqual(QuizGame.parse_int(" 3 ", 1, 5), 3)
        with self.assertRaises(ValueError):
            QuizGame.parse_int("abc", 1, 5)
        with self.assertRaises(ValueError):
            QuizGame.parse_int("9", 1, 5)


class QuizGameFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "state.json"
        self.game = QuizGame(self.path)

    def tearDown(self):
        self.temp.cleanup()

    def test_add_quiz_from_input(self):
        answers = ["New question?", "a", "b", "c", "d", "2", "a hint"]
        with patch("builtins.input", side_effect=answers):
            self.assertTrue(self.game.add_quiz())
        self.assertEqual(self.game.quizzes[-1].answer, 2)

    def test_add_quiz_cancelled_on_eof(self):
        with patch("builtins.input", side_effect=EOFError):
            self.assertFalse(self.game.add_quiz())

    def test_play_perfect_score_and_persist(self):
        self.game.quizzes = self.game.quizzes[:1]
        with patch("builtins.input", side_effect=["2"]):
            score = self.game.play(1)
        self.assertEqual(score, 100)
        self.assertEqual(self.game.best_score, 100)
        self.assertEqual(self.game.history[-1]["correct"], 1)

    def test_delete_quiz_removes_and_persists(self):
        before = len(self.game.quizzes)
        removed = self.game.quizzes[0].question
        with patch("builtins.input", side_effect=["1"]):
            self.assertTrue(self.game.delete_quiz())
        self.assertEqual(len(self.game.quizzes), before - 1)
        reloaded = QuizGame(self.path)
        self.assertNotIn(removed, [q.question for q in reloaded.quizzes])

    def test_delete_quiz_empty_and_invalid(self):
        with self.assertRaises(ValueError):
            self.game.delete_quiz(999)
        self.game.quizzes = []
        self.assertFalse(self.game.delete_quiz())

    def test_delete_quiz_cancelled_on_eof(self):
        before = len(self.game.quizzes)
        with patch("builtins.input", side_effect=EOFError):
            self.assertFalse(self.game.delete_quiz())
        self.assertEqual(len(self.game.quizzes), before)

    def test_list_quizzes_handles_empty(self):
        self.game.quizzes = []
        with patch("builtins.print") as mocked:
            self.game.list_quizzes()
        self.assertIn("등록된 퀴즈가 없습니다", mocked.call_args_list[0].args[0])

    def test_play_rejects_invalid_count(self):
        with self.assertRaises(ValueError):
            self.game.play(0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
