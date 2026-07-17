from rich import box
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from constants import CONSOLE


def render_schemas():
    tree = Tree('[bold red]TODO')
    plan_branch = tree.add('[bold cyan]Plan')
    plan_branch.add('[bold green]UUID: [italic yellow]UUID')
    plan_branch.add('[bold green]Title: [italic yellow]String')
    plan_branch.add('[bold green]Tasks: [italic yellow]List[Task]')
    task_branch = tree.add('[bold cyan]Task')
    task_branch.add('[bold green]UUID: [italic yellow]UUID')
    task_branch.add('[bold green]Plan UUID: [italic yellow]UUID')
    task_branch.add('[bold green]IDX: [italic yellow]Integer')
    task_branch.add('[bold green]Title: [italic yellow]String')
    task_branch.add(
        '[bold green]Status: [italic yellow]Literal["Done", "In Progress", "Pending"]'
    )
    panel = Panel.fit(tree, box=box.ROUNDED)
    table = Table(title='[bold blue]Database Schemas', border_style='bright_blue', box=box.ROUNDED)
    table.add_column('[bold blue]Schema', justify='center')
    table.add_column('[bold blue]Structure', justify='left')
    table.add_column('[bold blue]Explanation', justify='left')
    table.add_row('TODO', panel)
    table.add_section()
    table.add_row(
        'COMMANDS', 'to be implemented...', 'For better cli experience'
    )
    table.add_section()
    table.add_row('KANBAN', 'to be implemented...', '')
    CONSOLE.print(table, justify='center')


def render_help():
    table = Table(
        title='[bold blue]Commands',
        border_style='bright_blue',
        box=box.ROUNDED,
    )
    table.add_column('[bold blue]Command', justify='center')
    table.add_column('[bold blue]Description', justify='center')
    table.add_column('[bold blue]Options', justify='center')
    table.add_column('[bold blue]Abbreviation ', justify='center')

    table.add_row(
        '[italic green]help',
        'Shows this guide',
        '[italic red]--',
        '[italic green] h',
    )
    table.add_row(
        '[italic green]exit', 'Exits the CLI', '[italic red]--', '[italic green]e'
    )
    table.add_row(
        '[italic green]quit', 'Quits the CLI', '[italic red]--', '[italic green]q'
    )
    table.add_row(
        '[italic green]schemas',
        'Shows database schemas',
        '[italic red]--',
        '[italic red]--',
    )
    table.add_row(
        '[italic green]new',
        'Creates a new object in database',
        '[italic blue]<object>',
        '[italic green]n <object>',
    )
    table.add_row(
        '[green]new[/green] [yellow]plan',
        'Creates a new plan with a default name',
        '[italic blue]plan',
        '[italic green]n plan',
    )
    table.add_row(
        '[green]new[/green] [yellow]plan[/yellow] [red]<name>',
        'Creates a new plan with a specific name',
        '[italic blue]plan <name>',
        '[italic green]n plan <name>',
    )
    table.add_row(
        '[green]new[/green] [yellow]task[/yellow] [red]<plan>[/red] [red]<task>',
        'Creates a task in a plan',
        '[italic blue]task <plan> <title>',
        '[italic green]n task <plan> <task>',
    )
    table.add_row(
        '[italic green]get',
        'Reads an object from database',
        '[italic blue]<object>',
        '[italic green]g',
    )
    table.add_row(
        '[green]get[/green] [yellow]plans',
        'Lists all plans',
        '[italic blue]plans',
        '[italic green]g plans, ls',
    )
    table.add_row(
        '[green]get[/green] [yellow]plan[/yellow] [red]<name>',
        'Shows plan details and all tasks',
        '[italic blue]plan <name>',
        '[italic green]g plan <name>',
    )
    table.add_row(
        '[green]get[/green] [yellow]tasks[/yellow] [red]<plan>',
        'Lists tasks for a plan (or all tasks)',
        '[italic blue]tasks [<plan>]',
        '[italic green]g tasks',
    )
    table.add_row(
        '',
        '[italic blue]hint: just type a plan name to show its tasks',
        '',
        '',
    )
    table.add_row(
        '[italic green]delete[/italic green] [yellow]plan[/yellow] [red]<name>',
        'Deletes a plan by title',
        '[italic blue]plan <name>',
        '[italic green]d|rm plan <name>',
    )
    table.add_row(
        '[italic green]delete[/italic green] [yellow]task[/yellow] [red]<plan>[/red] [red]<idx>',
        'Deletes a task by plan and index',
        '[italic blue]task <plan> <idx>',
        '[italic green]d|rm task <plan> <idx>',
    )
    table.add_row(
        '[italic green]done[/italic green] [red]<plan> <idx>',
        'Marks a task as done',
        '[italic blue]done <plan> <idx>',
        '[italic green]done',
    )
    table.add_row(
        '[italic green]pending[/italic green] [red]<plan> <idx>',
        'Marks a task as pending',
        '[italic blue]pending <plan> <idx>',
        '[italic green]pending',
    )
    table.add_row(
        '[italic green]inprogress[/italic green] [red]<plan> <idx>',
        'Marks a task as in progress',
        '[italic blue]inprogress <plan> <idx>',
        '[italic green]inprogress',
    )
    table.add_row(
        '[italic green]u[/italic green] [red]<plan> <idx> --priority high',
        'Updates a task (--title, --status, --priority)',
        '[italic blue]--title|--status|--priority',
        '[italic green]upd',
    )
    table.add_row(
        '[italic green]swap[/italic green] [red]<plan> <idx1> <idx2>',
        'Swaps the order of two tasks in a plan',
        '[italic blue]<plan> <idx1> <idx2>',
        '[italic green]swap',
    )
    table.add_row(
        '[italic green]mv[/italic green] [red]<plan> <from> <to>',
        'Moves a task to a new position',
        '[italic blue]<plan> <from_idx> <to_idx>',
        '[italic green]mv | move',
    )
    table.add_row(
        '[green]mv[/green] [yellow]myplan[/yellow] [red]3[/red] [cyan]1',
        'Moves task #3 to position #1',
        '[italic blue]<plan> <from> <to>',
        '[italic green]mv',
    )
    table.add_row(
        '[italic green]today',
        "Shows today's Gregorian and Shamsi date",
        '[italic red]--',
        '[italic green]today',
    )
    table.add_row(
        '[italic green]pomo',
        'Starts a pomodoro timer for a task',
        '[italic blue]<plan> <idx> [minutes]',
        '[italic green]pomo',
    )
    table.add_row(
        '[green]pomo[/green] [yellow]myplan[/yellow] [red]1[/red] [cyan]25',
        'Allocates & starts a 25 min timer for task 1 in plan "myplan"',
        '[italic blue]<plan> <idx> <min>',
        '[italic green]pomo',
    )
    table.add_row(
        '[green]pomo[/green] [yellow]myplan[/yellow] [red]1',
        'Starts timer using existing allocation',
        '[italic blue]<plan> <idx>',
        '[italic green]pomo',
    )
    table.add_row(
        '[green]pomo[/green] [yellow]myplan[/yellow] [red]1 [cyan]--set 25',
        'Sets allocation without starting timer',
        '[italic blue]<plan> <idx> --set <min>',
        '[italic green]pomo',
    )
    table.add_row(
        '[italic green]u[/italic green] [red]<plan> <idx> --allocate 25',
        'Sets time allocation on a task',
        '[italic blue]--allocate <minutes>',
        '[italic green]upd',
    )
    CONSOLE.print(table, justify='center')
