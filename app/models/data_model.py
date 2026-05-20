import pandas as pd
from pathlib import Path
from datetime import datetime
import pyarrow.parquet as pq


class DataModel:
    def __init__(self):
        self.columns = ['Plan de trabajo', 'Descripción', 'Activo Principal', 'Estado Plan Trab', 'Clasificación', 'Fecha-Hora Inicio', 'Fecha-Hora Final', 'Observaciones de ops']
        self.reset_columns()

        self.backup_folder =  Path(r'app\resources\backup')

        if not self.backup_folder.exists():
            self.backup_folder.mkdir(parents=True, exist_ok=True)

        
    def add_element_to_data(self, new_data: dict[str, str]):
        new_row_df = pd.DataFrame([new_data]) 
        self.current_data = pd.concat([self.current_data, new_row_df], ignore_index=True)

    def get_data(self):
        return self.current_data.set_index('Plan de trabajo')
    
    def reset_columns(self):
        self.current_data = pd.DataFrame(columns = self.columns)

    # --- Backup methods ---------
    def recover_backup(self):   #TODO: Change it to recover by path
        try:
            self.current_data = pd.read_parquet(self.data_backup_path)

            print(f"🔄️  Data backup successfuly recovered")

        except Exception as e:
            print(f"‼️  An error occurred while reading data backup | {e}")
            return None
        
    def reassign_backup_path(self, backup_name: str):
        self.data_backup_path = self.backup_folder / (backup_name + '.parquet')
        
    def generate_backup(self, by_error = False):

        timestamp = datetime.now().strftime("%d-%m-%Y %H..%M..%S")

        self.data_backup_path = self.backup_folder / f'Data {timestamp}{' (No completado)' if by_error else ''}.parquet'
        self.current_data.to_parquet(str(self.data_backup_path), engine='pyarrow', compression='snappy')

        print(f"🔄️  Data backup created and saved\n")

    def write_date_in_backup_metadata(self, datetime_input: tuple):
        datetime_input: str = f'{datetime_input[0]}|{datetime_input[1]}'

        table = pq.read_table(self.data_backup_path)
        existing_meta = table.schema.metadata or {}

        new_metadata = {b'datetimes': datetime_input.encode('utf-8')}
        merged_metadata = {**existing_meta, **new_metadata}
        new_table = table.replace_schema_metadata(merged_metadata)

        print(f'🔎  datetime_input: {datetime_input}')

        pq.write_table(new_table, self.data_backup_path)

    def read_dates_in_backup_metadata(self):
        table = pq.read_table(self.data_backup_path)

        existing_meta: dict[bytes, bytes] = table.schema.metadata or {}

        datetime_input: str = existing_meta[b'datetimes'].decode('utf-8')

        return tuple(datetime_input.split('|'))

    def check_backup_existence(self):
        if any(self.backup_folder.glob('*.parquet')):
            print(f"🧵  Complete data backup files found\n")
            return True
        else:
            print(f"🧵  Complete data backup files not found\n")
            return False
        
    def delete_backup(self):
        files_to_delete = list(self.backup_folder.glob('*.parquet'))
    
        if files_to_delete:
            # Iterate over the list of Path objects and delete each one
            for file_path in files_to_delete:
                try:
                    file_path.unlink() # The .unlink() method is used to delete a file
                    print(f"🚮  Data backup deleted: {file_path}")
                except OSError as e:
                    print(f"‼️  Error deleting data backup in {file_path} | {e}")

    def get_backup_references(self, only_names = False):
        print(f'💼  Getting the data backup file names {'and their paths' if not only_names else ''}')

        data_backup_files = self.backup_folder.rglob('*.parquet')
        data_backup_files = {f.stem:f for f in data_backup_files if f.is_file()}

        print(f'💼✅  Data backup file names obtained')
        
        if only_names:
            return data_backup_files.keys()
        else:
            return data_backup_files