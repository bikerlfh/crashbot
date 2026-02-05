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

2. **GUI Layer** (`apps/gui/`): PyQt6 windows for login, parameters, bot config, console, configurations. Uses SocketIO client for real-time updates. Dark theme via pyqtdarktheme.

3. **API Layer** (`apps/api/`): REST API client for backend communication. Token-based authentication, prediction requests, multiplier/bet data submission, customer/subscription management. Key files: `services.py` (API calls), `bot_api.py` (connector + endpoint definitions), `models.py` (data models including `PlanData`, `CustomerData`, `Prediction`, `Bot`), `exceptions.py` (error handling with codes).

4. **External WebSocket Client** (`apps/ws_client.py`): Singleton WebSocket client connecting to the backend server. Handles version validation, duplicate session prevention, multiplier save permissions, and remote error/close signals.

5. **Game Layer** (`apps/game/games/`): Abstract `GameBase` with two implementations via `ConfigurationFactory`:
   - `GameAI` (`configuration="ai"`): Orchestrates betting with ML model predictions via `PredictionModel`.
   - `GameStrategy` (`configuration="strategy"`): Pure strategy-based betting without AI predictions.

6. **Bot Layer** (`apps/game/bots/`): Abstract `BotBase` (~543 lines) with two implementations:
   - `BotAI`: Uses ML predictions, adaptive Kelly criterion for bet sizing, category/probability filtering.
   - `BotStrategy`: Fixed multiplier approach, simpler bet generation, still uses Kelly formula.

7. **Scraper Layer** (`apps/scrappers/`): Playwright-based browser automation. `AbstractCrashGameBase` → game-specific base classes:
   - `aviator/`: `AviatorBase` → Demo, BetPlay, OneWin, Rivalo, 1xBet, Ecuabet, Default.
   - `to_the_moon/`: `ToTheMoonBase` → Demo, OneWin.

8. **Custom Bots Layer** (`apps/custom_bots/`): Fernet-encrypted `.bot` files. `CustomBotsEncryptHandler` handles save/load/migration. Custom bots use negative IDs, server bots use positive IDs.

9. **Prediction Layer** (`apps/game/prediction_core.py`): ML model evaluation, tracks accuracy per model, filters underperforming predictions.

10. **WebSocket Server** (`apps/game/ws_server/`): SocketIO server on localhost:5000 for real-time GUI events.

### Supported Bookmakers

| ID | Name | Games |
|----|------|-------|
| 1 | Demo | Aviator |
| 2 | BetPlay | Aviator |
| 3 | OneWin | Aviator, To The Moon |
| 4 | Rivalo | Aviator |
| 5 | 1xBet | Aviator |
| 6 | Demo To The Moon | To The Moon |
| 7 | ECUABET | Aviator |

Defined in `apps/game/bookmakers/constants.py` (`BookmakerIDS` enum). Each scraper registers via `ConfigurationFactory` with its bookmaker ID.

### Key Design Patterns

- **Singleton**: `GlobalVars` (`apps/globals.py`), `Config` (`apps/config.py`), `PredictionModel`, `LocalStorage`, `WebSocketClient`, `BotAPIConnector`
- **Factory**: `ConfigurationFactory` (uses `__init_subclass__` with `configuration` parameter) for plugin-based game/bot/scraper registration
- **Abstract Base Classes**: `BotBase`, `GameBase`, `AbstractCrashGameBase`

### Data Flow

```
GUI ←→ SocketIO ←→ WebSocket Server ←→ Game Logic ←→ Bot Decision ←→ Playwright Scraper
                                           ↑    ↑
                             Prediction API ┘    └── Multiplier/Bet Data
                                   ↑                        ↓
                               Backend REST API ←→ External WebSocket Client
                                   ↑
                          Auth / Subscription / Customer Data
```

### API Endpoints

Backend REST API endpoints (defined in `apps/api/bot_api.py`):

| Endpoint | Purpose |
|----------|---------|
| `api/auth/login/` | User authentication |
| `api/auth/verify/` | Token verification |
| `api/home-bet/multiplier/` | Submit multiplier history |
| `api/predictions/predict/` | Request AI predictions |
| `api/predictions/bots/` | Retrieve bot configurations |
| `api/predictions/positions/` | Historical multiplier positions |
| `api/customers/me/` | Customer data and subscription plan |
| `api/customers/live/` | Live session tracking |
| `api/bets/` | Submit and retrieve bets |

## Subscription & Auth

- **Login flow**: `apps/api/services.py::request_login()` → token stored in `BotAPIConnector` → `request_token_verify()` on reconnect
- **Subscription plans**: `PlanData` model with `name`, `with_ai`, `start_date`, `end_date`, `is_active` fields
- **Feature gating**: `with_ai` flag determines if AI predictions are available; otherwise only strategy mode
- **Session control**: External WebSocket validates version and prevents duplicate sessions

## Configuration

- **Main config**: `conf.ini` - API URLs, betting percentages, language, thresholds
- **API_URL**: Backend REST API URL (set in `apps/config.py`)
- **WS_URL**: Backend WebSocket URL for session control (set in `apps/config.py`)
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

- `apps/game/bots/bot_base.py`: Core betting logic (~543 lines), abstract base for all bots
- `apps/game/bots/bot_ai.py`: AI bot with Kelly criterion and prediction filtering
- `apps/game/bots/bot_strategy.py`: Strategy bot without AI dependency
- `apps/game/games/game_ai.py`: AI-enhanced game orchestration
- `apps/game/games/game_strategy.py`: Strategy-based game orchestration
- `apps/game/games/game_base.py`: Abstract game base with main game loop
- `apps/game/prediction_core.py`: Prediction model evaluation
- `apps/api/services.py`: All REST API service functions (auth, predictions, bets, customers)
- `apps/api/bot_api.py`: API connector singleton and endpoint definitions
- `apps/api/models.py`: Data models (Bot, Prediction, PlanData, CustomerData, etc.)
- `apps/ws_client.py`: External WebSocket client for backend communication
- `apps/custom_bots/handlers.py`: Fernet encryption handler for .bot files
- `apps/scrappers/aviator/aviator_base.py`: Aviator browser automation base
- `apps/scrappers/to_the_moon/to_the_moon_base.py`: To The Moon browser automation base
- `apps/game/bookmakers/constants.py`: BookmakerIDS enum
- `apps/game/bookmakers/home_bet.py`: Factory for scraper instantiation
- `apps/config.py`: Configuration singleton with all app settings

## Tests

- **Location**: `tests/bots/`
- **Coverage**: Bot condition logic — aggressive mode, forget losses, ignore model, make bet, streak multiplier conditions
- **Run**: `pytest tests/`

## Notebooks

- **Location**: `notebooks/`
- **Purpose**: Research and data analysis for trend detection and statistical modeling
- Key notebooks: Bollinger Bands analysis, bullish/bearish trend graphs, linear regression, round visualizations

## Data Storage

- **Logs**: SQLite at `data/logs.db`
- **Local storage**: Browser-like key-value via localStoragePy
- **Translations**: `locales/` with gettext `.mo` files (Spanish, English)
