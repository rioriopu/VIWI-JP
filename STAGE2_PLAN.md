# VIWI-JP Stage 2 作業計画

**作成:** 2026-06-01
**前提:** Stage 1（0.1.0.0）は公開済み・安定。Stage 2 はその上に積み増す。
**目標:** 公開UI・出力メッセージを全面日本語化し、本家との上流マージ追従性を維持する。

---

## 1. 対象規模

再スキャンの結果：**全173件**を確認。

| 種別 | 件数 | 翻訳手法 | 上流マージ衝突リスク |
|---|---:|---|---|
| リテラル文字列（`"foo"`） | 107 | `.T()` で1行ラップ | 小（1行のみ） |
| インターポレート（`$"foo {x}"`） | 66 | `"foo {0}".Tr(x)` へ構文変換 | 中（行全体書き換え） |

### ファイル別内訳（多い順）

| ファイル | リテラル | インターポレート | 計 |
|---|---:|---:|---:|
| `Modules/Workshoppa/Windows/WorkshoppaWindow.cs` | 17 | 10 | 27 |
| `UI/Pages/AutoLoginPage.cs` | 15 | 10 | 25 |
| `Modules/Workshoppa/Windows/WorkshoppaGrindstoneShopWindow.cs` | 8 | 7 | 15 |
| `UI/Pages/KitchenSinkPage.cs` | 12 | 2 | 14 |
| `Modules/KitchenSink/KitchenSink.Commands/CharacterSwitch.cs` | 11 | 1 | 12 |
| `UI/Pages/WorkshoppaPage.cs` | 9 | 2 | 11 |
| `Modules/Workshoppa/WorkshoppaModule.cs` | 0 | 11 | 11 |
| `Modules/KitchenSink/KitchenSink.Commands/GlamourSetter.cs` | 3 | 7 | 10 |
| `Modules/Workshoppa/Windows/WorkshoppaCeruleumTankWindow.cs` | 3 | 4 | 7 |
| `Modules/Workshoppa/WorkshoppaModule.Craft.cs` | 2 | 4 | 6 |
| `UI/Pages/OverviewPage.cs` | 4 | 2 | 6 |
| `Modules/Workshoppa/WorkshoppaModule.CraftingLog.cs` | 4 | 0 | 4 |
| `Modules/KitchenSink/KitchenSink.Commands/DropboxQueue.cs` | 4 | 0 | 4 |
| `Modules/Workshoppa/Windows/WorkshoppaRepairKitWindow.cs` | 1 | 2 | 3 |
| `Modules/AutoLogin/Windows/QuickLaunchOverlay.cs` | 3 | 0 | 3 |
| `UI/Windows/MainDashboardWindow.cs` | 3 | 0 | 3 |
| `UI/Pages/SideCheck.cs` | 2 | 1 | 3 |
| `UI/Pages/AoEasyPage.cs` | 2 | 1 | 3 |
| `Modules/Workshoppa/Windows/Shop/WorkshoppaShopWindowBase.cs` | 2 | 0 | 2 |
| `Modules/Workshoppa/WorkshoppaModule.SelectYesNo.cs` | 1 | 0 | 1 |
| `Modules/KitchenSink/KitchenSink.Commands/BunnyBlessed.cs` | 1 | 0 | 1 |
| `Modules/SideCheck/SideCheckModule.cs` | 0 | 1 | 1 |
| `Modules/KitchenSink/KitchenSink.Commands/WeatherForecast.cs` | 0 | 1 | 1 |
| **合計** | **107** | **66** | **173** |

スキャン検出のみで、tooltip/window title/popup名など漏れている可能性あり。実装中に追加発見したら都度ja.jsonに追記。

---

## 2. 翻訳手法

### 2-1. リテラル文字列
```csharp
// before
_chatGui.Print("No items need to be filled");
// after
_chatGui.Print("No items need to be filled".T());
```
- `using VIWI.Localization;` を当該ファイルに追加（無ければ）
- 1文字列＝1行差分のみ。マージ衝突しても解決容易

