# VIWI-JP — Vera's Integrated World Improvements 日本語クライアント対応フォーク

[本家 VeraNala/VIWI](https://github.com/VeraNala/VIWI) を日本語クライアントで動作するように改修したフォーク版です。

> English: [README.md](README.md)（本家のもの）

---

## 本家との違い

### 機能修正（言語非依存化）
本家は Workshoppa の中核選択肢（"Contribute materials" 等）を**英語固定文字列で照合**しているため、非ENクライアントでは自動化が停止します。本フォークは以下を改修：

- `Modules/Workshoppa/GameData/GameStrings.cs` に WorkshopDialogue キー由来の Regex を追加
- `WorkshoppaModule.Craft.cs` / `CraftingLog.cs` の英語直打ち照合を **`_gameStrings.X.IsMatch(s)`** に置換
- これにより JP/DE/FR クライアントでも工房の中核フローが動作

### 日本語化
- UI/メッセージを翻訳辞書方式で日本語化（**約180エントリ**）
- 辞書は `VIWI.Core/Localization/ja.json`（キー=英語原文／値=日本語訳）
- コード側は `"english".T()` / `.Tr(args)` ヘルパー経由で参照
- **本家コードへの侵襲は最小**（1行ラップのみ）で上流マージ追従性を維持

### Plugin Identity
- **InternalName: `VIWIJP`**（本家 VIWI と**併存可能**）
- 設定保存先: `%APPDATA%\XIVLauncher\pluginConfigs\VIWIJP\`
- Author: `VeraNala (forked by Estell)`

---

## インストール

### Dalamud カスタムリポジトリ経由（推奨）
1. ゲーム内 `/xlsettings` → 「Experimental」タブ
2. 「Custom Plugin Repositories」に以下を追加：
   ```
   https://raw.githubusercontent.com/rioriopu/PrivateReleaseRepo/main/repo.json
   ```
3. Save → `/xlplugins` で一覧をリロード
4. **Vera's Integrated World Improvements (JP)** をインストール

### Dev Plugin として
```powershell
git clone --recurse-submodules https://github.com/rioriopu/VIWI-JP.git
cd VIWI-JP
git checkout jp
dotnet build VIWI.sln -c Release
# → C:\DevPlugins\VIWIJP\ に自動デプロイされる (csproj AfterBuild ターゲット)
```

ゲーム内 `/xlsettings` → 「Dev Plugin Locations」に `C:\DevPlugins\VIWIJP\VIWIJP.dll` を追加。

---

## 翻訳辞書のカスタマイズ

訳語を変えたい / 新しい原文に対応したい場合：

1. `VIWI.Core/Localization/ja.json` を編集
   ```json
   {
     "English original": "日本語訳"
   }
   ```
2. プラグインを再起動 or `dotnet build` で自動デプロイ
3. 未登録キーは原文（英語）がそのまま表示されます

---

## 上流（VeraNala/VIWI）マージの追従

```powershell
# 1. master を上流に同期
git checkout master
git pull upstream master
git push origin master

# 2. jp ブランチに merge
git checkout jp
git merge master

# 3. バルク翻訳スクリプトを再実行（新規追加文字列を自動ラップ）
python scripts/translate_bulk.py
python scripts/translate_interpolated.py
python scripts/translate_3a.py

# 4. カバレッジ検証（未登録キーを抽出）
python scripts/ja_coverage.py --missing
# → _ja_missing.txt に未登録キー一覧。ja.json に追記して翻訳

# 5. ビルドして動作確認
dotnet build VIWI.sln -c Release
```

または `scripts/sync_upstream.sh` をワンコマンドで実行。

---

## ファイル構成（フォーク固有）

```
VIWI-JP/
├─ STAGE2_PLAN.md           # Stage 2 (全UI日本語化) 計画書
├─ STAGE3_PLAN.md           # Stage 3 (カバレッジ補完・運用・多言語化) 計画書
├─ README.jp.md             # このファイル
├─ scripts/
│   ├─ translate_bulk.py        # リテラル文字列を .T() ラップ
│   ├─ translate_interpolated.py# 補間文字列を .Tr(args) 形式へ変換
│   ├─ translate_3a.py          # HelpMarker/Window/HelpMessage 等を一括処理
│   ├─ ja_coverage.py           # ja.json と code の整合性検証
│   └─ sync_upstream.sh         # 上流マージ→翻訳ラップ→ビルドの自動化
└─ VIWI.Core/
    ├─ VIWIJP.json              # マニフェスト（本家 VIWI.json → リネーム）
    ├─ Localization/
    │   ├─ L.cs                  # 翻訳ヘルパー（.T() / .Tr() 拡張メソッド）
    │   └─ ja.json               # 翻訳辞書
    └─ ...                       # 以下は本家と同じ構成
```

---

## クレジット

- **原作**: [VeraNala/VIWI](https://github.com/VeraNala/VIWI) — Vera + コントリビューター各位
- **JP フォーク**: Estell（rioriopu）

ライセンスは上流に従います。

## フィードバック

[GitHub Issues (rioriopu/VIWI-JP)](https://github.com/rioriopu/VIWI-JP/issues) または PrivateReleaseRepo の Issues へ。
