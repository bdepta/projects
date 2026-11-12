using Avalonia;
using Avalonia.Media;
using AvaloniaEdit.Rendering;
using HanaScriptStudio.Core;

namespace HanaScriptStudio;

/// <summary>Paints the modification section with an orange band behind the text.</summary>
public sealed class SectionRenderer : IBackgroundRenderer
{
    public ModificationSection? Section { get; set; }
    public IBrush Fill { get; set; } = new SolidColorBrush(Color.Parse("#FFEBD6"));
    public IBrush Edge { get; set; } = new SolidColorBrush(Color.Parse("#E9730C"));

    public KnownLayer Layer => KnownLayer.Background;

    public void Draw(TextView textView, DrawingContext dc)
    {
        if (Section is not { } s || !textView.VisualLinesValid) return;

        foreach (var v in textView.VisualLines)
        {
            int line0 = v.FirstDocumentLine.LineNumber - 1;
            if (line0 < s.StartLine || line0 > s.EndLine) continue;
            double y = v.VisualTop - textView.VerticalOffset;
            var rect = new Rect(0, y, textView.Bounds.Width, v.Height);
            dc.FillRectangle(Fill, rect);
            dc.FillRectangle(Edge, new Rect(0, y, 3, v.Height));
        }
    }
}
