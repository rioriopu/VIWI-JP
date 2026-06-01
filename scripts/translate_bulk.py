#!/usr/bin/env python3
"""
[VIWI-JP Stage 2] バルク翻訳ラッパー

各ターゲット .cs ファイルに対して:
  1. `using VIWI.Localization;` を必要に応じて追加
  2. 単純リテラル文字列を `.T()` でラップ
     - ChatGui.Print / _chatGui.Print / ChatGui.PrintError / _chatGui.PrintError
     - Notify.Info / Warning / Success / Error
     - ImGui.Text / TextUnformatted / Button / Checkbox / MenuItem / Selectable / SetTooltip
     - ImGuiEx.Text(color, "text")
  3. 抽出した英語原文をリストアップ (ja.json への追加候補)

スキップ条件:
  - 既に .T() でラップ済み (".T()" が直後にある場合)
  - "##" 始まり (ImGui の隠し ID)
  - 空文字列
  - エスケープシーケンスを含む (安全のため対象外)
  - $"..."  インターポレート (対象外、後で手動)

冪等性: 既にラップ済みの行は変更しない。
"""

import re
import sys
from pathlib import Path

ROOT = Path("VIWI.Core")
USING_LINE = "using VIWI.Localization;"

# 翻訳対象ファイル (Localization 自身は除く)
TARGETS = [
    "Modules/Workshoppa/Windows/WorkshoppaWindow.cs",
    "UI/Pages/AutoLoginPage.cs",
    "Modules/Workshoppa/Windows/WorkshoppaGrindstoneShopWindow.cs",
    "UI/Pages/KitchenSinkPage.cs",
    "Modules/KitchenSink/KitchenSink.Commands/CharacterSwitch.cs",
    "UI/Pages/WorkshoppaPage.cs",
    "Modules/Workshoppa/WorkshoppaModule.cs",
    "Modules/KitchenSink/KitchenSink.Commands/GlamourSetter.cs",
    "Modules/Workshoppa/Windows/WorkshoppaCeruleumTankWindow.cs",
    "Modules/Workshoppa/WorkshoppaModule.Craft.cs",
    "UI/Pages/OverviewPage.cs",
    "Modules/Workshoppa/WorkshoppaModule.CraftingLog.cs",
    "Modules/KitchenSink/KitchenSink.Commands/DropboxQueue.cs",
    "Modules/Workshoppa/Windows/WorkshoppaRepairKitWindow.cs",
    "Modules/AutoLogin/Windows/QuickLaunchOverlay.cs",
    "UI/Windows/MainDashboardWindow.cs",
    "UI/Pages/SideCheck.cs",
    "UI/Pages/AoEasyPage.cs",
    "Modules/Workshoppa/Windows/Shop/WorkshoppaShopWindowBase.cs",
    "Modules/Workshoppa/WorkshoppaModule.SelectYesNo.cs",
    "Modules/KitchenSink/KitchenSink.Commands/BunnyBlessed.cs",
    "Modules/SideCheck/SideCheckModule.cs",
    "Modules/KitchenSink/KitchenSink.Commands/WeatherForecast.cs",
]

# パターン定義: (名前, 正規表現, 置換)
# キャプチャグループ:
#   \g<pre> = 直前部分 (置換時にそのまま付ける)
#   \g<s>   = 翻訳対象の英語原文
#   \g<post>= 直後部分 (置換時にそのまま付ける)
# 共通の文字列マッチ: 先頭は英字または[、$#\\で始まらない、内部にエスケープなし
# 直後に .T( が来ていないこと (冪等性)
STR = r'(?P<s>[A-Za-z\[][^"\\]*)'
NEG_T = r'(?!\.T\()'

