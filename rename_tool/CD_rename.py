"""
CD Rename for Autodesk Maya.

A comprehensive renaming utility for Maya scene objects, providing batch
renaming, prefix/suffix management, search-and-replace, and naming convention
enforcement.

Author: Clement Daures
"""

import contextlib

import maya.cmds as cmds

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

_renaming_history: list[tuple[str, str]] = []

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

QUICK_PREFIXES: list[str] = ["C", "L", "R", "U", "D", "F", "B"]

QUICK_SUFFIXES: list[str] = [
    "grp", "skn", "jnt", "geo", "ctl", "loc",
    "pxy", "eff", "ikhandle", "ikrp", "iksc",
    "ikspr", "ikspl", "crv", "bsp", "drv", "auto", "rbn",
]

NAMING_CONVENTIONS: dict[str, str] = {
    "Rig": "RIG",
    "Animation": "ANIM",
    "Geometry": "GEO",
    "Controller": "CTRL",
}

WINDOW_ID = "dc_renameWindow"
ADVANCED_WINDOW_ID = "dc_advancedWindow"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


@contextlib.contextmanager
def _undo_chunk(name: str = "CD Rename"):
    """Context manager that collapses all enclosed Maya operations into one undo step.

    A single ``Ctrl+Z`` will revert every rename made inside the block.

    Args:
        name: Label shown in Maya's undo queue (visible via ``Edit > Undo``).

    Yields:
        Nothing -- use as a plain ``with`` block.
    """
    cmds.undoInfo(openChunk=True, chunkName=name)
    try:
        yield
    finally:
        cmds.undoInfo(closeChunk=True)


def _get_short_name(full_path: str) -> str:
    """Return the short (leaf) name from a full DAG path.

    Args:
        full_path: A Maya full DAG path string, e.g. ``"|group1|pSphere1"``.

    Returns:
        The leaf node name without any path separators.
    """
    return full_path.split("|")[-1]


def _record(original: str, renamed: str) -> None:
    """Append a rename operation to the history log.

    Args:
        original: The name or path the object had before renaming.
        renamed: The new name the object received.
    """
    _renaming_history.append((original, renamed))


def _require_selection() -> list[str] | None:
    """Return the current selection, or warn and return ``None`` if empty.

    Returns:
        A list of selected object long-name strings, or ``None`` when nothing
        is selected.
    """
    selection = cmds.ls(selection=True, long=True)
    if not selection:
        cmds.warning("No objects selected.")
        return None
    return selection


def _safe_rename(obj: str, new_name: str) -> str | None:
    """Rename *obj* to *new_name*, recording the operation on success.

    Wraps ``cmds.rename`` in a try/except so that a single failed rename does
    not abort a batch operation.

    Args:
        obj: Full DAG path (or short name) of the object to rename.
        new_name: The desired new name.

    Returns:
        The actual new name returned by Maya, or ``None`` if renaming failed.
    """
    try:
        result = cmds.rename(obj, new_name)
        _record(obj, result)
        return result
    except RuntimeError as exc:
        cmds.warning(f"Could not rename '{obj}' to '{new_name}': {exc}")
        return None


# ---------------------------------------------------------------------------
# Core renaming operations
# ---------------------------------------------------------------------------


def rename_and_number_objects() -> None:
    """Rename selected objects sequentially with optional zero-padded numbering.

    Reads UI fields:
        - ``renameTextField``: Base name.
        - ``startNumberField``: Starting index.
        - ``paddingField``: Zero-padding width.
    """
    selection = _require_selection()
    if selection is None:
        return

    base_name = cmds.textFieldGrp("renameTextField", query=True, text=True).strip()
    if not base_name:
        cmds.warning("Please enter a base name.")
        return

    start = cmds.intFieldGrp("startNumberField", query=True, value1=True)
    padding = cmds.intFieldGrp("paddingField", query=True, value1=True)

    with _undo_chunk("Rename and Number"):
        for offset, obj in enumerate(selection):
            number_str = str(start + offset).zfill(padding)
            _safe_rename(obj, f"{base_name}{number_str}")


