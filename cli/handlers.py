import shlex
from commands import Command
from constants import CONSOLE
from db.plan import create_new_plan, get_plans, get_plan, delete_plan, rename_plan
from db.task import (
    create_task,
    get_tasks,
    get_task_by_plan_and_idx,
    delete_task,
    update_task,
    swap_task_indices,
)
from db.models import Status, Priority
from cli.renderers.exit import render_exit
from cli.renderers.help import render_help, render_schemas
from cli.renderers.unknown import render_unknown_cmd
from cli.renderers.plan import (
    render_plans,
    render_plan,
    render_tasks,
)


def cmd_handler(cmd: str):
    match cmd:
        case (
            Command.EXIT.value
            | Command.QUIT.value
            | Command.E.value
            | Command.Q.value
        ):
            render_exit()
            return True
        case Command.SCHEMAS.value:
            render_schemas()
        case Command.HELP.value | Command.H.value:
            render_help()
        case _:
            handled = handle_sequences(cmd)
            if not handled:
                render_unknown_cmd(cmd)


def handle_sequences(sequence: str) -> bool:
    try:
        args = shlex.split(sequence)
    except ValueError:
        args = sequence.split()
    if not args:
        return False
    match args[0]:
        case 'new' | 'n':
            handle_new(args)
        case 'get' | 'g':
            handle_get(args)
        case 'ls' | 'l':
            handle_ls(args)
        case 'd' | 'delete' | 'rm':
            handle_delete(args)
        case 'u' | 'update':
            handle_update(args)
        case 'pending':
            handle_status_change(Status.PENDING, args)
        case 'in_progress' | 'inprogress':
            handle_status_change(Status.IN_PROGRESS, args)
        case 'done':
            handle_status_change(Status.DONE, args)
        case 'swap':
            handle_swap(args)
        case 'rename' | 'r':
            handle_rename(args)
        case 'pomo':
            handle_pomo(args)
        case 'today':
            handle_today(args)
        case _:
            plan = get_plan(' '.join(args))
            if plan:
                render_plan(plan)
                return True
            return False
    return True


def handle_status_change(status: Status, args: list[str]):
    if len(args) < 3:
        CONSOLE.print(f'[bold red]Usage: {args[0]} <plan> <idx>')
        return
    plan = get_plan(' '.join(args[1:-1]))
    if not plan:
        CONSOLE.print('[bold red]Plan not found')
        return
    try:
        idx = int(args[-1])
    except ValueError:
        CONSOLE.print(f'[bold red]Usage: {args[0]} <plan> <idx>')
        return
    task = get_task_by_plan_and_idx(plan.uuid, idx)
    if not task:
        CONSOLE.print(f'[bold red]Task #{idx} not found in plan: {plan.title}')
        return
    update_task(task.uuid, status=status)
    CONSOLE.print(f'[bold green]Task #{idx} set to {status.value}')


def handle_swap(args: list[str]):
    if len(args) < 4:
        CONSOLE.print('[bold red]Usage: swap <plan> <idx1> <idx2>')
        return
    plan = get_plan(' '.join(args[1:-2]))
    if not plan:
        CONSOLE.print('[bold red]Plan not found')
        return
    try:
        idx1 = int(args[-2])
        idx2 = int(args[-1])
    except ValueError:
        CONSOLE.print('[bold red]Usage: swap <plan> <idx1> <idx2>')
        return
    if swap_task_indices(plan.uuid, idx1, idx2):
        CONSOLE.print(
            f'[bold green]Tasks #{idx1} and #{idx2} swapped in plan: {plan.title}'
        )
    else:
        CONSOLE.print(
            f'[bold red]Could not swap tasks #{idx1} and #{idx2} — check the indices are valid and different'
        )


def handle_new(args: list[str]):
    if len(args) < 2:
        CONSOLE.print('[bold red]Usage: new <plan|task> [args...]')
        return
    match args[1]:
        case 'plan':
            title = args[2] if len(args) >= 3 else None
            plan = create_new_plan(title)
            if plan:
                CONSOLE.print('[bold green]Plan created')
            else:
                CONSOLE.print('[bold red]A plan with that title already exists')
        case 'task':
            if len(args) < 4:
                CONSOLE.print(
                    '[bold red]Usage: new task <plan_title> <task_title>'
                )
                return
            plan = get_plan(args[2])
            if not plan:
                CONSOLE.print(f'[bold red]Plan not found: {args[2]}')
                return
            task = create_task(plan.uuid, ' '.join(args[3:]))
            if task:
                CONSOLE.print(f'[bold green]Task created in plan: {plan.title}')
            else:
                CONSOLE.print(
                    '[bold red]A task with that title already exists in this plan'
                )
        case _:
            CONSOLE.print(f'[bold red]Unknown object: {args[1]}')


