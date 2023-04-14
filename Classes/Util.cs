using DSharpPlus.CommandsNext;
using System;
using FluentScheduler;
using DSharpPlus.Entities;
using DSharpPlus.SlashCommands;
using System.Threading.Tasks;
using DSharpPlus.VoiceNext;
using DSharpPlus.Lavalink;

namespace Brawlbot
{
    public class Util : BaseCommandModule
    {
        public static char[] strAlpha = {
            (char)65,
            (char)66,
            (char)67,
            (char)68,
            (char)69,
            (char)70,
            (char)71,
            (char)72,
            (char)73,
            (char)74,
            (char)75,
            (char)76,
            (char)77,
            (char)78,
            (char)79,
            (char)80,
            (char)81,
            (char)82,
            (char)83,
            (char)84,
            (char)85,
            (char)86,
            (char)87,
            (char)88,
            (char)89,
            (char)90
        };

        public static bool CompareStrings(string arg1, string arg2)
        {
            if (arg1.Replace(".", string.Empty).Replace("_", " ").Replace("`", string.Empty).Replace("'", string.Empty).ToLowerInvariant() == arg2.Replace(".", string.Empty).Replace("_", " ").Replace("'", string.Empty).ToLowerInvariant())
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        public static bool CompareIncompleteStrings(string arg1, string arg2)
        {
            if (arg1.Replace(".", string.Empty).Replace("_", " ").Replace("`", string.Empty).Replace("'", string.Empty).ToLowerInvariant().Contains(arg2.Replace(".", string.Empty).Replace("_", " ").Replace("'", string.Empty).ToLowerInvariant()))
            {
                return true;
            }
            else
            {
                return false;
            }
        }

        public static bool CompareStringsLevenshteinDistance(string arg1, string arg2)
        {
            arg1 = arg1.ToLowerInvariant();
            arg2 = arg2.ToLowerInvariant();

            var bounds = new { Height = arg1.Length + 1, Width = arg2.Length + 1 };

            int[,] matrix = new int[bounds.Height, bounds.Width];

            for (int height = 0; height < bounds.Height; height++) { matrix[height, 0] = height; };
            for (int width = 0; width < bounds.Width; width++) { matrix[0, width] = width; };

            for (int height = 1; height < bounds.Height; height++)
            {
                for (int width = 1; width < bounds.Width; width++)
                {
                    int cost = (arg1[height - 1] == arg2[width - 1]) ? 0 : 1;
                    int insertion = matrix[height, width - 1] + 1;
                    int deletion = matrix[height - 1, width] + 1;
                    int substitution = matrix[height - 1, width - 1] + cost;

                    int distance = Math.Min(insertion, Math.Min(deletion, substitution));

                    if (height > 1 && width > 1 && arg1[height - 1] == arg2[width - 2] && arg1[height - 2] == arg2[width - 1])
                    {
                        distance = Math.Min(distance, matrix[height - 2, width - 2] + cost);
                    }

                    matrix[height, width] = distance;
                }
            }

            if (matrix[bounds.Height - 1, bounds.Width - 1] > 2)
            {
                return false;
            }
            else
            {
                return true;
            }
        }

        public static bool CompareStringAbbreviation(string abbr, string full)
        {
            string[] fullArray = full.Split(' ');

            string abbreviation = string.Empty;

            if (full.Contains(" ") && (fullArray[0] == "SNES" ||
                fullArray[0] == "N64" ||
                fullArray[0] == "GBA" ||
                fullArray[0] == "GCN" ||
                fullArray[0] == "DS" ||
                fullArray[0] == "3DS"))
            {
                abbreviation = $"{fullArray[0]} ";
                fullArray[0] = "";
            }

            for (int i = 0; i < fullArray.Length; i++)
            {
                if (fullArray[i].Length != 0)
                {
                    abbreviation += fullArray[i].Substring(0, 1);
                }
            }
            if (abbreviation.ToLowerInvariant() == abbr.ToLowerInvariant())
            {
                return true;
            }

            return false;
        }

        public static async Task ThrowError(InteractionContext ctx, Exception ex)
        {
            var embed = new DiscordEmbedBuilder
            {
                Color = new DiscordColor("#FF0000"),
                Title = $"__**Error:**__",
                Description = $"*{ex.Message}*",
            };
            await ctx.EditResponseAsync(new DiscordWebhookBuilder().AddEmbed(embed));

            Console.WriteLine(ex.ToString());
        }
    }
}
