using Avalonia;
using Avalonia.Controls;
using Avalonia.Layout;

namespace HanaScriptStudio;

public enum ConfirmResult { Save, Discard, Cancel }

/// <summary>Small modal asking what to do with unsaved changes.</summary>
public sealed class ConfirmDialog : Window
{
    private ConfirmResult _result = ConfirmResult.Cancel;

    private ConfirmDialog(string fileName)
    {
        Title = "Unsaved changes";
        Width = 420;
        SizeToContent = SizeToContent.Height;
        WindowStartupLocation = WindowStartupLocation.CenterOwner;
        CanResize = false;

        Button Make(string text, ConfirmResult r, bool primary)
        {
            var b = new Button { Content = text, MinWidth = 90 };
            b.Classes.Add("action");
            if (primary) b.Classes.Add("primary");
            b.Click += (_, _) => { _result = r; Close(); };
            return b;
        }

        Content = new StackPanel
        {
            Margin = new Thickness(20),
            Spacing = 18,
            Children =
            {
                new TextBlock { Text = $"Save changes to {fileName}?", FontSize = 15, FontWeight = Avalonia.Media.FontWeight.SemiBold, TextWrapping = Avalonia.Media.TextWrapping.Wrap },
                new TextBlock { Text = "Your edits will be lost if you don't save them.", Opacity = 0.7 },
                new StackPanel
                {
                    Orientation = Orientation.Horizontal, Spacing = 8, HorizontalAlignment = HorizontalAlignment.Right,
                    Children = { Make("Cancel", ConfirmResult.Cancel, false), Make("Don't save", ConfirmResult.Discard, false), Make("Save", ConfirmResult.Save, true) }
                }
            }
        };
    }

    public static async Task<ConfirmResult> AskAsync(Window owner, string fileName)
    {
        var dlg = new ConfirmDialog(fileName);
        await dlg.ShowDialog(owner);
        return dlg._result;
    }
}
