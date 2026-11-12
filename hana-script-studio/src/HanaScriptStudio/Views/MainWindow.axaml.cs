using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Platform.Storage;
using Avalonia.Styling;
using Avalonia.Threading;
using Avalonia.VisualTree;
using AvaloniaEdit.Document;
using HanaScriptStudio.Core;

namespace HanaScriptStudio.Views;

public partial class MainWindow : Window
{
    private readonly AppSettings _settings = App.Settings;
    private readonly SectionRenderer _sectionRenderer = new();
    private readonly Dictionary<string, ScriptItem> _items = new(StringComparer.OrdinalIgnoreCase);
    private readonly List<OpenTab> _tabs = new();
    private readonly DispatcherTimer _searchDebounce = new() { Interval = TimeSpan.FromMilliseconds(150) };
    private readonly DispatcherTimer _toastTimer = new() { Interval = TimeSpan.FromMilliseconds(1800) };

    private ScriptLibrary? _library;
    private OpenTab? _current;
    private SqlColorizer? _colorizer;
    private ModificationSection? _section;
    private bool _suppressEditorEvents;

    public MainWindow()
    {
        InitializeComponent();

        Editor.TextArea.TextView.BackgroundRenderers.Add(_sectionRenderer);
        Editor.Options.EnableHyperlinks = false;
        Editor.Options.EnableEmailHyperlinks = false;
        Editor.Options.ConvertTabsToSpaces = true;
        Editor.Options.IndentationSize = 2;
        Editor.TextArea.Caret.PositionChanged += (_, _) => UpdatePosition();
        Editor.TextArea.TextView.ScrollOffsetChanged += (_, _) => UpdateRail();
        Editor.TextArea.TextView.PropertyChanged += (_, e) => { if (e.Property == BoundsProperty) UpdateRail(); };
        RailTrack.PropertyChanged += (_, e) => { if (e.Property == BoundsProperty) UpdateRail(); };

        NameOnlyBox.IsChecked = _settings.SearchNameOnly;
        ThemeButton.Content = $"Theme: {_settings.Theme}";

        _searchDebounce.Tick += (_, _) => { _searchDebounce.Stop(); ApplyFilter(); };
        _toastTimer.Tick += (_, _) => { _toastTimer.Stop(); Toast.IsVisible = false; };
        SearchBox.TextChanged += (_, _) => { _searchDebounce.Stop(); _searchDebounce.Start(); };
        NameOnlyBox.IsCheckedChanged += (_, _) => { _settings.SearchNameOnly = NameOnlyBox.IsChecked == true; _settings.Save(); ApplyFilter(); };

        ScriptList.SelectionChanged += OnScriptSelected;
        TabStrip.AddHandler(PointerPressedEvent, OnTabPressed, RoutingStrategies.Bubble, handledEventsToo: true);
        JumpButton.Click += (_, _) => JumpToSection();
        RailTrack.PointerPressed += (_, _) => JumpToSection();
        ResetButton.Click += (_, _) => ResetCurrent();
        CopyButton.Click += async (_, _) => await CopyCurrentAsync();
        ChangeFolderButton.Click += async (_, _) => await ChooseFolderAsync();
        ThemeButton.Click += (_, _) => CycleTheme();

        ActualThemeVariantChanged += (_, _) => UpdateCodeBrushes();
        UpdateCodeBrushes();
        SetEditorEnabled(false);

        Opened += async (_, _) => await StartupAsync();
    }

    // ---------- startup & folder ----------

    private async Task StartupAsync()
    {
        if (!string.IsNullOrEmpty(_settings.LastFolder) && Directory.Exists(_settings.LastFolder))
            await LoadFolderAsync(_settings.LastFolder);
        else
            await ChooseFolderAsync();
    }

    private async Task ChooseFolderAsync()
    {
        var result = await StorageProvider.OpenFolderPickerAsync(new FolderPickerOpenOptions
        {
            Title = "Select the folder with your SAP HANA SQL scripts",
            AllowMultiple = false,
        });
        var path = result.FirstOrDefault()?.TryGetLocalPath();
        if (!string.IsNullOrEmpty(path)) await LoadFolderAsync(path);
    }

    private async Task LoadFolderAsync(string path)
    {
        if (!await CloseAllTabsAsync()) return;

        CountText.Text = "Loading scripts…";
        FolderText.Text = path;
        ScriptList.ItemsSource = null;
        try
        {
            _library = await ScriptLibrary.LoadAsync(path);
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            CountText.Text = $"Cannot read this folder: {ex.Message}";
            return;
        }

        _settings.LastFolder = path;
        _settings.Save();
        _items.Clear();
        foreach (var e in _library.Entries) _items[e.Path] = new ScriptItem(e);
        ApplyFilter();
    }

    // ---------- search ----------

