# JSON/JSONL Visualizer

A Terminal User Interface (TUI) tool for inspecting and navigating JSON and JSONL files.

## Features

- Supports both JSON and JSONL file formats
- Interactive tree-like structure for easy navigation
- Displays truncated previews of long text fields
- Modal view for full content of long text fields
- Keyboard shortcuts for efficient navigation

## Installation

1. Ensure you have Python 3.7+ installed on your system.

2. Install the required dependencies:

   ```
   pip install textual rich
   ```

3. Download the `jsonl-visualize.py` script to your local machine.

## Usage

To use the JSON/JSONL Visualizer, run the script from the command line, providing the path to your JSON or JSONL file:

```
python jsonl-visualize.py path/to/your/file.json
```

If you want to pipe data into the script, you can do so like this:

```
cat path/to/your/file.json | python jsonl-visualize.py
```

## Navigation

Once the visualizer is running, you can navigate through your JSON/JSONL data using the following keyboard shortcuts:

- **↑ / ↓**: Move up and down through the tree
- **→**: Expand a node
- **←**: Collapse a node
- **Enter**: Toggle node expansion/collapse
- **q**: Quit the application

When viewing long text fields in the modal view:

- **Esc**: Close the modal and return to the tree view

## Limitations

- The tool may not perform well with extremely large JSON/JSONL files due to memory constraints.
- Nested structures beyond a certain depth may become difficult to navigate.

## Troubleshooting

If you encounter any issues:

1. Ensure you're using the latest version of the script.
2. Check that you have the latest versions of the required dependencies installed.
3. If the problem persists, please open an issue on the project's GitHub repository with a detailed description of the problem and the steps to reproduce it.

## Contributing

Contributions to improve the JSON/JSONL Visualizer are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is open-source and available under the MIT License.