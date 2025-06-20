import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from project_scanner import get_project_info


if __name__ == '__main__':
    project_info = get_project_info()

    all_swift_files = project_info.all_swift_files
    for swift_file in all_swift_files:
        print(swift_file)

