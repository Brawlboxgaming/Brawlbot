using Brawlbot.Commands;
using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.EventArgs;
using DSharpPlus.Interactivity;
using DSharpPlus.Interactivity.Enums;
using DSharpPlus.Interactivity.Extensions;
using DSharpPlus.Lavalink;
using DSharpPlus.Net;
using DSharpPlus.SlashCommands;
using DSharpPlus.VoiceNext;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using System;
using System.IO;
using System.Text;
using System.Threading.Tasks;

namespace Brawlbot
{
    public class Bot
    {
        public static DiscordClient Client { get; private set; }
        public SlashCommandsExtension Commands { get; private set; }
        public InteractivityExtension Interactivity { get; private set; }

        private async Task ProcessCategory(DiscordChannel category)
        {
            int empty = 0;
            int n = 1;
            string baseName = string.Empty;
            string channelName = string.Empty;
            int? userLimit = null;
            foreach (var c in category.Children)
            {
                if (c.Type == ChannelType.Voice)
                {
                    if (c.Users.Count == 0)
                    {
                        empty++;
                    }
                    baseName = c.Name.Substring(0, c.Name.Length - 1);
                    n++;
                }
            }

            if (empty == 0)
            {
                // Create a channel
                bool already = true;
                while (already)
                {
                    channelName = baseName + n.ToString();
                    foreach (var c in category.Children)
                    {
                        if (c.Type == ChannelType.Voice)
                        {
                            userLimit = c.UserLimit;
                            already = false;
                            if (c.Name == channelName)
                            {
                                already = true;
                            }
                        }
                    }
                    n++;
                }
                await category.Guild.CreateVoiceChannelAsync(channelName, parent: category, user_limit: userLimit);
            }
            else if (empty > 1)
            {
                // Delete empty channels apart from first
                for (int i = 0; i < category.Children.Count; i++)
                {
                    if (category.Children[i].Type == ChannelType.Voice && category.Children[i].Users.Count == 0)
                    {
                        if (category.Children[i].Name.Substring(category.Children[i].Name.Length - 1) != "1")
                        {
                            await category.Children[i].DeleteAsync();
                            empty--;
                        }
                    }
                    if (empty == 1)
                    {
                        break;
                    }
                }
            }
            await Task.CompletedTask;
        }

        private async Task Events()
        {
            Client.VoiceStateUpdated += async (s, e) =>
            {
                if (e.Before != null &&
                e.Before.Channel != null &&
                e.Before.Channel.Parent != null)
                {
                    if (e.Before.Channel.ParentId == 989985250350354482)
                    {
                        await ProcessCategory(e.Before.Channel.Parent);
                    }
                }
                else if (e.After != null &&
                e.After.Channel != null &&
                e.After.Channel.Parent != null)
                {
                    if (e.After.Channel.ParentId == 989985250350354482)
                    {
                        await ProcessCategory(e.After.Channel.Parent);
                    }
                }
            };
            await Task.CompletedTask;
        }

        public async Task RunAsync()
        {
            var json = string.Empty;

            using (var fs = File.OpenRead("config.json"))
            using (var sr = new StreamReader(fs, new UTF8Encoding(false)))
                json = await sr.ReadToEndAsync().ConfigureAwait(false);

            var configJson = JsonConvert.DeserializeObject<ConfigJson>(json);

            var config = new DiscordConfiguration
            {
                Token = configJson.Token,
                TokenType = TokenType.Bot,
                AutoReconnect = true,
                MinimumLogLevel = LogLevel.Debug,
                Intents = DiscordIntents.All
            };

            Client = new DiscordClient(config);

            Client.Ready += OnClientReady;

            Client.UseInteractivity(new InteractivityConfiguration
            {
                PollBehaviour = PollBehaviour.KeepEmojis,
                AckPaginationButtons = true,
                Timeout = TimeSpan.FromSeconds(60)
            });

            Commands = Client.UseSlashCommands();

            Commands.RegisterCommands<TextCommands>();
            Commands.RegisterCommands<YoutubeDownload>();
            Commands.RegisterCommands<Music>();
            Commands.RegisterCommands<Announcements>(984507807393017976);

            await Events();

            var endpoint = new ConnectionEndpoint
            {
                Hostname = "127.0.0.1", // From your server configuration.
                Port = 2333 // From your server configuration
            };

            var lavalinkConfig = new LavalinkConfiguration
            {
                Password = "youshallnotpass", // From your server configuration.
                RestEndpoint = endpoint,
                SocketEndpoint = endpoint
            };

            var lavalink = Client.UseLavalink();

            Client.UseVoiceNext();

            await Client.ConnectAsync();
            await lavalink.ConnectAsync(lavalinkConfig);

            await Task.Delay(-1);
        }

        private Task OnClientReady(DiscordClient sender, ReadyEventArgs e)
        {
            DiscordActivity activity = new DiscordActivity();
            activity.Name = $"/help | https://discord.gg/ThYqfCWc4w";
            Client.UpdateStatusAsync(activity);

            return Task.CompletedTask;
        }
    }
}
