import re
from typing import List
from .Table import Table

class GoCodeGenerator:
    """
    Generates Go code based on the parsed Table objects.
    """
    def __init__(self, tables: List[Table]):
        self.tables = tables
        self.imports: set = set()
        self.imports.add('"errors"')

    def generate_structs(self) -> str:
        """
        Generates Go structs for all tables.
        """
        structs = []
        for table in self.tables:
            struct_lines = [f"type {table.name} struct " + "{"]
            for col in table.columns:
                # Convert column name to CamelCase
                field_name = ''.join(word.capitalize() for word in re.split('_| ', col.name))
                struct_lines.append(f"\t{field_name} {col.go_type} `json:\"{col.json_tag}\"`")
            struct_lines.append("}\n")
            structs.append('\n'.join(struct_lines))
        return '\n'.join(structs)

    def find_imports(self):
        """
        Collect necessary imports
        """
        for table in self.tables:
            for col in table.columns:
                if col.needs_sql:
                    self.imports.add('"database/sql"')
                if col.needs_time:
                    self.imports.add('"time"')

    def generate_repo_structs(self) -> str:
        """
        Generates Repo structs and their constructors for all tables.
        """
        repos = []
        for table in self.tables:
            repo_name = f"Repo{table.name}"
            constructor_name = f"NewRepo{table.name}"

            repo_lines = [f"type {repo_name} struct " + "{"]
            repo_lines.append("\tDB *sql.DB")
            repo_lines.append("}\n")

            # Constructor function
            repo_lines.append(f"// {constructor_name} creates a new repository for {table.name}.")
            repo_lines.append(f"func {constructor_name}(db *sql.DB) *{repo_name} " + "{")
            repo_lines.append(f"\treturn &{repo_name}{{DB: db}}")
            repo_lines.append("}\n")

            repos.append('\n'.join(repo_lines))
        return '\n'.join(repos)

    def generate_crud_methods(self) -> str:
        """
        Generates CRUD methods for all Repo structs.
        """
        methods = []
        for table in self.tables:
            repo_name = f"Repo{table.name}"
            struct_name = table.name
            pk = table.primary_key
            pk_name = pk.name
            pk_field = ''.join(word.capitalize() for word in re.split('_| ', pk.name))
            pk_type = pk.go_type

            # Prepare column lists for SQL queries
            insert_columns = [col for col in table.columns if col.name != pk_name]  # Assuming PK is auto-increment
            insert_fields = ', '.join([col.name for col in insert_columns])
            insert_placeholders = ', '.join([f"@{col.name}" for col in insert_columns])
            insert_struct_fields = ', '.join([
                f"sql.Named(\"{col.name}\", {struct_name.lower()}.{''.join(word.capitalize() for word in re.split('_| ', col.name))})"
                for col in insert_columns
            ])

            update_columns = [col for col in table.columns if col.name != pk_name]
            update_setters = ', '.join([f"{col.name} = @{col.name}" for col in update_columns])
            update_struct_fields = ', '.join([
                f"sql.Named(\"{col.name}\", {struct_name.lower()}.{''.join(word.capitalize() for word in re.split('_| ', col.name))})"
                for col in update_columns
            ] + [f"sql.Named(\"{pk_name}\", {struct_name.lower()}.{pk_field})"])

            search_fields = [col.name for col in table.columns]
            search_columns = ', '.join(search_fields)
            search_struct_fields = ', '.join([
                f"&{struct_name.lower()}.{''.join(word.capitalize() for word in re.split('_| ', col.name))}"
                for col in table.columns
            ])

            # Insert Method
            insert_method = f"""// Insert a new {struct_name} into the database.
func (repo *{repo_name}) Insert({struct_name.lower()} *{struct_name}) error {{
\tvar count int
\terr := repo.DB.QueryRow("SELECT COUNT(*) FROM {table.name} WHERE {pk_field} = @{pk_field}", sql.Named("{pk_field}", {struct_name.lower()}.{pk_field})).Scan(&count)
\tif err != nil {{
\t\treturn err
\t}}

\tif count == 0 {{
\t\tquery := "INSERT INTO {table.name} ({insert_fields}) VALUES ({insert_placeholders})"
\t\tstmt, err := repo.DB.Prepare(query)
\t\tif err != nil {{
\t\t\treturn err
\t\t}}
\t\tdefer stmt.Close()

\t\t_, err = stmt.Exec({insert_struct_fields})
\t\tif err != nil {{
\t\t\treturn err
\t\t}}
\t}}
\treturn nil
}}

"""
            methods.append(insert_method)

            # Update Method
            update_method = f"""// Update an existing {struct_name} in the database.
func (repo *{repo_name}) Update({struct_name.lower()} *{struct_name}) error {{
\tquery := "UPDATE {table.name} SET {update_setters} WHERE {pk_name} = @{pk_name}"
\tstmt, err := repo.DB.Prepare(query)
\tif err != nil {{
\t\treturn err
\t}}
\tdefer stmt.Close()

\t_, err = stmt.Exec({update_struct_fields})
\tif err != nil {{
\t\treturn err
\t}}

\treturn nil
}}

"""
            methods.append(update_method)

            # GetByID Method
            get_method = f"""// retrieves {struct_name} from the database by its primary key.
func (repo *{repo_name}) Get{struct_name}ByID(id {pk_type}) (*{struct_name}, error) {{
\tquery := "SELECT {search_columns} FROM {table.name} WHERE {pk_name} = @{pk_name}"
\trow := repo.DB.QueryRow(query, sql.Named("{pk_name}", id))

\tvar {struct_name.lower()} {struct_name}
\terr := row.Scan({search_struct_fields})
\tif err != nil {{
\t\treturn nil, err
\t}}

\treturn &{struct_name.lower()}, nil
}}

"""
            methods.append(get_method)

            # Delete Method
            delete_method = f"""// Delete {struct_name} from the database by its primary key.
func (repo *{repo_name}) Delete({pk_field} {pk_type}) error {{
\tresult, err := repo.DB.Exec("DELETE FROM {table.name} WHERE {pk_name} = @{pk_name}", sql.Named("{pk_name}", {pk_field}))

\tif err != nil {{
\t\treturn err
\t}}
\trowsAffected, _ := result.RowsAffected()

\tif rowsAffected == 0{{
\t\treturn errors.New("item not found")
\t}}
\treturn nil
}}

"""
            methods.append(delete_method)

        return '\n'.join(methods)

    def generate_code(self) -> str:
        """
        Generates the complete Go code.
        """
        code_sections = []

        # Package declaration
        code_sections.append("package repository\n")

        self.find_imports()

        # Imports
        if self.imports:
            import_section = "import (\n"
            for imp in sorted(self.imports):
                import_section += f"\t{imp}\n"
            import_section += ")\n"
            code_sections.append(import_section)

        # Structs
        structs = self.generate_structs()
        code_sections.append(structs)

        # Repo Structs
        repos = self.generate_repo_structs()
        code_sections.append(repos)

        # CRUD Methods
        crud_methods = self.generate_crud_methods()
        code_sections.append(crud_methods)

        return '\n'.join(code_sections)
