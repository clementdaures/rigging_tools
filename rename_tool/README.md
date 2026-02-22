# CD Rename Tool

A batch renaming utility for Autodesk Maya. Select objects, apply a rule, done.

---

## Features

| Section | What it does |
|---|---|
| **Rename and Number** | Rename selected objects to a base name with zero-padded incremental numbering |
| **Prefix / Suffix** | Add a custom prefix or suffix to every selected object |
| **Remove Characters** | Strip the first or last character from every selected object's name |
| **Quick Prefix** | One-click side tokens — `C`, `L`, `R`, `U`, `D`, `F`, `B` |
| **Quick Suffix** | One-click type tokens — `geo`, `jnt`, `ctl`, `grp`, `crv`, and more |
| **Search and Replace** | Find and replace a substring across selected objects, their hierarchy, or the entire scene |
| **Advanced Features** | Session rename history log and one-click naming convention prefixes |

---

## Installation

1. Open the **Script Editor** — `Windows > General Editors > Script Editor`.
2. Create a new **Python** tab.
3. Paste the contents of `cd_rename_tool.py` into the tab.
4. Press **Ctrl + Enter** to execute, or save it to a shelf button for repeat use.

> **Shelf button tip:** Highlight all the code, then middle-mouse-drag it onto a shelf to create a persistent button.

---

## Usage

### Rename and Number

Enter a base name (e.g. `leg_jnt`), set a start number and padding width, select your objects, and click **Rename and Number**. Objects are renamed in selection order:

```
leg_jnt01, leg_jnt02, leg_jnt03 …
```

### Prefix and Suffix

Type a string into the **Prefix** or **Suffix** field and click the matching button. The string is appended directly with no automatic separator — include one yourself if needed (e.g. `L_`).

For standard pipeline tokens, use the **Quick Prefix** and **Quick Suffix** buttons instead. These always insert an underscore separator automatically:

```
L_pCube1,  pCube1_geo
```

### Remove Characters

Click **Remove First Character** or **Remove Last Character** to strip one character from every selected object's name. Objects with single-character names are skipped with a warning.

### Search and Replace

| Field | Purpose |
|---|---|
| **Search** | Substring to find (case-sensitive) |
| **Replace** | Substring to substitute (leave empty to delete) |
| **Scope** | `Selected` — current selection only · `Hierarchy` — selection and all descendants · `All` — every object in the scene |

The rename walks top-down so parent paths stay valid when both a parent and its children match the search term.

### Advanced Features

**Renaming History** logs every rename made during the current session as `old_name → new_name`. Use **Refresh History** to update the list and **Clear History** to wipe it.

**Automated Naming Conventions** prepends a standard token to every selected object:

| Convention | Prefix applied |
|---|---|
| Rig | `RIG_` |
| Animation | `ANIM_` |
| Geometry | `GEO_` |
| Controller | `CTRL_` |

---

## Notes

- All operations act on the **current selection** at the moment the button is clicked — change your selection before applying each rule.
- History is in-memory only and is lost when Maya is closed or the script is re-executed.

---

## License

Free to use for personal and educational projects. Please do not redistribute without permission.

## Contact

clementdaures.contact@gmail.com