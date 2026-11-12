namespace HanaScriptStudio.Core;

/// <summary>
/// Scans a folder for script files and keeps their content in memory so that searching
/// by name and content stays instant even for thousands of files.
/// </summary>
public sealed class ScriptLibrary
{
    public static readonly string[] Extensions = [".txt", ".sql"];
    private const long MaxIndexedFileBytes = 4 * 1024 * 1024;

    private ScriptLibrary(string root, IReadOnlyList<ScriptEntry> entries)
    {
        Root = root;
        Entries = entries;
    }

    public string Root { get; }
    public IReadOnlyList<ScriptEntry> Entries { get; }

    public static async Task<ScriptLibrary> LoadAsync(string root, CancellationToken ct = default)
    {
        if (!Directory.Exists(root))
            throw new DirectoryNotFoundException(root);

        return await Task.Run(() =>
        {
            var opts = new EnumerationOptions
            {
                RecurseSubdirectories = true,
                IgnoreInaccessible = true,
                AttributesToSkip = FileAttributes.Hidden | FileAttributes.System,
            };

            var entries = Directory.EnumerateFiles(root, "*", opts)
                .Where(f => Extensions.Contains(System.IO.Path.GetExtension(f), StringComparer.OrdinalIgnoreCase))
                .Select(f => new ScriptEntry(f, root))
                .OrderBy(e => e.FileName, StringComparer.OrdinalIgnoreCase)
                .ToList();

            Parallel.ForEach(entries, new ParallelOptions { CancellationToken = ct }, e =>
            {
                try
                {
                    var info = new FileInfo(e.Path);
                    if (info.Length <= MaxIndexedFileBytes)
                        e.SearchableContent = File.ReadAllText(e.Path).ToLowerInvariant();
                }
                catch (IOException) { }
                catch (UnauthorizedAccessException) { }
            });

            return new ScriptLibrary(root, entries);
        }, ct);
    }

    /// <summary>
    /// Returns the entries whose file name (and, unless <paramref name="nameOnly"/>, content) contains
    /// every whitespace-separated word of <paramref name="query"/>, ignoring case.
    /// </summary>
    public IReadOnlyList<ScriptEntry> Search(string? query, bool nameOnly)
    {
        if (string.IsNullOrWhiteSpace(query)) return Entries;

        var words = query.Split((char[]?)null, StringSplitOptions.RemoveEmptyEntries)
            .Select(w => w.ToLowerInvariant())
            .ToArray();

        return Entries.Where(e => words.All(w =>
                e.LowerName.Contains(w, StringComparison.Ordinal) ||
                (!nameOnly && e.SearchableContent is { } c && c.Contains(w, StringComparison.Ordinal))))
            .ToList();
    }
}
