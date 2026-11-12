using System.Text.RegularExpressions;
using Avalonia.Media;
using AvaloniaEdit.Document;
using AvaloniaEdit.Rendering;

namespace HanaScriptStudio;

/// <summary>Light-weight SQL syntax colouring (keywords, strings, numbers, comments).</summary>
public sealed class SqlColorizer : DocumentColorizingTransformer
{
    private static readonly Regex Tokens = new(
        @"(?<str>'(?:[^']|'')*')|(?<num>\b\d+(?:\.\d+)?\b)|(?<kw>\b(?:SELECT|FROM|WHERE|GROUP|BY|ORDER|HAVING|WITH|AS|AND|OR|NOT|NULL|IS|IN|LIKE|BETWEEN|CASE|WHEN|THEN|ELSE|END|JOIN|INNER|LEFT|RIGHT|OUTER|FULL|ON|UNION|ALL|DISTINCT|TOP|LIMIT|DESC|ASC|OVER|PARTITION|CAST|COUNT|SUM|MIN|MAX|AVG|DUMMY|EXISTS|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER|TABLE|VIEW)\b)",
        RegexOptions.IgnoreCase | RegexOptions.Compiled);

    private static readonly Regex Comments = new(@"/\*.*?\*/|--[^\r\n]*", RegexOptions.Singleline | RegexOptions.Compiled);

    private readonly TextDocument _doc;
    private readonly List<(int Start, int End)> _comments = new();

    public IBrush Keyword { get; set; } = Brushes.RoyalBlue;
    public IBrush String { get; set; } = Brushes.SeaGreen;
    public IBrush Number { get; set; } = Brushes.OrangeRed;
    public IBrush Comment { get; set; } = Brushes.Gray;

    public SqlColorizer(TextDocument doc)
    {
        _doc = doc;
        Rescan();
        doc.TextChanged += (_, _) => Rescan();
    }

    private void Rescan()
    {
        _comments.Clear();
        foreach (Match m in Comments.Matches(_doc.Text))
            _comments.Add((m.Index, m.Index + m.Length));
    }

    private bool InComment(int offset)
    {
        foreach (var (s, e) in _comments)
            if (offset >= s && offset < e) return true;
        return false;
    }

    protected override void ColorizeLine(DocumentLine line)
    {
        if (line.Length == 0) return;
        var text = CurrentContext.Document.GetText(line);

        foreach (Match m in Tokens.Matches(text))
        {
            int abs = line.Offset + m.Index;
            if (InComment(abs)) continue;
            IBrush brush = m.Groups["str"].Success ? String : m.Groups["num"].Success ? Number : Keyword;
            ChangeLinePart(abs, abs + m.Length, el => el.TextRunProperties.SetForegroundBrush(brush));
        }

        foreach (var (s, e) in _comments)
        {
            int from = Math.Max(s, line.Offset), to = Math.Min(e, line.EndOffset);
            if (from < to)
                ChangeLinePart(from, to, el => el.TextRunProperties.SetForegroundBrush(Comment));
        }
    }
}