def handle_get(args: list[str]):
    if len(args) < 2:
        CONSOLE.print(
            '[bold red]Usage: get <plans|plan <title>|tasks [plan_title]>'
        )
        return
    match args[1]:
        case 'plans':
            plans = get_plans()
            render_plans(plans)
        case 'plan':
            if len(args) < 3:
                CONSOLE.print('[bold red]Usage: get plan <name>')
                return
            plan = get_plan(' '.join(args[2:]))
            render_plan(plan)
        case 'tasks':
            if len(args) >= 3:
                plan = get_plan(' '.join(args[2:]))
                if plan:
                    tasks = get_tasks(plan.uuid)
                    render_tasks(tasks)
                else:
                    CONSOLE.print('[bold red]Plan not found')
            else:
                tasks = get_tasks()
                render_tasks(tasks)
        case _:
            CONSOLE.print(f'[bold red]Unknown object: {args[1]}')


def handle_ls(args: list[str]):
    plans = get_plans()
    render_plans(plans)


def handle_delete(args: list[str]):
    if len(args) < 3:
        CONSOLE.print('[bold red]Usage: delete <plan|task> <args...>')
        return
    match args[1]:
        case 'plan':
            ok = delete_plan(' '.join(args[2:]))
            if ok:
                CONSOLE.print('[bold green]Plan deleted')
            else:
                CONSOLE.print('[bold red]Plan not found')
        case 'task':
            if len(args) < 4:
                CONSOLE.print('[bold red]Usage: delete task <plan_title> <idx>')
                return
            plan_title = ' '.join(args[2:-1])
            try:
                idx = int(args[-1])
            except ValueError:
                CONSOLE.print('[bold red]Usage: delete task <plan_title> <idx>')
                return
            plan = get_plan(plan_title)
            if not plan:
                CONSOLE.print(f'[bold red]Plan not found: {plan_title}')
                return
            task = get_task_by_plan_and_idx(plan.uuid, idx)
            if not task:
                CONSOLE.print(
                    f'[bold red]Task #{idx} not found in plan: {plan_title}'
                )
                return
            delete_task(task.uuid)
            CONSOLE.print('[bold green]Task deleted')
        case _:
            CONSOLE.print(f'[bold red]Unknown object: {args[1]}')


def handle_update(args: list[str]):
    if len(args) < 2:
        CONSOLE.print(
            '[bold red]Usage: u <plan> <idx> [--title <title>] [--status <status>]'
        )
        return
    offset = 2 if args[1] == 'task' else 1
    if len(args) < offset + 3:
        CONSOLE.print(
            '[bold red]Usage: u <plan> <idx> [--title <title>] [--status <status>]'
        )
        return
    plan = get_plan(args[offset])
    if not plan:
        CONSOLE.print(f'[bold red]Plan not found: {args[offset]}')
        return
    try:
        idx = int(args[offset + 1])
    except ValueError:
        CONSOLE.print(
            '[bold red]Usage: u <plan> <idx> [--title <title>] [--status <status>]'
        )
        return
    task = get_task_by_plan_and_idx(plan.uuid, idx)
    if not task:
        CONSOLE.print(f'[bold red]Task #{idx} not found in plan: {plan.title}')
        return
    title = None
    status = None
    priority = None
    allocated_minutes = None
    i = offset + 2
    while i < len(args):
        match args[i]:
            case '--title':
                i += 1
                if i >= len(args):
                    CONSOLE.print('[bold red]--title requires a value')
                    return
                title = args[i]
            case '--status':
                i += 1
                if i >= len(args):
                    CONSOLE.print('[bold red]--status requires a value')
                    return
                try:
                    status = Status(args[i])
                except ValueError:
                    valid = ', '.join(s.value for s in Status)
                    CONSOLE.print(
                        f'[bold red]Invalid status: {args[i]}. Valid: {valid}'
                    )
                    return
            case '--priority':
                i += 1
                if i >= len(args):
                    CONSOLE.print('[bold red]--priority requires a value')
                    return
                try:
                    priority = Priority(args[i])
                except ValueError:
                    valid = ', '.join(p.value for p in Priority)
                    CONSOLE.print(
                        f'[bold red]Invalid priority: {args[i]}. Valid: {valid}'
                    )
                    return
            case '--allocate':
                i += 1
                if i >= len(args):
                    CONSOLE.print('[bold red]--allocate requires a minutes value')
                    return
                try:
                    allocated_minutes = int(args[i])
                except ValueError:
                    CONSOLE.print('[bold red]--allocate requires an integer (minutes)')
                    return
                if allocated_minutes < 1:
                    CONSOLE.print('[bold red]Minutes must be >= 1')
                    return
            case _:
                CONSOLE.print(
                    f'[bold red]Unknown flag: {args[i]}. Use --title, --status, --priority, or --allocate'
                )
                return
        i += 1
    if title is None and status is None and priority is None and allocated_minutes is None:
        CONSOLE.print(
            '[bold red]At least one of --title, --status, --priority, or --allocate is required'
        )
        return
    update_task(task.uuid, title=title, status=status, priority=priority, allocated_minutes=allocated_minutes)
    CONSOLE.print('[bold green]Task updated')


