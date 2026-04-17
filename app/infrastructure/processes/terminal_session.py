"""PTY session helpers (infrastructure) used by the terminal WebSocket router.

Separated from the HTTP layer so they can be reused or tested independently.
"""
from __future__ import annotations

import os
import asyncio
import sys
from typing import Any, Awaitable, Callable

try:  # Platform dependent; Windows will set PTY_SUPPORTED = False
    import pty, fcntl, termios, struct, signal  # type: ignore
    PTY_SUPPORTED = (os.name != 'nt')
except Exception:  # pragma: no cover
    pty = fcntl = termios = struct = signal = None  # type: ignore
    PTY_SUPPORTED = False


async def set_winsize(fd: int, cols: int, rows: int) -> None:
    if not PTY_SUPPORTED:
        return
    try:
        if cols <= 0 or rows <= 0:
            return
        winsize = struct.pack('HHHH', rows, cols, 0, 0)  # type: ignore
        fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)  # type: ignore
    except Exception:  # pragma: no cover
        pass


def fork_shell() -> tuple[int, int]:
    """Fork a PTY and exec a login shell in the child. Returns (pid, fd)."""
    if not PTY_SUPPORTED:
        raise RuntimeError("PTY not supported on this platform")
    pid, fd = pty.fork()  # type: ignore
    if pid == 0:  # child
        try:
            chosen = None
            for key in ("APP_SHELL", "SHELL"):
                val = os.environ.get(key)
                if val and os.path.exists(val):
                    chosen = val
                    break
            if not chosen:
                try:
                    import pwd  # type: ignore
                    chosen = pwd.getpwuid(os.getuid()).pw_shell or None  # type: ignore
                except Exception:
                    pass
            if not chosen:
                for c in ["/bin/bash", "/usr/bin/bash", "/bin/zsh", "/bin/sh"]:
                    if os.path.exists(c):
                        chosen = c
                        break
            if not chosen:
                chosen = "sh"
            shell_name = os.path.basename(chosen)
            os.execvp(chosen, [shell_name, '-l'])
        except Exception:  # pragma: no cover
            os.execvp('sh', ['sh'])
    return pid, fd


async def bridge_pty_to_websocket(fd: int, ws_send: Callable[[str], Awaitable[Any]], stop_event: asyncio.Event) -> None:
    """Continuously read from PTY fd and forward to websocket send function."""
    os.set_blocking(fd, False)
    try:
        while not stop_event.is_set():
            await asyncio.sleep(0)
            try:
                data = os.read(fd, 4096)
                if not data:
                    break
                await ws_send(data.decode(errors='ignore'))
            except BlockingIOError:
                await asyncio.sleep(0.01)
            except OSError:
                break
    finally:
        stop_event.set()


async def close_session(pid: int, fd: int) -> None:
    try:
        if PTY_SUPPORTED:
            import signal as _signal  # type: ignore
            os.kill(pid, _signal.SIGTERM)  # type: ignore
    except Exception:  # pragma: no cover
        pass
    await asyncio.sleep(0.05)
    try:
        os.close(fd)
    except Exception:  # pragma: no cover
        pass
