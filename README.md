![Logo](https://raw.githubusercontent.com/spaghetti-backend/keyhunter/main/docs/logo.webp)

# KeyHunter

A simple terminal-based typing trainer built with [Textual].  
Minimalist interface, flexible configuration, and progress tracking — right in
your terminal.

---

## Project Status

The project is currently under development.  
Features are gradually expanding and may change over time.

---

## Features

<details>
<summary><strong>Training Modes</strong></summary>

Available modes:

- Standard multi-line mode  
- Scrolling line mode  

![StandardEngine](https://raw.githubusercontent.com/spaghetti-backend/keyhunter/main/docs/typer.webp)

</details>

<details>
<summary><strong>Flexible Configuration</strong></summary>

- Content type selection  
- Adjustable word count  
- Customizable typing area  

![TyperSettings](https://raw.githubusercontent.com/spaghetti-backend/keyhunter/main/docs/typing_settings.webp)  
![ContentSettings](https://raw.githubusercontent.com/spaghetti-backend/keyhunter/main/docs/content_settings.webp)

</details>

<details>
<summary><strong>Statistics & Profile</strong></summary>

View training results and track your progress.

![Profile](https://raw.githubusercontent.com/spaghetti-backend/keyhunter/main/docs/profile.webp)

</details>

---

## Requirements

- Python 3.10 or higher  
- Any modern terminal  

---

## Installation

It is recommended to install CLI applications in an isolated environment.

### Using uv

```bash
uv tool install keyhunter
```

### Using pipx

```bash
pipx install keyhunter
```

### Using pip

```bash
pip install keyhunter
```

Using [pipx] or [uv] is recommended for CLI tools.

## Usage

Run the application with:

```bash
keyhunter
```

Hotkeys are displayed in the bottom panel of the interface.

## Roadmap

- [ ] Improved navigation
- [ ] Advanced statistics
- [ ] Additional languages
- [ ] Code snippet training mode

<!-- external Links -->
[Textual]: https://textual.textualize.io
[uv]: https://docs.astral.sh/uv
[pipx]: https://github.com/pypa/pipx

