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

                ImGui.BulletText("Name: {0} @ {1}".Tr(localPlayer.Name, localPlayer.HomeWorld.Value.Name));
                ImGui.BulletText("Current World: {0}".Tr(localPlayer.CurrentWorld.Value.Name));
                ImGui.BulletText("Job: ({0}) \"{1}\"  Level: {2}".Tr(job.RowId, job.Abbreviation, playerState.GetClassJobLevel(job)));
                ImGui.BulletText("Exp in level: {0:N0}".Tr(playerState.GetClassJobExperience(job)));
                //ImGui.TextUnformatted("EXP needed to reach {0}: {1:N0}".Tr(targetLevel, expRemaining));

                var territoryId = VIWIContext.ClientState.TerritoryType;
                if (VIWIContext.DataManager.GetExcelSheet<TerritoryType>()
                    .TryGetRow(territoryId, out var territoryRow))
                {
                    ImGui.BulletText("Location: ({0}) \"{1}\"".Tr(territoryId, territoryRow.PlaceName.Value.Name));
                }
                else
                {
                    ImGui.BulletText("Location: Unknown / invalid territory.".T());
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

                    ImGui.BulletText("DistanceToTarget: {0:0.000}".Tr(adjustedDistance));
                    ImGui.BulletText("Player rot={0}, Target rot={1}".Tr(rot * 180f / MathF.PI, trot * 180f / MathF.PI));
                }
                else
                {
                    ImGui.BulletText("Target: None".T());
                    ImGui.BulletText("DistanceToTarget: 0".T());
                    ImGui.BulletText("Player rot={0}".Tr(localPlayer.Rotation * 180f / MathF.PI));
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
            ImGui.BulletText("Time: {0}".Tr(time));
            ImGui.BulletText("Time Zone: {0}".Tr(timeZone));

            var fps = io.Framerate;
            if (fps > 0.1f)
            {
                var ms = 1000f / fps;
                ImGui.BulletText("FPS: {0:0.0} ({1:0.0} ms/frame)".Tr(fps, ms));
            }
            else
            {
                ImGui.BulletText("FPS: Unknown".T());
            }

            ImGui.BulletText("Logged in: {0}".Tr(VIWIContext.ClientState.IsLoggedIn));

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

                    ImGui.BulletText("{0} (V{1}) - {2}".Tr(page.DisplayName, page.Version, status));
                }
            }
        }
    }
}
