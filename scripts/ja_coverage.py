#!/usr/bin/env python3
"""
[VIWI-JP Stage 3 共通] ja.json カバレッジ検証

CLI:
  --unused  : ja.json に登録されているがコード上で参照されないキー
  --missing : コード上で .T()/.Tr() に渡されているが ja.json に未登録のキー
  --all     : 両方
  (default) : --all

コード上の .T()/.Tr() のキーは、その直前のリテラル文字列を抽出する。
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path("VIWI.Core")
JA_JSON = ROOT / "Localization" / "ja.json"

# "..."（エスケープ対応）に続いて .T() または .Tr( が来るキーを検出
KEY_PATTERN = re.compile(
    r'"((?:[^"\\]|\\.)*)"\.(?:T\(\)|Tr\()'
)


def collect_code_keys():
    keys = set()
    for p in ROOT.rglob("*.cs"):
        if "Localization" in str(p):
            continue
        try:
            content = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for m in KEY_PATTERN.finditer(content):
            key = m.group(1)
            # JSON 互換にデコード（\n → 実際の改行）
            # キー側はソースコードの生表現を保持
            keys.add(key)
    return keys


def collect_json_keys():
    if not JA_JSON.exists():
        return set()
    data = json.loads(JA_JSON.read_text(encoding="utf-8"))
    return set(k for k in data.keys() if not k.startswith("//"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unused", action="store_true")
    ap.add_argument("--missing", action="store_true")
    ap.add_argument("--all", action="store_true")
    args = ap.parse_args()

    if not (args.unused or args.missing or args.all):
        args.all = True

    code_keys = collect_code_keys()
    json_keys = collect_json_keys()

    print(f"コード内 .T()/.Tr() キー数: {len(code_keys)}")
    print(f"ja.json キー数         : {len(json_keys)}")
    print()

    missing = sorted(code_keys - json_keys)
    unused = sorted(json_keys - code_keys)

    if args.missing or args.all:
        print(f"=== ja.json に未登録 (要追加): {len(missing)} 件 → _ja_missing.txt に出力 ===")
        Path("_ja_missing.txt").write_text("\n".join(missing) + "\n", encoding="utf-8")

    if args.unused or args.all:
        print(f"=== コード未使用キー (要削除候補): {len(unused)} 件 → _ja_unused.txt に出力 ===")
        Path("_ja_unused.txt").write_text("\n".join(unused) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