def add_prefix_to_selection() -> None:
    """Prepend a user-defined prefix to the name of every selected object.

    Reads the ``prefixTextField`` UI field for the prefix string.
    """
    selection = _require_selection()
    if selection is None:
        return

    prefix = cmds.textFieldGrp("prefixTextField", query=True, text=True).strip()
    if not prefix:
        cmds.warning("Please enter a prefix.")
        return

    with _undo_chunk("Add Prefix"):
        for obj in selection:
            _safe_rename(obj, f"{prefix}{_get_short_name(obj)}")


def add_suffix_to_selection() -> None:
    """Append a user-defined suffix to the name of every selected object.

    Reads the ``suffixTextField`` UI field for the suffix string.
    """
    selection = _require_selection()
    if selection is None:
        return

    suffix = cmds.textFieldGrp("suffixTextField", query=True, text=True).strip()
    if not suffix:
        cmds.warning("Please enter a suffix.")
        return

    with _undo_chunk("Add Suffix"):
        for obj in selection:
            _safe_rename(obj, f"{_get_short_name(obj)}{suffix}")


def remove_first_character() -> None:
    """Remove the leading character from each selected object's name."""
    _remove_character(position="first")


def remove_last_character() -> None:
    """Remove the trailing character from each selected object's name."""
    _remove_character(position="last")


def _remove_character(position: str) -> None:
    """Internal helper that strips one character from object names.

    Args:
        position: ``"first"`` to strip the leading character, ``"last"`` to
            strip the trailing character.

    Raises:
        ValueError: If *position* is neither ``"first"`` nor ``"last"``.
    """
    if position not in ("first", "last"):
        raise ValueError(f"position must be 'first' or 'last', got '{position}'.")

    selection = _require_selection()
    if selection is None:
        return

    with _undo_chunk("Remove Character"):
      for obj in selection:
        short = _get_short_name(obj)
        if len(short) <= 1:
            cmds.warning(f"Skipping '{short}': name too short to remove a character.")
            continue

        new_name = short[1:] if position == "first" else short[:-1]
        _safe_rename(obj, new_name)


def add_quick_prefix(prefix: str) -> None:
    """Add a predefined prefix token (e.g. ``"L"``) to selected objects.

    The separator ``"_"`` is inserted automatically between the prefix and the
    existing name.

    Args:
        prefix: A short prefix token such as ``"L"``, ``"R"``, or ``"C"``.
    """
    selection = _require_selection()
    if selection is None:
        return

    with _undo_chunk(f"Quick Prefix: {prefix}"):
        for obj in selection:
            _safe_rename(obj, f"{prefix}_{_get_short_name(obj)}")


def add_quick_suffix(suffix: str) -> None:
    """Append a predefined suffix token (e.g. ``"geo"``) to selected objects.

    The separator ``"_"`` is inserted automatically between the existing name
    and the suffix.

    Args:
        suffix: A short suffix token such as ``"geo"``, ``"jnt"``, or ``"ctl"``.
    """
    selection = _require_selection()
    if selection is None:
        return

    with _undo_chunk(f"Quick Suffix: {suffix}"):
        for obj in selection:
            _safe_rename(obj, f"{_get_short_name(obj)}_{suffix}")


def search_and_replace() -> None:
    """Search for a substring in object names and replace it.

    Reads UI fields:
        - ``searchTextField``: The substring to find.
        - ``replaceTextField``: The replacement substring (may be empty).
        - ``searchReplaceOption``: Scope radio button (1 = Hierarchy,
          2 = Selected, 3 = All objects in scene).
    """
    search_term = cmds.textFieldGrp("searchTextField", query=True, text=True)
    replace_term = cmds.textFieldGrp("replaceTextField", query=True, text=True)
    option = cmds.radioButtonGrp("searchReplaceOption", query=True, select=True)

    if not search_term:
        cmds.warning("Please enter a search term.")
        return

    if option == 1:
        objects = cmds.ls(selection=True, dag=True, long=True) or []
    elif option == 2:
        objects = cmds.ls(selection=True, long=True) or []
    else:
        objects = cmds.ls(long=True) or []

    if not objects:
        cmds.warning("No objects found for the selected scope.")
        return

    pending = list(objects)
    with _undo_chunk("Search and Replace"):
        for i, obj in enumerate(pending):
            short = _get_short_name(obj)
            if search_term not in short:
                continue

            new_short = short.replace(search_term, replace_term)
            result = _safe_rename(obj, new_short)

            if result is None:
                continue

            old_path = obj
            parent_path = "|".join(obj.split("|")[:-1])
            new_path = f"{parent_path}|{result}" if parent_path else f"|{result}"

            for j in range(i + 1, len(pending)):
                if pending[j].startswith(old_path + "|"):
                    pending[j] = new_path + pending[j][len(old_path):]


