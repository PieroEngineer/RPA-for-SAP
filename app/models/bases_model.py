from pathlib import Path
from PyQt6.QtWidgets import QFileDialog
from datetime import datetime
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class BasesModel:
    def __init__(self):
        self.resource_folder_path = Path(r'app\resources')
        self.input_folder_path = self.resource_folder_path / 'input'

        self.base_data_equipments_path = self.input_folder_path / 'EQUIPOS.parquet'
        self.base_data_coessap_path = self.input_folder_path / 'COES_SAP.parquet'
        self.base_format_excel_path = self.input_folder_path / r'bases\Base donde se descarga la INFO DE SAP - base.xlsx'

        self.downloads_path = self.resource_folder_path / 'downloads'

        self.current_email = ''
        self.current_password = ''

        if not self.input_folder_path.exists():
            self.input_folder_path.mkdir(parents=True, exist_ok=True)
        if not self.downloads_path.exists():
            self.downloads_path.mkdir(parents=True, exist_ok=True)

    def update_credentials(self, email, password):
        self.current_email = email + '@com.pe'
        self.current_password = password

    def get_last_updating_datetime(self):
        print(f'🔎  Sending last updating datetime {self.last_date_updated}')
        return self.last_date_updated

    def get_base_data(self):
        return self.df_equipements, self.df_coessap

    def load_base_data_by_cache(self):
        try:
            self.df_equipements = pd.read_parquet(str(self.base_data_equipments_path))
            self.df_equipements = self.df_equipements.set_index('EQUICODI')
            
            self.df_coessap = pd.read_parquet(str(self.base_data_coessap_path))
            self.df_coessap = self.df_coessap.set_index('UbicacionTecnica')

            print(f"✅🗳️  Base data loaded\n")
        except FileNotFoundError:
            print(f"🟥🗳️  Base data not found   |   Fallback: putting empty dataframes\n")
            self.df_equipements = pd.DataFrame()
            self.df_coessap = pd.DataFrame()


    def load_base_data_by_local_file(self, inserted_excel_path = '') -> bool:
        def remove_repeated_rows_keep_one(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
            if column_name not in df.columns:
                raise ValueError(f"Column '{column_name}' not found in the DataFrame.")
            unique_df = df.drop_duplicates(subset=[column_name], keep='first')
            return unique_df
        
        try:
            if not inserted_excel_path:
                print(f'📂🫳  Starting search of folders for the bases manually...\n')
                excel_base_path, _ = QFileDialog.getOpenFileName(
                    caption = "👷‍♂️  Seleccione el excel con las hojas de COES y EQUIPOS", 
                    filter = "Excel Files (*.xlsx *.xls);;All Files (*)"
                )
            else:
                excel_base_path = inserted_excel_path
                print(f'📂🌐  Using inserted files in downloads folder\n{excel_base_path}\n')

            if excel_base_path:
                # EQUIPOS
                df: pd.DataFrame = pd.read_excel(excel_base_path, sheet_name='EQUIPOS', engine='openpyxl', skiprows=6)
                df = remove_repeated_rows_keep_one(df, 'EQUICODI')

                df.to_parquet(self.base_data_equipments_path, index=False)

                self.df_equipements = df.set_index('EQUICODI')

                # COES
                df: pd.DataFrame = pd.read_excel(excel_base_path, sheet_name='COES-SAP', engine='openpyxl')
                df = remove_repeated_rows_keep_one(df, 'UbicacionTecnica')

                df['UbiTecCelda'] = df['UbiTecCelda'].astype(str)
                df['CodCOESOP'] = df['CodCOESOP'].astype(str)
                df['SSEE'] = df['SSEE'].astype(str)
                df['EMPRESA'] = df['EMPRESA'].astype(str)
                df['diacorte'] = df['diacorte'].astype(str)

                df.drop(columns = ['L']).to_parquet(self.base_data_coessap_path, index=False)

                self.df_coessap = df.set_index('UbicacionTecnica')

                self.last_date_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

                return True
            else:
                return False

        except ValueError as e:
            print(f"🟥  Error   | {e}")
            print("🟥  Please check if the sheet name is correct or if the required libraries are installed.")
            return False

        except Exception as e:
            print(f"🟥  An unexpected error occurred: {e}")
            return False
        
    def load_base_data_by_remote_file(self):
        # Clear the downloads folder
        for item in self.downloads_path.iterdir():
            if item.is_file():
                item.unlink()
        print("🧹  Folder cleaned\n")

        # Start downloading
        chrome_options = Options()
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        prefs = {
                "download.default_directory": str(self.downloads_path.resolve()),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
            }
        chrome_options.add_experimental_option("prefs", prefs)

        chromedriver_path = r"app\resources\google_driver\chromedriver-win64\chromedriver.exe"

        self.online_driver: WebDriver = webdriver.Chrome(
            service = Service(chromedriver_path),
            options = chrome_options
        )

        timeout_per_file = 60
        
        download_url = r''
        
        # try:
        # Navigate to download
        time.sleep(2)

        print("🔐  Please log in using the opened browser...\n")
        self.online_driver.get(download_url)

        # Waiting for items availability
        wait = WebDriverWait(self.online_driver, 10)

        # Skipping error button
        going_back_button = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_PlaceHolderGoBackLink_idSimpleGoBackToHome"))
        )
        going_back_button.click()
        print(f'🖱️  Back button clicked\n')

        time.sleep(2)
 
        # Automating email accessing
        email = wait.until(
            EC.element_to_be_clickable((By.ID, "i0116"))
        )
        email.clear()
        email.send_keys(self.current_email)
        print(f'#️⃣  E-mail written\n')    

        email_done_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        email_done_btn.click()
        print(f'🖱️  Continue button clicked\n')

        time.sleep(2)

        # Automating email accessing
        password = wait.until(
            EC.element_to_be_clickable((By.ID, "i0118"))
        )
        password.clear()
        password.send_keys(self.current_password)
        print(f'#️⃣  Password written\n')    

        password_done_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        password_done_btn.click()
        print(f'🖱️  Continue button clicked\n') 

        time.sleep(2)

        password_done_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "idSIButton9"))
        )
        password_done_btn.click()
        print(f'🖱️  Continue button clicked\n')

        time.sleep(2)

        self.online_driver.get(download_url)
        
        # except Exception as e:
        #     print(f'‼️  There was an error with the credentials, please continue Manually')

        #try:
        filename = 'CODIGO UBICACION TECNICA SAP_COES'
        file_path: Path = self.downloads_path / f'{filename}.xlsx'

        # Wait for current downloading
        start_time = time.time()

        print(f'⌛  Continue button clicked...\n')
        while (not file_path.exists()) and (time.time() - start_time < timeout_per_file):
            time.sleep(1)

        self.last_date_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        if time.time()-start_time < timeout_per_file:
            print(f"✅⬇️  Download completed for the file {filename}\n")
        else:
            print(f"‼️  It seems there was a problem downloading {filename}\n")
        
        # time.sleep(5)

        self.online_driver.quit()
        # --

        return self.load_base_data_by_local_file(str(file_path))

        # except Exception as e:
        #     print(f"‼️  Data couldn't be downloaded | {e}\n")