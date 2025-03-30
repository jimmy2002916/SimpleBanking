"""
Test cases for the scalable logging architecture.

This module tests the enterprise-ready logging architecture components
to ensure they work correctly and can scale to enterprise solutions.
"""

import unittest
import os
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, Any, List

from advanced_features.logging.architecture.interfaces import (
    LogEntry, ILogProducer, ILogProcessor, ILogConsumer
)
from advanced_features.logging.architecture.simple_implementation import (
    SimpleLogProcessor, FileLogConsumer, TimestampEnricher,
    SimpleLogRouter, BankingSystemLogProducer
)
from advanced_features.logging.architecture.facade import LoggingFacade


class MockLogConsumer(ILogConsumer):
    """Mock log consumer for testing."""
    
    def __init__(self):
        """Initialize with empty logs."""
        self.logs = []
    
    def consume(self, log_entry: LogEntry) -> bool:
        """Store log entry in memory."""
        self.logs.append(log_entry)
        return True
    
    def query(self, filter_criteria: Dict[str, Any]) -> List[LogEntry]:
        """Query logs based on filter criteria."""
        return [
            log for log in self.logs
            if all(log.get_value(key) == value for key, value in filter_criteria.items())
        ]


class MockLogProcessor(ILogProcessor):
    """Mock log processor for testing."""
    
    def __init__(self):
        """Initialize with empty consumers list."""
        self.consumers = []
        self.processed_entries = []
    
    def process(self, log_entry: LogEntry) -> LogEntry:
        """Process log entry by adding a test field."""
        log_entry.set_value('processed_by', 'MockLogProcessor')
        self.processed_entries.append(log_entry)
        return log_entry
    
    def attach_consumer(self, consumer: ILogConsumer) -> None:
        """Attach a consumer."""
        if consumer not in self.consumers:
            self.consumers.append(consumer)
    
    def detach_consumer(self, consumer: ILogConsumer) -> None:
        """Detach a consumer."""
        if consumer in self.consumers:
            self.consumers.remove(consumer)
    
    def forward_to_consumers(self, log_entry: LogEntry) -> None:
        """Forward log entry to all consumers."""
        for consumer in self.consumers:
            consumer.consume(log_entry)


