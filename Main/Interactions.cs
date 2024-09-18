using Brawlbot.Class;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.EventArgs;
using System;
using System.Diagnostics;
using System.Linq;
using System.Text.RegularExpressions;
using System.Threading.Tasks;

namespace Brawlbot
{
    public class Interactions
    {
        public async Task AssignAllInteractions()
        {
            Bot.Client.InteractionCreated += LogInteractions;
            Bot.Client.VoiceStateUpdated += UpdateVoiceChannels;

            await Task.CompletedTask;
        }

        private async Task LogInteractions(DiscordClient client, InteractionCreateEventArgs eventArgs)
        {
            DiscordChannel channel = Bot.Client.GetGuildAsync(1207775700883476580).Result.GetChannel(1207782639558201424);

            string options = "";

            if (eventArgs.Interaction.Data.Options != null)
            {
                foreach (DiscordInteractionDataOption option in eventArgs.Interaction.Data.Options)
                {
                    options += $" {option.Name}: *{option.Value}*";
                }
            }

            DiscordEmbedBuilder embed = new()
            {
                Color = new DiscordColor("#FF0000"),
                Title = $"__**Notice:**__",
                Description = $"'/{eventArgs.Interaction.Data.Name}{options}' was used by {eventArgs.Interaction.User.Mention}.",
                Footer = new DiscordEmbedBuilder.EmbedFooter
                {
                    Text = $"Server Time: {DateTime.Now}"
                }
            };
            await channel.SendMessageAsync(embed);
        }

        private bool _updatingChannels = false;
        private bool _eventDuringChannelUpdate = false;

        private async Task UpdateVoiceChannels(DiscordClient client, VoiceStateUpdateEventArgs eventArgs)
        {
            again:
            if (_updatingChannels)
            {
                _eventDuringChannelUpdate = true;
                return;
            }
            _updatingChannels = true;
            try
            {
                // Check if the channel(s) has/have the format "<name> #<number>"
                string? channelName = null;
                Match m;
                if (eventArgs.Before != null && eventArgs.Before.Channel != null && (m = Regex.Match(eventArgs.Before.Channel.Name, @"^(.*) #\d+$")).Success)
                {
                    channelName = m.Groups[1].Value;
                    await UpdateVoiceChannelCollection(eventArgs.Guild, channelName);
                }
                if (eventArgs.After != null && eventArgs.After.Channel != null &&
                    (m = Regex.Match(eventArgs.After.Channel.Name, @"^(.*) #\d+$")).Success && m.Groups[1].Value != channelName)
                {
                    await UpdateVoiceChannelCollection(eventArgs.Guild, m.Groups[1].Value);
                }

                _updatingChannels = false;
                if (_eventDuringChannelUpdate)
                {
                    _eventDuringChannelUpdate = false;
                    goto again;
                }
            }
            catch (Exception ex)
            {
                await Util.ThrowInteractionlessError(ex);
            }
            finally
            {
                _updatingChannels = false;
                _eventDuringChannelUpdate = false;
            }
        }

        private static async Task UpdateVoiceChannelCollection(DiscordGuild guild, string name)
        {
            // Get a list of all voice channels with this name, their number, and the number of users in them
            var channelInfos = (await guild.GetChannelsAsync())
                .Select(ch => new { Channel = ch, Match = Regex.Match(ch.Name, $@"^{Regex.Escape(name)} #(\d+)$") })
                .Where(inf => inf.Match.Success)
                .Select(inf => new { inf.Channel, UserCount = inf.Channel.Users.Count, Number = int.Parse(inf.Match.Groups[1].Value) })
                .OrderBy(inf => inf.Number)
                .ToList();

            // Delete empty voice channels except for the lowest-numbered one
            bool isFirst = true;
            for (int chIx = 0; chIx < channelInfos.Count; chIx++)
            {
                if (channelInfos[chIx].UserCount == 0)
                {
                    if (isFirst)
                    {
                        isFirst = false;
                    }
                    else
                    {
                        DiscordChannel logChannel = Bot.Client.GetGuildAsync(1207775700883476580).Result.GetChannel(1207782639558201424);
                        DiscordEmbedBuilder embed = new()
                        {
                            Color = new DiscordColor("#FF0000"),
                            Title = $"__**Notice:**__",
                            Description = $"Deleted VC {channelInfos[chIx].Channel.Name}.",
                            Footer = new DiscordEmbedBuilder.EmbedFooter
                            {
                                Text = $"Server Time: {DateTime.Now}"
                            }
                        };

                        await logChannel.SendMessageAsync(embed);

                        if (channelInfos[chIx].Channel.GetMessagesAsync(1000).Result.Count > 0) {
                            string txtFile = $"Last 1000 Messages from {channelInfos[chIx].Channel.Name}:\r\n";
                            var messages = channelInfos[chIx].Channel.GetMessagesAsync(1000).Result.ToList();
                            messages.Reverse();
                            foreach (var message in messages)
                            {
                                txtFile += $"[{message.CreationTimestamp}] {message.Author.Username}: {message.Content}";
                                foreach (var attachment in message.Attachments)
                                {
                                    txtFile += $" {attachment.Url}";
                                }
                                txtFile += "\r\n";
                            }
                            string fileName = $"{DateTime.Now.ToString().Replace(":", "").Replace("/", "-")} - {channelInfos[chIx].Channel.Name}.txt";
                            await File.WriteAllTextAsync(fileName, txtFile);
                            Stream stream = File.Open(fileName, FileMode.Open);
                            await logChannel.SendMessageAsync(new DiscordMessageBuilder().AddFile(fileName, stream));
                            stream.Close();
                            await stream.DisposeAsync();
                            File.Delete(fileName);
                        }
                        await channelInfos[chIx].Channel.DeleteAsync();
                        channelInfos.RemoveAt(chIx);
                        chIx--;
                    }
                }
            }

            // Rename channels whose numbers are now out of order
            bool hasEmpty = false;
            int curNum = 1;
            foreach (var ch in channelInfos)
            {
                if (ch.Number != curNum)
                {
                    DiscordChannel logChannel = Bot.Client.GetGuildAsync(1207775700883476580).Result.GetChannel(1207782639558201424);
                    DiscordEmbedBuilder embed = new()
                    {
                        Color = new DiscordColor("#FF0000"),
                        Title = $"__**Notice:**__",
                        Description = $"Renamed VC {ch.Channel.Name} to {name} #{curNum}.",
                        Footer = new DiscordEmbedBuilder.EmbedFooter
                        {
                            Text = $"Server Time: {DateTime.Now}"
                        }
                    };

                    await logChannel.SendMessageAsync(embed);

                    await ch.Channel.ModifyAsync(cem => cem.Name = $"{name} #{curNum}");
                }
                curNum++;
                hasEmpty = hasEmpty || ch.UserCount == 0;
            }

            // Create a new channel if no channels are empty
            if (!hasEmpty)
            {
                DiscordChannel lastChannel = channelInfos.Last().Channel;
                await guild.CreateChannelAsync($"{name} #{curNum}", ChannelType.Voice, parent: lastChannel.Parent, position: lastChannel.Position);

                DiscordChannel logChannel = Bot.Client.GetGuildAsync(1207775700883476580).Result.GetChannel(1207782639558201424);
                DiscordEmbedBuilder embed = new()
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = $"__**Notice:**__",
                    Description = $"Created VC {name} #{curNum}.",
                    Footer = new DiscordEmbedBuilder.EmbedFooter
                    {
                        Text = $"Server Time: {DateTime.Now}"
                    }
                };

                await logChannel.SendMessageAsync(embed);
            }
        }
    }
}
