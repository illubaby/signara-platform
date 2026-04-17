from dataclasses import dataclass, asdict, fields, Field, field
from typing import Optional, Annotated, get_type_hints, get_args


@dataclass
class Cell:
    """Domain entity representing a cell with its attributes across different stages."""
    
    # CKT macros information
    ckt_macros: Annotated[str, "CKT Macros"]
    tool: Annotated[str, "Tool"]
    pic: Annotated[Optional[str], "PIC"] = None
    netlist_snaphier: Annotated[Optional[str], "Netlist Snaphier"] = None
    ckt_snaphier: Annotated[Optional[str], "CKT Snaphier"] = None
    pvt_summary: Annotated[Optional[dict], "PVT Status"] = None
    
    # Alib Generation
    # raw_libs: Annotated[Optional[str], "Raw Libs"] = None
    tmqa: Annotated[Optional[str], "TMQA"] = None
    
    # Final Status
    final_status: Annotated[Optional[str], "Final Status"] = None
    
    tmqc_spice_vs_nt: Annotated[Optional[str], "TMQC (Spice vs NT)"] = None
    tmqc_spice_vs_spice: Annotated[Optional[str], "TMQC (Spice vs Spice)"] = None
    equalization: Annotated[Optional[str], "Equalization"] = None
    # final_release: Annotated[Optional[str], "Final Release"] = None


   
    # Internal Timing
    assignee: Annotated[Optional[int], "Assignee"] = None
    duedate: Annotated[Optional[str], "Due Date"] = None
    status: Annotated[Optional[str], "Status"] = None
    jira_link: Annotated[Optional[str], "Jira Link"] = None
    

    
    def to_dict(self):
        """Convert cell to dictionary with empty strings for None values.
        Also includes any extra attributes added dynamically (e.g., 'hidden' flag)."""
        data = asdict(self)
        result = {
            key: (val if isinstance(val, dict) else (str(val) if val is not None else ""))
            for key, val in data.items()
        }
        
        # Include any extra attributes not in the dataclass definition
        for key, val in self.__dict__.items():
            if key not in result:
                result[key] = val
        
        return result
    
    @staticmethod
    def get_column_metadata():
        """Extract column metadata from Annotated type hints."""
        hints = get_type_hints(Cell, include_extras=True)
        return [
            {
                "key": field.name,
                "label": get_args(hints[field.name])[1] if hasattr(hints[field.name], '__metadata__') else field.name.replace("_", " ").title()
            }
            for field in fields(Cell)
        ]
    