    private void ApplyFilter()
    {
        if (_library is null) return;
        var hits = _library.Search(SearchBox.Text, NameOnlyBox.IsChecked == true);
        var rows = hits.Select(e => _items[e.Path]).ToList();

        _suppressEditorEvents = true;
        ScriptList.ItemsSource = rows;
        ScriptList.SelectedItem = _current?.Item is { } cur && rows.Contains(cur) ? cur : null;
        _suppressEditorEvents = false;

        CountText.Text = $"{rows.Count:N0} of {_library.Entries.Count:N0} scripts";
        NoResultsText.IsVisible = rows.Count == 0;
        NoResultsText.Text = _library.Entries.Count == 0
            ? "No .txt or .sql files found in this folder. Use Change folder to pick another one."
            : "No scripts match your search.";
    }

    // ---------- tabs ----------

    private void OnScriptSelected(object? sender, SelectionChangedEventArgs e)
    {
        if (_suppressEditorEvents || ScriptList.SelectedItem is not ScriptItem item) return;
        OpenScript(item);
    }

    private void OpenScript(ScriptItem item)
    {
        var tab = _tabs.FirstOrDefault(t => string.Equals(t.Doc.Path, item.Entry.Path, StringComparison.OrdinalIgnoreCase));
        if (tab is null)
        {
            try { tab = new OpenTab(ScriptDocument.Load(item.Entry.Path), item); }
            catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
            {
                ShowToast($"Cannot open {item.Entry.FileName}: {ex.Message}");
                return;
            }
            tab.EditorDocument.TextChanged += (_, _) => OnEditorTextChanged(tab);
            _tabs.Add(tab);
        }
        SelectTab(tab);
    }

    private void SelectTab(OpenTab? tab)
    {
        _current = tab;
        foreach (var t in _tabs) t.IsSelected = t == tab;
        TabStrip.ItemsSource = null;
        TabStrip.ItemsSource = _tabs.ToList();

        SetEditorEnabled(tab is not null);
        if (tab is null) { _section = null; UpdateSection(); StateText.Text = "No changes"; return; }

        _suppressEditorEvents = true;
        Editor.Document = tab.EditorDocument;
        _colorizer = new SqlColorizer(tab.EditorDocument);
        UpdateCodeBrushes();
        Editor.TextArea.TextView.LineTransformers.Clear();
        Editor.TextArea.TextView.LineTransformers.Add(_colorizer);
        _suppressEditorEvents = false;

        ScriptList.SelectedItem = tab.Item is { } it && ScriptList.ItemsSource is IEnumerable<ScriptItem> rows && rows.Contains(it) ? it : null;
        UpdateSection();
        UpdateState();
        Editor.TextArea.Caret.Offset = 0;
        Editor.ScrollToHome();
        Editor.Focus();
    }

    private void SetEditorEnabled(bool on)
    {
        Editor.IsVisible = on;
        EmptyState.IsVisible = !on;
        JumpButton.IsEnabled = ResetButton.IsEnabled = CopyButton.IsEnabled = on;
    }

