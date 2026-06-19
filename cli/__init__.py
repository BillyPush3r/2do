from pathlib import Path
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings

from cli.handlers import cmd_handler
from cli.completer import TdoCompleter
from constants import CONSOLE
from db.command_history import save_command, load_history
from cli.renderers.exit import render_exit


def render_title():
    CONSOLE.clear()
    CONSOLE.rule('[bold green]PU$H3R\'S 2DO CLI', style='bold cyan')


def startup():
    render_title()

    history_file = Path.home() / '.2do_history'
    history = FileHistory(str(history_file))
    if not history_file.exists():
        for cmd in load_history(100):
            history.append_string(cmd)

    kb = KeyBindings()

    @kb.add('enter')
    def _(event):
        b = event.current_buffer
        if b.complete_state:
            completions = b.complete_state.completions
            if len(completions) == 1:
                b.apply_completion(completions[0])
                return
        b.validate_and_handle()

    session = PromptSession(
        history=history,
        auto_suggest=AutoSuggestFromHistory(),
        completer=TdoCompleter(),
        complete_while_typing=True,
        key_bindings=kb,
    )

    while True:
        try:
            cmd = session.prompt(HTML('<ansigreen>➜ 2DO: </ansigreen>'))
        except (EOFError, KeyboardInterrupt):
            render_exit()
            break
        save_command(cmd)
        if cmd_handler(cmd):
            break
