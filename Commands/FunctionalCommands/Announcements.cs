using Brawlbot.Class;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using DSharpPlus.SlashCommands.Attributes;
using System;
using System.Threading.Tasks;

namespace Brawlbot.Commands
{
    public class Announcements : ApplicationCommandModule
    {
        [SlashCommand("announcetwitch", "Sends an embed with an announcement for Twitch.")]
        [SlashRequireUserPermissions(Permissions.Administrator)]
        public async Task SendTwitchAnnouncement(InteractionContext ctx,
            [Option("description", "Adds pretext before the embed if extra information is prefered.")] string pretext = "")
        {
            try
            {
                await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !ctx.Interaction.Channel.IsPrivate });
                DiscordChannel channel = ctx.Channel;
                foreach (var c in ctx.Guild.Channels)
                {
                    if (c.Value.Id == 989985263700803656)
                    {
                        channel = c.Value;
                    }
                }
                var embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#6441a5"),
                    Title = "__**Watch Brawlbox Live:**__",
                    Description = $"{pretext}" +
                    $"\n*https://www.twitch.tv/brawlboxgaming*",
                    Footer = new DiscordEmbedBuilder.EmbedFooter
                    {
                        Text = "Come hang out!"
                    }
                };
                await channel.SendMessageAsync("@everyone", embed);

                embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = "__**Success:**__",
                    Description = $"*The announcement was posted successfully.*"
                };
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }
    }
}