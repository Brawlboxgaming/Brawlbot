using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using System.Threading.Tasks;

namespace Brawlbot.Commands
{
    public class TextCommands : ApplicationCommandModule
    {
        [SlashCommand("help", "Displays all available commands.")]
        public async Task Help(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });

            string description = "__**Standard Commands:**__" +
                "\n/help" +
                "\n/dlmp3 url" +
                "\n/dlmp4 url" +
                "\n/pause" +
                "\n/play search" +
                "\n/queue" +
                "\n/resume" +
                "\n/voteskip";

            /*foreach (var role in ctx.Member.Roles)
            {
                if (role.Id == 989985177226846278) // Admin
                {
                    {
                        description += "\n\n__**Admin Commands:**__" +
                            "\nb!update";
                    }
                }
            }*/

            var embed = new DiscordEmbedBuilder
            {
                Color = new DiscordColor("#FF0000"),
                Title = "__**Help**__",
                Description = description
            };

            await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));
        }
    }
}