# VIWI-JP Stage 3 作業計画

**作成:** 2026-06-01
**前提:** Stage 2（0.2.0.0）公開済み。166件の翻訳ラップ・135 ja.json エントリ・自動デプロイ動作中。
**目標:** Stage 2 で残ったカバレッジ穴埋め＋翻訳品質向上＋運用基盤の整備＋（任意）多言語化基盤。

---

## 0. プレースホルダ・前提

| 記法 | 意味 |
|---|---|
| `<REPO_ROOT>` | `C:\Users\Administrator\TempRepos\VIWI-JP`（このPC） |
| `<DEV_PLUGINS>` | `C:\DevPlugins\VIWIJP`（自動デプロイ先） |
| 前提ツール | dotnet 10 / Python 3.13 / git / gh / Dalamud Hooks `dev` |

---

## 1. スコープサマリ

Stage 3 は4ラウンドに分割：

| ラウンド | 範囲 | 性質 | 概算規模 |
|---|---|---|---|
| **3A** | カバレッジ埋め残し | 半自動＋手作業 | 推定 30〜60件 |
| **3B** | 翻訳品質向上 | 実機QA中心 | 反復作業 |
| **3C** | 運用・メンテ改善 | スクリプト・ドキュメント | 単発作業 |
| **3D**（任意） | 多言語化／動的切替 | 機能拡張 | 中規模 |

リリースは **0.3.0.0**（3A+3B+3C 完了時）を必須、**0.4.0.0**（3D 完了時）を任意とする。

---

## 2. ラウンド構成（推奨順）

```
3A (カバレッジ埋め)          ─┐
                              ├─→ 0.3.0.0 リリース
3B (翻訳品質)                 │
                              │
3C (運用基盤)                 ─┘

3D (多言語化) → 0.4.0.0 リリース（必要に応じ）
```

3A → 3B → 3C は依存があるので順次。3D は独立で着手可能。

---

## 3. ラウンド 3A: カバレッジ埋め残し

### 3A-1. HelpMarker / Tooltip 系
- 対象: `ImGuiEx.HelpMarker("...")`, `ImGui.SetTooltip("...")`, `ImGuiEx.Tooltip` 等
- 手順:
  ```bash
  grep -rnE 'HelpMarker\("[A-Za-z]|SetTooltip\("[A-Za-z]|Tooltip\("[A-Za-z]' --include="*.cs" VIWI.Core/
  ```
- 対応: `.T()` ラップ + ja.json 追加
- 候補件数: 推定 10〜20件

### 3A-2. Window タイトル
- 対象: `Window` 派生クラスのコンストラクタ `: base("...")` で渡すタイトル
- 手順:
  ```bash
  grep -rnE ': base\("[A-Z]' --include="*.cs" VIWI.Core/
  ```
- 対応: タイトル文字列を `.T()` ラップ（`: base("Workshoppa".T())` の形）
- 注意: Dalamud の WindowSystem は `Window.WindowName` を識別子として使うため、初期化時1回しか参照されない。再構築でOK
- 候補件数: 推定 5〜10件

### 3A-3. CommandManager HelpMessage
- 対象: `commandManager.AddHandler(..., new CommandInfo(...) { HelpMessage = "..." })`
- 手順:
  ```bash
  grep -rnE 'HelpMessage = "[A-Za-z]' --include="*.cs" VIWI.Core/
  ```
- 対応: `HelpMessage = "...".T()` ラップ
- 候補件数: 推定 5〜10件

### 3A-4. SeStringBuilder リッチテキスト
- 対象: `.AddUiForeground("...")`, `.Append("...")`, `.AddText("...")` 等の SeStringBuilder メソッドに渡すリテラル
- 手順:
  ```bash
  grep -rnE 'AddUiForeground\("[A-Za-z]|\.Append\("[A-Za-z]|AddText\("[A-Za-z]' --include="*.cs" VIWI.Core/
  ```
- 対応: 注意深く `.T()` ラップ（色コード等の数値引数と区別）
- 候補件数: 推定 3〜8件

