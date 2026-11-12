using CommunityToolkit.Mvvm.ComponentModel;
using HanaScriptStudio.Core;

namespace HanaScriptStudio;

/// <summary>One row in the script list.</summary>
public sealed partial class ScriptItem : ObservableObject
{
    public ScriptItem(ScriptEntry entry) => Entry = entry;

    public ScriptEntry Entry { get; }
    public string Prefix => Entry.Prefix;
    public string BaseName => Entry.BaseName;
    public string Version => Entry.Version;
    public string Folder => Entry.Folder;

    [ObservableProperty] private bool _isModified;
}

/// <summary>One open editor tab.</summary>
public sealed partial class OpenTab : ObservableObject
{
    public OpenTab(ScriptDocument doc, ScriptItem? item)
    {
        Doc = doc;
        Item = item;
        EditorDocument = new AvaloniaEdit.Document.TextDocument(doc.Text);
    }

    public ScriptDocument Doc { get; }
    public ScriptItem? Item { get; }
    public AvaloniaEdit.Document.TextDocument EditorDocument { get; }
    public string Title => System.IO.Path.GetFileNameWithoutExtension(Doc.Path).Replace("_2.00.040+", "");

    [ObservableProperty] private bool _isModified;
    [ObservableProperty] private bool _isSelected;

    public void SyncModified()
    {
        Doc.Text = EditorDocument.Text;
        IsModified = Doc.IsModified;
        if (Item is not null) Item.IsModified = IsModified;
    }
}
