import sys
from file_handler import FilesHandler
from ip_processor import IP_Processor

if __name__ == "__main__":
    command = sys.argv[1]
    if command == 'process_file':
        FilesHandler.get_ips_from_file()
    if command == 'run':
        ip_processor = IP_Processor()
        ip_processor.start_process()
    if command == 'export':
        FilesHandler.export_data()