### 3A-5. Popup タイトル
- 対象: `ImGui.OpenPopup("Title")` で `##` を含まないもの（表示名扱い）
- 手順:
  ```bash
  grep -rnE 'OpenPopup\("[A-Za-z]' --include="*.cs" VIWI.Core/ | grep -v '##'
  grep -rnE 'BeginPopup\w*\("[A-Za-z]' --include="*.cs" VIWI.Core/ | grep -v '##'
  ```
- 対応: 注意（OpenPopup と BeginPopup で同じ ID を使う必要があるため、`.T()` でラップすると ID が言語依存になり連動性が壊れる）。**`##key` 付きで内部 ID を分離した上でラベル部分のみ `.T()` する**のが正解：
  ```csharp
  // before: ImGui.OpenPopup("Save Preset")
  // after:  ImGui.OpenPopup("Save Preset##save_preset_popup".T()) ※内部ID部分は翻訳されない
  ```
  → ImGui の表示は `##` より前のみ、内部 ID は `##` より後ろ。`.T()` の登録キーは `##` 込みで、訳側は `"保存##save_preset_popup"` のように同じ ID を保つ。
- 候補件数: 推定 3〜5件

### 3A-6. Verbatim 補間文字列 `$@"..."`
- 対象: Stage 2 のスクリプトが意図的にスキップしたもの
- 手順:
  ```bash
  grep -rnE '\$@"[^"]+\{' --include="*.cs" VIWI.Core/
  ```
- 対応: 手動で `.Tr(args)` 形式に変換（改行 `\n` の保持に注意）
- 候補件数: 推定 0〜3件

### 3A-7. 文字列連結 `"foo " + var + " bar"` パターン
- 対象: 補間ではなく `+` 演算子で連結された英語リテラル
- 手順:
  ```bash
  grep -rnE '"[A-Za-z][^"]+"\s*\+\s*\w' --include="*.cs" VIWI.Core/
  ```
- 対応: `"foo {0} bar".Tr(var)` 形式に書き換え
- 候補件数: 推定 5〜10件

### 3A-8. CommandInfo / 例外メッセージ等の散在文字列
- 対象: `throw new Exception("...")`, `Notification` の Title 引数, etc.
- 手順: grep で個別調査
- 候補件数: 不明（実機検証で発見）

### 3A の完了判定
- すべての grep パターンで残存ヒット 0 件
- ビルド 0 エラー
- 自動デプロイ後、`/xlplugins` リロードで動作確認

---

## 4. ラウンド 3B: 翻訳品質向上

### 3B-1. ja.json 未使用キー検出と整理
- ねらい: コード上で `.T()` / `.Tr` 経由でアクセスされていないキーを ja.json から削除
- 自動化スクリプト案: `scripts/ja_coverage.py`
  ```python
  # 1. ja.json のキー一覧を取得
  # 2. *.cs を grep して使用文字列を抽出
  # 3. 差分を出力 (未使用キー / 未訳キー)
  ```
- 出力: 未使用キーのリスト → 手動で削除判断

### 3B-2. 未訳キー検出
- ねらい: コード上で `.T()` 渡しされているが ja.json に未登録の英語原文を列挙
- 同じ `ja_coverage.py` で対応
- 未訳キーがあれば翻訳追加

### 3B-3. 用語統一ルール定義
- `docs/JP_terminology.md` 作成（例）：
  ```
  | EN                  | JP（採用）       | 候補棄却                  |
  |---------------------|------------------|---------------------------|
  | preset              | プリセット       | 規定値, テンプレート      |
  | queue               | キュー           | 待ち行列                  |
  | inventory           | インベントリ     | 持ち物                    |
  | turn-in             | 納品             | 受け渡し                  |
  | leveling            | レベリング       | 育成                      |
  | merge               | マージ           | 統合, 結合                |
  | (Workshop) Project  | 工房プロジェクト | プロジェクト              |
  ```
- ja.json を grep-replace で揺れを統一

### 3B-4. ゲーム内公式訳との整合
- アイテム名（Mudstone → 泥岩 など）はゲーム内日本語版の正式名称に合わせる
- 手順: Lumina の Item シートを JP クライアントデータで参照、ja.json を照合・修正
- 自動化スクリプト案: `scripts/check_item_names.py`（オプション・実機データ要）

