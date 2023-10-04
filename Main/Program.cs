namespace Brawlbot
{
    class Program
    {
        static void Main() => new Bot().RunAsync().GetAwaiter().GetResult();
    }
}
