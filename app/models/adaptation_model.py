import re
import os
import shutil
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import pyarrow.parquet as pq

# from utils.points_handler import remove_last_point    # Called from other file works only if the program runs from the main
#from utils.date_helper import check_overlap

#--- TODO: Put it in "utils"
def order_dict(dict: dict, break_line = True): 
    return json.dumps(dict, indent=4, sort_keys=True) + ('\n' if break_line else '')

def remove_last_point(s) -> str: ##Put it in "utils"
    s = str(s)
    if not s:  # Check if the string is empty
        return s
        
    points_to_avoid = (',', '.')
    if s[-1] in points_to_avoid:
        return s[:-1]
    else:
        return s
    
def get_umpteenth_colon_string(strings, n):
    matches = [s for s in strings if ":" in s if bool(re.fullmatch(r"[0-9:]+", s))]
    return matches[n-1] if 0 < n <= len(matches) else ""

def check_overlap(range1: tuple, range2: tuple):
    
    date_format = "%d.%m.%Y"

    # Parse string dates into datetime objects
    # range1 = ("dd.mm.yyyy", "dd.mm.yyyy")
    start1 = datetime.strptime(range1[0], date_format)
    end1 = datetime.strptime(range1[1], date_format)
    
    start2 = datetime.strptime(range2[0], date_format)
    end2 = datetime.strptime(range2[1], date_format)
    
    # Overlap Logic: (StartA <= EndB) AND (EndA >= StartB)
    return start1 <= end2 and end1 >= start2
#---
    
# def format_year(date): ## Consider code it for those years that appear as with 2 digits instead of 4 (e.g. "26" instead of "2026")

