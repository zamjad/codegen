import re
from typing import List
from .Table import Table
from .Column import Column

class SQLParser:
    """
    Parses SQL CREATE TABLE statements and constructs Table objects.
    """
    CREATE_TABLE_REGEX = re.compile(
        r'CREATE\sTABLE\s+(\w+)\s*\((.*?)\);',
        re.IGNORECASE | re.DOTALL
    )

    COLUMN_REGEX = re.compile(
        r'(\w+)\s+([A-Z]+(?:\(\d+(?:,\s*\d+)?\))?)\s*(NOT NULL|NULL)?\s*(PRIMARY KEY)?',
        re.IGNORECASE
    )

    def __init__(self, sql_script: str):
        self.sql_script = sql_script
        self.tables: List[Table] = []

    def parse(self):
        """
        Parses the SQL script and populates the tables list.
        """
        create_table_statements = self.CREATE_TABLE_REGEX.findall(self.sql_script)
        if not create_table_statements:
            raise ValueError("No CREATE TABLE statements found in the input SQL.")

        for table_match in create_table_statements:
            table_name, columns_str = table_match
            table = Table(table_name)
            columns = self.COLUMN_REGEX.findall(columns_str)
            if not columns:
                raise ValueError(f"No columns found for table '{table_name}'.")

            for col in columns:
                name, sql_type, nullability, pk = col
                is_nullable = True  # Default to nullable
                if nullability:
                    if nullability.strip().upper() == 'NOT NULL':
                        is_nullable = False
                    elif nullability.strip().upper() == 'NULL':
                        is_nullable = True

                is_primary_key = bool(pk and pk.strip().upper() == 'PRIMARY KEY')
                column = Column(name, sql_type, is_nullable, is_primary_key)
                table.add_column(column)

            # Infer primary key if not explicitly defined
            table.infer_primary_key()
            if not table.primary_key:
                raise ValueError(f"Primary key not found or could not be inferred in table '{table_name}'.")

            self.tables.append(table)
