# HANA Script Studio

Szybka aplikacja okienkowa do pracy ze skryptami SQL dla SAP HANA (kolekcja „SQL Statement Collection", SAP Note 1969700). Przeglądasz katalog ze skryptami, filtrujesz je po słowie, otwierasz kilka naraz w zakładkach, zmieniasz parametry w sekcji **Modification section** i kopiujesz gotowy skrypt do schowka. Oryginalne pliki nie są zmieniane, dopóki sam nie zapiszesz (Ctrl+S).

Interfejs aplikacji jest po angielsku. Aplikacja jest napisana w C# (.NET 8) z użyciem Avalonia UI i edytora AvaloniaEdit. Działa na Windows, a ten sam kod można zbudować także na macOS i Linux.

## Instalacja (Windows)

### Wariant 1: instalator (zalecany)

1. Pobierz `HanaScriptStudio-Setup-<wersja>.exe` (z zakładki **Actions** / **Releases** repozytorium, patrz „Skąd wziąć instalator" niżej).
2. Uruchom plik i przejdź kreator: **Next → Install → Finish**.
3. Instalacja jest dla bieżącego użytkownika, więc nie wymaga praw administratora. Środowisko .NET jest w paczce i nie trzeba go instalować osobno.
4. Uruchom **HANA Script Studio** z menu Start lub z ikony na pulpicie.

Odinstalowanie: **Ustawienia → Aplikacje → HANA Script Studio → Odinstaluj**.

Jeśli Windows SmartScreen pokaże ostrzeżenie „Nieznany wydawca" (instalator nie jest podpisany certyfikatem), wybierz **Więcej informacji → Uruchom mimo to**.

### Wariant 2: wersja portable

1. Pobierz `HanaScriptStudio-portable-win-x64.zip`.
2. Rozpakuj do dowolnego folderu i uruchom `HanaScriptStudio.exe`. Instalacja nie jest potrzebna.

### Skąd wziąć instalator

Instalator i wersję portable buduje automatycznie GitHub Actions (workflow `HANA Script Studio`):

- po każdym pushu zmieniającym katalog `hana-script-studio/` pliki są dostępne jako artefakt `HanaScriptStudio-windows` w zakładce **Actions**,
- aby wydać wersję, utwórz tag, np. `git tag hana-v1.0.0 && git push origin hana-v1.0.0`. Nazwa pliku instalatora zawiera wtedy numer wersji.

## Użycie

1. **Pierwsze uruchomienie.** Aplikacja prosi o wskazanie katalogu ze skryptami (np. rozpakowana kolekcja SAP). Wybór zostaje zapamiętany. Katalog zmienisz przyciskiem **Change folder**. Wczytywane są pliki `.txt` i `.sql` ze wszystkich podkatalogów.
2. **Szukanie.** Wpisz słowo w polu wyszukiwania po lewej. Lista zawęża się na bieżąco i uwzględnia nazwę pliku oraz treść skryptu. Kilka słów oznacza, że wszystkie muszą wystąpić. Zaznacz **Match file names only**, jeśli chcesz szukać tylko w nazwach. Skrót: **Ctrl+F**.
3. **Otwieranie.** Kliknij skrypt na liście, a otworzy się w nowej zakładce. Możesz mieć otwartych wiele skryptów. Kropka przy nazwie oznacza niezapisane zmiany.
4. **Edycja.** Zmieniaj skrypt w edytorze. Sekcja modyfikacji jest podświetlona na pomarańczowo, a wąski pasek przy prawej krawędzi edytora pokazuje jej położenie w pliku (kliknięcie w niego przenosi do sekcji).
5. **Przyciski nad edytorem:**
   - **Go to modification section** przenosi kursor do linii z `Modification section`.
   - **Reset to original** wraca do treści pliku z dysku i usuwa wszystkie zmiany w tym skrypcie.
   - **Copy script** kopiuje cały, aktualny (zmieniony) skrypt do schowka. Wklej go w narzędziu, w którym uruchamiasz SQL (np. HANA Studio, SAP HANA Cockpit, DBeaver).
6. **Zapis.** Zmiany są tylko kopią roboczą. **Ctrl+S** zapisuje je do pliku na dysku. Przy zamykaniu zakładki lub okna z niezapisanymi zmianami aplikacja zapyta, co zrobić.

Skróty: `Ctrl+F` szukaj, `Ctrl+S` zapisz, `Ctrl+W` zamknij zakładkę.

Przycisk **Theme** w prawym górnym rogu przełącza motyw System / Light / Dark. Ustawienia (ostatni katalog, motyw) są w `%APPDATA%\HanaScriptStudio\settings.json`.

### Jak aplikacja rozpoznaje sekcję modyfikacji

Sekcja zaczyna się w pierwszej linii zawierającej `Modification section` (wielkość liter nie ma znaczenia) i kończy przed linią zawierającą `Internal section`. Jeśli skrypt nie ma takiej sekcji, przycisk jest nieaktywny, a obok widać informację o jej braku.

## Budowanie ze źródeł

Wymagania: [.NET SDK 8](https://dotnet.microsoft.com/download/dotnet/8.0).

```bash
cd hana-script-studio
dotnet test                              # testy logiki (parser sekcji, wyszukiwanie, reset)
dotnet run --project src/HanaScriptStudio  # uruchom aplikację

# wersja do dystrybucji dla Windows (self-contained)
dotnet publish src/HanaScriptStudio -c Release -r win-x64 --self-contained -p:DebugType=none -o publish/win-x64
```

Instalator budujesz w [Inno Setup 6](https://jrsoftware.org/isinfo.php) (Windows):

```powershell
iscc /DAppVersion=1.0.0 installer\HanaScriptStudio.iss   # wynik w artifacts\
```

Na macOS lub Linuksie użyj odpowiednio `-r osx-arm64`, `-r osx-x64` lub `-r linux-x64`. Pakiety instalacyjne dla tych systemów nie są jeszcze przygotowane.

## Struktura projektu

```
hana-script-studio/
├── src/HanaScriptStudio.Core/   logika bez UI: indeks i wyszukiwanie, parser sekcji, dokument, ustawienia
├── src/HanaScriptStudio/        aplikacja Avalonia (okno, style SAP, edytor SQL)
├── tests/HanaScriptStudio.Core.Tests/   testy xUnit
└── installer/                   skrypt instalatora Inno Setup
```

## Wydajność

- Treść wszystkich skryptów jest wczytywana raz, równolegle, po wyborze katalogu. Filtrowanie działa potem tylko w pamięci, z krótkim opóźnieniem (150 ms) po wpisaniu znaku.
- Lista jest wirtualizowana, więc tysiące plików nie spowalniają przewijania.
- Pliki większe niż 4 MB są widoczne na liście, ale pomijane przy wyszukiwaniu po treści.
