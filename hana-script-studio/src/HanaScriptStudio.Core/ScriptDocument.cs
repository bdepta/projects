namespace HanaScriptStudio.Core;

/// <summary>
/// A script opened for editing. <see cref="OriginalText"/> mirrors the file on disk,
/// <see cref="Text"/> is the working copy. The file is only written by <see cref="Save"/>.
/// </summary>
public sealed class ScriptDocument
{
    public ScriptDocument(string path, string originalText)
    {
        Path = path;
        OriginalText = originalText;
        Text = originalText;
    }

    public string Path { get; }
    public string Name => System.IO.Path.GetFileName(Path);
    public string OriginalText { get; private set; }
    public string Text { get; set; }
    public bool IsModified => !string.Equals(Text, OriginalText, StringComparison.Ordinal);

    public static ScriptDocument Load(string path) => new(path, File.ReadAllText(path));

    /// <summary>Discards edits and returns the text as it was on disk.</summary>
    public string Reset()
    {
        Text = OriginalText;
        return Text;
    }

    public void Save()
    {
        File.WriteAllText(Path, Text);
        OriginalText = Text;
    }
}
