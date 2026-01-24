# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CrashBot is a Python 3.10+ desktop application using PyQt6 for automated betting on crash-type games (Aviator, To The Moon). It combines a GUI frontend with a WebSocket server backend and uses Playwright for browser automation.

## Common Commands

```bash
# Run the application
make run
# or: python crashbot.py

# Format code with Black (line length 79)
make black

# Generate UI from Qt Designer files
make generate-ui-app          # Main window
make generate-ui-login        # Login window
make generate-ui-parameters   # Parameter settings
make generate-ui-console      # Console window
make generate-ui-configurations  # Config window
make generate-ui-config-bot   # Bot configuration

# Build executable
make generate-installer

# Compile translations
make translate
```

## Architecture

### Core Layers

1. **Entry Point** (`crashbot.py`): Initializes GlobalVars singleton, loads custom bots, starts WebSocket server in background thread, launches PyQt6 GUI.

2. **GUI Layer** (`apps/gui/`): PyQt6 windows for login, parameters, bot config, console. Uses SocketIO client for real-time updates. Dark theme via pyqtdarktheme.

3. **Game Layer** (`apps/game/games/`): Abstract `GameBase` → `GameAI` implementation. Orchestrates betting with AI model predictions.

4. **Bot Layer** (`apps/game/bots/`): Abstract `BotBase` → `BotAI`. Configurable betting logic with recovery strategies, stop loss, take profit.

5. **Scraper Layer** (`apps/scrappers/`): Playwright-based browser automation. `AbstractCrashGameBase` → game-specific implementations (Aviator, ToTheMoon) for multiple bookmakers.

6. **Prediction Layer** (`apps/game/prediction_core.py`): ML model evaluation, tracks accuracy per model, filters underperforming predictions.

7. **WebSocket Server** (`apps/game/ws_server/`): SocketIO server on localhost:5000 for real-time GUI events.

### Key Design Patterns

- **Singleton**: `GlobalVars` (`apps/globals.py`), `Config` (`apps/config.py`), `PredictionModel`, `LocalStorage`
- **Factory**: `ConfigurationFactory` for plugin-based game/bot registration
- **Abstract Base Classes**: `BotBase`, `GameBase`, `AbstractCrashGameBase`

### Data Flow

```
GUI ←→ SocketIO ←→ WebSocket Server ←→ Game Logic ←→ Bot Decision ←→ Playwright Scraper
                                              ↑
                                    Prediction API (external)
```

## Configuration

- **Main config**: `conf.ini` - API URLs, betting percentages, language, thresholds
- **Environment**: `.envrc` - `IS_ALLOWED_TO_SAVE_MULTIPLIERS`, `DATA_FILE_PATH`, `PLAYWRIGHT_BROWSERS_PATH`
- **Custom bots**: Encrypted `.bot` files in `custom_bots/` directory

## Code Quality

Pre-commit hooks enforce:
- Black formatting (line length 79)
- Flake8 linting (ignores W503, F405, TYP001)
- isort import ordering
- Safety vulnerability scanning

Files matching `*_designer.py` are auto-generated and excluded from checks.

## Key Files

- `apps/game/bots/bot_base.py`: Core betting logic (~500 lines)
- `apps/game/games/game_ai.py`: AI-enhanced game orchestration
- `apps/game/prediction_core.py`: Prediction model evaluation
- `apps/scrappers/aviator/aviator_base.py`: Browser automation base
- `apps/config.py`: Configuration singleton with all app settings

## Data Storage

- **Logs**: SQLite at `data/logs.db`
- **Local storage**: Browser-like key-value via localStoragePy
- **Translations**: `locales/` with gettext `.mo` files (Spanish, English)
