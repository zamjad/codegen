from typing import List, Optional
from .Column import Column

class Table:
    """
    Represents a database table.
    """
    def __init__(self, name: str):
        self.name = name
        self.columns: List[Column] = []
        self.primary_key: Optional[Column] = None

    def add_column(self, column: Column):
        self.columns.append(column)
        if column.is_primary_key:
            self.primary_key = column

    def infer_primary_key(self):
        """
        Infers the primary key if not explicitly defined.
        """
        if not self.primary_key:
            for col in self.columns:
                if col.name.lower() == 'id' or col.name.lower().endswith('id'):
                    self.primary_key = col
                    break