# ---------------------------------------------------------------------------
# Advanced features
# ---------------------------------------------------------------------------


def refresh_history_list() -> None:
    """Repopulate the history scroll list in the Advanced Features window."""
    cmds.textScrollList("historyTextScroll", edit=True, removeAll=True)
    for old_name, new_name in _renaming_history:
        cmds.textScrollList(
            "historyTextScroll", edit=True, append=f"{old_name}  →  {new_name}"
        )


def clear_history() -> None:
    """Wipe the in-memory renaming history and refresh the UI list."""
    _renaming_history.clear()
    refresh_history_list()


def apply_naming_convention() -> None:
    """Prefix selected objects with a convention token based on the UI menu.

    Supported conventions (from ``namingConventionMenu``): Rig, Animation,
    Geometry, Controller.  Unknown convention values are silently ignored.
    """
    selection = _require_selection()
    if selection is None:
        return

    convention = cmds.optionMenuGrp("namingConventionMenu", query=True, value=True)
    token = NAMING_CONVENTIONS.get(convention)
    if token is None:
        cmds.warning(f"Unknown naming convention: '{convention}'.")
        return

    with _undo_chunk(f"Naming Convention: {convention}"):
        for obj in selection:
            _safe_rename(obj, f"{token}_{_get_short_name(obj)}")


# ---------------------------------------------------------------------------
# UI builders
# ---------------------------------------------------------------------------


def _build_rename_and_number_section() -> None:
    """Create the Rename and Number frame in the main window."""
    cmds.frameLayout(
        label="Rename and Number", collapsable=True, width=380, marginHeight=5
    )
    cmds.textFieldGrp(
        "renameTextField",
        label="Rename:",
        columnAlign=(1, "right"),
        columnWidth=[(1, 80), (2, 280)],
    )
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.intFieldGrp(
        "startNumberField",
        label="Start Number:",
        value1=1,
        columnWidth=[(1, 90), (2, 90)],
    )
    cmds.intFieldGrp(
        "paddingField", label="Padding:", value1=2, columnWidth=[(1, 90), (2, 90)]
    )
    cmds.setParent("..")
    cmds.button(
        label="Rename and Number",
        height=30,
        command=lambda _: rename_and_number_objects(),
    )
    cmds.setParent("..")


def _build_prefix_suffix_section() -> None:
    """Create the Prefix and Suffix frame in the main window."""
    cmds.frameLayout(
        label="Prefix and Suffix", collapsable=True, width=380, marginHeight=5
    )
    cmds.textFieldGrp(
        "prefixTextField",
        label="Prefix:",
        columnAlign=(1, "right"),
        columnWidth=[(1, 80), (2, 280)],
    )
    cmds.textFieldGrp(
        "suffixTextField",
        label="Suffix:",
        columnAlign=(1, "right"),
        columnWidth=[(1, 80), (2, 280)],
    )
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.button(label="Add Prefix", command=lambda _: add_prefix_to_selection())
    cmds.button(label="Add Suffix", command=lambda _: add_suffix_to_selection())
    cmds.setParent("..")
    cmds.setParent("..")


def _build_remove_characters_section() -> None:
    """Create the Remove Characters frame in the main window."""
    cmds.frameLayout(
        label="Remove Characters", collapsable=True, width=380, marginHeight=5
    )
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.button(
        label="Remove First Character", command=lambda _: remove_first_character()
    )
    cmds.button(
        label="Remove Last Character", command=lambda _: remove_last_character()
    )
    cmds.setParent("..")
    cmds.setParent("..")


def _build_quick_prefix_section() -> None:
    """Create the Quick Prefix frame in the main window."""
    cmds.frameLayout(
        label="Quick Prefix", collapsable=True, width=380, marginHeight=5
    )
    cmds.rowColumnLayout(
        numberOfColumns=5,
        columnWidth=[(i + 1, 75) for i in range(5)],
    )
    for token in QUICK_PREFIXES:
        cmds.button(
            label=token, command=lambda _, p=token: add_quick_prefix(p)
        )
    cmds.setParent("..")
    cmds.setParent("..")


