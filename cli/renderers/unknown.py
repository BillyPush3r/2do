from rich import box
from rich.panel import Panel
from constants import CONSOLE


def render_unknown_cmd(other: str):
    panel = Panel.fit(
        f'[bold red]command not found: {other}[/bold red]',
        border_style='bold red',
        box=box.ROUNDED,
        padding=(0, 1),
    )
    CONSOLE.print(panel, justify='center')
