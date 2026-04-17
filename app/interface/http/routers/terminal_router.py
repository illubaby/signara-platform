from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, Body
import asyncio
import json
import os
import sys

from app.interface.http.schemas.terminal import ExecRequest, ExecResponse
from app.interface.http.dependencies.terminal import get_execute_terminal_command_uc
from app.application.terminal.use_cases import ExecuteTerminalCommand
from app.domain.terminal.entities import CommandRejectedError
from app.infrastructure.processes import terminal_session as session

router = APIRouter(prefix="/api/terminal", tags=["terminal"])


@router.post("/exec", response_model=ExecResponse)
async def exec_command(req: ExecRequest = Body(...), uc: ExecuteTerminalCommand = Depends(get_execute_terminal_command_uc)):
    try:
        result = uc.execute(command=req.command, timeout=req.timeout, workdir=req.workdir)
        return ExecResponse(**result.__dict__)
    except CommandRejectedError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.websocket("/ws/terminal")
async def terminal_ws(ws: WebSocket):  # type: ignore
    await ws.accept()
    if not session.PTY_SUPPORTED:
        await ws.send_text(f"\r\n[Interactive terminal not available on this platform ({sys.platform}).]\r\n")
        await ws.close()
        return
    try:
        pid, fd = session.fork_shell()
    except Exception as e:
        await ws.send_text(f"Failed to start shell: {e}\n")
        await ws.close()
        return

    stop = asyncio.Event()
    reader_task = asyncio.create_task(session.bridge_pty_to_websocket(fd, ws.send_text, stop))
    launched_shell = os.environ.get("APP_SHELL") or os.environ.get("SHELL") or "(auto-detected)"
    await ws.send_text(f"\r\n[Connected to server shell: {launched_shell}]\r\n")
    try:
        while not stop.is_set():
            msg = await ws.receive_text()
            try:
                obj = json.loads(msg)
            except json.JSONDecodeError:
                obj = {"type": "data", "data": msg}
            mtype = obj.get('type')
            if mtype == 'input':
                data = obj.get('data', '')
                if data:
                    try:
                        os.write(fd, data.encode())  # type: ignore
                    except OSError:
                        break
            elif mtype == 'resize':
                cols = int(obj.get('cols', 0))
                rows = int(obj.get('rows', 0))
                await session.set_winsize(fd, cols, rows)
            elif mtype == 'ping':
                await ws.send_text("\x1b[90m[pong]\x1b[0m")
    except WebSocketDisconnect:  # pragma: no cover
        pass
    except Exception as e:  # pragma: no cover
        try:
            await ws.send_text(f"\r\n[terminal error] {e}\r\n")
        except Exception:
            pass
    finally:
        stop.set()
        reader_task.cancel()
        await session.close_session(pid, fd)


@router.websocket("/ws")
async def terminal_ws_alt(ws: WebSocket):  # type: ignore
    await terminal_ws(ws)