def _build_quick_suffix_section() -> None:
    """Create the Quick Suffix frame in the main window."""
    cmds.frameLayout(
        label="Quick Suffix", collapsable=True, width=380, marginHeight=5
    )
    cmds.rowColumnLayout(
        numberOfColumns=5,
        columnWidth=[(i + 1, 75) for i in range(5)],
    )
    for token in QUICK_SUFFIXES:
        cmds.button(
            label=token, command=lambda _, s=token: add_quick_suffix(s)
        )
    cmds.setParent("..")
    cmds.setParent("..")


def _build_search_replace_section() -> None:
    """Create the Search and Replace frame in the main window."""
    cmds.frameLayout(
        label="Search and Replace", collapsable=True, width=380, marginHeight=5
    )
    cmds.textFieldGrp(
        "searchTextField",
        label="Search:",
        columnAlign=(1, "right"),
        columnWidth=[(1, 80), (2, 280)],
    )
    cmds.textFieldGrp(
        "replaceTextField",
        label="Replace:",
        columnAlign=(1, "right"),
        columnWidth=[(1, 80), (2, 280)],
    )
    cmds.radioButtonGrp(
        "searchReplaceOption",
        numberOfRadioButtons=3,
        label="Scope:",
        labelArray3=["Hierarchy", "Selected", "All"],
        select=2,
    )
    cmds.button(
        label="Apply Search and Replace",
        height=30,
        command=lambda _: search_and_replace(),
    )
    cmds.setParent("..")


# ---------------------------------------------------------------------------
# Window entry points
# ---------------------------------------------------------------------------


def open_advanced_features_window() -> None:
    """Open (or refresh) the Advanced Features secondary window.

    The window provides:
        - A scrollable renaming-history log with Refresh and Clear actions.
        - An option-menu for applying built-in naming conventions.
    """
    if cmds.window(ADVANCED_WINDOW_ID, exists=True):
        cmds.deleteUI(ADVANCED_WINDOW_ID)

    window = cmds.window(
        ADVANCED_WINDOW_ID,
        title="Advanced Features",
        widthHeight=(400, 400),
        sizeable=True,
    )
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

    cmds.frameLayout(label="Renaming History", collapsable=True, width=380)
    cmds.textScrollList(
        "historyTextScroll", numberOfRows=8, allowMultiSelection=False, height=150
    )
    cmds.rowColumnLayout(numberOfColumns=2, columnWidth=[(1, 180), (2, 180)])
    cmds.button(label="Refresh History", command=lambda _: refresh_history_list())
    cmds.button(label="Clear History", command=lambda _: clear_history())
    cmds.setParent("..")
    cmds.setParent("..")

    cmds.frameLayout(
        label="Automated Naming Conventions", collapsable=True, width=380
    )
    cmds.optionMenuGrp(
        "namingConventionMenu", label="Convention:", columnAlign=(1, "right")
    )
    for convention in NAMING_CONVENTIONS:
        cmds.menuItem(label=convention)
    cmds.button(
        label="Apply Convention", command=lambda _: apply_naming_convention()
    )
    cmds.setParent("..")

    cmds.showWindow(window)


def clementdaures_rename_tool() -> None:
    """Build and display the main CD Rename window.

    Clears any pre-existing instance of the window before creating a new one,
    ensuring a clean UI state on every launch.
    """
    if cmds.window(WINDOW_ID, exists=True):
        cmds.deleteUI(WINDOW_ID)

    window = cmds.window(
        WINDOW_ID,
        title="CD Rename",
        widthHeight=(400, 600),
        sizeable=True,
    )
    cmds.columnLayout(adjustableColumn=True, rowSpacing=10, columnAlign="center")

    _build_rename_and_number_section()
    cmds.separator(height=20, style="in")

    _build_prefix_suffix_section()
    cmds.separator(height=20, style="in")

    _build_remove_characters_section()
    cmds.separator(height=20, style="in")

    _build_quick_prefix_section()
    cmds.separator(height=20, style="in")

    _build_quick_suffix_section()
    cmds.separator(height=20, style="in")

    _build_search_replace_section()
    cmds.separator(height=20, style="in")

    cmds.button(
        label="Advanced Features",
        height=40,
        command=lambda _: open_advanced_features_window(),
    )

    cmds.showWindow(window)


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

if __name__=="__main__":
    clementdaures_rename_tool()