#!/usr/bin/env bash
# git 이력 증거를 텍스트로 저장합니다.  bash scripts/collect_git_evidence.sh
set +e
OUT=docs/evidence/git-log.txt
{
  echo "\$ git remote -v";                               git remote -v
  echo "\$ git branch -a";                               git branch -a
  echo "\$ git log --oneline --graph --decorate --all";  git log --oneline --graph --decorate --all
  echo "\$ git rev-list --count HEAD";                   git rev-list --count HEAD
  echo "\$ python --version";                            python3 --version
} 2>&1 | sed -E 's/[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/***@***/g' | tee "$OUT"
