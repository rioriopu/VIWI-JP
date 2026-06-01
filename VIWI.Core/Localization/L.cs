using System;
using System.Collections.Generic;
using System.IO;
using Newtonsoft.Json;
using VIWI.Core;

namespace VIWI.Localization;

/// <summary>
/// [VIWI-JP] 翻訳ヘルパー。
///
/// 設計方針:
///  - 翻訳は別ファイル <c>Localization/ja.json</c>（EN原文 → JP訳の辞書）に分離。
///    本家コードに対する変更は <c>"english".T()</c> の1行ラップだけに留め、上流マージ時の競合を最小化する。
///  - 辞書ファイルが見つからない／キーが無い場合は原文（英語）をそのまま返すので、本家との挙動上の差はない。
///  - 起動時に <see cref="Load"/> を一度呼ぶだけで全モジュールから利用可能。
/// </summary>
public static class L
{
    private static Dictionary<string, string> _ja = new();
    private static bool _loaded = false;

    /// <summary>翻訳辞書を読み込む。プラグイン起動時に一度だけ呼ぶ。</summary>
    public static void Load()
    {
        try
        {
            var dllDir = Path.GetDirectoryName(VIWIContext.PluginInterface.AssemblyLocation.FullName);
            if (dllDir == null) return;

            var path = Path.Combine(dllDir, "Localization", "ja.json");
            if (!File.Exists(path))
            {
                VIWIContext.PluginLog.Information($"[VIWI-JP] ja.json not found at {path}; falling back to English.");
                return;
            }

            var json = File.ReadAllText(path);
            var dict = JsonConvert.DeserializeObject<Dictionary<string, string>>(json);
            if (dict != null)
            {
                _ja = dict;
                _loaded = true;
                VIWIContext.PluginLog.Information($"[VIWI-JP] Loaded {_ja.Count} translations from ja.json");
            }
        }
        catch (Exception ex)
        {
            VIWIContext.PluginLog.Error($"[VIWI-JP] Failed to load ja.json: {ex.Message}");
        }
    }

    /// <summary>英語原文から日本語訳を返す（未登録なら原文をそのまま返す）。</summary>
    public static string T(this string en)
    {
        if (!_loaded || string.IsNullOrEmpty(en)) return en;
        return _ja.TryGetValue(en, out var jp) ? jp : en;
    }

    /// <summary>書式付き翻訳。<c>"Imported {0} items".Tr(count)</c> のように使う。</summary>
    public static string Tr(this string enFormat, params object[] args)
    {
        var template = enFormat.T();
        try { return string.Format(template, args); }
        catch { return string.Format(enFormat, args); }
    }
}
