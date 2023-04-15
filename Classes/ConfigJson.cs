using Newtonsoft.Json;

namespace Brawlbot
{
    public class ConfigJson
    {
        [JsonProperty("token")]
        public string Token { get; private set; }
        [JsonProperty("apikey")]
        public string ApiKey { get; private set; }
        [JsonProperty("youtubeCookie")]
        public string YoutubeCookie { get; private set; }
    }
}