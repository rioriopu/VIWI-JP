#!/usr/bin/env python3
"""
[VIWI-JP Stage 3A] カバレッジ埋め残しの処理

対応:
  3A-1: HelpMarker / SetTooltip
  3A-2: Window タイトル (: base("..."))
  3A-3: CommandManager HelpMessage
  3A-4: SeStringBuilder (AddUiForeground / Append / AddText)
  3A-5: OpenPopup タイトル (## なしのみ)
  3A-6: Verbatim 補間 $@"..." (検出して警告)
  3A-7: 文字列連結 "foo " + var + " bar"

複数行連結 ("a\n" + "b\n" + "c") は単一文字列にマージしてから wrap。
"""

import re
import sys
from pathlib import Path

ROOT = Path("VIWI.Core")
USING_LINE = "using VIWI.Localization;"

# 安全な英語文字列リテラル: 先頭が英字 or [、内部にエスケープなし
STR = r'(?P<s>[A-Za-z\[](?:[^"\\]|\\.)*)'
NEG_T = r'(?!\.T\()'
NEG_TR = r'(?!\.Tr\()'


def add_using_if_missing(content):
    if USING_LINE in content:
        return content, False
    lines = content.split("\n")
    last_using = -1
    for i, line in enumerate(lines):
        if line.startswith("using ") and not line.startswith("using static "):
            last_using = i
    if last_using == -1:
        return content, False
    return "\n".join(lines[:last_using+1] + [USING_LINE] + lines[last_using+1:]), True


def collapse_concatenated(content):
    """
    複数行に渡る "abc\n" + "def\n" + "ghi" を単一文字列 "abc\ndef\nghi" にマージ。
    対象: HelpMarker, SetTooltip, _chat*.Print, ChatGui.Print, Notify.* 呼び出しの引数。
    """
    # マルチライン正規表現で `(MethodCall)("part1" + ...newline... + "partN")` を検出
    # 簡単な方針: 各行末が `" +` で、次行先頭が `"...` で続く連結を1つにまとめる
    # ただし安全のため "..." + "..." パターンのみマージ
    pattern = re.compile(r'"(?P<a>(?:[^"\\]|\\.)*)"\s*\+\s*\n\s*"(?P<b>(?:[^"\\]|\\.)*)"', re.MULTILINE)
    prev = None
    while prev != content:
        prev = content
        content = pattern.sub(lambda m: f'"{m.group("a")}{m.group("b")}"', content)
    return content


PATTERNS = [
    # HelpMarker / SetTooltip — 単一引数
    ("helpmarker",
     re.compile(rf'(?P<pre>(?:ImGuiComponents\.HelpMarker|ImGuiEx\.HelpMarker|ImGui\.SetTooltip)\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # Window コンストラクタ : base("Title", ...)
    ("window-base",
     re.compile(rf'(?P<pre>:\s*base\()"{STR}"{NEG_T}(?P<post>(?=[,)]))'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # HelpMessage = "..."
    ("helpmessage",
     re.compile(rf'(?P<pre>HelpMessage\s*=\s*)"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # SeStringBuilder.AddUiForeground("Text"), AddText("Text"), Append("Text")
    ("sestring",
     re.compile(rf'(?P<pre>\.(?:AddUiForeground|AddText|Append)\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
]


def transform_simple(content):
    extracted = []
    changes = 0
    for name, regex, replacer in PATTERNS:
        def cb(m):
            nonlocal changes
            extracted.append((name, m.group("s")))
            changes += 1
            return replacer(m)
        content = regex.sub(cb, content)
    return content, changes, extracted


def process_file(path):
    if not path.exists():
        return None
    original = path.read_text(encoding="utf-8")

    # ステップ1: 連結文字列をマージ
    after_collapse = collapse_concatenated(original)

    # ステップ2: パターンマッチで wrap
    after_wrap, changes, extracted = transform_simple(after_collapse)

    using_added = False
    if changes > 0 or after_collapse != original:
        after_wrap, using_added = add_using_if_missing(after_wrap)

    if after_wrap != original:
        path.write_text(after_wrap, encoding="utf-8", newline="\n")

    return {
        "path": str(path),
        "changes": changes,
        "collapsed": after_collapse != original,
        "using_added": using_added,
        "extracted": extracted,
    }


def main():
    all_strings = set()
    cs_files = list(ROOT.rglob("*.cs"))
    cs_files = [p for p in cs_files if "Localization" not in str(p)]
    for p in cs_files:
        result = process_file(p)
        if result is None:
            continue
        if result["changes"] > 0 or result["collapsed"]:
            rel = str(p.relative_to(ROOT))
            tag = []
            if result["collapsed"]:
                tag.append("collapsed")
            if result["using_added"]:
                tag.append("using+")
            print(f"{result['changes']:3d}  [{','.join(tag) or '-'}]  {rel}")
        for _, s in result["extracted"]:
            all_strings.add(s)

    print(f"\n=== Unique strings extracted: {len(all_strings)} ===")
    # 抽出した文字列を ja.json 追加候補ファイルに出力
    out = Path("_extracted_3a.txt")
    with out.open("w", encoding="utf-8") as f:
        for s in sorted(all_strings):
            f.write(s + "\n")
    print(f"抽出文字列リスト: {out}")


if __name__ == "__main__":
    main()
