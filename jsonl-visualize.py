#!/usr/bin/env python3

import argparse
import json
import sys
from typing import Any, List, Union, Dict, Tuple
from pathlib import Path

# Updated imports for latest Textual version
from textual.app import App, ComposeResult
from textual.widgets import Tree, Header, Footer, Static
from textual.containers import Container, ScrollableContainer
from textual.screen import ModalScreen
from textual.binding import Binding
from rich.text import Text


# Constants
MAX_TEXT_DISPLAY = 500  # Characters

def parse_input(input_data: str) -> List[Union[Dict[str, Any], Tuple[int, str, str]]]:
    """
    Parse input data as JSON or JSONL, handling errors for individual lines.
    """
    lines = input_data.strip().splitlines()
    result = []

    # Try parsing as standard JSON first
    try:
        parsed_json = json.loads(input_data)
        return [parsed_json]
    except json.JSONDecodeError:
        # If standard JSON fails, parse line by line
        for idx, line in enumerate(lines, start=1):
            if line.strip():  # Ignore empty lines
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError as e:
                    result.append((idx, line, str(e)))

    return result

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

    def __init__(self, label: str, data: List[Union[Dict[str, Any], Tuple[int, str, str]]]):
        super().__init__(label)
        self.data = data

    def on_mount(self) -> None:
        self.root.expand()
        self.add_json_nodes(self.root, self.data)

    def add_json_nodes(self, parent, data: Any) -> None:
        if isinstance(data, list):
            for index, item in enumerate(data):
                if isinstance(item, tuple) and len(item) == 3:
                    # This is an error tuple (line_number, original_text, error_message)
                    line_number, original_text, error_message = item
                    error_node = parent.add(Text(f"[{index}]: Line {line_number}: Parsing Error", style="bold red"))
                    error_node.add(Text(f"Original text: {truncate_text(original_text)}", style="italic"))
                    error_node.add(Text(f"Error: {error_message}", style="dim red"))
                else:
                    node = parent.add(f"[{index}]: {self.format_value(item)}")
                    node.data = item
                    self.add_json_nodes(node, item)
        elif isinstance(data, dict):
            for key, value in data.items():
                node = parent.add(f"{key}: {self.format_value(value)}")
                node.data = value
                self.add_json_nodes(node, value)

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

    BINDINGS = [
        Binding("b", "app.pop_screen", "Back"),
        Binding("escape", "app.pop_screen", "Back"),
    ]

    def __init__(self, text: str):
        super().__init__()
        self.text = text

    def compose(self) -> ComposeResult:
        yield Container(
            Static("Full Text (Press 'b' to go back)", classes="modal-title"),
            ScrollableContainer(
                Static(self.text)
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

    def __init__(self, data: List[Union[Dict[str, Any], Tuple[int, str, str]]]):
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
    parsed_data = parse_input(input_data)

    # Run the app
    app = JSONInspectApp(parsed_data)
    app.run()

if __name__ == "__main__":
    main()