    private void OnTabPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.Source is not Visual v) return;
        var closeBtn = v.FindAncestorOfType<Button>(includeSelf: true);
        if (closeBtn?.Tag is OpenTab toClose && closeBtn.Classes.Contains("tabclose"))
        {
            _ = CloseTabAsync(toClose);
            e.Handled = true;
            return;
        }
        var border = v.FindAncestorOfType<Border>(includeSelf: true);
        while (border is not null && border.Tag is not OpenTab) border = border.FindAncestorOfType<Border>();
        if (border?.Tag is OpenTab tab) SelectTab(tab);
    }

    private async Task<bool> CloseTabAsync(OpenTab tab)
    {
        if (tab.IsModified)
        {
            switch (await ConfirmDialog.AskAsync(this, tab.Doc.Name))
            {
                case ConfirmResult.Cancel: return false;
                case ConfirmResult.Save: SaveTab(tab); break;
                case ConfirmResult.Discard:
                    tab.Doc.Reset();
                    if (tab.Item is not null) tab.Item.IsModified = false;
                    break;
            }
        }
        int i = _tabs.IndexOf(tab);
        _tabs.Remove(tab);
        if (_current == tab) SelectTab(_tabs.Count == 0 ? null : _tabs[Math.Min(i, _tabs.Count - 1)]);
        else { TabStrip.ItemsSource = null; TabStrip.ItemsSource = _tabs.ToList(); }
        return true;
    }

    private async Task<bool> CloseAllTabsAsync()
    {
        foreach (var t in _tabs.ToList())
            if (!await CloseTabAsync(t)) return false;
        return true;
    }

    // ---------- editor behaviour ----------

    private void OnEditorTextChanged(OpenTab tab)
    {
        if (_suppressEditorEvents) return;
        tab.SyncModified();
        if (tab != _current) return;
        UpdateSection();
        UpdateState();
    }

    private void UpdateSection()
    {
        _section = _current is null ? null : ModificationSection.Find(_current.EditorDocument.Text);
        _sectionRenderer.Section = _section;
        Editor.TextArea.TextView.InvalidateLayer(AvaloniaEdit.Rendering.KnownLayer.Background);

        SectionInfo.Text = _current is null ? "" :
            _section is { } s ? $"Modification section: lines {s.StartLine + 1}–{s.EndLine + 1}"
                              : "No modification section in this script";
        JumpButton.IsEnabled = _section is not null;
        UpdateRail();
    }

    private void UpdateRail()
    {
        double h = RailTrack.Bounds.Height - 2;
        int total = _current?.EditorDocument.LineCount ?? 0;
        if (_section is not { } s || total == 0 || h <= 0) { RailTrack.Opacity = 0; return; }
        RailTrack.Opacity = 1;
        Canvas.SetTop(RailTick, s.StartLine / (double)total * h);
        RailTick.Height = Math.Max(4, s.LineCount / (double)total * h);
    }

    private void UpdatePosition() =>
        PosText.Text = $"Ln {Editor.TextArea.Caret.Line}, Col {Editor.TextArea.Caret.Column}";

    private void UpdateState()
    {
        StateText.Text = _current?.IsModified == true ? "Modified (not saved)" : "No changes";
        StateText.Foreground = _current?.IsModified == true
            ? new SolidColorBrush(Color.Parse("#FFB070"))
            : this.TryFindResource("ShellDimBrush", ActualThemeVariant, out var dim) && dim is IBrush db ? db : Brushes.Gray;
    }

    // ---------- actions ----------

    private void JumpToSection()
    {
        if (_current is null || _section is not { } s) return;
        var line = _current.EditorDocument.GetLineByNumber(s.StartLine + 1);
        Editor.TextArea.Caret.Offset = line.Offset;
        Editor.ScrollToLine(s.StartLine + 1);
        Editor.Focus();
        ShowToast($"Jumped to line {s.StartLine + 1}");
    }

    private void ResetCurrent()
    {
        if (_current is null) return;
        _current.EditorDocument.Text = _current.Doc.OriginalText;
        ShowToast("Restored the original script from disk");
    }

    private async Task CopyCurrentAsync()
    {
        if (_current is null) return;
        var clipboard = GetTopLevel(this)?.Clipboard;
        if (clipboard is null) { ShowToast("Clipboard is not available"); return; }
        await clipboard.SetTextAsync(_current.EditorDocument.Text);
        ShowToast($"Copied the full script ({_current.EditorDocument.LineCount} lines)");
    }

    private void SaveTab(OpenTab tab)
    {
        try
        {
            tab.Doc.Text = tab.EditorDocument.Text;
            tab.Doc.Save();
            tab.IsModified = false;
            if (tab.Item is not null) tab.Item.IsModified = false;
        }
        catch (Exception ex) when (ex is IOException or UnauthorizedAccessException)
        {
            ShowToast($"Cannot save: {ex.Message}");
        }
    }

    protected override void OnKeyDown(KeyEventArgs e)
    {
        base.OnKeyDown(e);
        if (!e.KeyModifiers.HasFlag(KeyModifiers.Control) && !e.KeyModifiers.HasFlag(KeyModifiers.Meta)) return;

        switch (e.Key)
        {
            case Key.S when _current is not null:
                SaveTab(_current); UpdateState(); ShowToast("Saved to disk"); e.Handled = true; break;
            case Key.W when _current is not null:
                _ = CloseTabAsync(_current); e.Handled = true; break;
            case Key.F:
                SearchBox.Focus(); SearchBox.SelectAll(); e.Handled = true; break;
        }
    }

    protected override async void OnClosing(WindowClosingEventArgs e)
    {
        if (_tabs.Any(t => t.IsModified) && !_closingConfirmed)
        {
            e.Cancel = true;
            if (await CloseAllTabsAsync()) { _closingConfirmed = true; Close(); }
        }
        base.OnClosing(e);
    }
    private bool _closingConfirmed;

    // ---------- theme & toast ----------

    private void CycleTheme()
    {
        _settings.Theme = _settings.Theme switch { "System" => "Light", "Light" => "Dark", _ => "System" };
        _settings.Save();
        ThemeButton.Content = $"Theme: {_settings.Theme}";
        App.ApplyTheme(_settings.Theme);
    }

    private void UpdateCodeBrushes()
    {
        bool dark = ActualThemeVariant == ThemeVariant.Dark;
        IBrush B(string light, string darkC) => new SolidColorBrush(Color.Parse(dark ? darkC : light));
        if (_colorizer is not null)
        {
            _colorizer.Keyword = B("#0A57B8", "#82BBFF");
            _colorizer.String = B("#1F7A44", "#6ED29A");
            _colorizer.Number = B("#B5471F", "#F29B88");
            _colorizer.Comment = B("#7B8794", "#7F8E9D");
        }
        _sectionRenderer.Fill = B("#FFEBD6", "#3F2A14");
        _sectionRenderer.Edge = B("#E9730C", "#F29A4A");
        Editor.TextArea.TextView.Redraw();
        UpdateState();
    }

    private void ShowToast(string text)
    {
        ToastText.Text = text;
        Toast.IsVisible = true;
        _toastTimer.Stop();
        _toastTimer.Start();
    }
}
