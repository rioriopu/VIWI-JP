using System.Collections.Generic;
using VIWI.Core;
using VIWI.UI.Pages;

namespace VIWI.UI
{
    public static class DashboardRegistry
    {
        private static readonly List<IDashboardPage> pages = new();

        public static IReadOnlyList<IDashboardPage> Pages => pages;

        public static void Register(IDashboardPage page)
        {
            if (!pages.Contains(page))
                pages.Add(page);
        }
        public static bool ShouldShowPage(IDashboardPage page)
        {
            return !page.RequiresUnlock
                || VIWIContext.CoreConfig?.Unlocked == true
                || VIWIContext.CoreConfig?.SillyMode == true;
        }
    }
}