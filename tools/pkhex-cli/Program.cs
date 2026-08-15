using PKHeX.Core;
using System;
using System.IO;

class Program
{
    static void Main(string[] args)
    {
        if (args.Length == 0)
        {
            Console.WriteLine("Usage: PokesavCLI <savefile.sav>");
            return;
        }

        var path = args[0];
        var data = File.ReadAllBytes(path);
        var mem = new Memory<byte>(data);
        
        var sav = SaveUtil.GetSaveFile(mem, path);
        if (sav == null)
        {
            Console.WriteLine("Error: Could not detect save file format.");
            return;
        }

        Console.WriteLine($"Game: {sav.GetType().Name}");
        Console.WriteLine($"Trainer: {sav.OT}");
        Console.WriteLine($"TID: {sav.TID16}");
        Console.WriteLine($"SID: {sav.SID16}");
        Console.WriteLine($"Money: {sav.Money}");

        var party = sav.PartyData;
        Console.WriteLine($"\nParty ({party.Count}):");
        for (int i = 0; i < party.Count; i++)
        {
            var pk = party[i];
            if (pk.Species == 0) continue;
            var nickname = pk.Nickname;
            var speciesName = SpeciesName.GetSpeciesName(pk.Species, 2);
            Console.WriteLine($"  {i+1}. {nickname} ({speciesName}) Lv{pk.CurrentLevel}");
            Console.WriteLine($"     Nature: {pk.Nature}, Ability: {pk.Ability}");
            Console.WriteLine($"     Moves: {pk.Move1}/{pk.Move2}/{pk.Move3}/{pk.Move4}");
        }
    }
}
