#!/usr/bin/env bash
# clone/pull 실습 (미션 13단계). 원격(GitHub)에 push가 끝난 뒤, 저장소 루트에서 실행하세요.
#   bash scripts/clone_pull_practice.sh
# 실행 내용이 그대로 docs/evidence/clone-pull-log.txt 에 기록됩니다.
set -e
LOG=docs/evidence/clone-pull-log.txt
URL=$(git remote get-url origin)
CLONE=../ai-codyssey_mission2-clone
{
  echo "# $(date '+%Y-%m-%d %H:%M:%S')"
  echo "\$ git clone $URL $CLONE"; rm -rf "$CLONE"; git clone "$URL" "$CLONE"
  cd "$CLONE"
  echo "\$ (복제본에서 README 수정)"; echo "- clone/pull 실습: $(date +%F)" >> README.md
  git add README.md
  git commit -m "docs: clone/pull 실습 기록 추가"
  echo "\$ git push"; git push
  cd - >/dev/null
  echo "\$ git pull (원래 작업 폴더)"; git pull
  echo "\$ git log --oneline -3"; git log --oneline -3
  echo "\$ tail -2 README.md"; tail -2 README.md
} 2>&1 | tee "$LOG"
