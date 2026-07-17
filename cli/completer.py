import shlex
from prompt_toolkit.completion import Completer, Completion
from db.plan import get_plans, get_plan
from db.task import get_tasks
from db.models import Status, Priority

TOP_CMDS = [
    'exit', 'e', 'quit', 'q', 'help', 'h', 'schemas',
    'new', 'n', 'get', 'g', 'ls', 'l', 'delete', 'd', 'rm',
    'update', 'u', 'pending', 'in_progress', 'inprogress', 'done',
    'swap', 'mv', 'move', 'rename', 'r', 'today', 'pomo',
]

NEW_SUBS = ['plan', 'task']
GET_SUBS = ['plans', 'plan', 'tasks']
DELETE_SUBS = ['plan', 'task']
STATUS_VALUES = [s.value for s in Status]
PRIORITY_VALUES = [p.value for p in Priority]
UPDATE_FLAGS = ['--title', '--status', '--priority', '--allocate']


def _plan_titles():
    return [p.title for p in get_plans()]


def _task_indices(plan_title: str):
    plan = get_plan(plan_title)
    if not plan:
        return []
    return [str(t.idx) for t in get_tasks(plan.uuid)]


class TdoCompleter(Completer):
    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        text = document.text_before_cursor
        try:
            args = shlex.split(text.strip()) if text.strip() else []
        except ValueError:
            args = text.strip().split()

        matches = self._matches(args, word)
        for m in matches:
            yield Completion(m, start_position=-len(word))

    def _matches(self, args: list[str], text: str) -> list[str]:
        pos = len(args)

        if pos == 0:
            candidates = TOP_CMDS + _plan_titles()
        elif pos == 1:
            cmd = args[0]
            if cmd in ('new', 'n'):
                candidates = NEW_SUBS
            elif cmd in ('get', 'g'):
                candidates = GET_SUBS
            elif cmd in ('delete', 'd', 'rm'):
                candidates = DELETE_SUBS
            elif cmd in ('pending', 'in_progress', 'inprogress', 'done'):
                candidates = _plan_titles()
            elif cmd in ('update', 'u'):
                candidates = _plan_titles()
            elif cmd in ('mv', 'move'):
                candidates = _plan_titles()
            elif cmd in ('rename', 'r'):
                candidates = _plan_titles()
            elif cmd == 'pomo':
                candidates = _plan_titles()
            else:
                candidates = _plan_titles()
        elif pos == 2:
            cmd, sub = args[0], args[1]
            if cmd in ('new', 'n') and sub == 'task':
                candidates = _plan_titles()
            elif cmd in ('get', 'g') and sub in ('plan', 'tasks'):
                candidates = _plan_titles()
            elif cmd in ('delete', 'd', 'rm') and sub in ('plan', 'task'):
                candidates = _plan_titles()
            elif cmd in ('pending', 'in_progress', 'inprogress', 'done'):
                candidates = _task_indices(sub)
            elif cmd in ('update', 'u'):
                if sub == 'task':
                    candidates = _plan_titles()
                else:
                    candidates = _task_indices(sub)
            elif cmd in ('rename', 'r'):
                candidates = _plan_titles()
            elif cmd in ('mv', 'move'):
                candidates = _task_indices(sub)
            elif cmd == 'pomo':
                candidates = _task_indices(sub)
            else:
                candidates = _plan_titles()
        elif pos == 3:
            cmd = args[0]
            if cmd == 'pomo':
                candidates = ['--set']
            elif cmd in ('update', 'u'):
                if args[1] == 'task':
                    candidates = _task_indices(args[2])
                else:
                    candidates = UPDATE_FLAGS
            elif cmd in ('pending', 'in_progress', 'inprogress', 'done'):
                candidates = _task_indices(args[1])
            elif cmd in ('delete', 'd', 'rm') and args[1] == 'task':
                candidates = _plan_titles()
            else:
                candidates = []
        else:
            cmd = args[0]
            if cmd in ('update', 'u'):
                offset = 2 if args[1] == 'task' else 1
                if pos == offset + 2:
                    candidates = UPDATE_FLAGS
                else:
                    prev = args[-1]
                    if prev == '--status':
                        candidates = STATUS_VALUES
                    elif prev == '--priority':
                        candidates = PRIORITY_VALUES
                    elif prev == '--title':
                        candidates = []
                    else:
                        candidates = UPDATE_FLAGS
            else:
                candidates = []

        return [c for c in candidates if c.startswith(text)]
