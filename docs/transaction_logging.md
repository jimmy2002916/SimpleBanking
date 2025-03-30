# Transaction Logging Feature

The transaction logging feature provides comprehensive audit trails for all banking operations in the Simple Banking System.

## Capabilities
- Logs all banking operations (deposits, withdrawals, transfers, account creation)
- Records transaction details including:
  - Transaction type/action
  - Account IDs involved
  - Amount
  - Status (success/failed)
  - Timestamp
  - Reason for failure (if applicable)

## Enterprise-Ready Logging Architecture

The system implements a scalable, enterprise-ready logging architecture that can evolve from a simple file-based implementation to a distributed system using technologies like Filebeat, Logstash, and Kafka.

### Architecture Overview

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────────────┐
│                 │     │                 │     │                         │
│  Log Producers  │────▶│  Log Pipeline   │────▶│  Log Storage/Consumers  │
│                 │     │                 │     │                         │
└─────────────────┘     └─────────────────┘     └─────────────────────────┘
   (Banking System)        (Processors)           (File, DB, Analytics)
```

### Enterprise Scalability

The architecture is designed to scale to enterprise-level solutions like those used by major financial institutions:

- **Current Implementation**: Simple file-based logging
- **Future Scalability**:
  - Kafka integration for distributed log processing
  - Logstash for log enrichment and transformation
  - Filebeat for log collection
  - Elasticsearch for search and analytics
  - WORM storage for regulatory compliance

### Package Structure and Class Relationships

The logging architecture is organized in a package structure that separates concerns and allows for future extensibility:

```
advanced_features/
└── logging/                      # Main logging package
    ├── __init__.py               # Package initialization
    ├── transaction_logger.py     # Client-facing API
    └── architecture/             # Enterprise architecture components
        ├── __init__.py           # Subpackage initialization
        ├── interfaces.py         # Core interfaces
        ├── simple_implementation.py  # Concrete implementations
        ├── facade.py             # Simplified interface
        └── enterprise_placeholders.py  # Future enterprise interfaces
```

## Data Flow

1. `BankingSystem` calls methods on `TransactionLogger`
2. `TransactionLogger` formats data and calls `LoggingFacade.log_transaction()`
3. `LoggingFacade` creates a `LogEntry` and sends it to the producer
4. The producer notifies attached processors
5. Processors enrich the log and forward to consumers
6. Consumers (currently `FileLogConsumer`) store the log

## Usage

Transaction logging is automatically enabled when you run the application. Logs are stored in the `logs/transactions.log` file.

You can view and analyze logs through the command-line interface:
1. Select option 8 from the main menu
2. Choose from the following options:
   - View all logs
   - View logs for a specific account
   - View logs by action type (deposit, withdraw, transfer, etc.)