PATTERNS = [
    # ChatGui.Print("...") / _chatGui.Print("...") / 他類似
    ("chat-print",
     re.compile(rf'(?P<pre>(?:_chatGui|_chat|chatGui|ChatGui)\.(?:Print|PrintError)\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # Notify.*
    ("notify",
     re.compile(rf'(?P<pre>Notify\.(?:Info|Warning|Success|Error)\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGui.TextUnformatted("...")
    ("imgui-textunformatted",
     re.compile(rf'(?P<pre>ImGui\.TextUnformatted\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGui.Text("...")
    ("imgui-text",
     re.compile(rf'(?P<pre>ImGui\.Text\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGui.Button("...")
    ("imgui-button",
     re.compile(rf'(?P<pre>ImGui\.Button\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGui.Checkbox("...", ...)
    ("imgui-checkbox",
     re.compile(rf'(?P<pre>ImGui\.Checkbox\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGui.MenuItem("...")
    ("imgui-menuitem",
     re.compile(rf'(?P<pre>ImGui\.MenuItem\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGui.Selectable("...")
    ("imgui-selectable",
     re.compile(rf'(?P<pre>ImGui\.Selectable\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGui.SetTooltip("...")
    ("imgui-settooltip",
     re.compile(rf'(?P<pre>ImGui\.SetTooltip\()"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
    # ImGuiEx.Text(color, "...") — color部分を任意キャプチャ
    ("imguiex-text",
     re.compile(rf'(?P<pre>ImGuiEx\.Text\([^,]+,\s*)"{STR}"{NEG_T}'),
     lambda m: f'{m.group("pre")}"{m.group("s")}".T()'),
]

def add_using_if_missing(content: str) -> tuple[str, bool]:
    """using VIWI.Localization; が無ければ最後の using 行の直後に追加"""
    if USING_LINE in content:
        return content, False
    lines = content.split("\n")
    last_using = -1
    for i, line in enumerate(lines):
        if line.startswith("using ") and not line.startswith("using static "):
            last_using = i
        elif line.startswith("using static "):
            # static using より前に通常 using を入れる
            if last_using == -1:
                last_using = i - 1
                break
    if last_using == -1:
        return content, False
    new_lines = lines[:last_using+1] + [USING_LINE] + lines[last_using+1:]
    return "\n".join(new_lines), True

def process_file(path: Path):
    if not path.exists():
        return None
    content = path.read_text(encoding="utf-8")
    original = content

    extracted = []  # (pattern_name, string)
    total_changes = 0

    for pname, regex, replacer in PATTERNS:
        def cb(m):
            nonlocal total_changes
            s = m.group("s")
            extracted.append((pname, s))
            total_changes += 1
            return replacer(m)
        content = regex.sub(cb, content)

    using_added = False
    if total_changes > 0:
        content, using_added = add_using_if_missing(content)

    if content != original:
        path.write_text(content, encoding="utf-8", newline="\n")

    return {
        "path": str(path),
        "changes": total_changes,
        "using_added": using_added,
        "extracted": extracted,
    }

def main():
    all_results = []
    all_strings = set()
    for rel in TARGETS:
        path = ROOT / rel
        result = process_file(path)
        if result is None:
            print(f"SKIP (not found): {rel}")
            continue
        if result["changes"] > 0:
            print(f"{result['changes']:3d} changes  using+={'Y' if result['using_added'] else 'N'}  {rel}")
        for _, s in result["extracted"]:
            all_strings.add(s)
        all_results.append(result)

    total = sum(r["changes"] for r in all_results)
    print(f"\n=== TOTAL: {total} replacements across {sum(1 for r in all_results if r['changes']>0)} files ===")
    print(f"=== Unique strings extracted: {len(all_strings)} ===")

    # 抽出した文字列を ja.json 追加候補ファイルに出力
    out = Path("_extracted_strings.txt")
    with out.open("w", encoding="utf-8") as f:
        for s in sorted(all_strings):
            f.write(s + "\n")
    print(f"\n抽出文字列リスト: {out}")

if __name__ == "__main__":
    main()
