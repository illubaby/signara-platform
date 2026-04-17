"""Default checklist template."""


def get_default_checklist_template() -> list:
    """
    Return the default checklist template structure.
    
    This template is used when creating a new checklist for a project
    that doesn't have one in Perforce yet.
    
    Returns:
        List of checklist sections with task groups and items
    """
    return [
        {
            "title": "Preliminary Release",
            "milestone": "prelim",
            "task_groups": [
                {
                    "title": "Basic consistency checklist",
                    "duration": "1",
                    "tasks": [
                        {
                            "item": "Create ProjectInfo.xlsx. Place at: //wwcad/msip/projects/ucie/{project}/{rel}/pcs/design/timing/ProjectInfo.xlsx. Ensure the following are filled correctly: Project name, release, process, voltage / temperature corners, macro list",
                            "done": False,
                            "note": "",
                            "date": ""
                        },
                        {
                            "item": "Do Project Seeding. All data is seeded and uploaded to P4; all users are synced to their working dirs.",
                            "done": False,
                            "note": "",
                            "date": ""
                        },
                        {
                            "item": "Prepare Preliminary LIB (Define clearly where the data comes from, all preliminary data must be traceable to a source (reference project, spec, Jira, or CKT confirmation)",
                            "done": False,
                            "note": "",
                            "date": ""
                        },
                        {
                            "item": "Complete All TMQA Checks. Ensure no missing or mismatched fundamental data before moving forward.Mandatory TMQA focus areas: Slew / Load, Pin Consistency, Timing Arcs, Operating Condition, passed GTA",
                            "done": False,
                            "note": "",
                            "date": ""
                        }
                    ]
                }
            ]
        },
        {
            "title": "Prefinal Release",
            "milestone": "prefinal",
            "task_groups": [
                {
                    "title": "Week 1: Setup Clean",
                    "duration": "1",
                    "tasks": [
                        {
                            "item": "Collect and send BBOX list to CKT to clean SNE",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Open a Jira task to collect the design snapshot : Each macro must provide an ETA. The release can be done in sequence; it is not necessary for all macros to be released on the same date.",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Clean setup with nolpe netlist. (can be skiped if lpe netlist have already existed)",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Fix topology violations: Timing point, Netname, Connectivity. Confirm topology fixes with CKT team.",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Confirm setups are clean before proceeding LPE. Lib successfully generate and passed GTA",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "If auto-POCV not working, did you generate the POCV database using manual approach ?",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Open a Jira Collect Bias Voltage for Analog blocks (usually in RX)",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Create internal release lib path, update Porject Status in platform.Ex: //wwcad/msip/projects/ucie/{prj}/{rel}/design/timing/release/internal/{release_date}/",
                            "note": "",
                            "date": "",
                            "done": False
                        }
                    ]
                },
                {
                    "title": "Week 2: Design Freeze & Coordination",
                    "duration": "1",
                    "tasks": [
                        {
                            "item": "Extract netlist (bbox, flatten). Place netlist into corrected P4 paths",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Open a Jira Collect timing constraints/MPW for all cells",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Run characterization (NT & SiS)",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Check log file without errors",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Slew&Load match with golden plan",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Upload libs to final lib paths.",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Run TMQA using P4 path (final lib path)",
                            "note": "",
                            "date": "",
                            "done": False
                        }                    
                    
                    ]
                },
                {
                    "title": "Week 3: Reporting & Review",
                    "duration": "1",
                    "tasks": [
                        {
                            "item": "Send TMQC report to CKT (mandatory)",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Hold TMQC review meeting with CKT, send out Ais (Jira).",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Complete ALL reports 3 days before release day",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Run Package Compare (if any)",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Run Special Check. All fixes must be done in Final Timing Lib Path (p4)",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Review Final Timing Report (FTR) internally",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Schedule and hold FTR review with CKT team and VN timing team",
                            "note": "",
                            "date": "",
                            "done": False
                        }
                    ]
                }
            ]
        },
        {
            "title": "Final Release",
            "milestone": "final",
            "task_groups": [
                {
                    "title": "Final Database & GDS Updates",
                    "duration": "1",
                    "tasks": [
                        {
                            "item": "Open a Jira task to collect the design snapshot : Each macro must provide an ETA. The release can be done in sequence; it is not necessary for all macros to be released on the same date.",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Run TMQC on final GDS",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Review TMQC results with CKT team",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Review Spice vs Spice report",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Review NT vs Spice",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Regenerate corresponding reports and the Final Timing Review. Verify design intent with CKT team,Obtain final timing release signoff",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Update all affected cells, confirm no issues exist in updated database",
                            "note": "",
                            "date": "",
                            "done": False
                        }
                    ]
                }
            ]
        },
        {
            "title": "SwapGDS Release",
            "milestone": "swap_gds",
            "task_groups": [
                {
                    "title": "Final Database & GDS Updates",
                    "duration": "1",
                    "tasks": [
                        {
                            "item": "Finalize internal timing & GDS updates",
                            "note": "",
                            "date": "",
                            "done": False
                        },
                        {
                            "item": "Run TMQC only if critical updates from CKT",
                            "note": "",
                            "date": "",
                            "done": False
                        }
                    ]
                }
            ]
        }
    ]
