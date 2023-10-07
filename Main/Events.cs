using Brawlbot.Class;
using DSharpPlus;
using DSharpPlus.EventArgs;
using System.Threading.Tasks;

namespace Brawlbot
{
    public class Events
    {
        public async Task AssignAllEvents()
        {
            Bot.Client.GuildMemberAdded += AssignStarterRole;

            await Task.CompletedTask;
        }

        private async Task AssignStarterRole(DiscordClient client, GuildMemberAddEventArgs args)
        {
            try
            {
                await args.Member.GrantRoleAsync(args.Guild.GetRole(989985197049118770));
            }
            catch (Exception ex)
            {
                await Util.ThrowInteractionlessError(ex);
            }
        }
    }
}
