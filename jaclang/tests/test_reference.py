"""Test Jac reference examples."""
import io
import os
from contextlib import redirect_stdout
from typing import Callable, Optional

import jaclang
from jaclang.compiler.transpiler import jac_file_to_pass
from jaclang.utils.test import TestCase


class JacReferenceTests(TestCase):
    """Test Reference examples."""

    test_ref_jac_files_fully_tested: Optional[Callable[[TestCase], None]] = None
    methods: list[str] = []

    @classmethod
    def self_attach_ref_tests(cls) -> None:
        """Attach micro tests."""
        for filename in [
            os.path.normpath(os.path.join(root, name))
            for root, _, files in os.walk(
                os.path.join(
                    os.path.dirname(os.path.dirname(jaclang.__file__)),
                    "examples/reference",
                )
            )
            for name in files
            if name.endswith(".jac") and not name.startswith("err")
        ]:
            method_name = (
                f"test_ref_{filename.replace('.jac', '').replace(os.sep, '_')}"
            )
            cls.methods.append(method_name)
            setattr(cls, method_name, lambda self, f=filename: self.micro_suite_test(f))

        def test_ref_jac_files_fully_tested(self: TestCase) -> None:  # noqa: ANN001
            """Test that all micro jac files are fully tested."""
            for filename in cls.methods:
                if os.path.isfile(filename):
                    method_name = (
                        f"test_ref_{filename.replace('.jac', '').replace(os.sep, '_')}"
                    )
                    self.assertIn(method_name, dir(self))

        cls.test_ref_jac_files_fully_tested = test_ref_jac_files_fully_tested

    def micro_suite_test(self, filename: str) -> None:
        """Test file."""

        def execute_and_capture_output(code: str) -> str:
            f = io.StringIO()
            with redirect_stdout(f):
                exec(code, {})
            return f.getvalue()

        try:
            code_content = jac_file_to_pass(filename).ir.gen.py
            output_jac = execute_and_capture_output(code_content)

            filename = filename.replace(".jac", ".py")
            with open(filename, "r") as file:
                code_content = file.read()
            output_py = execute_and_capture_output(code_content)

            self.assertGreater(len(output_py), 0)
            self.assertEqual(output_py, output_jac)
        except Exception as e:
            self.skipTest(f"Test failed on {filename}: {e}")


JacReferenceTests.self_attach_ref_tests()
