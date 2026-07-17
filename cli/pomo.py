import os
import time
import sys
import select
import tty
import termios
from rich import box
from rich.live import Live
from rich.panel import Panel
from rich.align import Align
from constants import CONSOLE


class PomoTimer:
    def __init__(self, task, plan_title: str, total_minutes: int):
        self.task = task
        self.plan_title = plan_title
        self.total_seconds = total_minutes * 60
        self.remaining = self.total_seconds
        self.paused = False
        self.running = True
        self.completed = False
        self.spent_seconds = 0

    def _fmt(self, secs: int) -> str:
        m, s = divmod(int(secs), 60)
        h, m = divmod(m, 60)
        if h:
            return f'{h:02d}:{m:02d}:{s:02d}'
        return f'{m:02d}:{s:02d}'

    def _read_key(self, timeout: float = 0.05):
        fd = sys.stdin.fileno()
        if select.select([fd], [], [], timeout)[0]:
            return os.read(fd, 1).decode('utf-8', errors='replace')
        return None

    def _build_panel(self, final: bool = False):
        elapsed = self.total_seconds - self.remaining
        pct = (elapsed / self.total_seconds * 100) if self.total_seconds else 0

        bar_w = 30
        filled = int(bar_w * pct / 100)
        bar = '█' * filled + '░' * (bar_w - filled)

        time_str = self._fmt(self.remaining)

        if final or self.remaining <= 0:
            status = '[bold red]TIME\'S UP![/bold red]'
        elif self.paused:
            status = '[bold yellow]PAUSED[/bold yellow]'
        else:
            status = '[bold green]RUNNING[/bold green]'

        content = (
            f'[bold cyan]Plan:[/bold cyan]  [italic]{self.plan_title}[/italic]\n'
            f'[bold cyan]Task:[/bold cyan]  [italic]#{self.task.idx} {self.task.title}[/italic]\n\n'
            f'[bold white]{time_str}[/bold white]\n\n'
            f'{bar}  [bold]{pct:.0f}%[/bold]\n\n'
            f'{status}\n\n'
            f'[dim](p) pause  (c) resume  (q) quit[/dim]'
        )

        return Panel.fit(
            content,
            title='[bold blue]Pomodoro Timer',
            border_style='bold blue',
            box=box.ROUNDED,
            padding=(1, 3),
        )

    def run(self):
        old = termios.tcgetattr(sys.stdin)
        try:
            tty.setraw(sys.stdin.fileno())
            with Live(
                Align.center(self._build_panel()),
                refresh_per_second=10,
                console=CONSOLE,
                auto_refresh=False,
            ) as live:
                last_tick = time.monotonic()
                while self.running and self.remaining > 0:
                    now = time.monotonic()
                    dt = now - last_tick

                    key = self._read_key()
                    if key:
                        k = key.lower()
                        if k in ('p', ' '):
                            self.paused = not self.paused
                        elif k == 'c':
                            self.paused = False
                        elif k in ('q', '\x1b'):
                            self.running = False

                    if not self.paused and self.running:
                        self.remaining = max(0, self.remaining - dt)

                    last_tick = now
                    live.update(Align.center(self._build_panel()))
                    live.refresh()

                if self.remaining <= 0:
                    self.completed = True
                    self.spent_seconds = self.total_seconds
                    live.update(Align.center(self._build_panel(final=True)))
                    live.refresh()
                    sys.stdout.write('\a')
                    sys.stdout.flush()
                    time.sleep(0.3)
        finally:
            termios.tcflush(sys.stdin, termios.TCIFLUSH)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old)

        return {
            'completed': self.completed,
            'spent_seconds': int(self.total_seconds - self.remaining),
        }
