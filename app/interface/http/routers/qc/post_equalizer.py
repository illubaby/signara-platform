"""Post-Equalizer Router - Read Compatibility_Final.csv for Timing QC."""

from fastapi import APIRouter, HTTPException, Query
from app.domain.common.validation import validate_component, ValidationError
from app.infrastructure.fs.timing_paths import TimingPaths
from app.interface.http.schemas.qc import PostEqualizerRow, PostEqualizerData

router = APIRouter(prefix="/api/qc", tags=["qc"])


def _validate_component(name: str, field: str = "component") -> None:
    """Validate component and convert ValidationError to HTTPException."""
    try:
        validate_component(name, field)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project}/{subproject}/post-equalizer", response_model=PostEqualizerData)
async def get_post_equalizer_data(
    project: str,
    subproject: str,
    cell: str = Query(...),
):
    """Read Compatibility_Final.csv from cell's Equalizer directory."""
    import csv

    _validate_component(project, "project")
    _validate_component(subproject, "subproject")
    _validate_component(cell, "cell")

    tp = TimingPaths(project, subproject)
    post_equalizer_file = tp.qc_cell_root(cell) / "Equalizer" / "Compatibility_Final.csv"

    if not post_equalizer_file.exists():
        return PostEqualizerData(
            project=project,
            subproject=subproject,
            cell=cell,
            rows=[],
            exists=False,
            note="Compatibility_Final.csv not found"
        )

    rows = []
    try:
        with open(post_equalizer_file, "r", encoding="utf-8") as f:
            raw_lines = [line.rstrip("\n") for line in f]

        header_index = None
        for idx, line in enumerate(raw_lines):
            if line.startswith("#Type,") or line.startswith("Type,"):
                header_index = idx
                break

        if header_index is None:
            raise HTTPException(status_code=500, detail="Compatibility_Final.csv header not found")

        normalized_lines = [raw_lines[header_index].lstrip("#")]
        normalized_lines.extend(raw_lines[header_index + 1:])

        reader = csv.DictReader(normalized_lines)
        for row in reader:
            if not row:
                continue

            rows.append(PostEqualizerRow(
                type=(row.get("Type", "") or "").strip(),
                pin=(row.get("Pin", "") or "").strip(),
                related_pin=(row.get("Related Pin", "") or "").strip(),
                when=(row.get("When", "") or "").strip(),
                ff_max_min=(row.get("FF-Max (Min)", "") or "").strip(),
                tt_max_min=(row.get("TT-Max (Min)", "") or "").strip(),
                ss_max_min=(row.get("SS-Max (Min)", "") or "").strip(),
                sf_max_min=(row.get("SF-Max (Min)", "") or "").strip(),
                corner_status=(row.get("Corner:FF/TT/SS/SF/FS", "") or "").strip(),
                comment=(row.get("Comment", "") or "").strip(),
            ))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading Compatibility_Final.csv: {e}")

    return PostEqualizerData(
        project=project,
        subproject=subproject,
        cell=cell,
        rows=rows,
        exists=True,
        note=f"Loaded {len(rows)} rows"
    )
