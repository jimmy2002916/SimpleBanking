# Simple Banking System

A Python-based banking system for managing accounts and transactions.

## Features

### Basic Features
1. Create bank accounts with a name and starting balance
2. Deposit money to accounts
3. Withdraw money from accounts
4. Prevent overdrafting accounts
5. Transfer money between accounts in the same banking system
6. Save and load system state to CSV

### Advanced Features
- **[Transaction Management](docs/transaction_atomicity.md)**: Ensures atomicity and thread safety
- **[Transaction Logging](docs/logging_scalability.md)**: Logs all banking operations
- **[Database Storage](docs/database_storage.md)**: Optional SQLite storage (`-DStorage sqlite`)

## Usage

### Prerequisites
- Python 3.6 or higher
- No external dependencies required for basic functionality
- SQLite3 (included in Python standard library) for database storage

### Installation
1. Clone the repository:
   ```
   git clone https://github.com/yourusername/SimpleBanking.git
   cd SimpleBanking
   ```

2. No additional installation steps required - the system uses only Python standard libraries.

### Running the Application

#### Basic Usage with CSV Storage (Default)
```
python main.py
```

#### Using SQLite Storage
```
python main.py -DStorage sqlite -DStoragePath data/banking.db
```

### Using Docker

#### Prerequisites
- Docker installed on your system ([Get Docker](https://docs.docker.com/get-docker/))

#### Building the Docker Image
1. Navigate to the SimpleBanking directory (where the Dockerfile is located):
   ```
   cd /path/to/SimpleBanking
   ```

2. Build the Docker image:
   ```
   docker build -t simple-banking .
   ```

#### Running with Docker
All commands below should be run from the SimpleBanking directory:

1. Run with default CSV storage (Data will be lost when container is removed):
   ```
   docker run -it --name banking-app simple-banking
   ```

2. Run with SQLite storage (Data will be lost when container is removed):
   ```
   docker run -it --name banking-app simple-banking -DStorage sqlite
   ```

3. Run with persistent data storage (✅ RECOMMENDED):
   ```
   docker run -it -v $(pwd)/data:/app/data --name banking-app simple-banking
   ```

4. Run with both persistent data and specific storage type (RECOMMENDED):
   ```
   docker run -it -v $(pwd)/data:/app/data --name banking-app simple-banking -DStorage sqlite -DStoragePath data/banking.db
   ```

#### Important: Saving Your Data

When using Docker, follow these steps to ensure your data is saved:

1. **Always use volume mounting** (`-v $(pwd)/data:/app/data`) to persist your data
2. **Save system state before exiting** by selecting option 6 (Save system state) or option 9 (Exit) from the menu
3. **Use the same container name** when restarting to maintain your container state:
   ```
   docker start -i banking-app
   ```

If you don't follow these steps, your account data will be lost when the container stops!

#### Managing Docker Containers

1. Stop the container:
   ```
   docker stop banking-app
   ```

2. Restart an existing container (preserves container state):
   ```
   docker start -i banking-app
   ```

3. Remove the container (This will delete container state):
   ```
   docker rm banking-app
   ```

### Command-Line Options
- `-DStorage`: Storage type to use (`csv` or `sqlite`). Default is `csv`.
- `-DStoragePath`: Path to the storage file. If not provided, defaults to:
  - `data/banking_data.csv` for CSV storage
  - `data/banking.db` for SQLite storage

### Interactive Menu
Once running, the application presents an interactive menu:
1. Create a new account
2. Deposit money
3. Withdraw money
4. Transfer money
5. View account details
6. Save system state
7. Load system state
8. View transaction logs
9. Exit

Enter the number corresponding to the desired action and follow the prompts.

## Testing

The SimpleBanking system includes a comprehensive test suite to ensure all functionality works correctly.

### Prerequisites
- Python 3.6 or higher
- pytest (included in requirements.txt)

### Installing Test Dependencies
```
pip install -r requirements.txt
```

### Running Tests

#### Run All Tests
```
python -m pytest
```

#### Run Tests with Verbose Output
```
python -m pytest -v
```

#### Run Specific Test Modules
```
# Run basic features tests
python -m pytest tests/basic_required_features/

# Run advanced features tests
python -m pytest tests/advanced_features/
```

#### Run Specific Test Cases
```
# Run data quality tests
python -m pytest tests/basic_required_features/test_data_quality.py

# Run specific test method
python -m pytest tests/basic_required_features/test_data_quality.py::TestDataQuality::test_data_validation
```

#### Run Tests with Coverage Report
```
python -m pytest --cov=basic_required_features --cov=advanced_features
```

### Test Structure
- `tests/basic_required_features/`: Tests for core banking functionality
- `tests/advanced_features/`: Tests for enhanced features like transaction management and storage

## Project Structure

The project follows a modular architecture organized by functional domains:
- `basic_required_features/`: Core banking functionality
- `advanced_features/`: Enhanced functionality modules
- `facade/`: Simplified interface layer
- `tests/`: Comprehensive test suite
- `docs/`: Detailed documentation

## Documentation

The `docs/` directory contains detailed documentation on various aspects of the system:

- **[Transaction Atomicity](docs/transaction_atomicity.md)**: How the system ensures operations complete fully or not at all
- **[Logging Scalability](docs/logging_scalability.md)**: How the logging system scales for big data applications
- **[Database Storage](docs/database_storage.md)**: Details on the SQLite storage implementation

## Future Work

The following enhancements are planned for future development:

1. **User Authentication**: Implement secure login and user management
2. **Web Interface**: Develop a web-based frontend using Flask or Django
3. **Mobile App**: Develop mobile applications for iOS and Android
4. **API Service**: Create a RESTful API for third-party integrations
5. **Distributed Storage**: Support for distributed database systems
6. **Notifications**: Email and SMS alerts for account activities
7. **Backup and Recovery**: Advanced data backup and disaster recovery features
