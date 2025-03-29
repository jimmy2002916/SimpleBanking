# Simple Banking System

A Python-based banking system that allows users to manage accounts, perform transactions, and persist data.

## Project Overview

This project implements a banking system with both basic required features and advanced features (additional enhancements). The system follows the KISS (Keep It Simple, Stupid) principle while demonstrating good software design practices.

## Design Approach

The project uses the **Package-by-Feature** design pattern to clearly separate basic requirements from additional features:

```
SimpleBanking/
├── advanced/                 # Additional features implementation
├── basic_required_features/  # Required features implementation
└── tests/                    # Test suite organized by feature type
    ├── advanced/                 # Tests for additional features
    └── basic_required_features/  # Tests for required features
```

This design pattern was chosen because:
- It makes the separation between required and additional features immediately obvious
- It follows the KISS principle with a straightforward organization
- It allows for independent development and testing of features
- It provides clear boundaries between different parts of the system

## Features

### Basic Required Features

1. Users can create a new bank account with a name and starting balance
2. Users can deposit money to their accounts
3. Users can withdraw money from their accounts
4. Users are not allowed to overdraft their accounts
5. Users can transfer money to other accounts in the same banking system
6. Save and load system state to CSV

### Advanced Features (Additional)

1. **Multi-user Support**
   - Support for multiple users with different access levels
   - Account ownership and permissions

2. **Enhanced Storage Options**
   - Alternative storage formats (JSON, SQL)
   - Data migration between storage formats

3. **Security Features**
   - Transaction logging for audit purposes
   - Security validation for sensitive operations

4. **Analytics**
   - Account usage statistics
   - Transaction history and reporting

## Implementation Status

### Completed Features

All basic required features have been implemented and tested:

- Create bank accounts with name and starting balance
- Deposit money to accounts with validation
- Withdraw money with overdraft protection
- Transfer money between accounts
- CSV persistence for system state

### Next Steps

- Implement advanced features
- Create a command-line interface
- Add more comprehensive documentation

## Implementation Details

### Core Components

- **BankAccount**: Represents an individual bank account with balance and operations
- **BankingSystem**: Manages accounts and provides system-wide operations
- **Storage**: Handles data persistence across different formats

### Design Patterns Used

- **Package-by-Feature**: Main organizational pattern for project structure
- **Repository Pattern**: For data access abstraction
- **Service Layer**: For implementing business logic

## Getting Started

### Prerequisites

- Python 3.6 or higher

### Installation

1. Clone the repository
   ```
   git clone https://github.com/yourusername/SimpleBanking.git
   cd SimpleBanking
   ```

2. Set up a virtual environment (optional but recommended)
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies
   ```
   pip install -r requirements.txt
   ```

### Running the Application

```
python main.py
```

### Running Tests

```
python -m unittest discover tests
```

## Development Approach

This project follows Test-Driven Development (TDD):

1. Write tests that define the expected behavior
2. Implement the minimum code necessary to pass the tests
3. Refactor the code while maintaining test coverage

## Project Structure

```
SimpleBanking/
├── README.md                           # Project documentation
├── requirements.txt                    # Dependencies
├── main.py                             # Entry point
├── advanced/                           # Additional features module
│   ├── __init__.py
│   ├── logging.py                      # Transaction logging
│   ├── security.py                     # Security features
│   ├── analytics.py                    # User analytics
│   └── storage/                        # Alternative storage
│       ├── __init__.py
│       ├── json_storage.py             # JSON persistence
│       └── sql_storage.py              # SQL persistence
├── basic_required_features/            # Basic required features module
│   ├── __init__.py
│   ├── account.py                      # BankAccount class
│   ├── banking_system.py               # Core banking system
│   └── persistence.py                  # CSV storage
└── tests/                              # Test suite
    ├── __init__.py
    ├── advanced/                       # Tests for additional features
    │   ├── __init__.py
    │   └── test_advanced_features.py
    └── basic_required_features/        # Tests for basic required features
        ├── __init__.py
        └── test_basic_required_features.py
```

## Contributing

This is a demonstration project. Feel free to fork and extend it with your own features!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
