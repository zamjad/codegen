import re

# Mapping of SQL types to Go types for non-nullable fields
TYPE_MAPPING = {
    'IDENTITY': 'int',
    'BIT': 'bool',
    'INT': 'int',
    'BIGINT': 'int64',
    'VARCHAR': 'string',
    'NVARCHAR': 'string',
    'TEXT': 'string',
    'DATE': 'time.Time',
    'DATETIME': 'time.Time',
    'DECIMAL': 'float64',
    'BOOLEAN': 'bool',
    'FLOAT': 'float32',
    'DOUBLE': 'float64',
}

# Mapping of SQL types to Go sql.Null types for nullable fields
NULL_TYPE_MAPPING = {
    'IDENTITY': 'sql.NullInt32',
    'BIT': 'sql.NullBool',
    'INT': 'sql.NullInt32',
    'BIGINT': 'sql.NullInt64',
    'VARCHAR': 'sql.NullString',
    'NVARCHAR': 'sql.NullString',
    'TEXT': 'sql.NullString',
    'DATE': 'sql.NullTime',
    'DATETIME': 'sql.NullTime',
    'DECIMAL': 'sql.NullFloat64',
    'BOOLEAN': 'sql.NullBool',
    'FLOAT': 'sql.NullFloat32',
    'DOUBLE': 'sql.NullFloat64',
}

class Column:
    """
    Represents a single column in a table.
    """
    def __init__(self, name: str, sql_type: str, is_nullable: bool, is_primary_key: bool):
        self.name = name
        self.sql_type = sql_type.upper()
        self.is_nullable = is_nullable
        self.is_primary_key = is_primary_key
        self.go_type = self.determine_go_type()
        self.json_tag = self.name.lower()
        self.needs_sql = self.go_type.startswith('sql.')
        self.needs_time = self.go_type == 'time.Time'

    def determine_go_type(self) -> str:
        """
        Determines the Go type based on SQL type and nullability.
        """
        base_type_match = re.match(r'(\w+)', self.sql_type)
        base_type = base_type_match.group(1) if base_type_match else self.sql_type
        if self.is_nullable:
            return NULL_TYPE_MAPPING.get(base_type, 'sql.NullString')  # default to sql.NullString
        else:
            return TYPE_MAPPING.get(base_type, 'interface{}')  # default to interface{}
