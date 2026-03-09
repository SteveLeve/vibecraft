"""Tests for code_sandbox.py -- safety and functionality."""

import pytest

from vibecraft.code_sandbox import execute_command_generator
from vibecraft.exceptions import CodeSandboxError


# ---------------------------------------------------------------------------
# Functionality tests
# ---------------------------------------------------------------------------


def test_simple_loop():
    code = """
commands = []
for x in range(100, 110):
    commands.append(f"/setblock {x} 64 200 stone")
"""
    result = execute_command_generator(code)
    assert len(result) == 10
    assert result[0] == "/setblock 100 64 200 stone"


def test_function_definition_basic():
    code = """
commands = []

def fill(x1, z1, x2, z2, block):
    commands.append(f"/fill {x1} 64 {z1} {x2} 64 {z2} {block}")

fill(0, 0, 9, 9, "stone")
"""
    result = execute_command_generator(code)
    assert len(result) == 1
    assert result[0] == "/fill 0 64 0 9 64 9 stone"


def test_function_definition_with_return():
    code = """
commands = []

def block_for(x, z):
    if (x + z) % 2 == 0:
        return "white_concrete"
    return "black_concrete"

for x in range(4):
    for z in range(4):
        commands.append(f"/setblock {x} 64 {z} {block_for(x, z)}")
"""
    result = execute_command_generator(code)
    assert len(result) == 16
    assert "white_concrete" in result[0]
    assert "black_concrete" in result[1]


def test_helper_functions_called_from_helper():
    code = """
commands = []

def fill(x1, y1, x2, y2, block):
    commands.append(f"/fill {x1} {y1} 0 {x2} {y2} 0 {block}")

def rect(x, y, w, h, block):
    fill(x, y, x + w - 1, y + h - 1, block)

rect(0, 64, 10, 5, "oak_planks")
"""
    result = execute_command_generator(code)
    assert len(result) == 1
    assert result[0] == "/fill 0 64 0 9 68 0 oak_planks"


def test_random_available():
    code = """
commands = []
random.seed(42)
for i in range(5):
    x = random.randint(0, 100)
    commands.append(f"/setblock {x} 64 0 stone")
"""
    result = execute_command_generator(code)
    assert len(result) == 5


def test_random_deterministic():
    code = """
commands = []
random.seed(42)
commands.append(f"/setblock {random.randint(0, 1000)} 64 0 stone")
"""
    result1 = execute_command_generator(code)
    result2 = execute_command_generator(code)
    assert result1 == result2


def test_random_choice():
    code = """
commands = []
blocks = ["stone", "dirt", "sand"]
random.seed(1)
for i in range(3):
    commands.append(f"/setblock {i} 64 0 {random.choice(blocks)}")
"""
    result = execute_command_generator(code)
    assert len(result) == 3


def test_math_functions_available():
    code = """
commands = []
for angle_deg in range(0, 360, 90):
    angle = radians(angle_deg)
    x = int(cos(angle) * 5)
    z = int(sin(angle) * 5)
    commands.append(f"/setblock {x} 64 {z} stone")
"""
    result = execute_command_generator(code)
    assert len(result) == 4


# ---------------------------------------------------------------------------
# Security tests -- all must raise CodeSandboxError
# ---------------------------------------------------------------------------


def test_import_blocked():
    code = "commands = []\nimport os"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_import_inside_function_blocked():
    code = """
commands = []
def evil():
    import os
evil()
"""
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_eval_blocked():
    code = "commands = []\neval('1+1')"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_exec_blocked():
    code = "commands = []\nexec('pass')"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_dunder_class_blocked():
    code = "commands = []\nx = ''.__class__"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_dunder_globals_blocked():
    code = "commands = []\nx = ().__class__.__bases__[0].__subclasses__()"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_lambda_blocked():
    code = "commands = []\nf = lambda x: x"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_getattr_blocked():
    code = "commands = []\ngetattr(str, 'upper')"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_dangerous_command_stop_blocked():
    code = "commands = ['/stop']"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_dangerous_command_ban_blocked():
    code = "commands = ['/ban player']"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_range_too_large_blocked():
    code = "commands = []\nfor i in range(1000000): pass"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)


def test_dunder_name_blocked():
    code = "commands = []\n__name__"
    with pytest.raises(CodeSandboxError):
        execute_command_generator(code)