def handle_pomo(args: list[str]):
    if len(args) < 3:
        CONSOLE.print('[bold red]Usage: pomo <plan> <idx> [minutes]')
        return

    if '--set' in args:
        sp = args.index('--set')
        if sp + 1 >= len(args):
            CONSOLE.print('[bold red]--set requires a minutes value')
            return
        try:
            idx = int(args[sp - 1])
            minutes = int(args[sp + 1])
        except (ValueError, IndexError):
            CONSOLE.print('[bold red]Usage: pomo <plan> <idx> --set <minutes>')
            return
        plan = get_plan(' '.join(args[1:sp - 1]))
        if not plan:
            CONSOLE.print('[bold red]Plan not found')
            return
        task = get_task_by_plan_and_idx(plan.uuid, idx)
        if not task:
            CONSOLE.print(f'[bold red]Task #{idx} not found in plan: {plan.title}')
            return
        if minutes < 1:
            CONSOLE.print('[bold red]Minutes must be >= 1')
            return
        update_task(task.uuid, allocated_minutes=minutes)
        CONSOLE.print(f'[bold green]Time allocation for task #{idx} set to {minutes} min')
        return

    # pomo <plan> <idx> [minutes]
    try:
        maybe_minutes = int(args[-1])
        maybe_idx = int(args[-2])
        has_minutes = True
        plan_title = ' '.join(args[1:-2])
    except ValueError:
        try:
            idx = int(args[-1])
            has_minutes = False
            plan_title = ' '.join(args[1:-1])
        except ValueError:
            CONSOLE.print('[bold red]Usage: pomo <plan> <idx> [minutes]')
            return

    if has_minutes:
        idx, minutes = maybe_idx, maybe_minutes
    else:
        minutes = None

    plan = get_plan(plan_title)
    if not plan:
        CONSOLE.print(f'[bold red]Plan not found: {plan_title}')
        return

    task = get_task_by_plan_and_idx(plan.uuid, idx)
    if not task:
        CONSOLE.print(f'[bold red]Task #{idx} not found in plan: {plan.title}')
        return

    if minutes is not None:
        if minutes < 1:
            CONSOLE.print('[bold red]Minutes must be >= 1')
            return
        update_task(task.uuid, allocated_minutes=minutes)
        total = minutes
    else:
        if not task.allocated_minutes:
            CONSOLE.print(
                f'[bold red]No time allocated for task #{idx}. '
                f'Use: pomo {plan.title} {idx} <minutes>'
            )
            return
        total = task.allocated_minutes

    CONSOLE.print(f'[bold]Start {total} min timer for task #{idx}: "{task.title}"?[/bold]')
    try:
        response = input('[Y/n] ').strip().lower()
    except (EOFError, KeyboardInterrupt):
        CONSOLE.print('\n[bold yellow]Cancelled')
        return
    if response not in ('', 'y', 'yes'):
        CONSOLE.print('[bold yellow]Cancelled')
        return

    from cli.pomo import PomoTimer
    timer = PomoTimer(task, plan.title, total)
    result = timer.run()

    if result['completed']:
        CONSOLE.print('[bold green]✓ Timer completed![/bold green]')
        update_task(task.uuid, pomodoro_count=(task.pomodoro_count or 0) + 1)
        try:
            response = input('Mark task as done? [y/N] ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            CONSOLE.print()
            return
        if response in ('y', 'yes'):
            update_task(task.uuid, status=Status.DONE)
            CONSOLE.print(f'[bold green]Task #{idx} marked as done[/bold green]')
        else:
            CONSOLE.print('[dim]Task left as-is[/dim]')
    else:
        CONSOLE.print(f'[bold yellow]Timer stopped ({result["spent_seconds"]}s spent)[/bold yellow]')


def handle_today(args: list[str]):
    from datetime import date
    import jdatetime
    g = date.today()
    j = jdatetime.date.today()
    CONSOLE.print(f'[bold]Gregorian:[/bold] {g}')
    CONSOLE.print(f'[bold]Shamsi:[/bold] {str(j)}')


def handle_rename(args: list[str]):
    if len(args) < 3:
        CONSOLE.print('[bold red]Usage: rename <plan> <new_title>')
        return
    plan = get_plan(args[1])
    if not plan:
        CONSOLE.print('[bold red]Plan not found')
        return
    if len(args) >= 3:
        new_title = ' '.join(args[2:])
    else:
        CONSOLE.print('[bold red]New title is required')
        return
    if rename_plan(plan.uuid, new_title):
        CONSOLE.print(f'[bold green]Plan renamed to: {new_title}')
    else:
        CONSOLE.print('[bold red]A plan with that title already exists')
