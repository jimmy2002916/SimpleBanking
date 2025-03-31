import os
from typing import Dict, Any, List, Optional

from .interfaces import LogEntry
from .simple_implementation import (
    SimpleLogProcessor, FileLogConsumer, TimestampEnricher,
    SimpleLogRouter, BankingSystemLogProducer
)


class LoggingFacade:

    
    def __init__(self, log_file: str = "logs/transactions.log"):
        # Create directory for log file if it doesn't exist
        directory = os.path.dirname(log_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Create components
        self.producer = BankingSystemLogProducer()
        self.processor = SimpleLogProcessor()
        self.consumer = FileLogConsumer(log_file)
        self.enricher = TimestampEnricher()
        self.router = SimpleLogRouter()
        
        # Connect components
        self.producer.attach_processor(self.processor)
        self.processor.attach_consumer(self.consumer)
        self.router.set_default_processor(self.processor)
    
    def log_transaction(self, data: Dict[str, Any]) -> None:
        # Create log entry
        log_entry = LogEntry(data)
        
        # Enrich with timestamp
        log_entry = self.enricher.enrich(log_entry)
        
        # Send to producer
        self.producer.notify_processors(log_entry)
    
    def get_logs_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        log_entries = self.consumer.query(criteria)
        return [entry.data for entry in log_entries]
    
    def get_logs_by_account(self, account_id: str) -> List[Dict[str, Any]]:
        # Query for exact account_id match
        logs = self.get_logs_by_criteria({"account_id": account_id})
        
        # Also query for from_account_id and to_account_id (for transfers)
        logs.extend(self.get_logs_by_criteria({"from_account_id": account_id}))
        logs.extend(self.get_logs_by_criteria({"to_account_id": account_id}))
        
        return logs
    
    def get_logs_by_action(self, action: str) -> List[Dict[str, Any]]:
        return self.get_logs_by_criteria({"action": action})
    
    def get_all_logs(self) -> List[Dict[str, Any]]:
        # Empty criteria means match all
        return self.get_logs_by_criteria({})


# Create a singleton instance for easy access
default_logging_facade = LoggingFacade()
