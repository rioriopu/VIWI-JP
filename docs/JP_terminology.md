# VIWI-JP 用語対応表（FFXIV 公式JP名 / Lodestone照合）

このフォークの翻訳は **FFXIV 公式日本語版（クライアント上の表記）** を優先します。
Lodestone Eorzea Database で確認した名称が出典の信頼源です。

## アイテム名（Lodestone照合済み）

| EN | JP（公式） | Lodestone URL |
|---|---|---|
| Ceruleum Tank | **青燐水バレル** | [item/78bdb6ed006](https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/78bdb6ed006/) |
| Mudstone | **泥岩** | [item/49d2e893222](https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/49d2e893222/) |
| Elm Lumber | **エルム材** ⚠注意 (`ニレ材`ではない) | [item/8e59cd755d8](https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/8e59cd755d8/) |
| Spruce Log | **スプルース原木** ⚠注意 (`トウヒ丸太`ではない) | [item/abd30227264](https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/abd30227264/) |
| Grade 6 Dark Matter | **ダークマターG6** ⚠注意 (`ダークマター6`ではない、大文字G) | [item/115751af0a7](https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/115751af0a7/) |
| Dark Matter Cluster | **ダークマタークラスター** | [item/51162b17a9b](https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/51162b17a9b/) |

### 翻訳方針の注意点
- FFXIV JP は英語アイテム名を**カタカナ転写**することが多い（ニレ→エルム、トウヒ→スプルース 等）
- 直訳の和訳語で当てると誤訳になる。**必ず Lodestone で確認** すること

## クラス／ジョブ略号

| EN | JP（クラフター略号） |
|---|---|
| CRP | 木工 (CRP) |
| BSM | 鍛冶 |
| ARM | 甲冑 |
| GSM | 彫金 |
| LTW | 革細工 |
| WVR | 裁縫 |
| ALC | 錬金術 |
| CUL | 調理 |
| MIN | 採掘 (MIN) |
| BTN | 園芸 |
| FSH | 漁師 |
| DoH | クラフター（Disciples of the Hand） |
| DoL | ギャザラー（Disciples of the Land） |

> UI上では本フォークは略号を残しています（CRP/MIN等）。本家コードに合わせ、混乱を避ける目的。

## NPCタイプ・ベンダー（Lodestone照合済み）

| EN | JP（公式） | Lodestone URL |
|---|---|---|
| Junkmonger | **よろず屋** | [shop/db6a7c44696](https://jp.finalfantasyxiv.com/lodestone/playguide/db/shop/db6a7c44696/) |
| Resident Caretaker | **居住区担当官** | [shop/a949a719131](https://jp.finalfantasyxiv.com/lodestone/playguide/db/shop/a949a719131/) |
| Material Supplier | **素材屋** (証書: 雇用証書:素材屋) | [item/d3b13a1650a](https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/d3b13a1650a/) |
| FC Mammet | FCマメット | 公式表記未確認（コミュニティ標準採用） |

⚠ FFXIV JP の NPC 名は**意外な命名が多い**（Junkmongerは「よろず屋」、直訳の「ジャンクモンガー」ではない）。
未確認エントリは Lodestone NPC DB（https://jp.finalfantasyxiv.com/lodestone/playguide/db/npc/）で要確認。

## 通貨・ポイント（Lodestone PvPガイド照合済み）

| EN | JP（公式） | 出典 |
|---|---|---|
| Wolf Marks | **対人戦績** ⚠注意 (`ウルフマーク`ではない！) | [pvpguide/system](https://jp.finalfantasyxiv.com/lodestone/playguide/pvpguide/system/) |
| Trophy Crystals | トロフィークリスタル | (同上) |
| MGP | MGP（ゴールドソーサーポイント） | — |

⚠ Wolf Marks は **「対人戦績」** で漢字。直訳カタカナ表記は誤り。

## システム用語

| EN | JP |
|---|---|
| Workshop / FC Workshop | 工房 |
| Workshop project | 工房プロジェクト |
| Fabrication Station | 製作機 |
| Submarine | 潜水艦 |
| Airship | 飛行艇 |
| Glamour | ミラージュ |
| Glamour Dresser | ミラージュドレッサー |
| Glamour Plate / Set | ミラージュセット |
| Leve / Levequest | リーヴ |
| Leve Allowance | 受注許可 |
| Aetheryte | エーテライト |

## 翻訳ワークフロー（用語の追加・修正）

1. コードに新規英語リテラルが出てきたら `scripts/translate_*.py` を実行（`.T()` ラップ）
2. `scripts/ja_coverage.py --missing` で未訳キーを抽出
3. 該当アイテム名は **必ず Lodestone で確認**：
   - `https://jp.finalfantasyxiv.com/lodestone/playguide/db/item/?q=<英語名>`
4. `ja.json` に **公式JP名** で追記
5. 本ドキュメントの対応表に追加（次マージ時の検証用）

## 既知の翻訳齟齬の修正履歴

### 0.5.0.0 で修正
| EN | 旧訳（誤） | 新訳（正） |
|---|---|---|
| Ceruleum Tank | 蒸気タンク | 青燐水バレル |
| Elm Lumber | ニレ材 | エルム材 |
| Grade 6 Dark Matter | ダークマター6 | ダークマターG6 |
| Spruce Log（追加） | — | スプルース原木 |

### 0.5.1.0 で追加修正（NPC・通貨）
| EN | 旧訳（誤） | 新訳（正） |
|---|---|---|
| Wolf Marks | ウルフマーク | **対人戦績** |
| Junkmonger | ジャンクモンガー | **よろず屋** |
| Resident Caretaker | ハウジングケアテイカー | **居住区担当官** |
| Material Supplier | マテリアルサプライヤー | **素材屋** |

⚠ FFXIV JP は「直訳・カタカナ転写・全く異なる和訳」が混在するため、**必ず Lodestone で確認**する。
推測・思い込みでの翻訳は誤訳の温床。
