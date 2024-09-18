using Brawlbot.Class;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.Lavalink;
using DSharpPlus.SlashCommands;
using DSharpPlus.SlashCommands.Attributes;
using System.Diagnostics;

namespace Brawlbot.Commands
{
    public class Music : ApplicationCommandModule
    {
        public static DiscordGuild Guild = Bot.Client.GetGuildAsync(1207775700883476580).Result;

        public static LavalinkExtension LavaLink = Bot.Client.GetLavalink();
        public static List<LavalinkTrack> Queue = new List<LavalinkTrack>();
        public LavalinkGuildConnection GetLavalinkConnection()
        {
            var node = LavaLink.ConnectedNodes.Values.First();
            return node.GetGuildConnection(Guild);
        }

        public static Voting SkipVoting = new Voting()
        {
            Active = false,
            Votes = new List<ulong>()
        };

        public bool InVC(InteractionContext ctx)
        {
            DiscordChannel musicbox = Guild.GetChannel(1207783428695658566);
            if (musicbox.Users.Contains(ctx.Member))
            {
                return true;
            }
            return false;
        }

        public async Task PlayFromQueue()
        {
        Start:
            var conn = LavaLink.GetGuildConnection(Guild);
            while (conn.CurrentState.CurrentTrack != null)
            {
                await Task.Delay(1);
            }
            if (Queue.Count > 0)
            {
                DiscordChannel musicbox = Guild.GetChannel(1207783428695658566);
                await conn.PlayAsync(Queue[0]);
                Queue.RemoveAt(0);
                SkipVoting.Active = false;
                SkipVoting.Votes = new List<ulong>();
            }
            else
            {
                await Task.Delay(15000);
                if (conn.CurrentState.CurrentTrack == null)
                {
                    await conn.DisconnectAsync();
                    return;
                }
            }
            goto Start;
        }

        [SlashCommand("play", "Plays a track from the search specified.")]
        public async Task Play(InteractionContext ctx,
            [Option("Search", "The track you would like to search.")] string search)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });
            try
            {
                if (!InVC(ctx))
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("You must be connected to the Music channel to use the music commands."));
                    return;
                }
                var node = LavaLink.ConnectedNodes.Values.First();
                var conn = GetLavalinkConnection();

                var loadResult = await node.Rest.GetTracksAsync(search);

                if (loadResult.LoadResultType == LavalinkLoadResultType.LoadFailed
                    || loadResult.LoadResultType == LavalinkLoadResultType.NoMatches)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"Track search failed for {search}"));
                    return;
                }

                if (!LavaLink.ConnectedNodes.Any())
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("The Lavalink connection is not established."));
                    return;
                }

                DiscordChannel musicbox = Guild.GetChannel(1207783428695658566);

                await node.ConnectAsync(musicbox);

                var track = loadResult.Tracks.First();

                Queue.Add(track);
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"{track.Title} has been added to the queue!"));
                await PlayFromQueue();

            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }

        [SlashCommand("pause", "Pauses the current track.")]
        public async Task Pause(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });
            try
            {
                if (!InVC(ctx))
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("You must be connected to the Music channel to use the music commands."));
                    return;
                }
                var conn = GetLavalinkConnection();

                if (conn == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("The bot is not connected."));
                    return;
                }

                await conn.PauseAsync();

                await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"Track has been paused."));
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }

        [SlashCommand("resume", "Resumes the current track.")]
        public async Task Resume(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });
            try
            {
                if (!InVC(ctx))
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("You must be connected to the Music channel to use the music commands."));
                    return;
                }
                var conn = GetLavalinkConnection();

                if (conn == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("The bot is not connected."));
                    return;
                }

                if (conn.CurrentState.CurrentTrack == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("There are no tracks loaded."));
                    return;
                }

                await conn.ResumeAsync();

                await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("Track has been resumed."));
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }

        [SlashCommand("voteskip", "Votes to skip the current track.")]
        public async Task VoteSkip(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });
            try
            {
                IReadOnlyList<DiscordMember> users = Guild.GetChannel(1207783428695658566).Users;
                int userRequirement = (users.Count - 1) / 2 + 1;
                while (userRequirement > 5)
                {
                    userRequirement--;
                }
                if (!InVC(ctx))
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("You must be connected to the Music channel to use the music commands."));
                    return;
                }
                var conn = GetLavalinkConnection();

                if (conn == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("The bot is not connected."));
                    return;
                }

                if (SkipVoting.Votes.Contains(ctx.Member.Id))
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"You have already voted to skip the current track ({SkipVoting.Votes.Count}/{userRequirement})"));
                    return;
                }

                if (!SkipVoting.Active)
                {
                    if (users.Count > 3)
                    {
                        SkipVoting.Active = true;
                        SkipVoting.Votes.Add(ctx.Member.Id);
                        await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"You have voted to skip the current track (1/{userRequirement})."));
                    }
                    else
                    {
                        await conn.StopAsync();
                        await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("Track has been skipped."));
                    }
                    return;
                }
                else
                {
                    SkipVoting.Votes.Add(ctx.Member.Id);
                    if (SkipVoting.Votes.Count == userRequirement)
                    {
                        SkipVoting.Active = false;
                        SkipVoting.Votes = new List<ulong>();
                        await conn.StopAsync();
                        await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"You have voted to skip the current track ({userRequirement}/{userRequirement})." +
                            $"\nTrack has been skipped."));
                    }
                    else
                    {
                        await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent($"You have voted to skip the current track ({SkipVoting.Votes.Count}/{userRequirement})."));
                    }
                }
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }

        [SlashCommand("queue", "Displays the current queue.")]
        public async Task GetQueue(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });
            try
            {
                var conn = GetLavalinkConnection();

                if (conn == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("The bot is not connected."));
                    return;
                }

                string description = "";
                if (conn.CurrentState.CurrentTrack == null)
                {
                    description = "*There is nothing currently playing.*";
                }
                else
                {
                    description = $"__**Currently playing:**__\n*{conn.CurrentState.CurrentTrack.Title}*\n\n__**Queue:**__";
                    if (Queue.Count < 1)
                    {
                        description += "\n*The queue is currently empty.*";
                    }
                    for (int i = 0; i < Queue.Count; i++)
                    {
                        description += $"\n**{i + 1})** *{Queue[i].Title}*";
                    }
                }
                var embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = $"__**Queue:**__",
                    Description = description,
                };
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }

        [SlashCommand("clearqueue", "Clears the queue apart from what is currently playing.")]
        [SlashRequireOwner]
        public async Task ClearQueue(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });
            try
            {
                Queue = new List<LavalinkTrack>();
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("The queue has been cleared."));
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }

        [SlashCommand("skip", "Skips the current track.")]
        [SlashRequireOwner]
        public async Task Skip(InteractionContext ctx)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = !(ctx.Channel.Id == 1207783397045567579 || ctx.Channel.IsPrivate) });
            try
            {
                if (!InVC(ctx))
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("You must be connected to the Music channel to use the music commands."));
                    return;
                }
                var conn = GetLavalinkConnection();

                if (conn == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("The bot is not connected."));
                    return;
                }

                if (conn.CurrentState.CurrentTrack == null)
                {
                    await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("There is nothing currently playing."));
                    return;
                }

                await ctx.EditResponseAsync(new DiscordWebhookBuilder().WithContent("Track has been skipped."));
                await conn.StopAsync();
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }
    }
}
