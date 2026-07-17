from rich import box
from rich.panel import Panel
from rich.align import Align
from constants import CONSOLE


def render_exit():
    panel = Panel.fit(
        Align.center('[bold green]Goodbye![/bold green]'),
        border_style='bold green',
        box=box.ROUNDED,
    )
    CONSOLE.print(panel, justify='center')
