# RPAForSAP

Desktop RPA application for extracting SAP maintenance/work-plan data, backing it up, and adapting it into an Excel report format.

The app is built with **Python**, **PyQt6**, and an **MVC architecture**. It controls SAP GUI through Windows COM scripting, opens multiple SAP sessions, distributes extraction work across threads, stores the extracted data as parquet backups, and can generate a formatted Excel output from those backups.

## Main Features

- PyQt6 desktop interface for entering SAP credentials, dates, plan status, and transmission submanagement filters.
- SAP GUI automation through `win32com.client`.
- Parallel extraction across multiple SAP sessions.
- Local backup generation for extracted data and configuration.
- Data adaptation pipeline that maps extracted SAP fields to the target report structure.
- Excel export using a base workbook format.
- Optional backup selection/adaptation workflow after extraction.

## Architecture

This project follows an MVC-style structure:

- `views/`: PyQt6 windows, dialogs, and widgets.
- `controllers/`: application flow, UI events, extraction orchestration, and adaptation orchestration.
- `models/`: SAP automation, RPA actions, data storage, configuration, OCR experiment, and data transformation logic.
- `resources/`: styles and supporting resources.
- `utils/`: helper functions.

## Key Files

- `main.py`: application entry point. It creates the `QApplication`, applies the stylesheet, and starts `AppController`.
- `controllers/rpa_controller.py`: connects the UI with the RPA workflow. It reads user settings, starts SAP sessions, distributes extraction ranges across threads, receives extracted rows through a queue, and triggers backups/adaptation when configured.
- `models/sap_model.py`: handles SAP GUI startup/restart, login, session creation, COM session unmarshalling, and SAP window arrangement.
- `models/rpa_model.py`: contains the SAP GUI automation actions: navigating to transactions, setting filters, clicking buttons, selecting table rows, and extracting text from SAP fields/frames.
- `models/adaptation_model.py`: converts extracted SAP data into the final report structure. It loads base parquet data, maps equipment/company information, structures observations, splits rows by dates, handles bar-related disaggregations, and writes the final Excel report.
- `models/ocr_model.py`: currently **unused** in the active project flow. It remains in the repository as an alternative approach for recognizing text fields faster by cropping SAP screenshots and using Windows OCR.

## Requirements

This project is Windows-specific because it depends on SAP GUI scripting and Windows COM automation.

Expected environment:

- Windows
- Python 3.10+
- SAP GUI installed
- SAP GUI scripting enabled
- Access to the configured SAP system
- Local base files required by the adaptation process

Main Python dependencies used by the code include:

- `PyQt6`
- `pywin32`
- `pygetwindow`
- `screeninfo`
- `pandas`
- `numpy`
- `pyarrow`
- `openpyxl`
- `Pillow`
- `winrt`

Install the dependencies with your preferred environment manager, for example:

```bash
pip install PyQt6 pywin32 pygetwindow screeninfo pandas numpy pyarrow openpyxl Pillow winrt
```

## How To Run

From the project root:

```bash
python main.py
```

The application will open the desktop UI. After the user enters the required SAP settings and starts extraction, the app launches SAP GUI, logs in, creates multiple sessions, extracts maintenance data, and saves backups locally.

## Data Flow

1. The user selects SAP extraction parameters in the main window.
2. `RpaController` saves the configuration and starts the SAP/RPA workflow.
3. `SapModel` restarts SAP GUI, logs in, and creates several sessions.
4. `RpaModel` applies filters and extracts fields from each maintenance/work-plan row.
5. Extracted rows are collected in `DataModel`.
6. Data and configuration backups are written under `app/resources/backup`.
7. If full workflow mode is enabled, `AdaptationModel` converts the extracted backup into the final Excel report.
8. Output files are generated under `app/resources/output`, with processing reports under `app/resources/reports`.

## Notes

- The SAP element IDs in `RpaModel` and `SapModel` are specific to the target SAP environment and may need adjustment before using the project elsewhere.
- The OCR model is not wired into the active extraction pipeline. The current approach reads SAP fields directly through GUI scripting.
- The application stores SAP credentials in the local configuration file used by the app. Treat that folder as sensitive in real deployments.
- This project is available for public use. If you plan to distribute or reuse it formally, consider adding a dedicated license file.

## Credits

Author: **Piero Olivas**  
Email: **psot14022001@gmail.com**  
Version: **1.0.0**
