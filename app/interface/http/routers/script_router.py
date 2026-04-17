from __future__ import annotations

from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel

from app.application.script.use_cases import GenerateRunAllScript, OptionPair
from app.infrastructure.fs.script_repository_fs import ScriptRepositoryFS

router = APIRouter(prefix="/api/script", tags=["script"])

class GenerateScriptRequest(BaseModel):
    command: str
    options: list[
        tuple[str, str | None] | 
        tuple[str, str | None, str | None] | 
        tuple[str, str | None, str | None, bool]  # with no_prefix flag
    ]
    fill_space: str
    command_line_ending: str | None = None  # Custom line ending for command line
    output_dir: str | None = None
    script_name: str = "runall.csh"

class GenerateScriptResponse(BaseModel):
    content: str


def get_generate_script_uc() -> GenerateRunAllScript:
    repo = ScriptRepositoryFS()  # could inject base dir later
    return GenerateRunAllScript(repo)

@router.post("/runall", response_model=GenerateScriptResponse)
def generate_runall(req: GenerateScriptRequest = Body(...), uc: GenerateRunAllScript = Depends(get_generate_script_uc)):
    # Convert options to OptionPair, handling 2, 3, or 4-tuple formats
    option_pairs = []
    for opt in req.options:
        if len(opt) == 4:
            option_pairs.append(OptionPair(key=opt[0], value=opt[1], line_ending=opt[2], no_prefix=opt[3]))
        elif len(opt) == 3:
            option_pairs.append(OptionPair(key=opt[0], value=opt[1], line_ending=opt[2]))
        else:
            option_pairs.append(OptionPair(key=opt[0], value=opt[1]))
    
    content = uc.execute(
        command=req.command,
        options=option_pairs,
        fill_space=req.fill_space,
        command_line_ending=req.command_line_ending,
        output_dir=req.output_dir,
        script_name=req.script_name
    )
    return GenerateScriptResponse(content=content)