### 3B-5. 実機 QA チェックリスト
- 各タブ・各ウィンドウを開いて視覚確認
- 確認シート `docs/QA_checklist.md`:
  - [ ] メインダッシュボード
  - [ ] AutoLogin タブ全体
  - [ ] Workshoppa Window
  - [ ] Workshoppa CeruleumTank Window
  - [ ] Workshoppa Grindstone Window
  - [ ] Workshoppa RepairKit Window
  - [ ] KitchenSink タブ
  - [ ] GlamourSetter ウィンドウ
  - [ ] AoEasy タブ
  - [ ] SideCheck タブ
  - [ ] チャット出力（実際にトリガーして観察）

### 3B の完了判定
- ja.json の未使用キー 0、未訳キー 0
- 用語ドキュメント完備
- QA チェックリスト全項目 ✓

---

## 5. ラウンド 3C: 運用・メンテナンス改善

### 3C-1. `.gitignore` 整備
- 内容:
  ```
  VIWIJP.zip
  _extracted_strings.txt
  _translate_*.tmp
  bin/
  obj/
  ```
- `git rm --cached VIWIJP.zip` で誤コミット分を履歴整理（force push に注意）

### 3C-2. フォーク用 README.md（日本語）
- 既存の上流 README.md（英語）と独立に `README.jp.md` を追加
- 内容:
  - ※ このリポジトリは VeraNala/VIWI のフォークである旨
  - 本家との差分（言語非依存化・日本語翻訳）
  - インストール手順（PrivateReleaseRepo のURL）
  - 翻訳辞書のカスタマイズ方法
  - 上流追従の手順
- メインの `README.md` 冒頭に「日本語: [README.jp.md](README.jp.md)」リンク追加

### 3C-3. 上流マージ手順のスクリプト化
- `scripts/sync_upstream.sh` 作成：
  ```bash
  #!/usr/bin/env bash
  set -e
  # 1. master ブランチを upstream に同期
  git checkout master
  git pull upstream master
  git push origin master
  # 2. jp ブランチに merge
  git checkout jp
  git merge master
  # 3. 衝突があれば停止
  if [ -n "$(git status --porcelain | grep '^UU')" ]; then
    echo "コンフリクトあり。手動解消後に続行してください。"
    exit 1
  fi
  # 4. バルク翻訳スクリプトを再実行（追加分の自動ラップ）
  python scripts/translate_bulk.py
  python scripts/translate_interpolated.py
  # 5. 抽出済み英語文字列を表示（ja.json に追加すべきもの）
  python scripts/ja_coverage.py --missing
  # 6. ビルド確認
  dotnet build VIWI.sln -c Release
  echo "完了。差分をレビューしてコミットしてください。"
  ```

### 3C-4. ja.json カバレッジ検証スクリプト
- `scripts/ja_coverage.py`（3B-1/3B-2 と共用）
- CLI:
  - `--unused`: ja.json に登録されているがコード上で参照されないキーを出力
  - `--missing`: コード上で `.T()` / `.Tr` 渡されているが ja.json に未登録のキーを出力
  - `--all`: 両方
- CI/手動どちらでも実行可能

### 3C-5. ビルドのオプション化
- 既に `EnableDevPluginsDeploy=false` でデプロイ抑止可能
- 追加: `dotnet build /p:Configuration=Release /p:Version=0.3.0.0` のような版数指定でのワンライン化（既に可能）
- ドキュメント化: `docs/BUILD.md` を作成

### 3C の完了判定
- `.gitignore` 反映済み
- `README.jp.md` 配置済み
- `sync_upstream.sh` 動作確認済み
- `ja_coverage.py` で未使用/未訳ともに 0

---

## 6. ラウンド 3D: 多言語化／動的切替（オプショナル）

> このラウンドは**ユーザー要望次第**。EN/JP のみで運用する想定なら 3C 完了で打ち止め。

### 3D-1. 設定で言語切替
- `Config/VIWIConfig.cs` に `Language` プロパティ追加（既定 `"ja"`）
- 設定タブにドロップダウン UI を追加（"日本語" / "English" 等）
- 切替時は `L.Reload()` で辞書を入れ替え

