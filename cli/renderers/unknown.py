from rich.panel import Panel
from constants import CONSOLE


def render_unknown_cmd(other: str):
    panel = Panel.fit(
        f'[bold red]command not found: {other}',
    )
    CONSOLE.print(panel, justify='center')
