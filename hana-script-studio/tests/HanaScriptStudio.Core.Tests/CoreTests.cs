using HanaScriptStudio.Core;
using Xunit;

namespace HanaScriptStudio.Core.Tests;

public class ModificationSectionTests
{
    private const string Script =
        "/* header */\n\n/* Modification section */\nSELECT\n  1 A\nFROM DUMMY\n/* Internal section (do not modify below this point) */\nSELECT 2;";

    [Fact]
    public void Finds_range_between_modification_and_internal_section()
    {
        var s = ModificationSection.Find(Script);
        Assert.Equal(new ModificationSection(2, 5), s);
        Assert.Equal(4, s!.Value.LineCount);
    }

    [Fact]
    public void Handles_crlf_and_case_differences()
    {
        var s = ModificationSection.Find(Script.Replace("\n", "\r\n").Replace("Modification", "MODIFICATION"));
        Assert.Equal(new ModificationSection(2, 5), s);
    }

    [Fact]
    public void Section_runs_to_end_without_internal_section()
    {
        var s = ModificationSection.Find("a\n/* Modification section */\nb\nc");
        Assert.Equal(new ModificationSection(1, 3), s);
    }

    [Theory]
    [InlineData("")]
    [InlineData("SELECT 1 FROM DUMMY")]
    public void Returns_null_without_section(string text) => Assert.Null(ModificationSection.Find(text));
}

public class ScriptDocumentTests : IDisposable
{
    private readonly string _dir = Directory.CreateTempSubdirectory().FullName;
    public void Dispose() => Directory.Delete(_dir, true);

    [Fact]
    public void Edit_reset_and_save_keep_disk_file_untouched_until_save()
    {
        var path = Path.Combine(_dir, "a.txt");
        File.WriteAllText(path, "original");
        var doc = ScriptDocument.Load(path);

        doc.Text = "changed";
        Assert.True(doc.IsModified);
        Assert.Equal("original", File.ReadAllText(path));

        Assert.Equal("original", doc.Reset());
        Assert.False(doc.IsModified);

        doc.Text = "saved";
        doc.Save();
        Assert.Equal("saved", File.ReadAllText(path));
        Assert.False(doc.IsModified);
        Assert.Equal("saved", doc.Reset());
    }
}

public class ScriptLibraryTests : IDisposable
{
    private readonly string _dir = Directory.CreateTempSubdirectory().FullName;
    public void Dispose() => Directory.Delete(_dir, true);

    private void Write(string name, string content)
    {
        var p = Path.Combine(_dir, name);
        Directory.CreateDirectory(Path.GetDirectoryName(p)!);
        File.WriteAllText(p, content);
    }

    [Fact]
    public async Task Loads_only_script_files_recursively_and_searches_name_and_content()
    {
        Write("HANA_Memory_Overview_2.00.040+.txt", "SELECT * FROM M_HOST_RESOURCE_UTILIZATION");
        Write("sub/HANA_Locks_Overview.sql", "blocking transactions");
        Write("readme.md", "memory");

        var lib = await ScriptLibrary.LoadAsync(_dir);
        Assert.Equal(2, lib.Entries.Count);

        Assert.Equal(2, lib.Search("", false).Count);
        Assert.Single(lib.Search("MEMORY", true));
        Assert.Single(lib.Search("blocking", false));
        Assert.Empty(lib.Search("blocking", true));
        Assert.Single(lib.Search("locks overview", true));
    }

    [Fact]
    public async Task Splits_file_name_into_prefix_base_and_version()
    {
        Write("HANA_Memory_Overview_2.00.040+.txt", "x");
        var e = (await ScriptLibrary.LoadAsync(_dir)).Entries.Single();
        Assert.Equal("HANA_", e.Prefix);
        Assert.Equal("Memory_Overview", e.BaseName);
        Assert.Equal("2.00.040+", e.Version);
    }
}
