import time

class RpaModel:
    def __init__(self):

        self.window = 'wnd[0]/'
        self.base = self.window + 'usr/'
        self.elements = {
            '': self.window + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.window + '',
            '': self.base + '',
            '': self.base + '',
            '': self.window + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + '',
            '': self.base + ''
        }

        self.item_to_start_index = 0

    #-- Action blocks ---------------------------------------
    def access_filters(self, current_config: dict[str], submanagment: str, session, go_back_on_time = False):
        if go_back_on_time:
            self.check_box('back on time', session)
        else:
            self.check_box(current_config['Estado de plan de trabajo'], session)
        self.set_txt(self.elements[''], submanagment, session)
        self.set_txt(self.elements[''], 'N', session)
        self.set_txt(self.elements[''], current_config['Fecha inic. Plan Trab.'], session)
        self.set_txt(self.elements[''], current_config['Fecha fin. Plan Trab.'], session)
        self.click_btn(self.elements[''], session)
        
        print(f"✅🪥  Filters accessed\n")

    def extract_data_from_one_maintenance(self, session):
        description_text = self.extract_textfield_text(self.elements[''], session)
        work_plan_text = self.extract_textfield_text(self.elements[''], session)
        main_asset_text = self.extract_textfield_text(self.elements[''], session)
        work_plan_state_text = self.extract_textfield_text(self.elements[''], session)
        classification_text = self.extract_combobox_text(self.elements[''], session)

        initial_date_text = self.extract_textfield_text(self.elements[''], session)
        initial_time_text = self.extract_textfield_text(self.elements[''], session)

        final_date_text = self.extract_textfield_text(self.elements ['Fecha Final'], session)
        final_time_text = self.extract_textfield_text(self.elements ['Hora Final'], session)

        self.select_object(self.elements[''], session)
        frame_text = self.extract_frame_text(self.elements[''], session)

        data_to_send = {    #TODO: Change this kind of dicts for class entities
            'Plan de trabajo': work_plan_text,
            'Descripción': description_text,
            'Activo Principal': main_asset_text,
            'Estado Plan Trab': work_plan_state_text,
            'Clasificación': classification_text.strip(),
            'Fecha-Hora Inicio': f'{initial_date_text} {initial_time_text}',
            'Fecha-Hora Final': f'{final_date_text} {final_time_text}',
            'Observaciones de ops': frame_text
        }

        print(f"✅🔰  A piece of data sent\n{data_to_send}\n")

        return data_to_send
        
    #-- Action units ---------------------------------------

    def extract_textfield_text(self, textfield_id, session) -> str:

        # Wait until SAP is ready
        while session.Busy:
            time.sleep(0.1)

        print(f"🔎 Session no busy anymore\n")
        
        text_field = session.findById(textfield_id)

        # # Get textfield object
        text_field.setFocus()

        print(f"✅👓  Text field successfully read\n")

        return text_field.text

    def extract_combobox_text(self, combo_id, session) -> str:

        # Get the combobox object
        combobox = session.findById(combo_id)

        # Get the current selected key as a string
        selected_key = combobox.Key

        # Or get the displayed text
        selected_text = combobox.Text

        print(f"Selected Key: {selected_key}")
        print(f"Selected Text: {selected_text}")
        print(f"✅🎚️  Combobox successfuly read\n")
        return selected_text

    def extract_frame_text(self, frame_id, session):
        """
        Extracts all text from a SAP text frame (GuiTextEdit or similar GuiShell).

        Args:
            session: The active SAP GUI session object.
            frame_id: The full SAP element ID of the text frame (e.g., "wnd[0]/usr/.../shellcont/shell").

        Returns:
            str: The full extracted text, or empty string if error.
        """
        # try:

        # Get the text frame object
        text_frame = session.findById(frame_id)
        
        # Loop through lines (if selectedText fails)
        line_count = text_frame.lineCount
        full_text = ""
        for line in range(1, line_count + 1):  # Lines are 1-based
            full_text += text_frame.getLineText(line) + "\n"
        
        print(f"✅🔡  Text frame successfuly read\n")
        return full_text.strip()  # Remove trailing newline

        # except Exception as e:
        #     print(f"‼️  Error extracting text from {frame_id} | {e}\n")
        #     return ""
    
    def generate_sap_object(self, object_id, session):
        return session.findById(object_id)

    def select_object(self, selectable_id, session):
        try:
            session.findById(selectable_id).select()
            print(f"🔹  Selecting object: {selectable_id}\n")
        except Exception as e:
            print(f"‼️  Error selecting object {selectable_id}   | {e}\n")

    def click_btn(self , button_id, session):
        """
        Clicks a button in the SAP GUI by its ID.
        
        Args:
            session: The active SAP GUI session object.
            button_id: The SAP element ID of the button.
        """
        # try:
        session.findById(button_id).press()
        print(f"✅🖱️  Clicked button: {button_id}\n")
        # except Exception as e:
        #     print(f"‼️🖱️  Error clicking button {button_id}   | {e}\n")

    def navigate_to_transaction(self, combo_id, selection, session):
        """
        Navigates to a specific SAP transaction code.
        
        Args:
            session: The active SAP GUI session object.
            transaction_code: The SAP T-code.
        """
        try:
            # Enter the T-code in the command field
            session.findById(combo_id).text = selection
            # Press Enter
            session.findById(self.window).sendVKey(0)
            print(f"🧭  Navigated to transaction: {selection}\n")
        except Exception as e:
            print(f"‼️  Error navigating to {selection} | {e}\n")

    def check_box(self, checkbox_name, session):
        try:

            match checkbox_name:
                case '03':
                    session.findById(self.elements['']).selected = True
                    session.findById(self.elements['']).selected = False
                    session.findById(self.elements['']).selected = False
                    session.findById(self.elements['']).selected = False
                case '04':
                    session.findById(self.elements['']).selected = False
                    session.findById(self.elements['']).selected = True
                    session.findById(self.elements['']).selected = False
                    session.findById(self.elements['']).selected = False
                case '03 - 04':
                    session.findById(self.elements['']).selected = True
                    session.findById(self.elements['']).selected = True
                    session.findById(self.elements['']).selected = False
                    session.findById(self.elements['']).selected = False
                case 'back on time':
                    session.findById(self.elements['']).selected = False
                    session.findById(self.elements['']).selected = True
                    session.findById(self.elements['']).selected = True
                    session.findById(self.elements['']).selected = True

            # Checking the box
            print(f"▶️  Box checked: {checkbox_name}\n")

        except Exception as e:
            print(f"‼️  Error checking the box {checkbox_name}   | {e}\n")

    def set_txt(self, field_id, text_value, session):
        """
        Finds a text field by ID and sets its value.
        
        Args:
            session: The active SAP GUI session object.
            field_id: The SAP element ID of the text field (e.g., "wnd[0]/usr/ctxtVBAK-VKORG").
            text_value: The text to input into the field.
        """
        try:
            session.findById(field_id).text = text_value
            print(f"🖊️  Set text in field {field_id} to: {text_value}\n")
        except Exception as e:
            print(f"‼️  Error setting text in {field_id}    | {e}\n")

    def select_table_row_item(self, table_object, index):
        # try:

        # if not index:
        #     table_object.currentCellColumn = "REVNR"

        # table_object.currentCellRow = index
        # table_object.clickCurrentCell()

        # print(f"🔳  Item {table_object.Text} selected\n")

        column_id = "REVNR"
        # 1. Explicitly set the cell focus first
        table_object.setCurrentCell(index, column_id)   ## Continue here: Correct the error of this line when using a month back (Perhaps the session is not arriving reaching the correct screen)
        
        # 2. Use doubleClick which is more reliable for navigation than clickCurrentCell
        table_object.clickCurrentCell()
        
        print(f"🔳 Table item selected\n")
        # print(f"🔳 Item {table_object.getCellValue(index, column_id)} selected\n")

        # except Exception as e:
        #     print(f"‼️  Error in item selection of the row {index}  | {e}\n")

    def scroll_screen_horizontal_to_end(self, session, user_area_id):
        """
        Scrolls the entire SAP screen horizontally to the right end.
        
        Args:
            session: The active SAP GUI session object.
            user_area_id: The ID of the GuiUserArea (default works for most main screens).
            delay_after: Seconds to wait after scrolling (for UI to settle).
        
        Returns:
            bool: True if scrolled successfully, False otherwise.
        """
        delay_after=0.5

        try:
            user_area = session.findById(user_area_id)
            
            h_scroll = user_area.HorizontalScrollbar
            
            if h_scroll is None:
                print("‼️  No horizontal scrollbar found on this screen.\n")
                return False
            
            max_pos = h_scroll.Maximum
            current_pos = h_scroll.Position
            
            if max_pos <= 0:
                print("⚠️  Horizontal scrollbar exists but Maximum <= 0 (no overflow).\n")
                return False
            
            if current_pos == max_pos:
                print("⚠️  Already at the rightmost position.\n")
                return True
            
            # Scroll directly to the end
            h_scroll.Position = max_pos
            print(f"⏩  Scrolled horizontally to end: Position set to {max_pos} (from {current_pos}).\n")
            
            time.sleep(delay_after)
            return True
        
        except Exception as e:
            print(f"‼️  Error scrolling horizontally: {e}\n")
            
            # Fallback 1: Try keyboard shortcut (Shift + Mouse Wheel doesn't work via sendVKey)
            # Ctrl + End sometimes moves to bottom-right, but unreliable for horizontal only.
            
            # Fallback 2: Loop sending Page Right (VKey 82 is Page Down; for horizontal, try Right Arrow loops)
            print("🚧  Attempting fallback: repeated Right Arrow keys.\n")
            try:
                for _ in range(50):  # Arbitrary large number
                    session.findById(self.window).sendVKey(39)  # 39 = Right Arrow
                time.sleep(delay_after)
                print("⏩  Fallback scrolling completed.\n")
                return True
            except:
                print("‼️  Fallback also failed.\n")
                return False  
            
    #--Complementary---------------------------------------
    def get_item_index_to_start(self):
        return self.item_to_start_index
    
    def set_item_index_to_start(self, index):
        self.item_to_start_index = index