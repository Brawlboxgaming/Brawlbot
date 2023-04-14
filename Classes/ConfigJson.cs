using Newtonsoft.Json;

namespace Brawlbot
{
    public class ConfigJson
    {
        [JsonProperty("token")]
        public string Token { get; private set; }
        [JsonProperty("prefix")]
        public string Prefix { get; private set; }
        [JsonProperty("apikey")]
        public string ApiKey { get; private set; }
    }
}