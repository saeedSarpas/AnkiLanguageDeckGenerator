# Anki AI Helper

## Overview

This tool generates custom Anki language decks to aid in language learning. It is designed to leverage advanced GPU
capabilities to process and create decks efficiently.

## Prerequisites

Before starting the setup, ensure you have Python >3.8 installed on your system. This tool is tested only on Linux.

## Setup Instructions

Follow these steps to set up the Anki AI Helper in your local environment.

### Environment Setup

1. **Create a Python Virtual Environment**  
   This isolates the project dependencies. Run the following commands in the root directory of the project:

   ```shell
   python3 -m venv .venv
   source .venv/bin/activate
   ```

   On Windows, use `.\.venv\Scripts\activate` to activate the environment.

2. **Install the Package**
   Install the package and all its required python packages using the following command in the editable mode:

    ```shell
    pip install -e .
    ```

## Usage

This section provides step-by-step instructions to get you started with generating Anki decks using our tool. Ensure that you've completed the environment setup before proceeding. 

### Getting Started

Follow these steps to access the Tutorial notebook and explore the capabilities of this package:

#### 1. Activate the Python Environment

First, activate the virtual environment to ensure all dependencies are correctly loaded. Open a terminal, navigate to the root directory of the project, and execute the following command:

```shell
source .venv/bin/activate
```

#### 2. Launch JupyterLab

With the environment activated, change to the `notebook` directory and start JupyterLab. This environment hosts the interactive notebooks that guide you through the tool's functionalities. Run these commands from the terminal:

```
cd notebook
jupyter lab
```

#### 3. Explore the Tutorial Notebook

Within JupyterLab, locate and open the `Tutorial.ipynb` notebook. This tutorial introduces you to the various features of the package. You'll learn how to generate sentences, images, voices, and Anki decks to customize your learning experience. Feel free to experiment with the code cells and modify examples to better understand the tool's capabilities.

### Advanced Usage

#### Creating Custom Anki Styles and Decks

For users interested in further customization, follow these guidelines to create new Anki styles and decks:

- **Custom Styles:** To create a new style, navigate to the `anki_ai_helper.anki.styles` directory. Duplicate an existing style (e.g., `two_sentence_puzzler.py`) template and rename it to your preference. Modify the CSS and back and front cards definition within the file to achieve your desired look and feel for the Anki cards.

- **Custom Decks:** Creating a custom deck involves defining the fields and templates for your Anki cards. Navigate to `anki_ai_helper/anki` and duplicate an existing deck (e.g., `ai_sprach_meister.py`).

Please open a pull request if you believe your new deck can help other people.

TODO: Improve the instruction on how to create a new Anki Style and Deck.

## Limitations

* **GPU Requirements**: This package is optimized for single consumer GPUs with a minimum of 12-16GB of VRAM. It may not
  perform as expected on GPUs with lower VRAM.

## Contributing

We welcome contributions to the Anki AI Helper! If you have suggestions for improvements or encounter any
issues, please feel free to open an issue or submit a pull request on GitHub. 

## License

This project is licensed under the GNU General Public License v3.0. See the LICENSE file for more details.

## Contact

For any queries or support, please open an issue in the GitHub repository.

---

Note: This README is a living document and may be updated as the project evolves.
