import json
from pathlib import Path
from datetime import datetime, timedelta

class ConfigModel:
    def __init__(self):
        self.backup_folder =  Path(r'app\resources\backup')

        self.config_folder =  Path(r'app\resources\config')
        self.json_path = self.config_folder / 'configurations.json'

        if not self.json_path.exists():
            self.config_folder.mkdir(parents=True, exist_ok=True)
            config_base = { #TODO: Pass it to a entity class
                "Usuario": "",
                "Contraseña": "",
                "Estado de plan de trabajo": "",
                "Subgerencias de transmisión": [""],
                "Incluir mes atrás": False,
                "Fecha inic. Plan Trab.": f"{datetime.now().strftime("%d.%m.%Y")}",
                "Fecha fin. Plan Trab.": f"{datetime.now().strftime("%d.%m.%Y")}",
                "Last base updating": "undefinite"
            }
            self.update_config(config_base)

        self.set_config(self.load_config_())

        if not self.backup_folder.exists():
            self.backup_folder.mkdir(parents=True, exist_ok=True)

    def get_config(self):
        print(f"🗃️  Config got:\n{self.current_config}\n")
        return self.current_config
    
    def get_last_updating_datetime(self):
        try:
            return self.current_config['Last base updating']
        except KeyError:
            return 'undefinite'
    
    def get_dates(self):
        return (self.current_config['Fecha inic. Plan Trab.'], self.current_config['Fecha fin. Plan Trab.'])

    def set_config(self, new_config: dict[str]):
        self.current_config = new_config
        print(f"🗄️  Config established:\n{new_config}\n")

    def load_config_(self):
        try:
            with open(self.json_path, 'r', encoding='utf-8') as file:
                data: dict = json.load(file)

            print(f"📂  Config loaded correctly:\n{data}\n")
            return data 

        except FileNotFoundError:
            print(f"‼️  Error: The file '{self.json_path}' was not found.\n")
        except json.JSONDecodeError:
            print(f"‼️  Error: Failed to decode JSON from the file.\n")

    def update_config(self, new_config: dict[str]):
        with open(self.json_path, 'w') as json_file:
            json.dump(new_config, json_file, indent=4) # The 'indent' parameter makes the file human-readable
        print(f"🗳️  Config updated correctly\n{new_config}\n")

    def update_last_update_datetime(self, new_datetime: str):
        current_backup = self.load_config_()
        current_backup['Last base updating'] = new_datetime
        with open(self.json_path, 'w') as json_file:
            json.dump(current_backup, json_file, indent=4)
        print(f"✅🗳️  Base updating datetime updated in config correctly\n")

    # --- Backup methods ---------

    def recover_backup(self):
        config_backup_files = self.backup_folder.rglob('*.json')
        config_backup_files = [f for f in config_backup_files if f.is_file()]

        previous_username = self.current_config['Usuario']
        previous_password = self.current_config['Contraseña']

        try:
            last_modified_file = max(config_backup_files, key=lambda f: f.stat().st_mtime)

            with open(last_modified_file, 'r', encoding='utf-8') as file:
                self.current_config = json.load(file)

                self.current_config['Usuario'] = previous_username
                self.current_config['Contraseña'] = previous_password

            print(f"🔄️  Config backup successfuly recovered")

        except Exception as e:
            print(f"‼️  An error occurred while reading config backup | {e}")
            return None

    def generate_backup(self):

        timestamp = datetime.now().strftime("%d-%m-%Y %H..%M..%S")

        config_backup_path = self.backup_folder / f'Config {timestamp}.json'
        with open(str(config_backup_path), 'w') as json_file:
            json.dump(self.current_config, json_file, indent=4) # The 'indent' parameter makes the file human-readable
        
        print(f"🔄️  Backup created and saved\n")

    def check_backup_existence(self):
        if any(self.backup_folder.glob('*.json')):
            print(f"🧵  Complete config backup files found\n")
            return True
        else:
            print(f"🧵  Complete config backup files not found\n")
            return False
        
    def delete_backup(self):
        files_to_delete = list(self.backup_folder.glob('*.json'))
    
        if files_to_delete:
            # Iterate over the list of Path objects and delete each one
            for file_path in files_to_delete:
                try:
                    file_path.unlink() # The .unlink() method is used to delete a file
                    print(f"🚮  Config backup deleted: {file_path}")
                except OSError as e:
                    print(f"‼️  Error deleting config backup in {file_path} | {e}")

    @staticmethod
    def go_back_dates(date_str1):
        # Define the expected format
        fmt = "%d.%m.%Y"
        
        # Parse the first input string into a datetime object
        d1 = datetime.strptime(date_str1, fmt)
        
        # --- Transformation 1: Jump one month before ---
        try:
            # Determine the previous month and year
            if d1.month == 1:
                new_month, new_year = 12, d1.year - 1
            else:
                new_month, new_year = d1.month - 1, d1.year
            
            # Create the new date; this will fail if the day doesn't exist (e.g., Feb 31)
            new_d1 = datetime(new_year, new_month, d1.day)
        except ValueError:
            # If the date is invalid, subtract exactly 30 days
            new_d1 = d1 - timedelta(days=30)
        
        # --- Transformation 2: One day before the ORIGINAL first date ---
        new_d2 = d1 - timedelta(days=1)
        
        # Return both as formatted strings
        return new_d1.strftime(fmt), new_d2.strftime(fmt)

    