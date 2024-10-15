public class Program
{
    public static void Main(string[] args)
    {
        System.Console.WriteLine("Hello, World!");
        int a = 4, b = 3, c = 2;
        
        for (int i = 0; i < 100; i++)
        {
            a = b;
            b = c; 
            c = a + 1;
        }
         Console.WriteLine(a);
        
    }
}