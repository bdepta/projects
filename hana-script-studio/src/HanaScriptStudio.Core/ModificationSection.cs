namespace HanaScriptStudio.Core;

/// <summary>
/// Zero-based inclusive line range of the "Modification section" of a SAP HANA SQL script.
/// The range starts at the line containing "Modification section" and ends on the line before
/// the line containing "Internal section" (or on the last line when there is no such line).
/// </summary>
public readonly record struct ModificationSection(int StartLine, int EndLine)
{
    public int LineCount => EndLine - StartLine + 1;

    public static ModificationSection? Find(string text)
    {
        if (string.IsNullOrEmpty(text)) return null;

        int start = -1;
        int line = 0;
        int lineStart = 0;
        int lastLine = 0;

        while (lineStart <= text.Length)
        {
            int eol = text.IndexOf('\n', lineStart);
            int lineEnd = eol < 0 ? text.Length : eol;
            var span = text.AsSpan(lineStart, lineEnd - lineStart);

            if (start < 0)
            {
                if (span.Contains("Modification section", StringComparison.OrdinalIgnoreCase))
                    start = line;
            }
            else if (span.Contains("Internal section", StringComparison.OrdinalIgnoreCase))
            {
                return new ModificationSection(start, Math.Max(start, line - 1));
            }

            lastLine = line;
            if (eol < 0) break;
            lineStart = eol + 1;
            line++;
        }

        return start < 0 ? null : new ModificationSection(start, lastLine);
    }
}
