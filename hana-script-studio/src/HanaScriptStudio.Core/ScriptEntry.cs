namespace HanaScriptStudio.Core;

/// <summary>A script file found in the library folder.</summary>
public sealed class ScriptEntry
{
    public ScriptEntry(string path, string rootPath)
    {
        Path = path;
        FileName = System.IO.Path.GetFileName(path);
        var rel = System.IO.Path.GetDirectoryName(System.IO.Path.GetRelativePath(rootPath, path)) ?? "";
        Folder = rel;

        var stem = System.IO.Path.GetFileNameWithoutExtension(FileName);
        const string prefix = "HANA_";
        Prefix = stem.StartsWith(prefix, StringComparison.OrdinalIgnoreCase) ? stem[..prefix.Length] : "";
        var rest = stem[Prefix.Length..];

        // Version suffix such as _1.00.120+ or _2.00.040+
        int i = rest.LastIndexOf('_');
        if (i > 0 && i + 1 < rest.Length && char.IsDigit(rest[i + 1]))
        {
            Version = rest[(i + 1)..];
            rest = rest[..i];
        }
        else Version = "";
        BaseName = rest;
    }

    public string Path { get; }
    public string FileName { get; }
    public string Folder { get; }
    public string Prefix { get; }
    public string BaseName { get; }
    public string Version { get; }

    /// <summary>Lower-cased file content, filled by <see cref="ScriptLibrary"/> for content search.</summary>
    internal string? SearchableContent { get; set; }
    internal string LowerName => _lowerName ??= FileName.ToLowerInvariant();
    private string? _lowerName;

    public override string ToString() => FileName;
}