class AdaptationModel:
    def __init__(self):
        self.output_folder_path = Path(r'app\resources\output')
        self.input_folder_path = Path(r'app\resources\input')
        self.report_path = Path(r'app\resources\reports')

        self.base_data_equipments_path = self.input_folder_path / 'EQUIPOS.parquet'
        self.base_data_coessap_path = self.input_folder_path / 'COES_SAP.parquet'
        self.base_format_excel_path = self.input_folder_path / r'bases\Base donde se descarga la INFO DE SAP - base.xlsx'

        self.base_report_path = self.report_path / (str(datetime.now().strftime("%Y-%m-%d %H..%M..%S")) + '.txt')

        self.current_adapted_data = pd.DataFrame()

        if not self.output_folder_path.exists():
            self.output_folder_path.mkdir(parents=True, exist_ok=True)
        if not self.input_folder_path.exists():
            self.input_folder_path.mkdir(parents=True, exist_ok=True)
        if not self.report_path.exists():
            self.report_path.mkdir(parents=True, exist_ok=True)

    # -- Util functions ----

    def add_info_to_report_(self, new_info):
        new_info = str(new_info)
        with open(self.base_report_path, 'a', encoding='utf-8') as file:
            file.write(new_info + '\n')

    # -- Data obtaining functions ----

    def load_base_data(self, df_equipements: pd.DataFrame, df_coessap: pd.DataFrame):  
        # Raw items
        self.df_equipements = df_equipements
        self.df_coessap = df_coessap

        # Generating smaller dataframe
        self.sub_df_coessap = self.df_coessap[['IDCOES', 'CodCOESOP']].copy()
        self.sub_df_coessap['UbicacionTecnica_'] = self.sub_df_coessap.index.str[:7]
        self.sub_df_coessap:pd.DataFrame = self.sub_df_coessap[self.sub_df_coessap['CodCOESOP'].str.contains('barra', False)]
        self.sub_df_coessap = self.sub_df_coessap.drop_duplicates(subset=['UbicacionTecnica_', 'IDCOES'], keep='first')

    def set_input_dates(self, input_date_times: tuple):
        self.input_starting_datetime: str = input_date_times[0]
        self.input_ending_datetime: str = input_date_times[1]

    # -- Data processing functions ---- 

    def adapt_extracted_data(self, extracted_df: pd.DataFrame):

        self.add_info_to_report_(f"🔎  Data before adaptation:\n{extracted_df}\n")
        self.add_info_to_report_(f"🔎  'Activos principal's: \n{extracted_df['Activo Principal'].tolist()}\n")

        # Static info
        type_condition_mapping = {
            '': 'E/S',
            '': 'E/S',
            '': 'E/S',
            '': 'F/S',
            '': 'F/S',
            '': 'F/S',
            '': 'F/S',
            '': 'E/S'
        }

        company_id_map = {
            12: 'Company 1',
            64: 'Company 2',
            59: 'Company 3',
            13036: 'Company 4'
        }

        correct_order = [
            'ITEM', 'EMPRESA', 'UBICACION', 'EQUIPO', 'COD', 'INICIO', 'FINAL', 'DESCRIPCION',
            'MW INDISP.', 'Dispon', 'Interrupc.', 'Sist. Aisl.', 'Inst. Prov.', 'TIPO', 'PROGR.',
            'PT', 'DT', 'OBSERVACION ANTERIOR', 'Estado'
        ]

        # Mapping insertions
        self.current_adapted_data['Dispon'] = extracted_df['Clasificación'].map(type_condition_mapping).fillna('')
        self.current_adapted_data['COD'] = extracted_df['Activo Principal'].map(self.df_coessap['IDCOES'])
        self.current_adapted_data['EMPRESA'] = self.current_adapted_data['COD'].map(self.df_equipements['EMPRCODI']).map(company_id_map).fillna('')
        self.current_adapted_data['EQUIPO'] = self.current_adapted_data['COD'].map(self.df_equipements['EQUIABREV'])
        self.current_adapted_data['UBICACION'] = self.current_adapted_data['COD'].map(self.df_equipements['AREANOMB'])
        self.current_adapted_data['DT'] = self.current_adapted_data['COD'].map(self.df_equipements['Unnamed: 7'])  ## Since this column doesn't have name, all empty columns must be removed, otherwise change this "6"

        # Direct insertions
        self.current_adapted_data['INICIO'] = extracted_df['Fecha-Hora Inicio']
        self.current_adapted_data['FINAL'] = extracted_df['Fecha-Hora Final']
        self.current_adapted_data['OBSERVACION ANTERIOR'] = extracted_df['Observaciones de ops']
        self.current_adapted_data['Estado'] = extracted_df['Estado Plan Trab'].astype(int)
        self.current_adapted_data['PT'] = extracted_df.index
        self.current_adapted_data['DT'] = self.current_adapted_data['COD'].map(self.df_equipements['Unnamed: 7'])  ## Since this column doesn't have name, all empty columns must be removed, otherwise change this "6"
        self.current_adapted_data['DESCRIPCION'] = extracted_df['Descripción']

        # Static insertions
        self.current_adapted_data['ITEM'] = None
        self.current_adapted_data['MW INDISP.'] = 0
        self.current_adapted_data['Interrupc.'] = 'NO'
        self.current_adapted_data['Sist. Aisl.'] = 'NO'
        self.current_adapted_data['Inst. Prov.'] = 'NO'
        self.current_adapted_data['PROGR.'] = 'PROGRAMADO'
        print(f"🔎 self.current_adapted_data['Interrupc.']\n{self.current_adapted_data['Interrupc.']}\n")

        # Processed insertions
        self.extracted_data = extracted_df

        self.generate_type_()

        # Ordering columns
        self.current_adapted_data = self.current_adapted_data[correct_order]

        # Adapted data snapshot before heavy processing
        self.data_with_default_modifications = self.current_adapted_data.copy()

        self.add_info_to_report_(f"🔎  After default adaptation \n{self.current_adapted_data}\n\n")

        # Heavy processing
        self.start_heavy_adaptation()

        # Ordering and formatting table
        self.current_adapted_data = self.current_adapted_data.sort_values(by=['INICIO', 'PT'], ascending=[True, True])

        # Changing date format
        def transform_date(val: str):
            try:
                datetime.strptime(val, "%d.%m.%Y %H:%M:%S")
                return val.replace(".", "/")
            except:
                return val
        self.current_adapted_data['INICIO'] = self.current_adapted_data['INICIO'].apply(transform_date)
        self.current_adapted_data['FINAL'] = self.current_adapted_data['FINAL'].apply(transform_date)

        self.add_info_to_report_(f"🪞  Extracted data has been adapted\n")

    def generate_type_(self):
            preventive_state_hints = ['corregir', 'correctivo', 'corrección', 'correccion', 'reparar', 'reparación', 'reparacion', 'cambio', 'cambiar']
            self.current_adapted_data['TIPO'] = np.where(
                self.current_adapted_data['DESCRIPCION'].str.contains('|'.join(preventive_state_hints), case=False, na=False), 
                'MANTENIMIENTO CORRECTIVO',
                'MANTENIMIENTO PREVENTIVO'
            )

    def start_heavy_adaptation(self):
        updated_row_content = []
        for index, row in self.current_adapted_data.iterrows():
            related_row = row.copy()

            self.add_info_to_report_('-'*50 + f"\nℹ️  Current maintenance {row['PT']}\n")

            row_range = (related_row['INICIO'].split(' ')[0], related_row['FINAL'].split(' ')[0])
            input_range = (self.input_starting_datetime, self.input_ending_datetime)
            if not check_overlap(row_range, input_range):
                self.add_info_to_report_(f'🔎 row range is {row_range} and input range is {input_range}; they do not cross each other, so this row is not included\n')
                continue

            # Structuring observations
            self.add_info_to_report_(f'🔎🔍  observations before structurations:\n{related_row['OBSERVACION ANTERIOR']}\n')
            related_observation = self.structure_observations(related_row['OBSERVACION ANTERIOR'])
            self.add_info_to_report_(f'🔎🔍  observations after structurations:\n{order_dict(related_observation)}\n')

            # Disaggregating main row
            self.add_info_to_report_(f'▶️  Mean row disagraggregation\n')
            rows_from_main = self.split_by_dates_(related_row, related_observation['initial_conditions']['is_continue_cut'])
            
            # Disaggregating bars
            self.add_info_to_report_(f'🟰  Bar row disagraggregation\n')
            if related_observation['bar_changing_request']['n']:
                bar_rows = self.generate_bar_disaggregations_(related_row, related_observation)
            
                for bar_row_to_split in bar_rows:
                    divided_rows = self.split_by_dates_(bar_row_to_split)
                    updated_row_content += divided_rows

            # Updatind original description
            self.update_base_description_(rows_from_main, related_observation)  ## It should update in place

            #
            updated_row_content += rows_from_main

        self.current_adapted_data = pd.DataFrame(updated_row_content).reset_index(drop = True)
    
    def update_base_description_(self, rows_from_main: list[pd.Series], observations: dict):
        def find_first_word_with_prefixes(text: str, prefixes: list[str]):
            # Escape prefixes and join them with the | (OR) operator
            # Wrap them in a non-capturing group (?:...)
            joined_prefixes = "|".join(re.escape(p.upper()) for p in prefixes)
            
            # \b ensures we only match the start of a word
            pattern = rf"\b(?:{joined_prefixes})\w*"
            
            match = re.search(pattern, text.upper())

            return match.group() if match else ''

        for row_from_main in rows_from_main:

            # By bar
            if (len(set(observations['bar_changing_request']['date']))==1) and (observations['bar_changing_request']['n']>1):   # If all bars are in the same date
                row_from_main['DESCRIPCION'] += f', ACTIVIDAD CON CAMBIO DE BARRAS'
            else:
                for bar_i, bar_letter in enumerate(observations['bar_changing_request']['letters']):
                    if row_from_main['INICIO'].split(' ')[0]==observations['bar_changing_request']['date'][bar_i]:
                        row_from_main['DESCRIPCION'] += f', ACTIVIDAD CON BARRA "{bar_letter}" FUERA DE SERVICIO'
                        break

            # By reclouse
            if observations['enabling_indications']['has_reclosure']:
                requirement = find_first_word_with_prefixes(observations['enabling_indications']['info'], ['l-', 'l ', 'l'])
                if requirement:
                    row_from_main['DESCRIPCION'] += f', REQUIERE {requirement} CON RECIERRES DESHABILITADOS'

            # By unsupervised
            if observations['initial_conditions']['is_unsupervised']:
                row_from_main['DESCRIPCION'] += ', ACTIVIDAD CON PERDIDA DE SUPERVISION'

            # By shooting_risk
            if self.extracted_data.at[row_from_main['PT'], 'Clasificación'] == 'Riesgo de Disparo':
                row_from_main['DESCRIPCION'] += ', ACTIVIDAD CON RIESGO DE DISPARO'

            row_from_main['DESCRIPCION'] += f'. ({row_from_main['PT']})'

    def generate_bar_disaggregations_(self, related_row: pd.Series, observations: dict):
        # Updating dates if necessary
        if not observations['bar_changing_request']['data_was_specified']:  # So, both bars should have the same 

            if related_row['INICIO'].split(' ')[0]!=related_row['FINAL'].split(' ')[0]:
                self.add_info_to_report_('⚠️  There should be a specified date when there is only one date in "Fecha de planeación" | Fallback: returning the received row\n')
                return [related_row]
            
            for i in range(observations['bar_changing_request']['n']):
                observations['bar_changing_request']['date'][i] = related_row['INICIO'].split(' ')[0]

        # Bar logic
        bar_rows = []
        for bar_i in range(observations['bar_changing_request']['n']):
            bar_row = related_row.copy()

            same_area = self.sub_df_coessap.index.str[:7] == self.extracted_data.at[bar_row['PT'], 'Activo Principal'][:7]
            
            match_leter = self.sub_df_coessap['CodCOESOP']   \
                .str.lower().str.replace(' ', '')             \
                .str.replace('-', '')                          \
                .str.contains( 'barra' + observations['bar_changing_request']['letters'][bar_i].lower() )
            
            row_by_unique_matches = self.sub_df_coessap[same_area & match_leter] # Only one element excepted

            if not row_by_unique_matches.empty:
                bar_row['COD'] = row_by_unique_matches['IDCOES'].iat[0]
                bar_row['EQUIPO'] = row_by_unique_matches['CodCOESOP'].iat[0]

                if row_by_unique_matches.shape[0]>1:
                    self.add_info_to_report_('🚧  More than one possible bar found | Fallback the first one was selected')
            else:
                bar_row['COD'] = 'Observado'
                bar_row['EQUIPO'] = 'BARRA ' + observations['bar_changing_request']['letters'][bar_i]

            year_correction = lambda date: re.sub(r"\.(\d{2})(?=\s)", r".20\1", date)
        
            bar_row['TIPO'] = 'OTROS'
            bar_row['INICIO'] = year_correction(observations['bar_changing_request']['date'][bar_i]) + ' ' + observations['bar_changing_request']['starting_time'][bar_i]
            bar_row['FINAL'] = year_correction(observations['bar_changing_request']['date'][bar_i]) + ' ' + observations['bar_changing_request']['ending_time'][bar_i]
            bar_row['DESCRIPCION'] = f'FUERA DE SERVICIO DEBIDO A TRABAJOS DE {remove_last_point(related_row['EQUIPO'])}. ({related_row['PT']})'

            bar_rows.append(bar_row)

        # return tuple(observations['bar_changing_request']['date']), bar_rows #X I expect that the also dictionary is also modified, so don't return it
        return bar_rows           

    def split_by_dates_(self, row_to_split: pd.Series, continue_cut = False):
        def limit_start_date(line_date_str):   #TODO: Mix functions, they are almost the same
            # Define the date format
            date_format = "%d.%m.%Y"
            # date_format = "%d/%m/%Y"
            datetime_format = date_format + " %H:%M:%S"

            # try: 
            # Convert strings to datetime objects
            line_date = datetime.strptime(line_date_str, datetime_format)
            input_date = datetime.strptime(self.input_starting_datetime, date_format)
            self.add_info_to_report_(f'🔎  line date: {line_date}   |   input date: {input_date}\n')
            # except ValueError:
            #     return 'Fecha fuera de rango'

            # Check if input_date is earlier than line_date
            if line_date > input_date:
                return line_date_str  # Finish the function
            
            self.add_info_to_report_(f'🔎  line date ({input_date}) is later than the input date ({line_date})\n')    
            
            self.add_info_to_report_(f'🔎  In\n{row_to_split},\nthe input date is later than the start date\n')
            # Modify the line_date based on the boolean
            self.add_info_to_report_(f'🔎  Changing its time\n')
            # Boolean is True: becomes input_date + 1 day
            line_date = input_date.replace(hour=0, minute=0, second=0)# |X + timedelta(days=1)

            self.add_info_to_report_(f'🔎  Now its end date is {line_date}\n')
            
            # Return the result formatted back as a string
            return line_date.strftime(datetime_format)

        def limit_end_date(line_date_str, change_time): #TODO: Mix functions, they are almost the same
            # Define the date format
            date_format = "%d.%m.%Y"
            # date_format = "%d/%m/%Y"
            datetime_format = date_format + " %H:%M:%S"
            
            try: 
                # Convert strings to datetime objects
                line_date = datetime.strptime(line_date_str, datetime_format)
            except ValueError:
                return '01.01.01 00:00:00'  #TODO: change it, it's a temporal fallback

            try: 
                input_date = datetime.strptime(self.input_ending_datetime, date_format)
            except ValueError:
                return '01.01.01 00:00:00'

            self.add_info_to_report_(f'🔎  line date: {line_date}   |   input date: {input_date}\n')
                
            # Check if line_date is earlier than input_date
            if line_date < input_date:
                return line_date_str  # Finish the function
            
            self.add_info_to_report_(f'🔎  line date ({line_date}) is later than the input date ({input_date})\n')    
            
            self.add_info_to_report_(f'🔎  In\n{row_to_split},\nthe end date is later than the input date\n')
            # Modify the line_date based on the boolean
            if not change_time:
                self.add_info_to_report_(f'🔎  No changing its time\n')
                # Boolean is False: becomes input_date
                line_date = input_date.replace(hour=line_date.hour, minute=line_date.minute, second=line_date.second)
            else:
                self.add_info_to_report_(f'🔎  Changing its time\n')
                # Boolean is True: becomes input_date + 1 day
                line_date = input_date.replace(hour=0, minute=0, second=0) + timedelta(days=1)

            self.add_info_to_report_(f'🔎  Now its end date is {line_date}\n')
                
            # Return the result formatted back as a string
            return line_date.strftime(datetime_format)
        
        self.add_info_to_report_(f'🧩  Spliting by dates\n')

        format_year = lambda date_str: re.sub(r"(\d{2}\.\d{2}\.)(\d{2})(\b.*)", r"\g<1>20\2\3", date_str)
        self.add_info_to_report_(f'🔎  Before Inicio: {row_to_split['INICIO']}\n')
        self.add_info_to_report_(f'🔎  Before Final: {row_to_split['FINAL']}\n')
        self.add_info_to_report_(f'🔎  Before Inicio mod: {format_year(row_to_split['INICIO'])}\n')
        self.add_info_to_report_(f'🔎  Before Final mod: {format_year(row_to_split['FINAL'])}\n')
        line_starting_date: str = limit_start_date(format_year(row_to_split['INICIO']))
        line_finishing_date: str = limit_end_date(format_year(row_to_split['FINAL']), continue_cut)
        self.add_info_to_report_(f'🔎  Now Inicio: {line_starting_date}\n')
        self.add_info_to_report_(f'🔎  Now Final: {line_finishing_date}\n')

        date_format = "%d.%m.%Y"
        # date_format = "%d/%m/%Y"
        datetime_format = date_format + " %H:%M:%S"

        try:
            n_days = abs((datetime.strptime(line_starting_date.split(' ')[0], date_format) - datetime.strptime(line_finishing_date.split(' ')[0], date_format)).days)+1
            self.add_info_to_report_(f'🔎  Days calculated: {n_days}\n')        
        except ValueError:
            self.add_info_to_report_(f'🔎🟥  Error trying to calculate the days: {line_starting_date}\n')
            return [row_to_split]

        #V
        if n_days>1:
            self.add_info_to_report_(f'🔎  {row_to_split['PT']} has more than one date\n')

        if continue_cut:
            line_starting_date_in_0 = line_starting_date.split(' ')[0] + ' 00:00:00'
            line_finishing_date_in_0 = line_finishing_date.split(' ')[0] + ' 00:00:00'

        generated_rows = []

        description: str = row_to_split['DESCRIPCION']           # e.g. 'MP 4A SILICONADO AISL / BARRA B - VOLTAN (R0125585)'
        new_comment_position = description.rfind(' ')
        
        for n_counted_days in range(n_days):
            
            related_row = row_to_split.copy()
            try:
                related_row['INICIO'] = (datetime.strptime(
                    line_starting_date_in_0 if n_counted_days and continue_cut else line_starting_date, 
                    datetime_format
                ) + timedelta(days=n_counted_days)).strftime(datetime_format)

                self.add_info_to_report_(f'🔎  Initial day: {related_row['INICIO']}\n')        
            except ValueError:
                self.add_info_to_report_(f'🔎🟥  Error calculating the initial day\n')        
                related_row['INICIO'] = 'Fecha no calculable'
            
            try:
                related_row['FINAL'] = (datetime.strptime(
                    line_finishing_date_in_0 if ((n_counted_days+1)<n_days) and continue_cut else line_finishing_date, 
                    datetime_format) - (timedelta(days= n_days-n_counted_days-(1 + continue_cut)) if (n_counted_days+1)<n_days else timedelta(days=0))
                ).strftime(datetime_format)
                self.add_info_to_report_(f'🔎  End day: {related_row['FINAL']}\n')        
            except ValueError:
                self.add_info_to_report_(f'🔎🟥  Error calculating the end day\n')        
                related_row['FINAL'] = 'Fecha no calculable'
            
            if related_row['INICIO'] != related_row['FINAL']:
                #Xrelated_row['DESCRIPCION'] = description[:new_comment_position] + (f', ACTIVIDAD CON CORTE CONTINUO.' if continue_cut else '') + description[new_comment_position:]  #TODO: Cut the other months except the limit
                related_row['DESCRIPCION'] = description + (f', ACTIVIDAD CON CORTE CONTINUO' if continue_cut else '')  #TODO: Cut the other months except the limit

                generated_rows.append(related_row)
                self.add_info_to_report_(f'🔎➕  For {related_row['PT']} one row with this {related_row['EQUIPO']} equipment was added\n')

        return generated_rows
    

    # -- Observation functions ----

    def structure_observations(self, raw_observation: str):
        # -- Preprocessing observation
        index = raw_observation.find('2.2.1')
        raw_observation = raw_observation[index:] if index != -1 else raw_observation

        # -- Collecting observation
        sections: list[str] = [line.strip() for line in raw_observation.strip().split('2.2.') if line.strip()]
        ##Maybe later it will be necessary in case there aren't at least 5 sections, otherwise, notify that the observation is broken
        
        fragmented_sections = [section.split('\n\n') if len(section.split('\n\n'))!=1 else section.rsplit('\n', 1) for section in sections if section.strip()] ## This line still has a fail; it's assuming that if there is an breaking line error, there will be only one extra object note there.  

        section_names = ['initial_conditions', 'enabling_indications', 'bar_changing_request', 'operational_conditions_outside', 'operational_conditions_inside']

        collected_observations = {section_names[i]:(section[1:] if section else ['']) for i, section in enumerate(fragmented_sections)}    ## An error here could mean that "section_names" and "fragmented_sections" don't have the same lenght

        # -- Structuring information
        structured_observations = {
            'initial_conditions': {},
            'enabling_indications': {},
            'bar_changing_request': {},
            'operational_conditions_outside': {},
            'operational_conditions_inside': {}
        }

        # Bar changing request data
        bars = collected_observations['bar_changing_request'][0]    # e.g. 'Barra B F/S de 08:00 a 12:00 DIA: 23.04.06\nBarra A F/S de 12:00 a 16:00 DIA: 23.04.06'
        bar_description_list = [bar for bar in bars.split('\n') if (('barra' in bar.lower()) and ('no' not in bar.lower()) and (len(bar)>25))]                     # e.g. ['Barra B F/S de 08:00 a 12:00', 'Barra A F/S de 12:00 a 16:00']
        bar_description_list_splited = [bar_description.split(' ') for bar_description in bar_description_list]             # e.g. [['Barra', 'B', 'F/S', 'de', '08:00', 'a', '12:00', 'DIA:', '23.04.26'], ['Barra', 'A', 'F/S', 'de', '08:00', 'a', '12:00', 'DIA:', '23.04.26']]
        dates_specified = any(('dia' in bar_description_part.lower()) for bar_description_part in bar_description_list)
        
        self.add_info_to_report_(f"🔎🟰  bars {bars}\n")
        self.add_info_to_report_(f"🔎🟰  bar_description_list {bar_description_list}\n")
        self.add_info_to_report_(f"🔎🟰  bar_description_list_splited {bar_description_list_splited}\n")

        structured_observations['bar_changing_request']['n'] = len(bar_description_list)
        structured_observations['bar_changing_request']['letters'] = tuple(bar_description_splited[1] for bar_description_splited in bar_description_list_splited) if len(bar_description_list) else ('', '')
        structured_observations['bar_changing_request']['date'] = [bar_description_splited[-1] if dates_specified else '' for bar_description_splited in bar_description_list_splited] if len(bar_description_list) else ['', '']
        structured_observations['bar_changing_request']['starting_time'] = tuple(get_umpteenth_colon_string(bar_description_splited, 1) +':00' if len(bar_description_splited)>4 else '' for bar_description_splited in bar_description_list_splited) if len(bar_description_list) else ('', '')
        structured_observations['bar_changing_request']['ending_time'] = tuple(get_umpteenth_colon_string(bar_description_splited, 2)+':00' if len(bar_description_splited)>6 else '' for bar_description_splited in bar_description_list_splited) if len(bar_description_list) else ('', '')
        structured_observations['bar_changing_request']['data_was_specified'] = dates_specified if len(bar_description_list) else ''

        self.add_info_to_report_(f"🔎🟰  starting_time {structured_observations['bar_changing_request']['starting_time']}\n")
        self.add_info_to_report_(f"🔎🟰  ending_time {structured_observations['bar_changing_request']['ending_time']}\n")

        # Continue cut data
        structured_observations['initial_conditions']['is_continue_cut'] = 'continu' in collected_observations['initial_conditions'][0].lower()

        # Reclosure data
        # word_repeated = str(fragmented_observation[1][0]).lower().count('recierre')>1
        word_is_present = 'recierre' in str(collected_observations['enabling_indications'][0]).lower()
        structured_observations['enabling_indications']['has_reclosure'] = word_is_present
        structured_observations['enabling_indications']['info'] = str(collected_observations['enabling_indications'][0])

        # By unsupervised
        message_present = any(('perdida de superv' in line.lower()) for line in collected_observations['initial_conditions'])
        structured_observations['initial_conditions']['is_unsupervised'] = message_present

        return structured_observations
    
    def generate_excel(self):   #TODO: Include an option that allows user generating the raw extracted data too

        timestamp = datetime.now().strftime("%Y-%m-%d %H..%M..%S")

        self.output_path = self.output_folder_path / f'Data {timestamp}.xlsx'

        # Writing the content over the base format
        shutil.copy(self.base_format_excel_path, self.output_path)
        with pd.ExcelWriter(str(self.output_path), engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:

            self.current_adapted_data.to_excel(
                writer, sheet_name='Después de agregaciones', 
                startrow=9, startcol=2,
                header=False, index=False
            )

            self.data_with_default_modifications.to_excel(writer, sheet_name='Antes de agregaciones', index=False)

            self.extracted_data.to_excel(writer, sheet_name='Data extraída')

        os.startfile(self.output_path)

        print(f"✅  Adapted data converted into excel\n")

if __name__ == '__main__':
    file_path = r'app\resources\backup\Data 04-05-2026 11..22..26.parquet'

    df = pd.read_parquet(file_path).set_index('Plan de trabajo')

    table = pq.read_table(file_path)
    existing_meta: dict[bytes, bytes] = table.schema.metadata or {}
    datetime_input: str = existing_meta[b'datetimes'].decode('utf-8')

    a = AdaptationModel()

    base_data_equipments_path = r'app\resources\input\EQUIPOS.parquet'
    base_data_coessap_path = r'app\resources\input\COES_SAP.parquet'
    df_equipements = pd.read_parquet(base_data_equipments_path)
    df_equipements = df_equipements.set_index('EQUICODI')
    df_coessap = pd.read_parquet(base_data_coessap_path)
    df_coessap = df_coessap.set_index('UbicacionTecnica')

    a.load_base_data(df_equipements, df_coessap)

    print(f"Datetime input: {tuple(datetime_input.split('|'))}\n")

    a.set_input_dates(tuple(datetime_input.split('|')))
    a.adapt_extracted_data(df)

    a.generate_excel()