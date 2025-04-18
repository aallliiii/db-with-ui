import os
import json
import shutil
import threading
from typing import List
from pathlib import Path
import logging
import pandas as pd

# --- Setup Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class TransactionError(Exception):
    """Base exception for transaction-related errors"""
    pass

class TransactionManager:
    def __init__(self, db_name: str):
        self.db_name = db_name
        self.transaction_log: List = []
        self.in_transaction: bool = False
        self.backup_dir = Path(f"Project_ADBMS/databases/{db_name}/_backup")
        self._lock = threading.Lock()
        
    def begin(self) -> None:
        """Begin a new transaction"""
        with self._lock:
            if self.in_transaction:
                raise TransactionError("⚠️ Transaction already in progress")
            
            logging.info("🔄 Transaction started")
            self.in_transaction = True
            self.transaction_log.clear()
            self._backup_database()

    def commit(self) -> None:
        """Commit the current transaction"""
        with self._lock:
            if not self.in_transaction:
                raise TransactionError("⚠️ No transaction to commit")
            
            logging.info("✅ Transaction committed")
            self.in_transaction = False
            self._clear_backup()

    def rollback(self) -> None:
        """Rollback the current transaction"""
        with self._lock:
            if not self.in_transaction:
                raise TransactionError("⚠️ No transaction to rollback")
            
            logging.info("🔁 Transaction rollback triggered")
            try:
                self._restore_backup()
                self.transaction_log.clear()
                self.in_transaction = False
                self._clear_backup()
                # self._reload_database_state()  
                logging.info("🧼 Rollback successful. Database restored.")
            except Exception as e:
                logging.error("❌ Rollback failed", exc_info=True)
                raise TransactionError("Rollback failed") from e

    def _backup_database(self) -> None:
        """Create backup of the database state"""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            db_path = Path(f"Project_ADBMS/databases/{self.db_name}")
            
            for item in db_path.iterdir():
                if item.suffix == ".csv" or item.name == "metadata.json":
                    shutil.copy2(item, self.backup_dir)
                    logging.debug(f"📦 Backed up: {item.name}")
            
            logging.info("📂 Backup completed")
        except (OSError, shutil.Error) as e:
            logging.error("❌ Backup failed", exc_info=True)
            raise TransactionError("Backup failed") from e

    def _restore_backup(self) -> None:
        """Restore database from backup"""
        try:
            db_path = Path(f"Project_ADBMS/databases/{self.db_name}")
            
            # Clear existing .csv and metadata.json
            for item in db_path.iterdir():
                if item.is_file() and (item.suffix == ".csv" or item.name == "metadata.json"):
                    item.unlink()
                    logging.debug(f"🗑️ Deleted: {item.name}")
            
            # Restore files from backup
            for item in self.backup_dir.iterdir():
                if item.is_file():
                    shutil.copy2(item, db_path)
                    logging.debug(f"♻️ Restored: {item.name}")
        except (OSError, shutil.Error) as e:
            logging.error("❌ Restore failed", exc_info=True)
            raise TransactionError("Restore failed") from e

    def _clear_backup(self) -> None:
        """Remove backup files"""
        try:
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)
                logging.info("🧹 Cleared backup folder")
        except OSError as e:
            logging.error("❌ Failed to clear backup", exc_info=True)
            raise TransactionError("Failed to clear backup") from e

    def status(self) -> str:
        """Return current transaction status"""
        return "Active" if self.in_transaction else "No active transaction"

    def __enter__(self):
        """Context manager entry"""
        self.begin()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - commit or rollback based on success"""
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()




    # def _reload_database_state(self):
    #     """Reload database state after rollback: rebuild tables, indexes from disk."""
    #     try:
    #         # Clear current state
    #         self.database.tables.clear()
    #         self.database.index_manager.indexes.clear()

    #         # Reload tables
    #         for file in os.listdir(f"Project_ADBMS/databases/{self.database.db_name}"):
    #             if file.endswith(".csv"):
    #                 table_name = file[:-4]  # Remove '.csv'
    #                 table_path = f"Project_ADBMS/databases/{self.database.db_name}/{file}"

    #                 df = pd.read_csv(table_path)
    #                 if df.empty:
    #                     continue

    #                 columns = list(df.columns)

    #                 # Optional: you may want to store column types and primary key info separately
    #                 # For now assuming you can retrieve them from somewhere (metadata)

    #                 # Rebuild table
    #                 table = Table(
    #                     table_name=table_name,
    #                     db_name=self.database.db_name,
    #                     columns=columns,
    #                     column_types=self.database.metadata_manager.get_column_types(table_name),
    #                     primary_key=self.database.metadata_manager.get_primary_key(table_name),
    #                     foreign_keys=self.database.metadata_manager.get_foreign_keys(table_name),
    #                     index_manager=self.database.index_manager
    #                 )
    #                 self.database.tables[table_name] = table

    #                 Rebuild primary key indexes
    #                 primary_key = table.primary_key
    #                 if primary_key:
    #                     for offset, pk_value in enumerate(df[primary_key].astype(str).values):
    #                         self.database.index_manager.add_primary_index(table_name, pk_value, offset)

    #         print("✅ Database state reloaded successfully after rollback.")

    #     except Exception as e:
    #         raise TransactionError("Failed to reload database state") from e

