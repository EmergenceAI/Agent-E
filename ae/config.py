# config.py at the project source code root
import os

PROJECT_SOURCE_ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCE_LOG_FOLDER_PATH = os.path.join(PROJECT_SOURCE_ROOT, 'log_files')

PROJECT_ROOT = os.path.dirname(PROJECT_SOURCE_ROOT)

PROJECT_TEMP_PATH = os.path.join(PROJECT_ROOT, 'temp')

USER_PREFERENCES_PATH = os.path.join(PROJECT_SOURCE_ROOT, 'user_preferences')
PROJECT_TEST_ROOT = os.path.join(PROJECT_ROOT, 'test')

# Check if the log folder exists, and if not, create it
if not os.path.exists(SOURCE_LOG_FOLDER_PATH):
    os.makedirs(SOURCE_LOG_FOLDER_PATH)
    print(f"Created log folder at: {SOURCE_LOG_FOLDER_PATH}")

#create user prefernces folder if it does not exist
if not os.path.exists(USER_PREFERENCES_PATH):
    os.makedirs(USER_PREFERENCES_PATH)
    print(f"Created user preferences folder at: {USER_PREFERENCES_PATH}")

if not os.path.exists(PROJECT_TEMP_PATH):
    os.makedirs(PROJECT_TEMP_PATH)
    print(f"Created temp folder at: {PROJECT_TEMP_PATH}")
