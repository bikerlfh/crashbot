# CrashBot Technical Documentation

**Version:** 2.0.0
**Last Updated:** January 2026

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Overview](#architecture-overview)
4. [Core Layers](#core-layers)
5. [Key Classes and Methods](#key-classes-and-methods)
6. [Configuration](#configuration)
7. [WebSocket Events Protocol](#websocket-events-protocol)
8. [Database Schema](#database-schema)
9. [Custom Bot Plugin System](#custom-bot-plugin-system)
10. [API Integrations](#api-integrations)
11. [Build and Development](#build-and-development)
12. [Code Quality Standards](#code-quality-standards)

---

## Project Overview

CrashBot is a Python 3.10+ desktop application designed for automated betting on crash-type games such as Aviator and To The Moon. The application combines a modern PyQt6 GUI frontend with a WebSocket server backend, utilizing Playwright for browser automation to interact with bookmaker websites.

### Key Features

- **Automated Betting**: Places bets automatically based on configurable bot strategies
- **Multi-Bookmaker Support**: Supports various bookmakers through a plugin-based architecture
- **Real-time Communication**: WebSocket-based communication between GUI and backend
- **Recovery Strategies**: Intelligent bet recovery mechanisms to manage losses
- **Custom Bot System**: Encrypted `.bot` files for custom betting strategies
- **Multi-language Support**: English and Spanish translations via gettext

### System Requirements

- Python 3.10 or higher
- Operating Systems: Windows, macOS, Linux
- Chromium browser (installed automatically by Playwright)
- Minimum 4GB RAM recommended
- Internet connection for bookmaker access

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| GUI Framework | PyQt6 | 6.5.0 | Desktop user interface |
| GUI Theme | pyqtdarktheme | 2.1.0 | Dark theme styling |
| Communication | python-socketio | 5.8.0 | Real-time WebSocket messaging |
| ASGI Server | Uvicorn | 0.21.1 | WebSocket server hosting |
| Browser Automation | Playwright | 1.57.0 | Web scraping and betting automation |
| HTTP Client | requests | 2.31.0 | API communication |
| Database | SQLite | Built-in | Local logging and storage |
| Encryption | cryptography | Latest | Bot file encryption |
| Charts | matplotlib | 3.10.8 | Multiplier visualization |
| Local Storage | localStoragePy | 0.2.3 | Browser-like key-value storage |

---

## Architecture Overview

For comprehensive architecture diagrams including component relationships, data flows, class hierarchies, and sequence diagrams, please refer to:

**[Architecture Documentation](./architecture.md)**

The architecture document includes:
- High-level architecture diagram
- Component diagram
- Data flow diagram
- Class hierarchy with UML
- Sequence diagrams for startup and betting cycles
- Design patterns overview

### Directory Structure

```
crashbot/
├── crashbot.py              # Application entry point
├── conf.ini                 # User configuration file
├── config/
│   └── app_data.json        # Local data configuration (home bets, games)
├── apps/
│   ├── __init__.py
│   ├── config.py            # Config singleton
│   ├── globals.py           # GlobalVars singleton
│   ├── constants.py         # Application constants
│   ├── api/                 # API models and services
│   │   ├── models.py        # Data models (Bot, Prediction, etc.)
│   │   ├── services.py      # API request functions
│   │   └── exceptions.py    # Custom exceptions
│   ├── custom_bots/         # Custom bot loading system
│   │   ├── services.py      # Bot file parsing
│   │   ├── handlers.py      # Encryption handlers
│   │   └── constants.py     # Bot constants
│   ├── data/
│   │   └── local_data_loader.py  # Local JSON data loader
│   ├── game/
│   │   ├── bots/            # Bot implementations
│   │   │   ├── bot_base.py  # Abstract bot class
│   │   │   ├── bot_ai.py    # AI betting bot
│   │   │   ├── bot_strategy.py  # Strategy-based bot
│   │   │   └── helpers.py   # Bot condition helpers
│   │   ├── games/           # Game implementations
│   │   │   ├── game_base.py # Abstract game class (if exists)
│   │   │   └── game_strategy.py  # Strategy game implementation
│   │   ├── ws_server/       # WebSocket server
│   │   │   ├── server.py    # SocketIO ASGI server
│   │   │   ├── events.py    # Event handlers
│   │   │   └── utils.py     # Server utilities
│   │   ├── prediction_core.py   # ML model evaluation
│   │   └── models.py        # Game data models (Bet, Multiplier)
│   ├── gui/
│   │   ├── app.py           # PyQt6 application entry
│   │   ├── socket_io_client.py  # SocketIO client thread
│   │   ├── gui_events.py    # GUI event helpers
│   │   ├── services.py      # GUI services
│   │   ├── constants.py     # GUI constants
│   │   ├── graphs/          # Chart widgets
│   │   │   └── bar_multipliers.py
│   │   └── windows/         # PyQt6 window classes
│   │       ├── main/        # Main window
│   │       ├── console/     # Console/betting window
│   │       ├── parameter/   # Parameter selection
│   │       ├── credential/  # Credential management
│   │       ├── config_bot/  # Bot configuration
│   │       └── configurations/  # App settings
│   ├── scrappers/           # Browser automation
│   │   ├── game_base.py     # Abstract scraper class
│   │   └── aviator/         # Aviator game scrapers
│   │       ├── aviator_base.py      # Core automation
│   │       ├── aviator_demo.py      # Demo mode
│   │       ├── aviator_bet_play.py  # BetPlay variant
│   │       ├── aviator_ecuabet.py   # Ecuabet variant
│   │       └── bet_control.py       # Bet control automation
│   └── utils/
│       ├── patterns/        # Design patterns
│       │   ├── singleton.py # Singleton metaclass
│       │   └── factory.py   # Factory pattern
│       ├── local_storage.py # Key-value storage
│       ├── sqlite_engine.py # SQLite wrapper
│       ├── security/        # Encryption utilities
│       │   └── encrypt.py
│       ├── logs/            # Logging services
│       │   ├── services.py
│       │   └── logs_db_handler.py
│       └── datetime.py      # Date/time utilities
├── custom_bots/             # Encrypted .bot files
├── locales/                 # i18n translations
│   ├── en/LC_MESSAGES/
│   └── es/LC_MESSAGES/
└── data/                    # Runtime data (logs.db)
```

---

## Core Layers

### 1. Entry Point Layer (`crashbot.py`)

The application entry point that orchestrates initialization:

```python
def init_app():
    # 1. Initialize GlobalVars singleton with base path
    GlobalVars.init(base_path)

    # 2. Load local data configuration
    LocalDataLoader(base_path)

    # 3. Setup language translations
    setup_language(GlobalVars.config.LANGUAGE)

    # 4. Load custom bots from encrypted files
    custom_bots = custom_bots_services.read_custom_bots(custom_bot_path)
    GlobalVars.set_bots(custom_bots)

    # 5. Start WebSocket server in background thread
    ws_server_thread = Thread(target=game_server.run_server, args=(event,))
    ws_server_thread.start()

    # 6. Launch PyQt6 GUI
    gui_app.run_gui()
```

### 2. GUI Layer (`apps/gui/`)

Built with PyQt6 and pyqtdarktheme for a modern dark interface.

**Key Components:**

- **MainForm**: Primary window managing screen navigation
- **ParameterForm**: Bot and bookmaker selection
- **ConsoleForm**: Live betting console with balance, logs, and charts
- **CredentialDialog**: Bookmaker credential management
- **ConfigBotDialog**: Bot configuration interface
- **ConfigurationsDialog**: Application settings
- **SocketIOClient**: QThread-based WebSocket client

**Signal-Slot Pattern:**

The GUI uses PyQt6's signal-slot mechanism for thread-safe communication:

```python
class ConsoleForm(QWidget):
    receive_log_signal = QtCore.pyqtSignal(dict)

    def on_log(self, data):
        # Called from WebSocket thread
        self.receive_log_signal.emit(data)

    @QtCore.pyqtSlot(dict)
    def _on_receive_log(self, data):
        # Executed in GUI thread
        self.__add_item_to_list(data)
```

### 3. Game Layer (`apps/game/games/`)

Manages game orchestration and betting cycles.

**GameStrategy Class:**

```python
class GameStrategy(GameBase):
    def initialize_bot(self, bot_name: str):
        # Initialize bot with balance and multipliers

    def add_multiplier(self, multiplier: float):
        # Process new multiplier result

    async def wait_next_game(self):
        # Wait for betting window

    def get_next_bet(self) -> list[Bet]:
        # Request next betting decision from bot
```

### 4. Bot Layer (`apps/game/bots/`)

Contains betting logic and decision-making.

**BotBase Abstract Class:**

Core properties and methods inherited by all bots:

| Property | Type | Description |
|----------|------|-------------|
| `BOT_NAME` | str | Bot identifier |
| `RISK_FACTOR` | float | Risk percentage (0.1 = 10%) |
| `MIN_MULTIPLIER_TO_BET` | float | Minimum multiplier to place bets |
| `STOP_LOSS_PERCENTAGE` | float | Stop loss as percentage of initial balance |
| `TAKE_PROFIT_PERCENTAGE` | float | Take profit as percentage of initial balance |
| `RECOVERY_LOSSES` | bool | Enable loss recovery mode |

**Key Methods:**

| Method | Description |
|--------|-------------|
| `initialize(balance, multipliers)` | Setup bot with initial state |
| `generate_bets(prediction_data)` | Create bet list based on predictions |
| `get_next_bet(prediction, auto_play)` | Main decision method |
| `evaluate_bets(multiplier_result)` | Process bet results |
| `in_stop_loss()` | Check if stop loss reached |
| `in_take_profit()` | Check if take profit reached |
| `determine_bullish_game()` | Analyze market trend |

**BotStrategy Class:**

Strategy-based betting using Kelly Criterion:

```python
def generate_bets(self, multiplier: float):
    if profit < 0 and self.RECOVERY_LOSSES:
        return self.generate_recovery_bets(multiplier)

    # Use adaptive Kelly formula for bet sizing
    kelly_amount = adaptive_kelly_formula(
        multiplier, risk_factor, max_amount
    )
```

### 5. Scraper Layer (`apps/scrappers/`)

Playwright-based browser automation for bookmaker interaction.

**AbstractCrashGameBase Interface:**

```python
class AbstractCrashGameBase(ABC):
    url: str
    multipliers: List[float]
    balance: float
    minimum_bet: float
    maximum_bet: float

    async def open(self): ...
    async def close(self): ...
    async def read_balance(self) -> float: ...
    async def read_multipliers(self): ...
    async def bet(self, bets: list[Bet], use_auto_cash_out: bool): ...
    async def wait_next_game(self): ...
```

**AviatorBase Implementation:**

```python
class AviatorBase(AbstractCrashGameBase, ConfigurationFactory):
    async def open(self):
        self.playwright = await async_playwright().start()
        self._browser = await self.playwright.chromium.launch(headless=False)
        self._page = await self._context.new_page()
        await self._page.goto(self.url)
        # Initialize game elements

    async def bet(self, bets: list[Bet], use_auto_cash_out: bool):
        for bet in bets:
            await self._controls.bet(
                amount=bet.amount,
                multiplier=bet.multiplier,
                control=control,
                use_auto_cash_out=use_auto_cash_out
            )
```

### 6. WebSocket Server Layer (`apps/game/ws_server/`)

SocketIO ASGI server for real-time communication.

```python
sio = socketio.AsyncServer(async_mode="asgi")
app = socketio.ASGIApp(sio)

@sio.on(WSEvent.START_BOT)
async def start_bot(sid, data, room=None):
    await events.start_bot_event(data, sio, sid)

def run_server(event: Event):
    GlobalVars.set_io(sio)
    uvicorn.run(app, host=host, port=port)
```

---

## Key Classes and Methods

### GlobalVars Singleton

Central application state management:

```python
class GlobalVars:
    APP_NAME: str = "CrashBot"
    APP_VERSION: str = "2.0.0"
    SIO: AsyncServer = None
    GAME: any = None
    config: Config

    class VARS(str, Enum):
        AUTO_PLAY = "AUTO_PLAY"
        MAX_AMOUNT_TO_BET = "MAX_AMOUNT_TO_BET"
        BOTS = "BOTS"
        # ... more variables

    @classmethod
    def emit_to_gui(cls, event: str, data: any):
        asyncio.run_coroutine_threadsafe(
            cls.SIO.emit(event, data=data),
            asyncio.get_event_loop()
        )
```

### Config Singleton

Configuration management:

```python
class Config(metaclass=Singleton):
    # Default values
    MAX_AMOUNT_HOME_BET_PERCENTAGE = 0.5
    MAX_AMOUNT_BALANCE_PERCENTAGE = 0.005
    MIN_VALUE_TO_BULLISH_GAME = 0.26
    LEN_WINDOW_TO_BULLISH_GAME = 6
    LANGUAGE = "en"
    WS_SERVER_HOST = "localhost"
    WS_SERVER_PORT = 5000

    def read_config(self): ...
    def write_config(self, language=None, ...): ...
```

### SendEventToGUI Helper

Utility for sending events to GUI:

```python
class SendEventToGUI:
    class _LogEvent:
        @staticmethod
        def info(message: str): ...
        @staticmethod
        def success(message: str): ...
        @staticmethod
        def warning(message: str): ...
        @staticmethod
        def error(message: str): ...
        @staticmethod
        def debug(message: str): ...

    log = _LogEvent

    @staticmethod
    def send_balance(balance: float, initial_balance: float): ...
    @staticmethod
    def send_multipliers(multipliers: list[float]): ...
    @staticmethod
    def game_loaded(is_game_loaded: bool): ...
```

### Bot Data Model

```python
class Bot:
    id: int
    name: str
    bot_type: str
    risk_factor: float
    min_multiplier_to_bet: float
    min_multiplier_to_recover_losses: float
    min_probability_to_bet: float
    min_category_percentage_to_bet: float
    max_recovery_percentage_on_max_bet: float
    min_average_model_prediction: float
    stop_loss_percentage: float
    take_profit_percentage: float
    conditions: list[BotCondition]
    only_bullish_games: bool
    make_second_bet: bool
```

### Bet Model

```python
class Bet:
    external_id: str  # 16-char random ID
    amount: float
    multiplier: float
    prediction: float
    multiplier_result: float
    profit: float

    def evaluate(self, multiplier_result: float) -> float:
        if multiplier_result > self.multiplier:
            self.profit = self.amount * (self.multiplier - 1)
        else:
            self.profit = -self.amount
        return self.profit
```

---

## Configuration

### conf.ini

Main user configuration file:

```ini
# Default configuration
MAX_AMOUNT_HOME_BET_PERCENTAGE=0.5
MAX_AMOUNT_BALANCE_PERCENTAGE=0.005
NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH=30
MIN_VALUE_TO_BULLISH_GAME=0.26
LEN_WINDOW_TO_BULLISH_GAME=20
MULTIPLIERS_TO_SHOW_LAST_POSITION=10,15,20,50,100
LANGUAGE=en
```

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `MAX_AMOUNT_HOME_BET_PERCENTAGE` | float | 0.5 | Maximum bet as percentage of home bet limit |
| `MAX_AMOUNT_BALANCE_PERCENTAGE` | float | 0.005 | Maximum bet as percentage of balance |
| `NUMBER_OF_MULTIPLIERS_IN_BAR_GRAPH` | int | 30 | Multipliers shown in chart |
| `MIN_VALUE_TO_BULLISH_GAME` | float | 0.26 | Slope threshold for bullish detection |
| `LEN_WINDOW_TO_BULLISH_GAME` | int | 20 | Window size for trend analysis |
| `MULTIPLIERS_TO_SHOW_LAST_POSITION` | list | 10,15,20,50,100 | Multipliers to track position |
| `LANGUAGE` | string | en | UI language (en/es) |

### config/app_data.json

Local data configuration (replaces backend API):

```json
{
  "home_bets": [
    {
      "id": 1,
      "name": "BookmakerName",
      "url": "https://bookmaker.com/aviator"
    }
  ],
  "home_bet_games": [
    {
      "id": 1,
      "home_bet_id": 1,
      "crash_game": "Aviator",
      "limits": {
        "USD": {
          "min_bet": 0.10,
          "max_bet": 100.00,
          "amount_multiple": 0.01
        }
      }
    }
  ],
  "plan": {
    "with_ai": false
  }
}
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `IS_ALLOWED_TO_SAVE_MULTIPLIERS` | Enable multiplier history saving |
| `DATA_FILE_PATH` | Custom data directory path |
| `PLAYWRIGHT_BROWSERS_PATH` | Custom Playwright browser location |

---

## WebSocket Events Protocol

### Client to Server Events

| Event | Data | Description |
|-------|------|-------------|
| `verify` | `{}` | Verify connection |
| `startBot` | `{bot_name, home_bet_id, max_amount_to_bet, auto_play, use_game_ai, username?, password?}` | Start betting bot |
| `autoPlay` | `{auto_play: bool}` | Toggle auto-betting |
| `changeBot` | `{bot_name: str}` | Change active bot |
| `setMaxAmountToBet` | `{max_amount_to_bet: float}` | Update bet amount |
| `closeGame` | `{}` | Stop bot and close browser |

### Server to Client Events

| Event | Data | Description |
|-------|------|-------------|
| `verify` | `{verified: bool}` | Connection verified |
| `startBot` | `{started: bool, error?: {code, message}}` | Bot start result |
| `autoPlay` | `{auto_play: bool}` | Auto-play state changed |
| `log` | `{message: str, code: str}` | Log message |
| `update_balance` | `{balance: float, initial_balance: float}` | Balance update |
| `add_multipliers` | `{multipliers: list[float]}` | New multipliers |
| `game_loaded` | `{loaded: bool}` | Game ready status |
| `receive_multiplier_positions` | `{positions: list, len_multipliers: int}` | Multiplier positions |
| `error` | `{error: str}` | Error notification |
| `exception` | `{exception: str}` | Exception notification |

### Log Codes

| Code | Color | Description |
|------|-------|-------------|
| `info` | Default | General information |
| `success` | Green | Successful operations |
| `warning` | Yellow | Warnings |
| `error` | Red | Errors |
| `debug` | Gray | Debug information (when DEBUG=1) |

---

## Database Schema

### Logs Table (SQLite)

Location: `data/logs.db`

```sql
CREATE TABLE IF NOT EXISTS Logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    level TEXT,
    app TEXT,
    path TEXT NULL,
    timestamp TEXT
)
```

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Auto-increment primary key |
| `message` | TEXT | Log message content |
| `level` | TEXT | Log level (info, success, warning, error, debug, exception) |
| `app` | TEXT | Application source (gui, game) |
| `path` | TEXT | Optional file path reference |
| `timestamp` | TEXT | ISO format timestamp |

### Log Operations

```python
class LogsDBHandler(SQLiteEngine):
    def insert_log(self, message, level, app, timestamp=None, path=None): ...
    def get_logs(self, timestamp=None): ...
    def delete_logs(self, days): ...  # Delete logs older than N days
```

---

## Custom Bot Plugin System

### Bot File Format

Custom bots are stored as encrypted `.bot` files in the `custom_bots/` directory.

**File Structure (decrypted JSON):**

```json
{
  "id": -1,
  "name": "CustomBot",
  "description": "My custom betting strategy",
  "bot_type": "aggressive",
  "number_of_min_bets_allowed_in_bank": 50,
  "risk_factor": 0.1,
  "min_multiplier_to_bet": 1.5,
  "min_multiplier_to_recover_losses": 2.0,
  "min_probability_to_bet": 0.5,
  "min_category_percentage_to_bet": 0.8,
  "max_recovery_percentage_on_max_bet": 0.5,
  "min_average_model_prediction": 0.8,
  "stop_loss_percentage": 0.1,
  "take_profit_percentage": 0.2,
  "only_bullish_games": false,
  "make_second_bet": true,
  "max_second_multiplier": 3.0,
  "conditions": [
    {
      "id": 1,
      "condition_on": "streak_losses",
      "condition_on_value": 3,
      "actions": [
        {
          "condition_action": "change_multiplier",
          "action_value": 1.2
        }
      ],
      "others": {}
    }
  ]
}
```

### Bot Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `risk_factor` | float | Kelly criterion risk adjustment (0.0-1.0) |
| `min_multiplier_to_bet` | float | Minimum multiplier for regular bets |
| `min_multiplier_to_recover_losses` | float | Multiplier for recovery bets |
| `min_probability_to_bet` | float | Minimum prediction probability |
| `min_category_percentage_to_bet` | float | Minimum category accuracy |
| `max_recovery_percentage_on_max_bet` | float | Max recovery bet as % of max bet |
| `stop_loss_percentage` | float | Stop loss as % of initial balance |
| `take_profit_percentage` | float | Take profit as % of initial balance |
| `only_bullish_games` | bool | Only bet in bullish markets |
| `make_second_bet` | bool | Enable secondary bets |

### Encryption Handler

```python
class CustomBotsEncryptHandler:
    BOT_EXTENSION = ".bot"

    def save(self, bot: Bot): ...
    def load(self, bot_path: str) -> Bot: ...
    def load_all(self) -> list[Bot]: ...
    def convert_json_to_encrypted(self) -> list[Bot]: ...
```

### Loading Custom Bots

```python
def read_custom_bots(custom_bots_path: str) -> list[Bot]:
    bots_handler = CustomBotsEncryptHandler(custom_bots_path)
    custom_bots = bots_handler.load_all()
    return custom_bots
```

---

## API Integrations

> **Note:** This version of CrashBot operates in standalone mode and does not connect to any external backend API. All configuration data is loaded from local files.

### Local Data Loader

The application uses local JSON configuration instead of a backend API:

```python
class LocalDataLoader:
    """Singleton that loads configuration data from local JSON file."""

    def get_home_bets(self) -> list[HomeBetModel]: ...
    def get_home_bet_games(self) -> list[HomeBetGameModel]: ...
    def get_plan(self) -> dict: ...
```

### Data Sources

| Data | Source | Description |
|------|--------|-------------|
| Home Bets | `config/app_data.json` | Bookmaker configurations |
| Home Bet Games | `config/app_data.json` | Game configurations per bookmaker |
| Bot Configurations | `custom_bots/*.bot` | Encrypted bot strategy files |
| User Settings | `conf.ini` | User preferences |

### External Connections

The only external connections made by this version are:

1. **Bookmaker Websites**: Via Playwright browser automation for placing bets
2. **No Backend API**: This version does not require or use any backend server

---

## Build and Development

### Development Setup

```bash
# Clone repository
git clone <repository-url>
cd crashbot

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Running the Application

```bash
# Using Make
make run

# Or directly
python crashbot.py
```

### UI Generation

Qt Designer files are located in `apps/gui/resources/ui/`. Generate Python code:

```bash
make generate-ui-app          # Main window
make generate-ui-login        # Login window
make generate-ui-parameters   # Parameter settings
make generate-ui-console      # Console window
make generate-ui-configurations  # Config window
make generate-ui-config-bot   # Bot configuration
```

### Building Executable

```bash
make generate-installer
# Uses PyInstaller to create standalone executable
```

### Translation Compilation

```bash
make translate
# Compiles .po files to .mo in locales/
```

---

## Code Quality Standards

### Formatting

- **Black**: Line length 79 characters
- **isort**: Import sorting

```bash
make black
```

### Pre-commit Hooks

The project uses pre-commit hooks for:

- Black formatting
- Flake8 linting (ignores W503, F405, TYP001)
- isort import ordering
- Safety vulnerability scanning

### Excluded Files

Files matching `*_designer.py` are auto-generated by pyuic6 and excluded from quality checks.

### Code Style Guidelines

1. **Type Hints**: Use type hints for function parameters and return values
2. **Docstrings**: Document public methods and classes
3. **Naming**:
   - Classes: PascalCase
   - Functions/methods: snake_case
   - Constants: UPPER_SNAKE_CASE
4. **Imports**: Group by standard library, third-party, internal

```python
# Standard Library
import os
from typing import Optional

# Libraries
from PyQt6.QtWidgets import QWidget

# Internal
from apps.globals import GlobalVars
```

---

## Appendix

### Design Patterns Used

1. **Singleton**: GlobalVars, Config, LocalStorage, LogsDBHandler, LocalDataLoader
2. **Factory**: ConfigurationFactory for game/bot registration
3. **Abstract Base Classes**: BotBase, GameBase, AbstractCrashGameBase
4. **Observer**: SocketIO events, PyQt6 signals/slots
5. **Strategy**: BotStrategy, GameStrategy for interchangeable algorithms

### Error Handling

```python
# GUI exceptions logged and displayed
try:
    # operation
except Exception as e:
    logs_services.save_gui_log(
        message=f"Error: {e}", level="exception"
    )
    SendEventToGUI.exception(str(e))
```

### Thread Safety

- WebSocket server runs in background thread
- GUI updates via PyQt6 signal-slot mechanism
- `QMetaObject.invokeMethod` for cross-thread calls

---

**Document Version:** 1.0.0
**CrashBot Version:** 2.0.0
