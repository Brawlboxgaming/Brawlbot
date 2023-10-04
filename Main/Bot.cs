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
using System.Threading.Tasks;

namespace Brawlbot
{
    public class Bot
    {
        public Interactions interactions = new();
        public static DiscordClient Client { get; private set; }
        public SlashCommandsExtension SlashCommands { get; private set; }
        public async Task RunAsync()
        {
            var configJson = JsonConvert.DeserializeObject<ConfigJson>(File.ReadAllText("config.json"));

            var config = new DiscordConfiguration
            {
                Token = configJson.Token,
                TokenType = TokenType.Bot,
                AutoReconnect = true,
                MinimumLogLevel = LogLevel.Debug,
                Intents = DiscordIntents.All,
            };

            Client = new DiscordClient(config);

            Client.Ready += OnClientReady;

            Client.UseInteractivity(new InteractivityConfiguration
            {
                PollBehaviour = PollBehaviour.KeepEmojis,
                AckPaginationButtons = true,
                Timeout = TimeSpan.FromSeconds(60)
            });

            SlashCommands = Client.UseSlashCommands();

            SlashCommands.RegisterCommands<TextCommands>();
            SlashCommands.RegisterCommands<YoutubeDownload>();
            SlashCommands.RegisterCommands<Music>();
            SlashCommands.RegisterCommands<Announcements>(984507807393017976);

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
#if !DEBUG
            await lavalink.ConnectAsync(lavalinkConfig);
#endif

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
