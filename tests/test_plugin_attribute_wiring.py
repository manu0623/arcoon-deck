"""Every attribute ``Plugin`` reads must be one it actually sets.

Measured on the reference Deck at 0.48.51: the PC save handlers ran their work
through ``self._loop``, while the plugin's event loop is ``self.loop`` — so the
first launch answered the gate with ``pre-launch sync failed: Python Exception``
and the Saves row logged ``getSaveFolder failed: Python Exception``, with every
in-process check of the service having passed. The break was entirely in the
handlers, which no test could import (decky is not available off the Deck).

This reads ``main.py`` as text instead of importing it, so it runs anywhere and
fails on exactly that mistake: a ``self.x`` that is neither assigned somewhere in
the class, declared as a class attribute, nor a method of it.
"""

from __future__ import annotations

import ast
from pathlib import Path

MAIN_PY = Path(__file__).resolve().parent.parent / "main.py"


def _plugin_class() -> ast.ClassDef:
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef)]
    plugin = next((node for node in classes if node.name == "Plugin"), None)
    assert plugin is not None, "main.py no longer defines class Plugin"
    return plugin


def _module_level_names() -> set[str]:
    """Names the module defines, which a method may legitimately read off ``self``."""
    names: set[str] = set()
    tree = ast.parse(MAIN_PY.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    names.add(target.id)
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            names.add(node.target.id)
    return names


def test_every_self_attribute_is_one_the_class_sets() -> None:
    plugin = _plugin_class()
    assigned: set[str] = set()
    used: set[str] = set()
    for node in ast.walk(plugin):
        if not (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)):
            continue
        if node.value.id != "self":
            continue
        if isinstance(node.ctx, (ast.Store, ast.Del)):
            assigned.add(node.attr)
        else:
            used.add(node.attr)
    for node in plugin.body:
        # Class-level attributes: ``_MIN_REQUIRED_VERSION = (4, 9, 0)`` and
        # ``loop: asyncio.AbstractEventLoop`` — declared on the class, so a method
        # reading them off ``self`` is legitimate.
        if isinstance(node, ast.Assign):
            assigned.update(target.id for target in node.targets if isinstance(target, ast.Name))
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            assigned.add(node.target.id)
    methods = {
        node.name for node in plugin.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    }

    unset = sorted(used - assigned - methods - _module_level_names())

    assert unset == [], (
        "Plugin reads attributes it never sets (a handler would raise AttributeError at runtime): "
        + ", ".join(unset)
    )
