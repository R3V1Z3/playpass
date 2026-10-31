# Play Pass Directory

A fast, zero-dependency, ad-free web application that extracts and indexes the complete list of **Google Play Pass** games and apps from [Ytechb's Google Play Pass Games List](https://www.ytechb.com/google-play-pass-games-list/).

## Features

- **Instant Multi-Term Search & Highlighting**: Filter by title or category in real time (`<2ms`) with matched substring highlighting.
- **Category & Alphabetical Filtering**: Filter by any of the 16 genres (Action, Adventure, Arcade, Board, Card, Casual, Educational, Music, Puzzle, Racing, Role-Playing, Simulation, Sports, Strategy, Trivia, Word) or jump by starting letter (`#`, `A–Z`).
- **One-Click Google Play Store Links**: Every game and app links directly to its Google Play Store search/listing.
- **Saved / Bookmarks List**: Star your favorite games (persisted in `localStorage`) and filter to view only your saved collection.
- **Supported Countries & Regions Explorer**: Searchable modal of all 100 countries where Google Play Pass is available.
- **Responsive Desktop + Mobile UI**: Seamless layout with Card Grid & Compact List views, Dark/Light mode toggle, and keyboard shortcuts (`/` to search, `R` for random pick, `Esc` to clear).

## Usage

### 1. Launch via `build.ps1` (Local Server + Browser)
Run `build.ps1` to automatically pick an available port (starting at `8090`), start a local HTTP server, and open the app in your default browser:
```powershell
c:\git\playpass\build.ps1
```
Pass `-Sync` to refresh the dataset from Ytechb before launching:
```powershell
c:\git\playpass\build.ps1 -Sync
```

### 2. Open Directly
No server or build step is required. Simply open `index.html` in any modern desktop or mobile browser:
```powershell
Invoke-Item c:\git\playpass\index.html
```

### 2. Refresh the Dataset from Ytechb
Whenever Ytechb updates their catalog, run the synchronization script to fetch the latest HTML and regenerate `data.js` and `data.json`:
```powershell
python c:\git\playpass\sync.py
```
