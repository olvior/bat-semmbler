import sys
from dataclasses import dataclass

import file_io
from exceptions import InternalCompilerError
from memory.register import Register
from parser_stuff.inbuilt_functions import deal_with_inbuilt_function, deal_with_if


@dataclass
class CompilerMetadata:
    if_stack: list[str]
    halted: bool


def main() -> None:
    argv = sys.argv

    if len(argv) < 3:
        print("Usage: python3 main.py path/to/file.hb path/to/output.as\n"
              "Docs to .hb language can be found in LANGUAGE_README.md")
        return

    file_io.in_file_path = argv[1]
    file_io.out_file_path = argv[2]

    file_io.create_out_file()
    file_io.append_to_out("// Generated by an assembler I wrote in python")
    file_io.append_to_out("ldi r15 248")

    compiler_metadata = CompilerMetadata(if_stack=[], halted=False)

    lines = file_io.read_lines_from_input()

    for line_number, line in enumerate(lines):
        interpret_line(compiler_metadata, line, line_number)

    if not compiler_metadata.halted:
        file_io.append_to_out("HLT")


def interpret_line(compiler_metadata: CompilerMetadata, line: str, line_number: int) -> None:
    if line.startswith("//"):
        # we can skip the comment
        return

    line_segments = line.split()
    start = line_segments.pop(0)

    try:
        deal_with_inbuilt_function(start, line_segments)
        return
    except KeyError:
        pass
    except InternalCompilerError:
        print(f"current line: {line}")
        raise

    if start == "if":
        deal_with_if(line_segments, line_number, compiler_metadata.if_stack)

    elif start == "endif":
        file_io.append_to_out(compiler_metadata.if_stack.pop())

    elif start[0] == ".":
        file_io.append_to_out(line)

    elif start == "return":
        file_io.append_to_out("RET")

    elif start == "HLT" or start == "halt":
        file_io.append_to_out("HLT")
        compiler_metadata.halted = True


if __name__ == '__main__':
    main()