### 3D-2. L.cs を多言語化
- 現在: `Localization/ja.json` 固定
- 改修: `Localization/<lang>.json` を可変パスで読む
  ```csharp
  public static void Load(string lang = "ja")
  {
      var path = Path.Combine(dllDir, "Localization", $"{lang}.json");
      // ...
  }
  ```
- `en.json` は実質空（フォールバックなのでキー一致で英語が返る）

### 3D-3. 追加言語ファイルのスタブ
- `Localization/de.json` / `fr.json` を空 `{}` で配置
- コミュニティ翻訳の受け入れ口

### 3D-4. ホットリロードコマンド
- `/viwijp reload-localization` のようなコマンドを追加
- ja.json を再読込してUI即時反映（ゲーム再起動不要）

### 3D の完了判定
- 言語切替UIが動作
- en.json（空）でフォールバックして英語が返る
- ホットリロードコマンドが動作

---

## 7. リリース戦略

| バージョン | 内容 |
|---|---|
| **0.3.0.0** | 3A + 3B + 3C 完了。「実用品質に到達」リリース |
| **0.4.0.0** | 3D 追加リリース（やる場合のみ） |

リリース手順は STAGE2_PLAN.md §7 と同じ：
1. csproj の `<Version>` を更新
2. ビルド → `bin\Release\VIWIJP\latest.zip` → `VIWIJP.zip` にコピー
3. PrivateReleaseRepo に GitHub Release `VIWIJP-<Version>` を `--prerelease` で作成
4. `repo.json` の AssemblyVersion / DownloadLink / Changelog を更新
5. commit & push（Author は rioriopu 単独）

---

## 8. 上流マージとの整合性

Stage 3 完了後の上流追従手順（3C-3 で自動化されたフローの活用）：

```
./scripts/sync_upstream.sh
# → master 同期 → jp マージ → バルク翻訳再実行 → カバレッジ検証 → ビルド
# 衝突発生時は手動解消後に再実行
```

衝突しやすい箇所（Stage 2 と同じ）：
- 翻訳ラップ済み行
- `using VIWI.Localization;` 追加箇所
- VIWIJP.json（マニフェスト）

衝突解消の方針: 上流側の変更を採用 → `translate_bulk.py` / `translate_interpolated.py` が自動再ラップ。

---

## 9. 完了判定基準（Stage 3 全体）

### 必須（3A + 3B + 3C）
- [ ] 3A の grep パターン全て残存ヒット 0
- [ ] ビルド 0 エラー
- [ ] 自動デプロイ動作
- [ ] `scripts/ja_coverage.py --all` で未使用・未訳ともに 0
- [ ] `docs/JP_terminology.md` 整備
- [ ] `docs/QA_checklist.md` 全項目 ✓
- [ ] `.gitignore` で `VIWIJP.zip` 等を除外
- [ ] `README.jp.md` 配置
- [ ] `scripts/sync_upstream.sh` 動作確認
- [ ] 0.3.0.0 として PrivateReleaseRepo にリリース

### 任意（3D）
- [ ] 言語切替UI動作
- [ ] `en.json` / `de.json` / `fr.json` 配置
- [ ] ホットリロードコマンド動作
- [ ] 0.4.0.0 リリース

---

## 10. 次セッションでの再開手順

```powershell
cd C:\Users\Administrator\TempRepos\VIWI-JP
git checkout jp
git pull origin jp     # STAGE3_PLAN.md / 既存翻訳を取得
# §3 の 3A-1 から順次実装
# 各 3A-x 完了ごとに dotnet build で確認
# 3A 完了 → 3B → 3C の順
# 全部完了したら csproj Version を 0.3.0.0 にして §7 のリリース手順
```

---

## 11. 想定セッション数

- **3A**: 1〜2 セッション（30〜60件、grep→ラップ→ja.json追加の反復）
- **3B**: 1〜2 セッション（実機QA含む、対話的）
- **3C**: 1 セッション（スクリプト作成・README）
- **3D**: 1〜2 セッション（任意）

**合計**: 必須3〜5セッション、任意込みで4〜7セッション。
