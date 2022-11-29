import sys
from os import getcwd
from pathlib import Path
from types import TracebackType
from typing import List, Type, Union

__pwd = getcwd()


def __reverse_stacktrace(ex_tb: Type[TracebackType]) -> List[Type[TracebackType]]:
    stacktrace = []
    while ex_tb:
        stacktrace.insert(0, ex_tb)
        ex_tb = ex_tb.tb_next
    return stacktrace


def __detailed_trace(ex_type: BaseException, ex_value: Union[BaseException, None], ex_tb_arg: Type[TracebackType]):
    result = []
    result.append(f" EXCEPTION {ex_type}: {ex_value}")
    result.append(" Extended stacktrace follows (most recent call last)")
    stacktrace = __reverse_stacktrace(ex_tb_arg)

    result.append("###") # This is a marker for later substitution
    result.append("Quick Stack Visualization")
    stack_level = 0
    for ex_tb in stacktrace:
        frame = ex_tb.tb_frame
        source_filename = frame.f_code.co_filename
        try:  # To prevent the cases where the file does not belong to the program/project code
            source_file_location = Path(source_filename).absolute().relative_to(__pwd)
        except ValueError:
            source_file_location = Path(source_filename)

        if "self" in frame.f_locals:
            frame_name = frame.f_locals["self"].__class__.__name__
            frame_co_name = frame.f_code.co_name
            location = f"{frame_name}.{frame_co_name}"
        else:
            location = frame.f_code.co_name

        result.append(f"{stack_level:2d}: File \"{source_file_location}\", line {ex_tb.tb_lineno}, in {location}")
        stack_level += 1

    max_len = len(max(result, key=len))
    for i, _ in enumerate(result):
        if result[i] == "###":
            result[i] = "-" * max_len
    result.insert(0, "-" * max_len)
    result.append("-" * max_len)
    result.append(f" EXCEPTION {ex_type}: {ex_value}")
    result.append("-" * max_len)
    return result


def custom_logging_callback(log_book, level, ex_type, ex_value, ex_tb):
    result = __detailed_trace(ex_type, ex_value, ex_tb)
    result = ["\n"] + result
    log_book.log(level, "\n".join(result))

    if ex_type is AssertionError:
        sys.exit(f"Assertion Failure: {ex_value}")
