using DSharpPlus;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using Newtonsoft.Json;
using System;
using System.Diagnostics;
using System.IO;
using System.Net;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Threading.Tasks;
using YoutubeExplode;
using YoutubeExplode.Converter;
using YoutubeExplode.Videos.Streams;

namespace Brawlbot.Commands
{
    public class YoutubeDownload : ApplicationCommandModule
    {
        [SlashCommand("dlmp4", "Downloads an mp4 file from a YouTube URL.")]
        public async Task DownloadMP4FromYT(InteractionContext ctx,
            [Option("youtube-url", "The YouTube link you would like to download.")] string url)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = true });
            try
            {
                var embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = "__**Progress:**__",
                    Description = "*Getting Youtube Data.*"
                };
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));

                var configJson = JsonConvert.DeserializeObject<ConfigJson>(File.ReadAllText("config.json"));

                var authHttpClient = new HttpClient();
                authHttpClient.DefaultRequestHeaders.Add("Cookie", configJson.YoutubeCookie);

                var youtube = new YoutubeClient(authHttpClient);

                var streamManifest = await youtube.Videos.Streams.GetManifestAsync(url);

                var audioStreamInfo = streamManifest.GetAudioStreams().GetWithHighestBitrate();
                var videoStreamInfo = streamManifest.GetVideoStreams().GetWithHighestVideoQuality();
                var streamInfos = new IStreamInfo[] { audioStreamInfo, videoStreamInfo };

                var video = await youtube.Videos.GetAsync(url);

                var title = video.Title.Replace("\"", "")
                     .Replace("(", "[")
                     .Replace(")", "]")
                     .Replace(" ", "_")
                     .Replace("&", "and")
                     .Replace("\\", "_")
                     .Replace("/", "_")
                     .Replace(":", "_")
                     .Replace("*", "_")
                     .Replace("?", "_")
                     .Replace("\"", "_")
                     .Replace("<", "_")
                     .Replace(">", "_")
                     .Replace("|", "_")
                     .Replace("#", "")
                     .Replace("'", "");

                embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = "__**Progress:**__",
                    Description = $"*Downloading {title}.mp4.*"
                };
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));

                await youtube.Videos.DownloadAsync(streamInfos, new ConversionRequestBuilder($"{title}.mp4").Build());

                var processInfo = new ProcessStartInfo();
                processInfo.FileName = @"C:\Windows\system32\cmd.exe";
                processInfo.Arguments = $"/C move /y {title}.mp4 C:/Files/Brawlbot/";
                processInfo.CreateNoWindow = true;
                processInfo.WindowStyle = ProcessWindowStyle.Hidden;
                processInfo.UseShellExecute = false;
                processInfo.RedirectStandardOutput = true;

                var process = new Process();
                process.StartInfo = processInfo;
                process.Start();
                process.WaitForExit();

                embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = "__**Success:**__",
                    Description = $"https://files.brawlbox.co.uk/Brawlbot/{title}.mp4"
                };
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));
            }
            catch (Exception ex)
            {
                await Util.ThrowError(ctx, ex);
            }
        }

        [SlashCommand("dlmp3", "Downloads an mp3 file from a YouTube URL.")]
        public async Task DownloadMP3FromYT(InteractionContext ctx,
            [Option("youtube-url", "The YouTube link you would like to download.")] string url)
        {
            await ctx.CreateResponseAsync(InteractionResponseType.DeferredChannelMessageWithSource, new DiscordInteractionResponseBuilder() { IsEphemeral = true });
            try
            {
                var embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = "__**Progress:**__",
                    Description = "*Getting Youtube Data.*"
                };
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));

                var youtube = new YoutubeClient();

                var streamManifest = await youtube.Videos.Streams.GetManifestAsync(url);

                var audioStreamInfo = streamManifest.GetAudioStreams().GetWithHighestBitrate();
                var streamInfos = new IStreamInfo[] { audioStreamInfo };

                var video = await youtube.Videos.GetAsync(url);

                var title = video.Title.Replace("\"", "'")
                    .Replace("(", "[")
                    .Replace(")", "]")
                    .Replace(" ", "_")
                    .Replace("&", "and")
                    .Replace("\\", "_")
                    .Replace("/", "_")
                    .Replace(":", "_")
                    .Replace("*", "_")
                    .Replace("?", "_")
                    .Replace("\"", "_")
                    .Replace("<", "_")
                    .Replace(">", "_")
                    .Replace("|", "_")
                    .Replace("#", "")
                    .Replace("'", ""); ;

                embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = "__**Progress:**__",
                    Description = $"*Downloading {title}.mp3.*"
                };
                await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));

                await youtube.Videos.DownloadAsync(streamInfos, new ConversionRequestBuilder($"{title}.mp3").Build());

                var processInfo = new ProcessStartInfo();
                processInfo.FileName = @"C:\Windows\system32\cmd.exe";
                processInfo.Arguments = $"/C move /y {title}.mp3 C:/Files/Brawlbot/";
                processInfo.CreateNoWindow = true;
                processInfo.WindowStyle = ProcessWindowStyle.Hidden;
                processInfo.UseShellExecute = false;
                processInfo.RedirectStandardOutput = true;

                var process = new Process();
                process.StartInfo = processInfo;
                process.Start();
                process.WaitForExit();

                embed = new DiscordEmbedBuilder
                {
                    Color = new DiscordColor("#FF0000"),
                    Title = "__**Success:**__",
                    Description = $"https://files.brawlbox.co.uk/Brawlbot/{title}.mp3"
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