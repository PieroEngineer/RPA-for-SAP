from datetime import datetime


def append_new_line(line_to_add: str):
    """
    Appends a new line of text to a specified file with UTF-8 encoding.

    Args:
        file_path (str): The path to the text file.
        line_to_add (str): The new line of text to be added.
    """
    # Open the file in append mode ('a') with UTF-8 encoding.
    # Using a context manager (with statement) ensures the file is closed automatically.
    file_path = 'app\\resources\\reports\\' + str(datetime.now().strftime("%d.%m.%Y")) + '.txt'
    with open(file_path, 'a', encoding='utf-8') as file:
        # Write the new line to the file. 
        # Manually add the newline character '\n' as the write() method does not add it by default.
        file.write(line_to_add + '\n')

# Example usage:
text_content = 'This is a new log entry, including special characters like ☕ and 😊'

# This will create the file if it doesn't exist, and append the line otherwise.
append_new_line(text_content)
