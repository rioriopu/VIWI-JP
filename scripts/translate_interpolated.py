#!/usr/bin/env python3
"""
[VIWI-JP Stage 2] インターポレート文字列を .Tr(args) 形式へ変換

例:
  $"Foo {bar} baz"             → "Foo {0} baz".Tr(bar)
  $"Foo {x:N0} bar {y}"        → "Foo {0:N0} bar {1}".Tr(x, y)
  $"Foo {func(a, b)}"          → "Foo {0}".Tr(func(a, b))

スキップ条件 (安全のため):
  - 文字列内に補間が無い ($"foo" のような)
  - 補間式に二重引用符を含む ($"... {a ? \"yes\" : \"no\"} ...")
  - $@"..." (verbatim interpolated string)

対象パターン:
  - ChatGui/_chatGui.Print/PrintError($"...")
  - Notify.*($"...")
  - ImGui.Text/TextUnformatted/Button($"...")
  - ImGuiEx.Text(color, $"...")

すでに .Tr( が直後にある場合はスキップ (冪等性)。
"""

import re
import sys
from pathlib import Path

ROOT = Path("VIWI.Core")
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
    "UI/Pages/OverviewPage.cs",
    "Modules/Workshoppa/Windows/WorkshoppaRepairKitWindow.cs",
    "UI/Pages/SideCheck.cs",
    "UI/Pages/AoEasyPage.cs",
    "Modules/SideCheck/SideCheckModule.cs",
    "Modules/KitchenSink/KitchenSink.Commands/WeatherForecast.cs",
]


def parse_interp_body(body):
    """C# 補間文字列の本体（$" と " の間）をパースして
    (format_string, [args]) を返す。失敗時は None。"""
    out_chars = []
    args = []
    i = 0
    n = len(body)
    while i < n:
        c = body[i]
        if c == '{':
            if i + 1 < n and body[i + 1] == '{':
                out_chars.append('{{')
                i += 2
                continue
            # find matching }
            depth = 1
            j = i + 1
            expr_start = j
            while j < n and depth > 0:
                ch = body[j]
                if ch == '{':
                    depth += 1
                    j += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        break
                    j += 1
                elif ch == '(':
                    # skip balanced parens
                    pd = 1
                    j += 1
                    while j < n and pd > 0:
                        if body[j] == '(':
                            pd += 1
                        elif body[j] == ')':
                            pd -= 1
                        elif body[j] == '"':
                            # 文字列リテラル含む → 安全のため失敗扱い
                            return None
                        j += 1
                elif ch == '"':
                    # 補間式中の二重引用符 → 安全のため失敗扱い
                    return None
                else:
                    j += 1
            if j >= n:
                return None
            expr_end = j
            inside = body[expr_start:expr_end]
            # 書式指定子 ':' の検出 (top-level only)
            colon_idx = -1
            pd = 0
            for k, ch in enumerate(inside):
                if ch == '(':
                    pd += 1
                elif ch == ')':
                    pd -= 1
                elif ch == ':' and pd == 0:
                    rest = inside[k + 1:]
                    if rest and all(r.isalnum() or r in ' ,.+-0#' for r in rest):
                        colon_idx = k
                    break
            if colon_idx >= 0:
                expr = inside[:colon_idx].strip()
                fmt = inside[colon_idx:]
            else:
                expr = inside.strip()
                fmt = ''
            args.append(expr)
            out_chars.append('{' + str(len(args) - 1) + fmt + '}')
            i = expr_end + 1
        elif c == '}':
            if i + 1 < n and body[i + 1] == '}':
                out_chars.append('}}')
                i += 2
                continue
            out_chars.append('}')
            i += 1
        elif c == '\\':
            # escape - keep two chars
            if i + 1 < n:
                out_chars.append(body[i:i + 2])
                i += 2
            else:
                out_chars.append(c)
                i += 1
        else:
            out_chars.append(c)
            i += 1
    return ''.join(out_chars), args


