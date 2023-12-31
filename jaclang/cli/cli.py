"""Command line interface tool for the Jac language."""
import os
import shutil
import unittest

from jaclang import jac_import as __jac_import__
from jaclang.cli.cmdreg import CommandRegistry, CommandShell
from jaclang.compiler.constant import Constants
from jaclang.utils.lang_tools import AstTool


cmd_registry = CommandRegistry()


@cmd_registry.register
def run(filename: str, main: bool = True) -> None:
    """Run the specified .jac file.

    :param filename: The path to the .jac file.
    :param main: If True, use '__main__' as the module name, else use the actual module name.
    """
    if filename.endswith(".jac"):
        base, mod = os.path.split(filename)
        base = base if base else "./"
        mod = mod[:-4]
        __jac_import__(
            target=mod, base_path=base, override_name="__main__" if main else None
        )
    else:
        print("Not a .jac file.")


@cmd_registry.register
def enter(filename: str, entrypoint: str, args: list) -> None:
    """Run the specified entrypoint function in the given .jac file.

    :param filename: The path to the .jac file.
    :param entrypoint: The name of the entrypoint function.
    :param args: Arguments to pass to the entrypoint function.
    """
    if filename.endswith(".jac"):
        base, mod = os.path.split(filename)
        base = base if base else "./"
        mod = mod[:-4]
        mod = __jac_import__(target=mod, base_path=base)
        if not mod:
            print("Errors occurred while importing the module.")
            return
        else:
            getattr(mod, entrypoint)(*args)
    else:
        print("Not a .jac file.")


@cmd_registry.register
def test(filename: str) -> None:
    """Run the test suite in the specified .jac file.

    :param filename: The path to the .jac file.
    """
    if filename.endswith(".jac"):
        base, mod = os.path.split(filename)
        base = base if base else "./"
        mod = mod[:-4]
        mod = __jac_import__(target=mod, base_path=base)
        unittest.TextTestRunner().run(mod.__jac_suite__)
    else:
        print("Not a .jac file.")


@cmd_registry.register
def ast_tool(tool: str, args: list = None) -> None:
    """Run the specified AST tool with optional arguments.

    :param tool: The name of the AST tool to run.
    :param args: Optional arguments for the AST tool.
    """
    if hasattr(AstTool, tool):
        try:
            if args and len(args):
                print(getattr(AstTool(), tool)(*args))
            else:
                print(getattr(AstTool(), tool)())
        except Exception:
            print(f"Error while running ast tool {tool}, check args.")
    else:
        print(f"Ast tool {tool} not found.")


@cmd_registry.register
def clean() -> None:
    """Remove the __jac_gen__ , __pycache__ folders.

    from the current directory recursively.
    """
    current_dir = os.getcwd()
    py_cache = "__pycache__"
    for root, dirs, _files in os.walk(current_dir, topdown=True):
        for folder_name in dirs[:]:
            if folder_name == Constants.JAC_GEN_DIR or folder_name == py_cache:
                folder_to_remove = os.path.join(root, folder_name)
                shutil.rmtree(folder_to_remove)
                print(f"Removed folder: {folder_to_remove}")
    print("Done cleaning.")


def start_cli() -> None:
    """
    Start the command line interface.

    Returns:
    - None
    """
    parser = cmd_registry.parser
    args = parser.parse_args()
    command = cmd_registry.get(args.command)
    if command:
        args = vars(args)
        args.pop("command")
        ret = command.call(**args)
        if ret:
            print(ret)
    else:
        CommandShell(cmd_registry).cmdloop()


if __name__ == "__main__":
    start_cli()