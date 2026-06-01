using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using VIWI.Core;

namespace VIWI.Localization;

/// <summary>
/// [VIWI-JP] 多言語翻訳ヘルパー（Stage 3D で多言語化）。
///
/// 設計方針:
///  - 翻訳は <c>Localization/{lang}.json</c>（EN原文 → 訳の辞書）に分離。
///    <c>ja.json</c> / <c>en.json</c> / <c>de.json</c> / <c>fr.json</c> 等を選択可能。
///  - en.json は空でも動作する（fallback で EN 原文が返るため）。
///  - 本家コードへの変更は <c>"english".T()</c> の1行ラップだけ。上流マージ衝突を最小化。
///  - 起動時に <see cref="Load(string)"/> を一度呼び、設定変更時は <see cref="Reload(string)"/> でホットスワップ可能。
/// </summary>
public static class L
{
    /// <summary>サポートする言語コード（UI のドロップダウン用）。</summary>
    public static readonly (string code, string label)[] AvailableLanguages = new[]
    {
        ("ja", "日本語"),
        ("en", "English"),
        ("de", "Deutsch"),
        ("fr", "Français"),
    };

    private static Dictionary<string, string> _dict = new();
    private static bool _loaded = false;
    private static string _currentLang = "ja";

    /// <summary>現在ロード中の言語コード。</summary>
    public static string CurrentLanguage => _currentLang;

    /// <summary>登録済み翻訳エントリ数（UIでの確認用）。</summary>
    public static int EntryCount => _dict.Count;

    /// <summary>翻訳辞書を読み込む。プラグイン起動時に <c>Load(config.Language)</c> で呼ぶ想定。</summary>
    public static void Load(string lang = "ja") => LoadInternal(lang);

    /// <summary>設定変更時に呼ぶホットスワップ用。失敗時は前の辞書を保持する。</summary>
    public static bool Reload(string lang)
    {
        var oldDict = _dict;
        var oldLoaded = _loaded;
        var oldLang = _currentLang;

        if (LoadInternal(lang)) return true;

        // 失敗時はロールバック
        _dict = oldDict;
        _loaded = oldLoaded;
        _currentLang = oldLang;
        return false;
    }

    private static bool LoadInternal(string lang)
    {
        try
        {
            _currentLang = lang;

            // en は実質フォールバック（空辞書で原文を返せばよい）
            if (lang == "en")
            {
                _dict = new Dictionary<string, string>();
                _loaded = true;
                VIWIContext.PluginLog?.Information($"[VIWI-JP] Language set to English (fallback mode).");
                return true;
            }

            var dllDir = Path.GetDirectoryName(VIWIContext.PluginInterface.AssemblyLocation.FullName);
            if (dllDir == null) return false;

            var path = Path.Combine(dllDir, "Localization", $"{lang}.json");
            if (!File.Exists(path))
            {
                VIWIContext.PluginLog?.Warning($"[VIWI-JP] {lang}.json not found at {path}; falling back to English.");
                _dict = new Dictionary<string, string>();
                _loaded = true;
                return false;
            }

            var json = File.ReadAllText(path);
            var dict = JsonConvert.DeserializeObject<Dictionary<string, string>>(json);
            if (dict != null)
            {
                _dict = dict;
                _loaded = true;
                VIWIContext.PluginLog?.Information($"[VIWI-JP] Loaded {_dict.Count} translations from {lang}.json");
                return true;
            }
            return false;
        }
        catch (Exception ex)
        {
            VIWIContext.PluginLog?.Error($"[VIWI-JP] Failed to load {lang}.json: {ex.Message}");
            return false;
        }
    }

    /// <summary>英語原文から訳を返す（未登録なら原文をそのまま返す）。</summary>
    public static string T(this string en)
    {
        if (!_loaded || string.IsNullOrEmpty(en)) return en;
        return _dict.TryGetValue(en, out var translated) ? translated : en;
    }

    /// <summary>書式付き翻訳。<c>"Imported {0} items".Tr(count)</c> のように使う。</summary>
    public static string Tr(this string enFormat, params object[] args)
    {
        var template = enFormat.T();
        try { return string.Format(template, args); }
        catch { return string.Format(enFormat, args); }
    }
}
