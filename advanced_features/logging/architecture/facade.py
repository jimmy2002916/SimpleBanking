"""
Logging Architecture Facade

This module provides a simple facade for the logging architecture,
making it easy to use while maintaining compatibility with the current implementation.
"""

import os
from typing import Dict, Any, List, Optional

from .interfaces import LogEntry
from .simple_implementation import (
    SimpleLogProcessor, FileLogConsumer, TimestampEnricher,
    SimpleLogRouter, BankingSystemLogProducer
)


class LoggingFacade:
    """
    A facade for the logging architecture that simplifies its usage
    while allowing for future scalability.
    """
    
    def __init__(self, log_file: str = "logs/transactions.log"):
        """
        Initialize the logging facade.
        
        Args:
            log_file: Path to the log file
        """
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
        """
        Log a transaction.
        
        Args:
            data: Transaction data
        """
        # Create log entry
        log_entry = LogEntry(data)
        
        # Enrich with timestamp
        log_entry = self.enricher.enrich(log_entry)
        
        # Send to producer
        self.producer.notify_processors(log_entry)
    
    def get_logs_by_criteria(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get logs that match the given criteria.
        
        Args:
            criteria: Filter criteria
            
        Returns:
            List of matching log entries as dictionaries
        """
        log_entries = self.consumer.query(criteria)
        return [entry.data for entry in log_entries]
    
    def get_logs_by_account(self, account_id: str) -> List[Dict[str, Any]]:
        """
        Get logs for a specific account.
        
        Args:
            account_id: ID of the account
            
        Returns:
            List of log entries for the account
        """
        # Query for exact account_id match
        logs = self.get_logs_by_criteria({"account_id": account_id})
        
        # Also query for from_account_id and to_account_id (for transfers)
        logs.extend(self.get_logs_by_criteria({"from_account_id": account_id}))
        logs.extend(self.get_logs_by_criteria({"to_account_id": account_id}))
        
        return logs
    
    def get_logs_by_action(self, action: str) -> List[Dict[str, Any]]:
        """
        Get logs for a specific action.
        
        Args:
            action: Type of action
            
        Returns:
            List of log entries for the action
        """
        return self.get_logs_by_criteria({"action": action})
    
    def get_all_logs(self) -> List[Dict[str, Any]]:
        """
        Get all logs.
        
        Returns:
            List of all log entries
        """
        # Empty criteria means match all
        return self.get_logs_by_criteria({})


# Create a singleton instance for easy access
default_logging_facade = LoggingFacade()
