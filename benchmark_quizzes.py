"""퀴즈 1,000~10,000개 규모에서 저장/불러오기/출제 시간과 메모리를 측정한다."""
import tempfile
import time
import tracemalloc
from pathlib import Path

from main import Quiz, QuizGame


def make_quizzes(n):
    return [Quiz(f"문제 {i}", ["a", "b", "c", "d"], (i % 4) + 1) for i in range(n)]


def measure(fn, repeat=3):
    start = time.perf_counter()
    for _ in range(repeat):
        fn()
    return (time.perf_counter() - start) / repeat * 1000


def run(sizes=(1000, 5000, 10000)):
    print(f"{'퀴즈 수':>8} {'저장(ms)':>10} {'불러오기(ms)':>13} {'출제 추출(ms)':>14} {'파일(KB)':>9} {'피크 메모리(KB)':>16}")
    for n in sizes:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "state.json"
            game = QuizGame(path)
            game.quizzes = make_quizzes(n)
            save_ms = measure(game.save_state)
            tracemalloc.start()
            load_ms = measure(lambda: QuizGame(path))
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            pick_ms = measure(lambda: game.rng.sample(game.quizzes, min(10, n)))
            print(f"{n:>8} {save_ms:>10.2f} {load_ms:>13.2f} {pick_ms:>14.4f} {path.stat().st_size/1024:>9.0f} {peak/1024:>16.0f}")


if __name__ == "__main__":
    run()