### 2-2. インターポレート文字列
```csharp
// before
_chatGui.Print($"Imported {count} items from preset.");
// after
_chatGui.Print("Imported {0} items from preset.".Tr(count));
```
- 行全体が書き換わるため衝突リスク中。上流が同じ行を編集した場合は手動マージが必要
- 順序のある引数は `{0} {1} {2}` で。複雑な書式（`{x:N0}` 等）は **`L.Tr` 拡張に書式保持の対応を追加**する（後述）

### 2-3. 翻訳辞書 `ja.json` の運用
- キー：英語原文そのまま（リテラルなら原文、インターポレートなら `{0}` 形式に変換した文字列）
- 値：日本語訳
- 未登録キーは原文（英語）がフォールバック → ビルドに影響しない・段階追加可能
- マージで上流が文字列を変更したら、`.T()` ラップ周辺で衝突 → 受け入れて ja.json のキーも更新

---

## 3. 作業順序（推奨）

セッション分割の目安：1セッションあたり 30〜50 件処理（Edit中心で）。**全体で 4〜5 セッション**を想定。

### ラウンド1：基盤と低リスクなリテラル（~50件）
1. **デプロイ自動化セットアップ**（§5、最初に必ず）
2. Workshoppa core ファイル群（Craft / CraftingLog / SelectYesNo の出力 = 既知）
3. 小ファイル（BunnyBlessed/QuickLaunchOverlay/MainDashboardWindow/AoEasyPage/SideCheck/WorkshoppaShopWindowBase/RepairKitWindow/SelectYesNo 等）
4. DropboxQueue / CharacterSwitch のリテラル

→ ビルド・実機軽確認 → `jp` ブランチに push（リリースなし）

### ラウンド2：Workshoppa Windows と CraftingLog/Module（~50件）
1. WorkshoppaWindow.cs（最大）
2. WorkshoppaGrindstoneShopWindow.cs
3. WorkshoppaCeruleumTankWindow.cs
4. WorkshoppaModule.cs / Craft.cs / CraftingLog.cs のインターポレート分

→ ビルド・実機確認

### ラウンド3：UI Pages（~45件）
1. AutoLoginPage.cs（最大）
2. KitchenSinkPage.cs
3. WorkshoppaPage.cs
4. OverviewPage.cs

→ ビルド・実機確認

### ラウンド4：残り＋仕上げ（~30件）
1. GlamourSetter.cs（多めのインターポレート）
2. その他検出漏れの拾い上げ
3. ja.json コンプリート率の最終確認（未登録キーが残っていないか）

→ ビルド・実機確認 → **0.2.0.0 リリース**（GitHub Release + repo.json更新）

---

## 4. ファイル別作業手順テンプレ

各ファイルに対して：

1. ファイル全体を Read（または該当範囲）
2. `using VIWI.Localization;` を追加（無ければ）
3. リテラル文字列を `.T()` でラップ（順次 Edit）
4. インターポレート文字列を `.Tr(args)` 形式に変換（順次 Edit）
5. 出てきた英語原文を Localization/ja.json に和訳キーとして追加（後でまとめて or 都度）
6. 次のファイルへ
7. ラウンド終了時にビルド → 自動デプロイ → 動作確認

---

## 5. ビルド/デプロイ自動化（Stage 2 開始時に最初にセットアップ）

ご指示：**実装段階で `C:\DevPlugins\VIWIJP\` への自動デプロイ**。

### 5-1. csproj に AfterBuild ターゲットを追加

```xml
<!-- [VIWI-JP] Release ビルド時に C:\DevPlugins\VIWIJP\ へ自動デプロイ。
     パスは MSBuild プロパティで上書き可能（他環境では /p:DevPluginsDir=... を指定）。 -->
<PropertyGroup>
  <DevPluginsDir Condition="'$(DevPluginsDir)' == ''">C:\DevPlugins\VIWIJP</DevPluginsDir>
</PropertyGroup>
<Target Name="DeployToDevPlugins" AfterTargets="Build" Condition="'$(Configuration)' == 'Release'">
  <ItemGroup>
    <_DeployFiles Include="$(OutputPath)VIWIJP.dll" />
    <_DeployFiles Include="$(OutputPath)VIWIJP.json" />
    <_DeployFiles Include="$(OutputPath)ECommons.dll" />
    <_DeployFiles Include="$(OutputPath)Pictomancy.dll" />
    <_DeployFiles Include="$(OutputPath)SharpDX*.dll" />
  </ItemGroup>
  <MakeDir Directories="$(DevPluginsDir);$(DevPluginsDir)\Localization" />
  <Copy SourceFiles="@(_DeployFiles)" DestinationFolder="$(DevPluginsDir)" SkipUnchangedFiles="true" />
  <Copy SourceFiles="$(OutputPath)Localization\ja.json" DestinationFolder="$(DevPluginsDir)\Localization" SkipUnchangedFiles="true" />
  <Message Importance="high" Text="[VIWI-JP] Deployed to $(DevPluginsDir)" />
