# CrashBot Architecture

This document provides a comprehensive overview of the CrashBot application architecture, including component relationships, data flows, and design patterns.

## Table of Contents

- [High-Level Architecture](#high-level-architecture)
- [Component Diagram](#component-diagram)
- [Data Flow Diagram](#data-flow-diagram)
- [Class Hierarchy](#class-hierarchy)
- [Sequence Diagrams](#sequence-diagrams)
- [Design Patterns](#design-patterns)

---

## High-Level Architecture

```mermaid
flowchart TB
    subgraph External["External Services"]
        API["Prediction API<br/>(ML Backend)"]
        Browser["Chromium Browser<br/>(Playwright)"]
        Bookmaker["Bookmaker Website<br/>(Aviator/ToTheMoon)"]
    end

    subgraph CrashBot["CrashBot Application"]
        subgraph EntryPoint["Entry Point"]
            Main["crashbot.py<br/>Application Bootstrap"]
        end

        subgraph Singletons["Singletons"]
            GlobalVars["GlobalVars<br/>(apps/globals.py)"]
            Config["Config<br/>(apps/config.py)"]
            PredictionModel["PredictionModel<br/>(apps/game/prediction_core.py)"]
            LocalStorage["LocalStorage<br/>(apps/utils/local_storage.py)"]
        end

        subgraph GUILayer["GUI Layer (PyQt6)"]
            GUIApp["GUI Application<br/>(apps/gui/app.py)"]
            Windows["Windows<br/>(Login, Console, Config)"]
            SocketIOClient["SocketIO Client<br/>(apps/gui/socket_io_client.py)"]
        end

        subgraph WSServerLayer["WebSocket Server Layer"]
            WSServer["SocketIO Server<br/>(apps/game/ws_server/server.py)"]
            WSEvents["Event Handlers<br/>(apps/game/ws_server/events.py)"]
        end

        subgraph GameLayer["Game Layer"]
            GameBase["GameBase<br/>(Abstract)"]
            GameAI["GameAI<br/>(AI-Enhanced Game)"]
        end

        subgraph BotLayer["Bot Layer"]
            BotBase["BotBase<br/>(Abstract)"]
            BotAI["BotAI<br/>(AI Betting Logic)"]
        end

        subgraph PredictionLayer["Prediction Layer"]
            PredictionCore["PredictionCore<br/>(Model Evaluation)"]
        end

        subgraph ScraperLayer["Scraper Layer (Playwright)"]
            AbstractCrashGame["AbstractCrashGameBase<br/>(Abstract)"]
            AviatorBase["AviatorBase<br/>(Aviator Scraper)"]
            ToTheMoon["ToTheMoonBase<br/>(ToTheMoon Scraper)"]
        end

        subgraph UtilsLayer["Utilities"]
            HTTP["HTTP Client"]
            SQLite["SQLite Engine"]
            Logs["Log Services"]
            Encryption["Security/Encryption"]
        end
    end

    Main --> GlobalVars
    Main --> WSServer
    Main --> GUIApp

    GUIApp --> Windows
    GUIApp --> SocketIOClient
    SocketIOClient <-->|"Events"| WSServer

    WSServer --> WSEvents
    WSEvents --> GameAI

    GameAI --> BotAI
    GameAI --> PredictionCore
    GameAI --> AviatorBase

    BotAI --> BotBase
    GameAI --> GameBase

    AviatorBase --> AbstractCrashGame
    ToTheMoon --> AbstractCrashGame

    AbstractCrashGame --> Browser
    Browser --> Bookmaker

    PredictionCore --> API

    GlobalVars --> Config
    GameAI --> GlobalVars
    BotAI --> GlobalVars

    style External fill:#f9f,stroke:#333,stroke-width:2px
    style CrashBot fill:#bbf,stroke:#333,stroke-width:2px
    style Singletons fill:#ffd,stroke:#333,stroke-width:1px
    style GUILayer fill:#dfd,stroke:#333,stroke-width:1px
    style WSServerLayer fill:#fdd,stroke:#333,stroke-width:1px
    style GameLayer fill:#ddf,stroke:#333,stroke-width:1px
    style BotLayer fill:#fdf,stroke:#333,stroke-width:1px
    style ScraperLayer fill:#dff,stroke:#333,stroke-width:1px
```

---

## Component Diagram

```mermaid
flowchart LR
    subgraph Frontend["Frontend (PyQt6)"]
        direction TB
        LoginWindow["Login Window"]
        ConsoleWindow["Console Window"]
        ConfigWindow["Config Window"]
        ParametersWindow["Parameters Window"]
        BotConfigWindow["Bot Config Window"]
    end

    subgraph Communication["Communication Layer"]
        direction TB
        SIOClient["SocketIO Client<br/>(QThread)"]
        SIOServer["SocketIO Server<br/>(ASGI/Uvicorn)"]
    end

    subgraph Backend["Backend Logic"]
        direction TB
        GameLogic["Game Logic<br/>(GameAI/GameBase)"]
        BotLogic["Bot Logic<br/>(BotAI/BotBase)"]
        Prediction["Prediction Core"]
    end

    subgraph Automation["Browser Automation"]
        direction TB
        Aviator["Aviator Scraper"]
        ToTheMoon["ToTheMoon Scraper"]
        BetControl["Bet Controls"]
    end

    subgraph Storage["Data Storage"]
        direction TB
        ConfigFile["conf.ini"]
        SQLiteDB["logs.db"]
        CustomBots[".bot files"]
    end

    Frontend <-->|"localhost:5000"| SIOClient
    SIOClient <-->|"WebSocket"| SIOServer
    SIOServer --> GameLogic
    GameLogic --> BotLogic
    GameLogic --> Prediction
    GameLogic --> Aviator
    GameLogic --> ToTheMoon
    Aviator --> BetControl
    ToTheMoon --> BetControl

    BotLogic --> ConfigFile
    GameLogic --> SQLiteDB
    GameLogic --> CustomBots
```

---

## Data Flow Diagram

```mermaid
flowchart TD
    subgraph UserActions["User Actions"]
        Start["Start Bot"]
        Stop["Stop/Close"]
        Config["Configure"]
        SetBet["Set Bet Amount"]
    end

    subgraph GUIEvents["GUI Events (SocketIO)"]
        StartBotEvent["START_BOT"]
        AutoPlayEvent["AUTO_PLAY"]
        CloseGameEvent["CLOSE_GAME"]
        SetAmountEvent["SET_MAX_AMOUNT_TO_BET"]
        LogEvent["LOG"]
        BalanceEvent["UPDATE_BALANCE"]
    end

    subgraph GameFlow["Game Flow"]
        InitGame["Initialize Game"]
        LoadMultipliers["Load Multipliers<br/>from Scraper"]
        WaitNextGame["Wait for Next Game"]
        GetPrediction["Request Prediction<br/>from API"]
        EvaluateBet["Bot Evaluates<br/>Betting Decision"]
        PlaceBet["Place Bet<br/>via Playwright"]
        WaitResult["Wait for<br/>Game Result"]
        UpdateBalance["Update Balance<br/>& Statistics"]
    end

    subgraph ExternalData["External Data"]
        PredictionAPI["Prediction API<br/>(ML Models)"]
        BookmakerSite["Bookmaker Website<br/>(Live Game Data)"]
    end

    Start --> StartBotEvent
    Stop --> CloseGameEvent
    Config --> SetAmountEvent
    SetBet --> SetAmountEvent

    StartBotEvent --> InitGame
    InitGame --> LoadMultipliers
    LoadMultipliers --> BookmakerSite
    LoadMultipliers --> WaitNextGame

    WaitNextGame --> GetPrediction
    GetPrediction --> PredictionAPI
    PredictionAPI -->|"Prediction Data"| EvaluateBet
    EvaluateBet -->|"Bets[]"| PlaceBet
    PlaceBet --> BookmakerSite
    PlaceBet --> WaitResult
    WaitResult -->|"Multiplier Result"| UpdateBalance
    UpdateBalance --> BalanceEvent
    UpdateBalance --> LogEvent
    UpdateBalance -->|"Loop"| WaitNextGame

    CloseGameEvent -->|"Stop Loop"| Stop
```

---

## Class Hierarchy

```mermaid
classDiagram
    direction TB

    class BotBase {
        <<abstract>>
        +BOT_NAME: str
        +RISK_FACTOR: float
        +MIN_MULTIPLIER_TO_BET: float
        +STOP_LOSS_PERCENTAGE: float
        +TAKE_PROFIT_PERCENTAGE: float
        +balance: float
        +bets: List~Bet~
        +initialize(balance, multipliers)
        +generate_bets(prediction_data)*
        +get_next_bet(prediction, multiplier_positions, auto_play)*
        +evaluate_bets(multiplier_result)
        +update_balance(balance)
        +in_stop_loss() bool
        +in_take_profit() bool
    }

    class BotAI {
        +generate_bets(prediction_data) List~Bet~
        +get_next_bet(prediction, multiplier_positions, auto_play) List~Bet~
    }

    class GameBase {
        <<abstract>>
        +BOT_NAME: str
        +home_bet: HomeBet
        +bot: BotBase
        +multipliers: List
        +bets: List~Bet~
        +initialize_bot(bot_name)*
        +get_next_bet()*
        +add_multiplier(multiplier)
        +run()
    }

    class GameAI {
        -_prediction_model: PredictionModel
        +initialize_bot(bot_name)
        +request_get_prediction() PredictionCore
        +get_next_bet() List~Bet~
    }

    class AbstractCrashGameBase {
        <<abstract>>
        +url: str
        +multipliers: List~float~
        +balance: int
        +minimum_bet: int
        +maximum_bet: int
        +open()*
        +close()*
        +read_balance()*
        +read_multipliers()*
        +bet(bets, use_auto_cash_out)*
        +wait_next_game()*
    }

    class AviatorBase {
        +open()
        +close()
        +read_balance() float
        +read_multipliers()
        +bet(bets, use_auto_cash_out)
        +wait_next_game()
    }

    class ToTheMoonBase {
        +open()
        +close()
        +read_balance() float
        +bet(bets)
    }

    class PredictionCore {
        +id: int
        +average_predictions_of_model: float
        +prediction_values: List
        +add_prediction(prediction, round, probability)
        +add_multiplier_result(multiplier)
        +get_prediction_value() int
        +get_category_percentage() float
    }

    class PredictionModel {
        <<singleton>>
        -__instance: PredictionModel
        +predictions: List
        +get_instance() PredictionModel
        +add_predictions(predictions)
        +evaluate_models(min_average)
        +get_best_prediction() PredictionCore
    }

    BotBase <|-- BotAI
    GameBase <|-- GameAI
    AbstractCrashGameBase <|-- AviatorBase
    AbstractCrashGameBase <|-- ToTheMoonBase

    GameAI --> BotAI : uses
    GameAI --> PredictionModel : uses
    GameAI --> AviatorBase : uses
    PredictionModel --> PredictionCore : manages
    BotAI --> PredictionCore : evaluates
```

---

## Sequence Diagrams

### Application Startup

```mermaid
sequenceDiagram
    participant Main as crashbot.py
    participant GV as GlobalVars
    participant CB as CustomBots
    participant WS as WebSocket Server
    participant GUI as PyQt6 GUI

    Main->>GV: init(base_path)
    GV->>GV: init_config()
    Main->>Main: setup_language()
    Main->>CB: read_custom_bots()
    CB-->>Main: custom_bots[]
    Main->>GV: set_bots(custom_bots)

    Main->>WS: Thread(run_server)
    activate WS
    WS-->>Main: Server Running (localhost:5000)

    Main->>GV: set_ws_client_backend_started(True)
    Main->>GUI: run_gui()
    activate GUI
    GUI-->>Main: GUI Running

    Note over Main,GUI: Application Running

    GUI->>Main: User closes app
    deactivate GUI
    Main->>WS: event.set()
    deactivate WS
    Main->>Main: Exit
```

### Betting Cycle

```mermaid
sequenceDiagram
    participant GUI as GUI Client
    participant WS as WS Server
    participant Game as GameAI
    participant Bot as BotAI
    participant Pred as PredictionCore
    participant API as Prediction API
    participant Scraper as Aviator Scraper
    participant Site as Bookmaker Site

    GUI->>WS: START_BOT(bot_name, home_bet_id)
    WS->>Game: start_bot_event()
    Game->>Scraper: open()
    Scraper->>Site: Navigate & Login
    Site-->>Scraper: Page Ready
    Scraper->>Site: read_multipliers()
    Site-->>Scraper: multipliers[]
    Game->>Bot: initialize(balance, multipliers)
    Game-->>WS: GAME_LOADED
    WS-->>GUI: Game Ready

    loop Betting Loop
        Game->>Scraper: wait_next_game()
        Scraper->>Site: Monitor game state
        Site-->>Scraper: Betting window open

        Game->>API: request_prediction(multipliers)
        API-->>Pred: predictions[]
        Pred->>Pred: evaluate_models()
        Pred-->>Game: best_prediction

        Game->>Bot: get_next_bet(prediction)
        Bot->>Bot: evaluate conditions
        Bot->>Bot: calculate bet amounts
        Bot-->>Game: bets[]

        alt Auto Play Enabled
            Game->>Scraper: bet(bets)
            Scraper->>Site: Place bets
            Site-->>Scraper: Bet confirmed
        else Manual Mode
            Game-->>WS: LOG(recommended bet)
            WS-->>GUI: Show recommendation
        end

        Scraper->>Site: Wait for result
        Site-->>Scraper: multiplier_result

        Game->>Bot: evaluate_bets(multiplier_result)
        Game->>Scraper: read_balance()
        Scraper-->>Game: new_balance
        Game->>Bot: update_balance(new_balance)
        Game-->>WS: UPDATE_BALANCE
        WS-->>GUI: Display balance
    end
```

---

## Design Patterns

### Pattern Overview

```mermaid
flowchart TB
    subgraph Singleton["Singleton Pattern"]
        direction LR
        GV["GlobalVars<br/>(Application State)"]
        CF["Config<br/>(Configuration)"]
        PM["PredictionModel<br/>(ML Model State)"]
        LS["LocalStorage<br/>(Persistent Storage)"]
    end

    subgraph Factory["Factory Pattern"]
        direction LR
        CF2["ConfigurationFactory<br/>(Game/Bot Registration)"]
        GT["GameType Enum"]
        BT["Bot Types"]
    end

    subgraph ABC["Abstract Base Classes"]
        direction LR
        BB["BotBase"]
        GB["GameBase"]
        ACGB["AbstractCrashGameBase"]
        ACB["AbstractControlBase"]
    end

    subgraph Observer["Observer Pattern (Events)"]
        direction LR
        SIO["SocketIO Events"]
        SIGE["SendEventToGUI"]
    end

    subgraph Strategy["Strategy Pattern"]
        direction LR
        BS["BotStrategy<br/>(Betting Strategies)"]
        GS["GameStrategy<br/>(Game Strategies)"]
    end

    Singleton --> Factory
    Factory --> ABC
    ABC --> Observer
    Observer --> Strategy
```

### Singleton Implementation

```mermaid
classDiagram
    class Singleton {
        <<metaclass>>
        -_instances: dict
        +__call__(cls, *args, **kwargs)
    }

    class GlobalVars {
        <<singleton>>
        +APP_NAME: str
        +APP_VERSION: str
        +SIO: AsyncServer
        +GAME: any
        +config: Config
        +init(base_path)$
        +get_game()$
        +set_game(game)$
        +emit_to_gui(event, data)$
    }

    class Config {
        <<singleton>>
        +API_URL: str
        +WS_SERVER_HOST: str
        +WS_SERVER_PORT: int
        +LANGUAGE: str
        +read_config()
        +write_config()
    }

    class PredictionModel {
        <<singleton>>
        -__instance: PredictionModel
        +predictions: List
        +get_instance()$
        +add_predictions(predictions)
        +get_best_prediction()
    }

    Singleton <.. GlobalVars : uses metaclass
    Singleton <.. Config : uses metaclass
    PredictionModel ..> PredictionModel : self-managed
```

---

## Directory Structure

```
crashbot/
+-- crashbot.py              # Entry point
+-- conf.ini                 # Configuration file
+-- apps/
|   +-- config.py            # Config singleton
|   +-- globals.py           # GlobalVars singleton
|   +-- constants.py         # Application constants
|   +-- ws_client.py         # WebSocket client (unused)
|   +-- api/                 # External API services
|   |   +-- services.py      # API request functions
|   |   +-- models.py        # API data models
|   +-- custom_bots/         # Custom bot loading
|   |   +-- services.py      # Bot file parsing
|   |   +-- handlers.py      # Bot handlers
|   +-- game/
|   |   +-- bots/
|   |   |   +-- bot_base.py  # Abstract bot class
|   |   |   +-- bot_ai.py    # AI betting bot
|   |   |   +-- bot_strategy.py
|   |   +-- games/
|   |   |   +-- game_base.py # Abstract game class
|   |   |   +-- game_ai.py   # AI-enhanced game
|   |   +-- ws_server/
|   |   |   +-- server.py    # SocketIO ASGI server
|   |   |   +-- events.py    # Event handlers
|   |   +-- prediction_core.py # ML model evaluation
|   |   +-- models.py        # Game data models
|   +-- gui/
|   |   +-- app.py           # PyQt6 application
|   |   +-- socket_io_client.py # SocketIO client thread
|   |   +-- gui_events.py    # GUI event helpers
|   |   +-- windows/         # PyQt6 window classes
|   +-- scrappers/
|   |   +-- game_base.py     # Abstract scraper class
|   |   +-- aviator/
|   |   |   +-- aviator_base.py    # Core Aviator automation
|   |   |   +-- aviator_*.py       # Bookmaker variants
|   |   |   +-- bet_control.py     # Bet control automation
|   |   +-- to_the_moon/
|   +-- utils/
|       +-- patterns/
|       |   +-- singleton.py # Singleton metaclass
|       |   +-- factory.py   # Factory pattern
|       +-- local_storage.py # Key-value storage
|       +-- sqlite_engine.py # SQLite wrapper
|       +-- logs/            # Logging services
+-- custom_bots/             # Encrypted .bot files
+-- locales/                 # i18n translations
+-- data/                    # Runtime data (logs.db)
```

---

## Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| GUI | PyQt6 + pyqtdarktheme | Desktop user interface |
| Communication | SocketIO (python-socketio) | Real-time GUI-backend messaging |
| Server | Uvicorn (ASGI) | WebSocket server hosting |
| Browser Automation | Playwright | Web scraping and betting automation |
| HTTP Client | requests/aiohttp | API communication |
| Database | SQLite | Local logging and storage |
| Configuration | INI files | User settings |
| Translations | gettext | Multi-language support (en/es) |

---

## Key Configuration

### conf.ini Settings

| Setting | Description | Default |
|---------|-------------|---------|
| `API_URL` | Prediction API endpoint | `http://localhost:8000` |
| `WS_SERVER_HOST` | Local WS server host | `localhost` |
| `WS_SERVER_PORT` | Local WS server port | `5000` |
| `LANGUAGE` | UI language (en/es) | `en` |
| `MAX_AMOUNT_HOME_BET_PERCENTAGE` | Max bet % of home bet limit | `0.5` |
| `MAX_AMOUNT_BALANCE_PERCENTAGE` | Max bet % of balance | `0.005` |
| `MIN_VALUE_TO_BULLISH_GAME` | Slope threshold for bullish detection | `0.26` |
| `LEN_WINDOW_TO_BULLISH_GAME` | Window size for trend analysis | `6` |

---

## Event Reference

### WebSocket Events (GUI <-> Server)

| Event | Direction | Description |
|-------|-----------|-------------|
| `LOGIN` | GUI -> Server | Authenticate user |
| `VERIFY` | GUI -> Server | Verify session |
| `START_BOT` | GUI -> Server | Start betting bot |
| `AUTO_PLAY` | Bidirectional | Toggle auto-betting |
| `CLOSE_GAME` | GUI -> Server | Stop bot and close browser |
| `SET_MAX_AMOUNT_TO_BET` | Bidirectional | Update bet amount |
| `LOG` | Server -> GUI | Send log message |
| `UPDATE_BALANCE` | Server -> GUI | Update balance display |
| `GAME_LOADED` | Server -> GUI | Game ready notification |
| `ERROR` | Server -> GUI | Error notification |
| `EXCEPTION` | Server -> GUI | Exception notification |
| `ADD_MULTIPLIERS` | Server -> GUI | Send multiplier history |
