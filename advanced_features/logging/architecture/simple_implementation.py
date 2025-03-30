"""
Simple Implementation of Logging Architecture

This module provides a simple implementation of the logging architecture interfaces
that can be used immediately while allowing for future scalability to enterprise solutions.
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from decimal import Decimal

from .interfaces import (
    LogEntry, ILogProducer, ILogProcessor, 
    ILogConsumer, ILogEnricher, ILogRouter
)


class JsonEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles Decimal objects."""
    
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)


class SimpleLogProcessor(ILogProcessor):
    """
    A simple implementation of ILogProcessor that enriches logs with
    basic information and forwards them to consumers.
    """
    
    def __init__(self):
        """Initialize the processor with an empty list of consumers."""
        self.consumers = []
    
    def process(self, log_entry: LogEntry) -> LogEntry:
        """
        Process a log entry by enriching it with basic information.
        
        Args:
            log_entry: The log entry to process
            
        Returns:
            The processed log entry
        """
        # Add processing timestamp if not present
        if 'processing_timestamp' not in log_entry.data:
            log_entry.set_value('processing_timestamp', datetime.now().isoformat())
        
        # Add log level if not present
        if 'log_level' not in log_entry.data:
            log_entry.set_value('log_level', 'INFO')
        
        return log_entry
    
    def attach_consumer(self, consumer: ILogConsumer) -> None:
        """
        Attach a log consumer to this processor.
        
        Args:
            consumer: The log consumer to attach
        """
        if consumer not in self.consumers:
            self.consumers.append(consumer)
    
    def detach_consumer(self, consumer: ILogConsumer) -> None:
        """
        Detach a log consumer from this processor.
        
        Args:
            consumer: The log consumer to detach
        """
        if consumer in self.consumers:
            self.consumers.remove(consumer)
    
    def forward_to_consumers(self, log_entry: LogEntry) -> None:
        """
        Forward a processed log entry to all attached consumers.
        
        Args:
            log_entry: The processed log entry to forward
        """
        for consumer in self.consumers:
            consumer.consume(log_entry)


class FileLogConsumer(ILogConsumer):
    """
    A simple implementation of ILogConsumer that stores logs in a file.
    This is similar to our current implementation but follows the new interface.
    """
    
    def __init__(self, log_file: str):
        """
        Initialize the consumer with a log file.
        
        Args:
            log_file: Path to the log file
        """
        self.log_file = log_file
        
        # Create directory for log file if it doesn't exist
        directory = os.path.dirname(log_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
    
    def consume(self, log_entry: LogEntry) -> bool:
        """
        Consume a log entry by writing it to the log file.
        
        Args:
            log_entry: The log entry to consume
            
        Returns:
            True if consumption was successful, False otherwise
        """
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry.data, cls=JsonEncoder) + "\n")
            return True
        except Exception as e:
            print(f"Error writing to log file: {e}")
            return False
    
    def query(self, filter_criteria: Dict[str, Any]) -> List[LogEntry]:
        """
        Query log entries based on filter criteria.
        
        Args:
            filter_criteria: Criteria to filter log entries
            
        Returns:
            List of matching log entries
        """
        if not os.path.exists(self.log_file):
            return []
        
        matching_entries = []
        
        with open(self.log_file, 'r') as f:
            for line in f:
                try:
                    data = json.loads(line)
                    # Check if entry matches all filter criteria
                    if all(data.get(key) == value for key, value in filter_criteria.items()):
                        matching_entries.append(LogEntry(data))
                except json.JSONDecodeError:
                    continue
        
        return matching_entries


class TimestampEnricher(ILogEnricher):
    """
    A simple implementation of ILogEnricher that adds timestamps to log entries.
    """
    
    def enrich(self, log_entry: LogEntry) -> LogEntry:
        """
        Enrich a log entry with timestamp information.
        
        Args:
            log_entry: The log entry to enrich
            
        Returns:
            The enriched log entry
        """
        if 'timestamp' not in log_entry.data:
            log_entry.set_value('timestamp', datetime.now().isoformat())
        
        return log_entry


class SimpleLogRouter(ILogRouter):
    """
    A simple implementation of ILogRouter that routes logs based on action type.
    """
    
    def __init__(self):
        """Initialize the router with an empty dictionary of processors."""
        self.processors_by_action = {}
        self.default_processor = None
    
    def register_processor(self, action: str, processor: ILogProcessor) -> None:
        """
        Register a processor for a specific action.
        
        Args:
            action: The action to register for
            processor: The processor to handle logs for this action
        """
        self.processors_by_action[action] = processor
    
    def set_default_processor(self, processor: ILogProcessor) -> None:
        """
        Set the default processor for actions that don't have a specific processor.
        
        Args:
            processor: The default processor
        """
        self.default_processor = processor
    
    def route(self, log_entry: LogEntry) -> Optional[ILogProcessor]:
        """
        Route a log entry to the appropriate processor based on its action.
        
        Args:
            log_entry: The log entry to route
            
        Returns:
            The processor to handle the log entry, or None if no processor is found
        """
        action = log_entry.get_value('action')
        
        if action in self.processors_by_action:
            return self.processors_by_action[action]
        
        return self.default_processor


class BankingSystemLogProducer(ILogProducer):
    """
    An implementation of ILogProducer for the banking system.
    This serves as an adapter for our existing BankingSystem class.
    """
    
    def __init__(self):
        """Initialize the producer with an empty list of processors."""
        self.processors = []
    
    def attach_processor(self, processor: ILogProcessor) -> None:
        """
        Attach a log processor to this producer.
        
        Args:
            processor: The log processor to attach
        """
        if processor not in self.processors:
            self.processors.append(processor)
    
    def detach_processor(self, processor: ILogProcessor) -> None:
        """
        Detach a log processor from this producer.
        
        Args:
            processor: The log processor to detach
        """
        if processor in self.processors:
            self.processors.remove(processor)
    
    def notify_processors(self, log_entry: LogEntry) -> None:
        """
        Notify all attached processors about a new log entry.
        
        Args:
            log_entry: The log entry to process
        """
        for processor in self.processors:
            processed_entry = processor.process(log_entry)
            processor.forward_to_consumers(processed_entry)
    
    def create_log_entry(self, data: Dict[str, Any]) -> LogEntry:
        """
        Create a log entry from data and notify processors.
        
        Args:
            data: Data for the log entry
            
        Returns:
            The created log entry
        """
        log_entry = LogEntry(data)
        self.notify_processors(log_entry)
        return log_entry
