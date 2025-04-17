from flask import Flask, render_template, request, redirect, url_for, flash
from Project_ADBMS.database_man import DatabaseManager
from Project_ADBMS.file_storage_manager import FileStorageManager
from Project_ADBMS.Index_Manager import IndexManager
from Project_ADBMS.transaction_manager import TransactionManager
import os
import shutil
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize the database manager
db_manager = DatabaseManager()

@app.context_processor
def inject_db_manager():
    """Make db_manager available to all templates"""
    return dict(db_manager=db_manager)

def get_db_path(db_name):
    """Helper function to get database path"""
    return os.path.join("Project_ADBMS", "databases", db_name)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/database', methods=['GET', 'POST'])
def database_operations():
    if request.method == 'POST':
        operation = request.form.get('operation')
        db_name = request.form.get('db_name', '').strip()
        
        if not db_name:
            flash("Database name cannot be empty!", 'error')
            return redirect(url_for('database_operations'))
        
        db_path = get_db_path(db_name)
        
        try:
            if operation == 'create':
                if not os.path.exists(db_path):
                    os.makedirs(db_path)
                    # Initialize metadata file
                    with open(os.path.join(db_path, "metadata.json"), 'w') as f:
                        json.dump({}, f)
                    flash(f"Database '{db_name}' created successfully!", 'success')
                    db_manager.db_name = db_name
                else:
                    flash(f"Database '{db_name}' already exists!", 'error')
                    
            elif operation == 'use':
                if os.path.exists(db_path):
                    db_manager.db_name = db_name
                    db_manager.index_manager = IndexManager()
                    db_manager.transaction_manager = TransactionManager(db_name)
                    flash(f"Using database '{db_name}'", 'info')
                    return redirect(url_for('index'))
                else:
                    flash(f"Database '{db_name}' doesn't exist!", 'error')
                    
            elif operation == 'delete':
                if os.path.exists(db_path):
                    shutil.rmtree(db_path)
                    flash(f"Database '{db_name}' deleted successfully!", 'success')
                    if db_manager.db_name == db_name:
                        db_manager.db_name = None
                else:
                    flash(f"Database '{db_name}' doesn't exist!", 'error')
                    
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
    
    return render_template('database.html')

@app.route('/tables', methods=['GET', 'POST'])
def table_operations():
    if not db_manager.db_name:
        return redirect(url_for('database_operations'))
    
    if request.method == 'POST':
        operation = request.form.get('operation')
        table_name = request.form.get('table_name', '').strip()
        
        if not table_name:
            flash("Table name cannot be empty!", 'error')
            return redirect(url_for('table_operations'))
        
        try:
            if operation == 'create':
                columns = request.form.get('columns', '').strip()
                primary_key = request.form.get('primary_key', '').strip()
                foreign_keys = request.form.get('foreign_keys', '').strip()
                
                # Process columns
                columns_dict = {}
                for col in columns.split(','):
                    col = col.strip()
                    if ':' in col:
                        name, col_type = col.split(':', 1)
                        columns_dict[name.strip()] = col_type.strip()
                
                # Process foreign keys
                fk_dict = {}
                if foreign_keys:
                    for fk in foreign_keys.split(','):
                        fk = fk.strip()
                        if ':' in fk:
                            col, ref = fk.split(':', 1)
                            if '(' in ref and ')' in ref:
                                ref_table = ref.split('(')[0].strip()
                                ref_col = ref.split('(')[1].replace(')', '').strip()
                                fk_dict[col.strip()] = (ref_table, ref_col)
                
                # Create the table
                table = FileStorageManager(
                    db_name=db_manager.db_name,
                    table_name=table_name,
                    index_manager=db_manager.index_manager,
                    columns=columns_dict,
                    primary_key=primary_key,
                    foreign_keys=fk_dict
                )
                flash(f"Table '{table_name}' created successfully!", 'success')
                
            elif operation == 'delete':
                table_path = os.path.join("Project_ADBMS", "databases", db_manager.db_name, f"{table_name}.csv")
                if os.path.exists(table_path):
                    os.remove(table_path)
                    # Update metadata
                    metadata_path = os.path.join("Project_ADBMS", "databases", db_manager.db_name, "metadata.json")
                    if os.path.exists(metadata_path):
                        with open(metadata_path, 'r') as f:
                            metadata = json.load(f)
                        if table_name in metadata:
                            del metadata[table_name]
                            with open(metadata_path, 'w') as f:
                                json.dump(metadata, f, indent=4)
                    flash(f"Table '{table_name}' deleted successfully!", 'success')
                else:
                    flash(f"Table '{table_name}' doesn't exist!", 'error')
                    
        except Exception as e:
            flash(f"Error: {str(e)}", 'error')
    
    return render_template('tables.html')
import pandas as pd
@app.route('/sql', methods=['GET', 'POST'])
def sql_interface():
    if not db_manager.db_name:
        return redirect(url_for('database_operations'))
    
    result = None
    columns = []
    rows = []
    message = None
    
    if request.method == 'POST':
        sql_query = request.form.get('sql_query', '').strip()
        if not sql_query:
            flash("SQL query cannot be empty!", 'error')
        else:
            try:
                # Execute the query
                
                result = db_manager.execute_sql(sql_query)
                print(db_manager.execute_sql(sql_query))
                
                # Handle different result types
                if isinstance(result, pd.DataFrame):
                    if not result.empty:
                        columns = list(result.columns)
                        rows = result.to_dict('records')
                        print(columns,rows)
                    else:
                        message = "Query executed successfully but returned no results"
                elif isinstance(result, str):
                    message = result
                elif result is None:
                    message = "Query executed successfully"
                else:
                    message = str(result)
                    
            except Exception as e:
                flash(f"Error executing query: {str(e)}", 'error')
                message = str(e)
    print(columns,rows)
    return render_template('sql.html', 
                         query=request.form.get('sql_query', ''),
                         columns=columns,
                         rows=rows,
                         message=message)

@app.route('/transaction', methods=['GET', 'POST'])
def transaction_management():
    if not db_manager.db_name:
        return redirect(url_for('database_operations'))
    
    status = "No active transaction"
    if hasattr(db_manager, 'transaction_manager') and db_manager.transaction_manager:
        status = db_manager.transaction_manager.status()
    
    if request.method == 'POST':
        operation = request.form.get('operation')
        try:
            if operation == 'begin':
                db_manager._begin_transaction_sql()
                flash("Transaction started", 'info')
            elif operation == 'commit':
                db_manager._commit_transaction_sql()
                flash("Transaction committed", 'success')
            elif operation == 'rollback':
                db_manager._rollback_transaction_sql()
                flash("Transaction rolled back", 'warning')
        except Exception as e:
            flash(str(e), 'error')
    
    return render_template('transaction.html', status=status)

if __name__ == '__main__':
    app.run(debug=True)