class TestLoggingArchitecture(unittest.TestCase):
    """Test cases for the logging architecture."""
    
    def setUp(self):
        """Set up test environment."""
        self.log_file = "test_architecture.log"
        # Clean up any existing log file
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def tearDown(self):
        """Clean up after tests."""
        if os.path.exists(self.log_file):
            os.remove(self.log_file)
    
    def test_log_entry(self):
        """Test LogEntry class."""
        # Create a log entry
        data = {
            "action": "test",
            "account_id": "ACC0001",
            "amount": Decimal("100.00")
        }
        entry = LogEntry(data)
        
        # Test get_value
        self.assertEqual(entry.get_value("action"), "test")
        self.assertEqual(entry.get_value("account_id"), "ACC0001")
        self.assertEqual(entry.get_value("amount"), Decimal("100.00"))
        self.assertIsNone(entry.get_value("non_existent"))
        self.assertEqual(entry.get_value("non_existent", "default"), "default")
        
        # Test set_value
        entry.set_value("status", "success")
        self.assertEqual(entry.get_value("status"), "success")
        
        # Test to_dict
        self.assertEqual(entry.to_dict(), {
            "action": "test",
            "account_id": "ACC0001",
            "amount": Decimal("100.00"),
            "status": "success"
        })
    
    def test_file_log_consumer(self):
        """Test FileLogConsumer class."""
        # Create a consumer
        consumer = FileLogConsumer(self.log_file)
        
        # Create and consume a log entry
        entry = LogEntry({
            "action": "test",
            "account_id": "ACC0001",
            "amount": "100.00",
            "timestamp": datetime.now().isoformat()
        })
        
        self.assertTrue(consumer.consume(entry))
        
        # Verify file was created and contains the entry
        self.assertTrue(os.path.exists(self.log_file))
        
        with open(self.log_file, 'r') as f:
            content = f.read().strip()
            data = json.loads(content)
            self.assertEqual(data["action"], "test")
            self.assertEqual(data["account_id"], "ACC0001")
            self.assertEqual(data["amount"], "100.00")
    
    def test_simple_log_processor(self):
        """Test SimpleLogProcessor class."""
        # Create processor and consumer
        processor = SimpleLogProcessor()
        consumer = MockLogConsumer()
        processor.attach_consumer(consumer)
        
        # Create and process a log entry
        entry = LogEntry({
            "action": "test",
            "account_id": "ACC0001"
        })
        
        processed_entry = processor.process(entry)
        self.assertTrue("processing_timestamp" in processed_entry.data)
        self.assertTrue("log_level" in processed_entry.data)
        
        # Forward to consumers
        processor.forward_to_consumers(processed_entry)
        
        # Verify consumer received the entry
        self.assertEqual(len(consumer.logs), 1)
        self.assertEqual(consumer.logs[0].get_value("action"), "test")
        
        # Test detaching consumer
        processor.detach_consumer(consumer)
        self.assertEqual(len(processor.consumers), 0)
    
    def test_timestamp_enricher(self):
        """Test TimestampEnricher class."""
        enricher = TimestampEnricher()
        
        # Create a log entry without timestamp
        entry = LogEntry({
            "action": "test",
            "account_id": "ACC0001"
        })
        
        # Enrich the entry
        enriched_entry = enricher.enrich(entry)
        
        # Verify timestamp was added
        self.assertTrue("timestamp" in enriched_entry.data)
        
        # Create a log entry with timestamp
        timestamp = "2023-01-01T12:00:00"
        entry_with_timestamp = LogEntry({
            "action": "test",
            "account_id": "ACC0001",
            "timestamp": timestamp
        })
        
        # Enrich the entry
        enriched_entry = enricher.enrich(entry_with_timestamp)
        
        # Verify timestamp was not changed
        self.assertEqual(enriched_entry.get_value("timestamp"), timestamp)
    
    def test_simple_log_router(self):
        """Test SimpleLogRouter class."""
        router = SimpleLogRouter()
        
        # Create processors
        deposit_processor = MockLogProcessor()
        withdraw_processor = MockLogProcessor()
        default_processor = MockLogProcessor()
        
        # Register processors
        router.register_processor("deposit", deposit_processor)
        router.register_processor("withdraw", withdraw_processor)
        router.set_default_processor(default_processor)
        
        # Create log entries
        deposit_entry = LogEntry({"action": "deposit", "account_id": "ACC0001"})
        withdraw_entry = LogEntry({"action": "withdraw", "account_id": "ACC0001"})
        transfer_entry = LogEntry({"action": "transfer", "account_id": "ACC0001"})
        
        # Route entries
        self.assertEqual(router.route(deposit_entry), deposit_processor)
        self.assertEqual(router.route(withdraw_entry), withdraw_processor)
        self.assertEqual(router.route(transfer_entry), default_processor)
    
    def test_banking_system_log_producer(self):
        """Test BankingSystemLogProducer class."""
        producer = BankingSystemLogProducer()
        processor = MockLogProcessor()
        
        # Attach processor
        producer.attach_processor(processor)
        
        # Create and notify about a log entry
        data = {
            "action": "test",
            "account_id": "ACC0001"
        }
        producer.create_log_entry(data)
        
        # Verify processor received the entry
        self.assertEqual(len(processor.processed_entries), 1)
        self.assertEqual(processor.processed_entries[0].get_value("action"), "test")
        
        # Test detaching processor
        producer.detach_processor(processor)
        self.assertEqual(len(producer.processors), 0)
    
    def test_logging_facade(self):
        """Test LoggingFacade class."""
        # Create facade
        facade = LoggingFacade(self.log_file)
        
        # Log a transaction
        facade.log_transaction({
            "action": "deposit",
            "account_id": "ACC0001",
            "amount": "100.00"
        })
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.log_file))
        
        # Log more transactions
        facade.log_transaction({
            "action": "withdraw",
            "account_id": "ACC0001",
            "amount": "50.00"
        })
        
        facade.log_transaction({
            "action": "transfer",
            "from_account_id": "ACC0001",
            "to_account_id": "ACC0002",
            "amount": "25.00"
        })
        
        # Test get_all_logs
        all_logs = facade.get_all_logs()
        self.assertEqual(len(all_logs), 3)
        
        # Test get_logs_by_account
        account_logs = facade.get_logs_by_account("ACC0001")
        self.assertEqual(len(account_logs), 3)
        
        # Test get_logs_by_action
        deposit_logs = facade.get_logs_by_action("deposit")
        self.assertEqual(len(deposit_logs), 1)
        self.assertEqual(deposit_logs[0]["action"], "deposit")
        
        withdraw_logs = facade.get_logs_by_action("withdraw")
        self.assertEqual(len(withdraw_logs), 1)
        self.assertEqual(withdraw_logs[0]["action"], "withdraw")
    
    def test_end_to_end_flow(self):
        """Test end-to-end logging flow."""
        # Create components
        producer = BankingSystemLogProducer()
        processor = SimpleLogProcessor()
        consumer = FileLogConsumer(self.log_file)
        
        # Connect components
        producer.attach_processor(processor)
        processor.attach_consumer(consumer)
        
        # Create and log entries
        producer.create_log_entry({
            "action": "deposit",
            "account_id": "ACC0001",
            "amount": "100.00",
            "status": "success"
        })
        
        producer.create_log_entry({
            "action": "withdraw",
            "account_id": "ACC0001",
            "amount": "50.00",
            "status": "success"
        })
        
        # Verify logs were written to file
        with open(self.log_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)
            
            deposit_log = json.loads(lines[0])
            self.assertEqual(deposit_log["action"], "deposit")
            self.assertEqual(deposit_log["account_id"], "ACC0001")
            
            withdraw_log = json.loads(lines[1])
            self.assertEqual(withdraw_log["action"], "withdraw")
            self.assertEqual(withdraw_log["account_id"], "ACC0001")


if __name__ == "__main__":
    unittest.main()
