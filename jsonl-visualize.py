#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Any, List, Union
from pathlib import Path

# Updated imports for latest Textual version
from textual.app import App, ComposeResult
from textual.widgets import Tree, Header, Footer, Static
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from rich.syntax import Syntax
from textual.binding import Binding


# Constants
MAX_TEXT_DISPLAY = 500  # Characters

def parse_input(input_data: str) -> Union[dict, List[Any]]:
    """
    Parse input data as JSON or JSONL.
    """
    try:
        # Try parsing as standard JSON
        return json.loads(input_data)
    except json.JSONDecodeError:
        # If fails, try parsing as JSONL
        lines = input_data.strip().splitlines()
        json_list = []
        for idx, line in enumerate(lines, start=1):
            if line.strip():  # Ignore empty lines
                try:
                    json_list.append(json.loads(line))
                except json.JSONDecodeError as e:
                    raise json.JSONDecodeError(
                        f"Invalid JSON in JSONL at line {idx}: {e.msg}",
                        e.doc,
                        e.pos
                    )
        return json_list

def truncate_text(text: str, limit: int = MAX_TEXT_DISPLAY) -> str:
    """
    Truncate text to a specified limit.
    """
    if len(text) > limit:
        return text[:limit] + "..."
    return text

class JSONTree(Tree):
    """
    Tree to display JSON data.
    """

    def __init__(self, label: str, data: Any):
        super().__init__(label)
        self.data = data

    def on_mount(self) -> None:
        self.root.expand()
        self.add_json_nodes(self.root, self.data)

    def add_json_nodes(self, parent, data: Any) -> None:
        if isinstance(data, dict):
            for key, value in data.items():
                node = parent.add(f"{key}: {self.format_value(value)}")
                self.add_json_nodes(node, value)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                node = parent.add(f"[{index}]: {self.format_value(item)}")
                self.add_json_nodes(node, item)

    def format_value(self, value: Any) -> str:
        if isinstance(value, str):
            return truncate_text(value) if len(value) > MAX_TEXT_DISPLAY else value
        elif isinstance(value, dict):
            return "{...}"
        elif isinstance(value, list):
            return "[...]"
        else:
            return str(value)

    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        node = event.node
        data = node.data

        if isinstance(data, str) and len(data) > MAX_TEXT_DISPLAY:
            self.app.push_screen(TextModal(data))

class TextModal(ModalScreen):
    """
    Modal to display full text.
    """

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Full Text", classes="modal-title"),
            ScrollableContainer(
                Static(Syntax(self.text, "json", theme="monokai", line_numbers=True))
            ),
            id="dialog"
        )

class JSONInspectApp(App):
    """
    Main application class.
    """

    CSS = """
    Tree {
        width: 100%;
    }
    .modal-title {
        dock: top;
        padding: 1;
        background: $boost;
        text-align: center;
    }
    #dialog {
        padding: 1;
        width: 80%;
        height: 80%;
        border: thick $background 80%;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def __init__(self, data: Any):
        super().__init__()
        self.data = data

    def compose(self) -> ComposeResult:
        yield Header()
        yield JSONTree("JSON Data", self.data)
        yield Footer()

    def action_quit(self) -> None:
        """Quit the application."""
        self.exit()


def main():
    parser = argparse.ArgumentParser(
        description="Inspect JSON or JSONL files with a TUI."
    )
    parser.add_argument(
        "file",
        nargs="?",
        type=str,
        help="Path to the JSON or JSONL file. If omitted, reads from stdin.",
    )

    args = parser.parse_args()

    # Read input
    if args.file:
        path = Path(args.file)
        if not path.exists():
            print(f"Error: File '{args.file}' does not exist.", file=sys.stderr)
            sys.exit(1)
        try:
            with path.open("r", encoding="utf-8") as f:
                input_data = f.read()
        except Exception as e:
            print(f"Error reading file '{args.file}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if sys.stdin.isatty():
            print("Error: No input provided. Please provide a file or pipe data.", file=sys.stderr)
            sys.exit(1)
        try:
            input_data = sys.stdin.read()
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)

    # Parse input
    try:
        parsed_data = parse_input(input_data)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input. {e}", file=sys.stderr)
        sys.exit(1)

    # Run the app
    app = JSONInspectApp(parsed_data)
    app.run()

if __name__ == "__main__":
    main()