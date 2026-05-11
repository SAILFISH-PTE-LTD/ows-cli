"""Generate docs/sdk.md from source docstrings.

Run from project root:
    python scripts/generate_sdk_doc.py

Reads docstrings from ows/*.py and ows/api/*.py, generates a structured
Markdown SDK reference at docs/sdk.md.  Manual content blocks (code
examples, narrative) are preserved across runs via HTML comment markers.
"""

import ast
import importlib
import inspect
import re
import textwrap
from dataclasses import fields as dc_fields, is_dataclass, MISSING
from pathlib import Path
from typing import get_type_hints, TypeVar

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "sdk.md"

# --- Modules to document ---
API_MODULES = {
    "Planet": "ows.api.planet",
    "Product": "ows.api.product",
    "Order": "ows.api.order",
    "Bill": "ows.api.bill",
}

CORE_MODULES = {
    "OwsClient": "ows.client",
    "AuthSession": "ows.auth",
    "Config": "ows.config",
}

MODEL_MODULE = "ows.models"

# Models to exclude from generated doc (internal / deploy)
_EXCLUDE_MODELS = {
    "VpsLoginInfo", "DeployRequest", "DeployResult",
}


# ============================================================================
# Markdown helpers
# ============================================================================

def _hdr(level: int, text: str) -> str:
    return f"{'#' * level} {text}\n"


def _table(headers: list[str], rows: list[list[str]], colaligns: list[str] | None = None) -> str:
    """Render a GitHub-flavoured Markdown table."""
    lines = []
    lines.append("| " + " | ".join(headers) + " |")
    if colaligns:
        sep = "| " + " | ".join(f":{a}" if a else "---" for a in colaligns) + " |"
    else:
        sep = "| " + " | ".join("---" for _ in headers) + " |"
    lines.append(sep)
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines) + "\n"


def _code(lang: str, body: str) -> str:
    body = textwrap.dedent(body).strip()
    return f"```{lang}\n{body}\n```\n"


def _inline_code(text: str) -> str:
    return f"`{text}`"


def _escape_pipe(text: str) -> str:
    return text.replace("|", r"\|")


# ============================================================================
# Docstring helpers
# ============================================================================

def _first_sentence(doc: str | None) -> str:
    """Extract the first sentence from a docstring."""
    if not doc:
        return ""
    doc = inspect.cleandoc(doc)
    # Stop at blank line, "Args:", "Returns:", "Raises:", "Fields:"
    for line in doc.split("\n"):
        line = line.strip()
        if not line:
            continue
        if line.endswith(":") and line[:-1] in ("Args", "Returns", "Raises", "Fields", "Fields"):
            continue
        if line.startswith("Note:"):
            continue
        return line
    return ""


def _get_type_name(annotation) -> str:
    """Return a readable string for a type annotation."""
    if annotation is None or annotation is inspect.Parameter.empty:
        return ""
    origin = getattr(annotation, "__origin__", None)
    if origin is not None:
        args = getattr(annotation, "__args__", ())
        origin_name = origin.__name__ if hasattr(origin, "__name__") else str(origin)
        if args:
            arg_names = []
            for a in args:
                if hasattr(a, "__name__"):
                    arg_names.append(a.__name__)
                elif isinstance(a, TypeVar):
                    arg_names.append(a.__name__)
                else:
                    arg_names.append(str(a))
            return f"{origin_name}[{', '.join(arg_names)}]"
        return origin_name
    if hasattr(annotation, "__name__"):
        return annotation.__name__
    return str(annotation)


def _format_params(params: list[tuple[str, inspect.Parameter]]) -> str:
    """Format parameter list as `(param: Type, ...)`."""
    if not params:
        return "()"
    parts = []
    for _, p in params:
        ptype = _get_type_name(p.annotation)
        if p.default is not inspect.Parameter.empty:
            parts.append(f"{p.name}: {ptype} = {p.default!r}")
        else:
            parts.append(f"{p.name}: {ptype}")
    return "(" + ", ".join(parts) + ")"


# ============================================================================
# Section: API methods
# ============================================================================

def _generate_api_section(name: str, module_path: str) -> str:
    """Generate a Markdown section for an API class."""
    mod = importlib.import_module(module_path)
    cls_name = f"{name}API"
    cls = getattr(mod, cls_name)
    cls_doc = inspect.getdoc(cls) or ""

    lines = [f"## {cls_name}\n", f"{cls_doc}\n"]

    for mname, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if mname.startswith("_"):
            continue
        doc = inspect.getdoc(method) or ""
        sig = inspect.signature(method)
        params = [(n, p) for n, p in sig.parameters.items() if n != "self"]
        rtype = _get_type_name(get_type_hints(method).get("return", ""))

        param_lines = []
        for _, p in params:
            ptype = _get_type_name(p.annotation)
            if p.default is not inspect.Parameter.empty:
                param_lines.append(f"**{p.name}** ({ptype}, default={p.default!r})")
            else:
                param_lines.append(f"**{p.name}** ({ptype})")

        lines.append(f"### `{mname}`\n")
        summary = _first_sentence(doc)
        if summary:
            lines.append(f"{summary}\n")

        # Signature
        sig_str = f"{cls_name}.{mname}{_format_params(params)}"
        if rtype:
            sig_str += f" → {rtype}"
        lines.append(_code("python", sig_str))
        lines.append("")

        # Parameters table
        if param_lines:
            param_desc = _extract_section(doc, "Args")
            rows = []
            for pline in param_lines:
                m = re.search(r"\*\*(.+?)\*\*", pline)
                key = m.group(1) if m else ""
                desc = param_desc.get(key, "")
                rows.append([pline, desc if desc else "-"])
            lines.append(_table(["Parameter", "Description"], rows))
            lines.append("")

        # Returns
        returns = _extract_section(doc, "Returns")
        if returns:
            lines.append("**Returns:**")
            for v in returns.values():
                lines.append(f"- {v}")
            lines.append("")

        # Raises
        raises = _extract_section(doc, "Raises")
        if raises:
            lines.append("**Raises:**")
            for k, v in raises.items():
                lines.append(f"- `{k}`: {v}")
            lines.append("")

    return "\n".join(lines)


