import datetime
import traceback
import sys

class Logger:
    """
    ## Basic logging utility class.

    ### Supports:
        - Logging to any stdout;
            - if a string is passed, it will be treated as a file path.
        - Colored messages (Only if stdout is sys.stdout)
        - Different log levels (test, debug, info, warning, error)

    ### Usage:
        - logger = Logger(loglevel="debug", stdout="logfile.txt") # Or any other stdout like sys.stdout
        - logger.Test("This is a test message")  
        - logger.Debug("This is a debug message")
        - logger.Info("This is an info message")
        - logger.Warning("This is a warning message")
        - logger.Error("This is an error message")

    ### Special functions:
    ##### logger.Except(func, exceptions=[Exception], *args, **kwargs)

        - Used for logging exceptions and returning a value
        - Either returns the value of the function or the value of the exception
        - Raises exception if the exception is not in the exceptions list.


    ##### logger.ExceptWithSolve(func, exceptions: dict, *args, **kwargs)

        - Used for logging exceptions and returning a value
        - When a exception is raised, it will try to solve it with the exception's class name as a key in the exceptions dict.
            - To learn about exception dict, see the docstring of logger.ExceptWithSolve
        - Either returns the value of the function or the value of the exception
        - Raises exception if the exception is not in the exceptions list.
    """

    reset  = "\033[0m"
    error    = "\033[31m"
    warning  = "\033[33m"
    debug  = "\033[32m"
    info   = "\033[34m"
    test = "\033[35m"
    stdout = sys.stdout
    use_color = True

    def __init__(self, loglevel=0, stdout=sys.stdout, use_color: bool=True):
        """loglevel: 0 = test, 1 = debug, 2 = info, 3 = warning, 4 = error"""
        if isinstance(loglevel, int):
            self.__loglevel = loglevel
        else:
            if isinstance(loglevel, str):
                self.__loglevel = self.getlevelfromstr(loglevel)
        if isinstance(stdout, str):
            self.stdout = open(stdout, "a")
        else:
            self.stdout = stdout
        self.use_color = use_color

    def __write(self, msg: str):
        self.stdout.write(msg + "\n")

    def getlevelfromstr(self, loglevel: str):
        """Converts a string to a loglevel"""
        if isinstance(loglevel, str):
            match loglevel.lower():
                case "error":
                    loglevel = 4
                case "warning":
                    loglevel = 3
                case "info":
                    loglevel = 2
                case "debug":
                    loglevel = 1
                case "test":
                    loglevel = 0
                case _:
                    loglevel = 0
            return loglevel
        else:
            raise TypeError("loglevel must be a string to call getlevelfromstr")

    def craft(self, msg, loglevel: str, prefix: str="", suffix: str=""):
        """Crafts a (maybe colored) message with a prefix and suffix"""
        nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Get the color
        if not hasattr(self, loglevel.lower()):
            raise AttributeError("Invalid loglevel")
        # If stdout is not sys.stdout, we don't want to color the output.
        if sys.stdout != self.stdout or not self.use_color:
            return f"{prefix}[{nowtime} {loglevel.upper()}] {msg}{suffix}"
        return f"{getattr(self, loglevel.lower())}{prefix}[{nowtime} {loglevel.upper()}] {msg}{suffix}{self.reset}"

    def log(self, msg, loglevel: str, prefix: str="", suffix: str=""):
        if self.getlevelfromstr(loglevel.lower()) >= self.__loglevel:
            self.__write(self.craft(msg, loglevel, prefix=prefix, suffix=suffix))

    def Except(self, func, exceptions=[Exception], *args, **kwargs):
        """
        Used for logging exceptions and returning a value
        Either returns the value of the function or the value of the exception

        Raises exception if the exception is not in the exceptions list.
        Returns: (Exception|Data), OK 
        """
        excepted: Exception = None
        try:
            retval = func(*args, **kwargs)
        except Exception as e:
            flag = False
            for exception in exceptions:
                if isinstance(e, exception):
                    flag = True
                    excepted = e
                    break
            if not flag:
                raise e
        else:
            return retval, True
        finally:
            self.log(
                f"""Function raised an exception:\n""" + 
                f"""  Function: {func.__name__}\n""" + 
                f"""  Exception: {excepted.__class__.__name__}\n""" + 
                f"""  Args: {excepted.args}\n""" + 
                f"""  Traceback:    V-V-V-V-V-V-V\n\n""" + 
                "\n".join(traceback.format_tb(excepted.__traceback__)),
                loglevel="error", 
                prefix="-" * 40 + "\n",
                suffix="\n" + "-" * 40
            )
            return excepted, False
        
    def ExceptWithSolve(self, func, exceptions: dict, *args, **kwargs):
        """
        Logs exceptions if any occurred, provides a way to run code based on exception thrown.
        Standart exceptions dictionary looks like:
        
        {
            ValueError:{
                "func": func,
                "args": args, # Optional
                "kwargs": kwargs # Optional
            },
            TypeError:{
                "func": func,
                "args": args, # Optional
                "kwargs": kwargs # Optional
            }
        }
        :return: (DATA)
        """
        exception_list = exceptions.keys()
        data, ok = self.Except(func, exception_list, *args, **kwargs)
        if not ok:
            for exception in exceptions:
                if isinstance(data, exception):
                    args = exceptions[exception].get("args", [])
                    kwargs = exceptions[exception].get("kwargs", {})
                    new_data = exceptions[exception]["func"](*args, **kwargs)
                    return new_data
        else:
            return data

    def Error(self, msg):
        """Used for logging error messages"""
        self.log(msg, "error")

    def Warning(self, msg):
        """Used for logging warning messages, does not nescicarily mean exception"""
        self.log(msg, "warning")

    def Info(self, msg):
        '''Used for logging generic info messages'''
        self.log(msg, "info")

    def Debug(self, msg):
        """Used for logging debug messages"""
        self.log(msg, "debug")

    def Test(self, msg):
        """Used for logging test messages"""
        self.log(msg, "test")