</Target>
```

これにより `dotnet build VIWI.sln -c Release` が走れば直後に `C:\DevPlugins\VIWIJP\` が更新される。実機側で `/xlplugins` リロードすれば即反映。

### 5-2. デプロイ確認手順

1. `dotnet build VIWI.sln -c Release`
2. ビルドログに `[VIWI-JP] Deployed to C:\DevPlugins\VIWIJP` が出ること
3. `Get-ChildItem C:\DevPlugins\VIWIJP\` で更新日時を確認
4. ゲーム内 `/xlplugins` でリロード

### 5-3. 初回 Dev Plugin 登録（実機側1回だけ）

ゲーム内：`/xlsettings` → 「Dev Plugin Locations」→ `C:\DevPlugins\VIWIJP\VIWIJP.dll` を追加。

---

## 6. `L.Tr` の書式拡張（必要なら実装段階で対応）

現状の `L.Tr` は `string.Format` 互換。`{0:N0}` などの書式指定子もそのまま動く。

注意点：
- インターポレートの `$"{count:N0}"` を `"{0:N0}".Tr(count)` に変換すれば挙動同等
- カルチャ依存の数値書式は通常問題にならないが、必要なら `Tr(IFormatProvider, ...)` も追加可能

---

## 7. リリース戦略

中間状態は jp ブランチへの push のみ（GitHub Release は作らない）。**全ラウンド完了時に 0.2.0.0 を一括リリース**：

1. csproj `<Version>` と `VIWIJP.json` の `AssemblyVersion` を `0.2.0.0` に変更
2. ビルド → C:\DevPlugins\VIWIJP\ へ自動デプロイ
3. `latest.zip` から配布用 `VIWIJP.zip` を作成
4. PrivateReleaseRepo に GitHub Release `VIWIJP-0.2.0.0`（prerelease）を作成して資産アップロード
5. PrivateReleaseRepo の `repo.json` の TradeVendorJP エントリを 0.2.0.0 に更新＋Changelog 追記
6. commit → push（Author は rioriopu 単独、Claude共著行なし）

---

## 8. 上流マージとの整合性

Stage 2 完了後、本家 VIWI が新機能を追加した場合の対応：

1. `master` を上流同期（`git pull upstream master && git push origin master`）
2. `jp` に `master` をマージ
3. **衝突しやすい箇所**：
   - `WorkshoppaWindow.cs` / `WorkshoppaModule.cs` 等：`.T()` ラップが入っている行
   - インターポレート→`.Tr` 変換した行（行全体書き換えのため上流変更とぶつかりやすい）
4. **衝突解消の方針**：上流側の変更を採用しつつ `.T()` / `.Tr` ラップを再適用
5. 新規追加された英語文字列は ja.json に追記（コード変更なしで対応可能なものは追記のみ）

---

## 9. 完了判定基準

- [ ] 173件すべてに `.T()` / `.Tr` ラップ適用済み
- [ ] ja.json の全キーに日本語訳が登録済み（未登録 = 英語フォールバック扱いだが、出荷時はゼロを目指す）
- [ ] `dotnet build VIWI.sln -c Release` が 0 エラー
- [ ] C:\DevPlugins\VIWIJP\ への自動デプロイが機能
- [ ] 実機で主要画面の日本語表示を確認（最低：Workshoppaダッシュボード・各モジュール設定タブ）
- [ ] 0.2.0.0 として PrivateReleaseRepo 経由でリリース

---

## 10. 次セッションでの再開手順

```powershell
cd C:\Users\Administrator\TempRepos\VIWI-JP
git checkout jp
git status     # クリーンなはず（24763da Stage 1）
# §5 の AfterBuild ターゲットを csproj に追加
# §3 のラウンド1から開始
```
