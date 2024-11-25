import argparse
import sys
from codegen import SQLParser, GoCodeGenerator

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Generate Go structs and CRUD methods from SQL CREATE TABLE statements.")
    parser.add_argument('-i', '--input', type=str, required=True, help="Input SQL file containing CREATE TABLE statements.")
    parser.add_argument('-o', '--output', type=str, required=True, help="Output file name for the generated Go code.")
    args = parser.parse_args()

    try:
        # Read SQL script from input file
        with open(args.input, 'r') as f:
            sql_script = f.read()

        # Parse SQL
        parser = SQLParser(sql_script)
        parser.parse()

        # Generate Go code
        generator = GoCodeGenerator(parser.tables)
        go_code = generator.generate_code()

        # Write the generated code to the specified output file
        with open(args.output, 'w') as f:
            f.write(go_code)

        print(f"Go code successfully generated and written to '{args.output}'")

    except ValueError as ve:
        print(f"Error: {ve}", file=sys.stderr)
        sys.exit(1)
    except IOError as ioe:
        print(f"IO Error: {ioe}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()