def find_interp(content, start):
    """content の start 位置から $" を探し、本体終了位置と本体テキストを返す。
    失敗時 None。"""
    i = content.find('$"', start)
    if i == -1:
        return None
    # verbatim ($@"...") はスキップ
    if i > 0 and content[i - 1] == '@':
        return (i, i + 2, None, None)
    if i + 2 < len(content) and content[i + 2] == '@':
        # $@" 形式 - 違法的に長くなりやすいのでスキップ
        return (i, None, None, 'verbatim')
    j = i + 2
    n = len(content)
    while j < n:
        ch = content[j]
        if ch == '\\':
            j += 2
            continue
        if ch == '"':
            # 補間内で開く { の中の文字列は parse_interp_body 側でNG扱い
            # ここはトップレベルの "
            body = content[i + 2:j]
            return (i, j + 1, body, None)
        if ch == '{':
            # 内部の { ... } をネストとして処理
            depth = 1
            j += 1
            while j < n and depth > 0:
                cc = content[j]
                if cc == '{':
                    depth += 1
                elif cc == '}':
                    depth -= 1
                elif cc == '"':
                    # nested string in expression — close-quote tracking
                    j += 1
                    while j < n and content[j] != '"':
                        if content[j] == '\\':
                            j += 2
                            continue
                        j += 1
                elif cc == '\\':
                    j += 1
                j += 1
            continue
        j += 1
    return None


def transform(content):
    # 対象メソッド呼び出しパターンの開始を検出してから補間文字列を解析
    method_pattern = re.compile(
        r'((?:_chatGui|_chat|chatGui|ChatGui)\.(?:Print|PrintError)\(|'
        r'Notify\.(?:Info|Warning|Success|Error)\(|'
        r'ImGui\.(?:Text|TextUnformatted|Button|BulletText|CollapsingHeader|SeparatorText|BeginMenu|BeginTabItem|RadioButton)\(|'
        r'ImGuiEx\.Text\([^,]+,\s*)'
    )
    out = []
    pos = 0
    n = len(content)
    while pos < n:
        m = method_pattern.search(content, pos)
        if not m:
            out.append(content[pos:])
            break
        out.append(content[pos:m.end()])
        # m.end() 位置から $" を期待
        after = m.end()
        if after >= n - 1 or content[after:after + 2] != '$"':
            pos = m.end()
            continue
        result = find_interp(content, after)
        if not result or result[2] is None or result[3] == 'verbatim':
            pos = m.end()
            continue
        start_dollar, end_quote, body, _ = result
        parsed = parse_interp_body(body)
        if parsed is None:
            # 解析失敗（ネスト文字列など）→ スキップ
            pos = m.end()
            continue
        fmt_str, args = parsed
        if not args:
            # 補間プレースホルダ無し → 普通の文字列扱いで .T()
            replacement = f'"{fmt_str}".T()'
        else:
            args_joined = ', '.join(args)
            replacement = f'"{fmt_str}".Tr({args_joined})'
        out.append(replacement)
        pos = end_quote
    return ''.join(out)


def main():
    total_files = 0
    total_changes_estimate = 0
    for rel in TARGETS:
        p = ROOT / rel
        if not p.exists():
            continue
        original = p.read_text(encoding='utf-8')
        modified = transform(original)
        if modified != original:
            # 変化件数を概算（".Tr(" の増加数）
            before_tr = original.count('.Tr(')
            after_tr = modified.count('.Tr(')
            before_t = original.count('".T()')
            after_t = modified.count('".T()')
            delta = (after_tr - before_tr) + (after_t - before_t)
            total_files += 1
            total_changes_estimate += delta
            p.write_text(modified, encoding='utf-8', newline='\n')
            print(f'{delta:3d}  {rel}')
    print(f'\n=== TOTAL: ~{total_changes_estimate} interpolated conversions across {total_files} files ===')


if __name__ == '__main__':
    main()
