using System.Collections.Generic;

namespace Brawlbot
{
    public class Voting
    {
        public bool Active { get; set; }
        public List<ulong> Votes { get; set; }
    }
}