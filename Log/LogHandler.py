import logging

class LogHandler(object):
    def __init__(self):
        # Create a logger for info messages
        self.info_logger = logging.getLogger('info_logger')
        self.info_logger.setLevel(logging.INFO)
        self.info_handler = logging.FileHandler("InfoLog.log")
        self.info_handler.setLevel(logging.INFO)
        self.info_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.info_handler.setFormatter(self.info_formatter)
        self.info_logger.addHandler(self.info_handler)
        
        # Create a logger for error messages
        self.error_logger = logging.getLogger('error_logger')
        self.error_logger.setLevel(logging.ERROR)
        self.error_handler = logging.FileHandler("ErrorLog.log")
        self.error_handler.setLevel(logging.ERROR)
        self.error_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.error_handler.setFormatter(self.error_formatter)
        self.error_logger.addHandler(self.error_handler)
    
    def log_info(self, message):
        self.info_logger.info(message)
    
    def log_error(self, message):
        self.error_logger.error(message)

    def remove_duplicates(self, input_file):
        # Set to store unique lines
        unique_lines = set()

        # Open input file for reading
        with open(input_file, 'r') as file:
            # Read each line in the file
            for line in file:
                # Add the line to the set of unique lines
                unique_lines.add(line)

        # Open output file for writing
        with open(input_file, 'w') as file:
            # Write unique lines to the output file
            for line in unique_lines:
                file.write(line) 