#!/usr/bin/env bash
# [VIWI-JP] 上流マージ自動化スクリプト
#
# 動作:
#   1. master ブランチを upstream/master に同期
#   2. jp ブランチに master を merge（衝突時は停止）
#   3. バルク翻訳スクリプト3本を再実行（新規追加文字列を自動ラップ）
#   4. ja.json カバレッジ検証（未登録キーを表示）
#   5. ビルド確認
#
# 使用前提:
#   - upstream remote が設定されていること（git remote add upstream https://github.com/VeraNala/VIWI.git）
#   - Python 3 / dotnet がパス上にあること

set -e

cd "$(dirname "$0")/.."

PYTHON="${PYTHON:-python3}"
DOTNET="${DOTNET:-dotnet}"

echo "=== [1/5] master を upstream/master に同期 ==="
git checkout master
git pull upstream master
git push origin master

echo
echo "=== [2/5] jp ブランチに master を merge ==="
git checkout jp
if ! git merge master; then
  echo
  echo "!! コンフリクト発生。手動で解消後、以下を実行してください："
  echo "   git commit"
  echo "   $0 --resume"
  exit 1
fi

resume() {
  echo
  echo "=== [3/5] バルク翻訳スクリプトを実行 ==="
  "$PYTHON" scripts/translate_bulk.py
  "$PYTHON" scripts/translate_interpolated.py
  "$PYTHON" scripts/translate_3a.py

  echo
  echo "=== [4/5] ja.json カバレッジ検証 ==="
  "$PYTHON" scripts/ja_coverage.py --all

  if [ -s _ja_missing.txt ]; then
    echo
    echo "!! 未登録キーがあります。_ja_missing.txt を確認して ja.json に追記してください。"
    cat _ja_missing.txt
  fi

  echo
  echo "=== [5/5] ビルド確認 ==="
  "$DOTNET" build VIWI.sln -c Release

  echo
  echo "=== 完了 ==="
  echo "差分を確認してコミットしてください："
  echo "   git status"
  echo "   git diff"
}

if [ "$1" = "--resume" ]; then
  resume
  exit 0
fi

resume
