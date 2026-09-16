"""
================================================================================
LLD: Logging System
================================================================================

Logging system :
Accept log messages/events and decide how/where they should be recorded.

We may have different logging levels like DEBUG, INFO, WARN, ERROR
1. Check if log levels is enabled
2. Format the msg
3. Send to the destinations like console, file, db and so on....

Clarifying Questions:
1. What destinations should the logging system support — console, file, database, or external systems?
- For now, support console and file. We may want to add other destinations later.

2. What format should each log message follow? Do we have a standard template?
- Use a simple format for now: timestamp, log level, and message.

3. What log levels and filtering behaviour do we need?
- DEBUG, INFO, WARN, ERROR + configurable minimum level.

1. Functional Requirements:

- log messages at different severity levels like DEBUG, INFO, WARN, ERROR, FATAL
- filter out messages configured below the minimum log level
- Format the log message; timestamp, log level, log name and message consistently.
- Destinations can be extensible
- The entire application should have one global logger registry.

2. Non - Functional Requirements:
- Thread safety — multiple threads should be able to log concurrently and safely access the shared logger registry/configuration.
- Extensibility — support adding new formatters and appenders (e.g. JSON formatter, database appender) without modifying existing core classes.
- Reliability — failure of one appender should not prevent other appenders from processing the log message.

3. Core entities

LogLevel(enum):  enum representing severity and ordering.
    - DEBUG = 0
    - INFO  = 1
    - WARN  = 2
    - ERROR = 3
    - FATAL = 4

Logger: Logger is responsible for accepting a log event, checking whether its level is enabled, and initiating the logging process.
    - name
    - min_lvl
    - List<LogAppender>
    - formatter

    + log(loglevel, message)
    + set_min_lvl(min_lvl)
    + info()
    + debug()
    + warn()
    + error()
    + fatal()

LogMessage:     carries the logging event data: timestamp, level, logger name, message.
    - timestamp
    - loglevel
    - message
    - logger_Name

LogFormatter -- strategy design pattern    (abstraction for converting a LogMessage into formatted output)
    + SimpleLogFormatter()
        + format(message: LogMessage)

LogAppender — abstraction/interface for destination-specific logging
    + FileAppender()
        + append(formattedMessage)
    + ConsoleAppender()
        + append(formattedMessage)
    +....

LogManager  -- orchestartor/coordinater

4. Identify relationships

Logger --uses/creates--> LogMessage
Logger --HAS-A--> LogAppender
Logger --uses--> LogFormatter

LogManager --manages--> Logger

ConsoleAppender --IS-A--> LogAppender
FileAppender --IS-A--> LogAppender

5. Coding

"""

from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime
import threading

class LogLevel(Enum):
    DEBUG = 0
    INFO  = 1
    WARN  = 2
    ERROR = 3
    FATAL = 4

class LogMessage:
    def __init__(self, logger_name, log_level: LogLevel, message):
        self.logger_name = logger_name
        self.time_stamp = datetime.now()
        self.log_level = log_level
        self.message = message

class LogFormatter(ABC):
    @abstractmethod
    def format(self, message: LogMessage):
        pass

class SimpleLogFormatter(LogFormatter):
    def format(self, message: LogMessage):
        time_stamp = message.time_stamp.strftime("%Y-%m-%d %H:%M:%S")
        return f"[{time_stamp}] [{message.log_level.name}] [{message.logger_name}] {message.message}"

class LogAppender(ABC):
    @abstractmethod
    def append(self, formatted_msg):
        pass

class ConsoleAppender(LogAppender):
    def append(self, formatted_msg):
        print(formatted_msg)

class FileAppender(LogAppender):
    def __init__(self, file_path):
        self.file_path = file_path
        self.file = open(file_path,'a')
        
    def append(self, formatted_msg):
        self.file.write(formatted_msg + "\n")

    def close(self):
        self.file.close()

class Logger:
    def __init__(self, logger_name, min_lvl: LogLevel, log_formatter: LogFormatter):
        self.logger_name = logger_name
        self.min_lvl = min_lvl
        self.log_formatter = log_formatter
        self.appenders = []
        self.lock = threading.Lock()

    def add_appender(self, appender: LogAppender):
        with self.lock:
            self.appenders.append(appender)

    def set_min_lvl(self, min_lvl: LogLevel):
        with self.lock:
            self.min_lvl = min_lvl

    def log(self, level: LogLevel, message):
        with self.lock:
            if level.value < self.min_lvl.value:
                return 
            
            # Snapshot so we don't hold the lock during potentially slow I/O
            appenders = list(self.appenders)

        log_message = LogMessage(self.logger_name, level, message)
        formatted_msg = self.log_formatter.format(log_message)

        for appender in appenders:
            try:
                appender.append(formatted_msg)
            except Exception as e:
                # One failing appender should not affect other appenders
                print(f"Appender failed: {e}")

    def debug(self, message):
        self.log(LogLevel.DEBUG, message)

    def info(self, message):
        self.log(LogLevel.INFO, message)

    def warn(self, message):
        self.log(LogLevel.WARN, message)

    def error(self, message):
        self.log(LogLevel.ERROR, message)

    def fatal(self, message):
        self.log(LogLevel.FATAL, message)

class LogManager:
    instance = None
    instance_lock = threading.Lock() # Protect Singleton initialization

    def __init__(self):
        self.loggers = {}
        self.lock = threading.Lock()  # Protect logger registry

    @classmethod
    def get_instance(cls):
        with cls.instance_lock:
            if cls.instance is None:
                cls.instance = LogManager()
            return cls.instance

    def get_logger(self, logger_name, formatter):
        with self.lock:
            if logger_name not in self.loggers:
                self.loggers[logger_name] = Logger(logger_name, LogLevel.DEBUG, formatter)

            return self.loggers[logger_name]

if __name__ == "__main__":
    formatter = SimpleLogFormatter()
    app_logger = LogManager.get_instance().get_logger("app", formatter)

    app_logger.add_appender(ConsoleAppender())
    app_logger.add_appender(FileAppender("app.logdemo"))

    app_logger.set_min_lvl(LogLevel.INFO)

    print("Testing log levels:")
    app_logger.debug("This debug message should be filtered")
    app_logger.info("Application started")
    app_logger.warn("Low memory")
    app_logger.error("Something went wrong")
    app_logger.fatal("Critical failure")

    print("Same logger instance")

    app_logger2 = LogManager.get_instance().get_logger("app", formatter)
    print(app_logger is app_logger2)