def _extract_section(doc: str | None, heading: str) -> dict[str, str]:
    """Parse a ``heading:`` section from a docstring into a dict.

    Supports two formats:

    1. ``key: description`` one-per-line
    2. ``key (type): description`` for typed keys
    """
    if not doc:
        return {}
    doc = inspect.cleandoc(doc)
    in_section = False
    result = {}
    current_key = None
    current_val: list[str] = []

    for line in doc.split("\n"):
        stripped = line.strip()
        if not stripped:
            if current_key is not None:
                result[current_key] = " ".join(current_val)
                current_key = None
                current_val = []
            continue
        # Start of target section
        if not in_section and stripped.rstrip(":") == heading:
            in_section = True
            continue
        # Next section heading ends current section
        if in_section and re.match(r"^[A-Z][a-z]+:$", stripped):
            if current_key is not None:
                result[current_key] = " ".join(current_val)
            break
        if in_section:
            # key: value line
            m = re.match(r"^(\w[\w._]+)\s*(?:\(.*?\))?\s*:\s*(.*)", stripped)
            if m:
                if current_key is not None:
                    result[current_key] = " ".join(current_val)
                current_key = m.group(1)
                current_val = [m.group(2)] if m.group(2) else []
            elif current_key is not None:
                current_val.append(stripped)

    if current_key is not None:
        result[current_key] = " ".join(current_val)
    return result


# ============================================================================
# Section: Models
# ============================================================================

def _generate_models_section() -> str:
    """Generate documentation for all dataclass models."""
    mod = importlib.import_module(MODEL_MODULE)
    lines = [_hdr(2, "Models")]

    # Collect dataclasses, preserve definition order
    with open(ROOT / "ows" / "models.py", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source)
    model_order = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ClassDef):
            for dec in node.decorator_list:
                if isinstance(dec, ast.Name) and dec.id == "dataclass":
                    if node.name not in _EXCLUDE_MODELS:
                        model_order.append(node.name)
                    break

    for name in model_order:
        cls = getattr(mod, name, None)
        if cls is None:
            continue
        doc = inspect.getdoc(cls) or ""
        summary = _first_sentence(doc)

        lines.append(f"### `{name}`\n")
        if summary:
            lines.append(f"{summary}\n")

        # Parse Fields section from docstring
        field_descs = _extract_section(doc, "Fields")

        # Build table from actual dataclass fields
        hints = get_type_hints(cls) if hasattr(cls, "__dataclass_fields__") else {}
        rows = []
        for fdef in dc_fields(cls):
            ftype = _get_type_name(hints.get(fdef.name, fdef.type))
            # Determine default display
            if fdef.default is not MISSING:
                default = repr(fdef.default) if fdef.default != "" else '""'
            elif fdef.default_factory is not MISSING:
                default = "(factory)"
            else:
                default = "*(required)*"
            desc = field_descs.get(fdef.name, "-")
            rows.append([f"`{fdef.name}`", ftype, default, desc])

        lines.append(_table(["Field", "Type", "Default", "Description"], rows))
        lines.append("")

    return "\n".join(lines)


# ============================================================================
# Section: Quick Start / Core
# ============================================================================

def _generate_core_section() -> str:
    """Generate the Quick Start content."""
    return textwrap.dedent("""\
    ## Quick Start

    ```python
    from ows.client import OwsClient

    # From config file
    client = OwsClient.from_config("config.json")

    # From environment variables (OWS_APP_ID / OWS_APP_SECRET)
    client = OwsClient.from_config()   # config.json not found → env vars
    ```
    """)


def _generate_errors_section() -> str:
    """Generate error handling documentation."""
    mod = importlib.import_module("ows.errors")
    lines = [_hdr(2, "Error Handling")]

    for ename in ("OwsError", "AuthError", "APIError", "NetworkError"):
        cls = getattr(mod, ename, None)
        if cls is None:
            continue
        doc = inspect.getdoc(cls) or ""
        lines.append(f"- **`{ename}`** — {_first_sentence(doc)}")

    lines.append("")
    lines.append(_code("python", """\
from ows.errors import AuthError, APIError, NetworkError

try:
    client.planet.create(req)
except AuthError:
    print("Credentials invalid or expired")
except APIError as e:
    print(f"API error [{e.code}]: {e.message}")
except NetworkError:
    print("Network connection failed")
"""))
    return "\n".join(lines) + "\n"


# ============================================================================
# Main
# ============================================================================

def generate():
    """Generate docs/sdk.md from source docstrings."""
    parts = []

    # Title
    parts.append("# ows SDK Reference\n")
    parts.append("Auto-generated from source docstrings.  Run "
                  "`python scripts/generate_sdk_doc.py` to update.\n")

    # Quick Start
    parts.append(_generate_core_section())

    # API sections
    for name, modpath in API_MODULES.items():
        parts.append(_generate_api_section(name, modpath))

    # Models
    parts.append(_generate_models_section())

    # Error handling
    parts.append(_generate_errors_section())

    # CLI
    parts.append(_hdr(2, "CLI"))
    parts.append("For CLI usage, run `ows --help` or see the README.\n")

    output = "\n".join(parts)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(output, encoding="utf-8")
    print(f"Generated {OUTPUT} ({len(output)} bytes)")


if __name__ == "__main__":
    generate()
