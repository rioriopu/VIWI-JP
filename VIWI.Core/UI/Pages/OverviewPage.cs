using Dalamud.Bindings.ImGui;
using Dalamud.Interface.Components;
using Dalamud.Interface.Utility;
using Dalamud.Interface.Utility.Raii;
using Lumina.Excel.Sheets;
using System;
using System.Linq;
using System.Numerics;
using VIWI.Core;
using VIWI.Localization;

namespace VIWI.UI.Pages
{
    public sealed class OverviewDashboardPage : IDashboardPage
    {
        public string DisplayName => "Overview";
        public string Category => "Core";
        public string Version => $"{VIWIContext.PluginInterface.Manifest.AssemblyVersion}";

        public bool SupportsEnableToggle => false;
        public bool IsEnabled => true;
        public void SetEnabled(bool value) { }

        public void Draw()
        {
            var io = ImGui.GetIO();

            // ---------------------------
            // Header
            // ---------------------------
            ImGui.TextUnformatted("VIWI – Vera's Integrated World Improvements".T());
            ImGui.TextUnformatted("VIWI Version: {0}".Tr(VIWIContext.PluginInterface.Manifest.AssemblyVersion));
            ImGuiHelpers.ScaledDummy(4f);
            ImGui.Separator();
            ImGuiHelpers.ScaledDummy(8f);

            // ---------------------------
            // Character Details
            // ---------------------------
            ImGui.TextUnformatted("Character Details:".T());
            ImGuiHelpers.ScaledDummy(4f);
 
            if (VIWIContext.ObjectTable.LocalPlayer != null)
            {
                var localPlayer = VIWIContext.ObjectTable.LocalPlayer;
                var playerState = VIWIContext.PlayerState;
                var targetLevel = 60;

                var job = localPlayer.ClassJob.Value;

                var expRemaining = ExpCalc.GetExpRemainingToLevel(VIWIContext.DataManager, playerState, job, targetLevel);

                ImGui.BulletText($"Name: {localPlayer.Name} @ {localPlayer.HomeWorld.Value.Name}");
                ImGui.BulletText($"Current World: {localPlayer.CurrentWorld.Value.Name}");
                ImGui.BulletText($"Job: ({job.RowId}) \"{job.Abbreviation}\"  Level: {playerState.GetClassJobLevel(job)}");
                ImGui.BulletText($"Exp in level: {playerState.GetClassJobExperience(job):N0}");
                //ImGui.TextUnformatted("EXP needed to reach {0}: {1:N0}".Tr(targetLevel, expRemaining));

                var territoryId = VIWIContext.ClientState.TerritoryType;
                if (VIWIContext.DataManager.GetExcelSheet<TerritoryType>()
                    .TryGetRow(territoryId, out var territoryRow))
                {
                    ImGui.BulletText($"Location: ({territoryId}) \"{territoryRow.PlaceName.Value.Name}\"");
                }
                else
                {
                    ImGui.BulletText("Location: Unknown / invalid territory.");
                }

                var target = localPlayer.TargetObject;
                if (target != null)
                {
                    ImGui.BulletText(
                        $"Target: {target.Name}, BaseID: {target.BaseId}, ObjID: {target.GameObjectId}");

                    Vector3 pos = localPlayer.Position;
                    float rot = localPlayer.Rotation;
                    Vector3 tpos = target.Position;
                    float trot = target.Rotation;
                    var distanceToTarget = Vector3.Distance(pos, tpos);
                    var adjustedDistance = distanceToTarget - target.HitboxRadius - localPlayer.HitboxRadius;
                    if (adjustedDistance < 0)
                    { 
                        adjustedDistance = 0;
                    }

                    ImGui.BulletText($"DistanceToTarget: {adjustedDistance:0.000}");
                    ImGui.BulletText($"Player rot={rot * 180f / MathF.PI}, Target rot={trot * 180f / MathF.PI}");
                }
                else
                {
                    ImGui.BulletText("Target: None");
                    ImGui.BulletText("DistanceToTarget: 0");
                    ImGui.BulletText($"Player rot={localPlayer.Rotation * 180f / MathF.PI}");
                }
            }
            else
            {
                ImGui.TextDisabled("Busy / Not Loaded");
            }

                ImGuiHelpers.ScaledDummy(10f);

            // ---------------------------
            // [VIWI-JP] Language Selector (Stage 3D)
            // ---------------------------
            ImGui.TextUnformatted("Language / 言語".T());
            ImGuiHelpers.ScaledDummy(4f);
            var currentLangIdx = System.Array.FindIndex(L.AvailableLanguages, l => l.code == L.CurrentLanguage);
            if (currentLangIdx < 0) currentLangIdx = 0;
            var langLabels = System.Linq.Enumerable.Select(L.AvailableLanguages, l => l.label).ToArray();
            ImGui.SetNextItemWidth(180f);
            if (ImGui.Combo("##viwijp_lang", ref currentLangIdx, langLabels, langLabels.Length))
            {
                var newCode = L.AvailableLanguages[currentLangIdx].code;
                if (L.Reload(newCode))
                {
                    VIWIContext.CoreConfig.Language = newCode;
                    VIWIContext.CoreConfig.Save();
                }
            }
            ImGui.SameLine();
            ImGuiComponents.HelpMarker("Language settings for the VIWI UI (hot-swap). Future modules use the dictionary at runtime; some texts only refresh on plugin reload.".T());
            ImGuiHelpers.ScaledDummy(10f);

            // ---------------------------
            // System Info
            // ---------------------------
            ImGui.TextUnformatted("System Info".T());
            ImGuiHelpers.ScaledDummy(4f);

            var time = System.DateTime.Now;
            var timeZone = System.TimeZoneInfo.Local;
            ImGui.BulletText($"Time: {time}");
            ImGui.BulletText($"Time Zone: {timeZone}");

            var fps = io.Framerate;
            if (fps > 0.1f)
            {
                var ms = 1000f / fps;
                ImGui.BulletText($"FPS: {fps:0.0} ({ms:0.0} ms/frame)");
            }
            else
            {
                ImGui.BulletText("FPS: Unknown");
            }

            ImGui.BulletText($"Logged in: {VIWIContext.ClientState.IsLoggedIn}");

            ImGuiHelpers.ScaledDummy(10f);

            // ---------------------------
            // Loaded Modules
            // ---------------------------
            ImGui.TextUnformatted("Loaded Modules".T());
            ImGuiHelpers.ScaledDummy(4f);

            var remaining = ImGui.GetContentRegionAvail().Y;
            if (remaining < 80f * ImGuiHelpers.GlobalScale)

                remaining = 80f * ImGuiHelpers.GlobalScale;
            using (ImRaii.Child("##loaded_modules", new Vector2(0, remaining), true))
            {
                var orderedModules = DashboardRegistry.Pages
                    .Where(p => p.Category == "Modules" && DashboardRegistry.ShouldShowPage(p))
                    .OrderBy(p => p.DisplayName);

                foreach (var page in orderedModules)
                {
                    var status = page.SupportsEnableToggle
                        ? (page.IsEnabled ? "Enabled" : "Disabled")
                        : "N/A";

                    ImGui.BulletText($"{page.DisplayName} (V{page.Version}) - {status}");
                }
            }
        }
    }
}
