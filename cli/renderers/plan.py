from datetime import datetime
from rich.table import Table
from constants import CONSOLE
from db.models import Plan, Task
from db.task import get_tasks


def _fmt_date(iso: str | None) -> str:
    if not iso:
        return ''
    try:
        return datetime.fromisoformat(iso).strftime('%Y-%m-%d')
    except ValueError, TypeError:
        return iso[:10]


def render_plans(plans: list[Plan]):
    if not plans:
        CONSOLE.print('[bold yellow]No plans found')
        return
    table = Table(
        title='[bold blue]Plans',
        title_style='bold',
        header_style='bold cyan',
    )
    table.add_column('[bold green]Title')
    table.add_column('[bold green]Tasks', justify='center')
    table.add_column('[bold green]Created')
    for plan in plans:
        task_count = len(plan.tasks) if plan.tasks else 0
        table.add_row(
            f'[italic]{plan.title}',
            str(task_count),
            _fmt_date(plan.created_at),
        )
    CONSOLE.print(table, justify='center')


def render_plan(plan: Plan | None):
    if not plan:
        CONSOLE.print('[bold red]Plan not found')
        return
    CONSOLE.print(f'[bold cyan]Plan: [green]{plan.title}', justify='center')
    CONSOLE.print(
        f'[bold]Created: [yellow]{_fmt_date(plan.created_at)}',
        justify='center',
    )
    tasks = get_tasks(plan.uuid)
    if tasks:
        render_tasks(tasks)
    else:
        CONSOLE.print('[dim]No tasks', justify='center')


def render_tasks(tasks: list[Task]):
    if not tasks:
        CONSOLE.print('[bold yellow]No tasks found')
        return
    table = Table(
        title='[bold blue]Tasks',
        title_style='bold',
        header_style='bold cyan',
    )
    table.add_column('[bold green]#', justify='center')
    table.add_column('[bold green]Title')
    table.add_column('[bold green]Status', justify='center')
    table.add_column('[bold green]Priority', justify='center')
    table.add_column('[bold green]Allocated', justify='center')
    table.add_column('[bold green]Created')
    for task in tasks:
        priority = task.priority.value if task.priority else ''
        allocated = f'{task.allocated_minutes}m' if task.allocated_minutes else ''
        table.add_row(
            str(task.idx),
            f'[italic]{task.title}',
            f'[italic]{task.status.value.replace("_", " ")}',
            f'[italic]{priority}',
            f'[italic]{allocated}',
            _fmt_date(task.created_at),
        )
    CONSOLE.print(table, justify='center')
