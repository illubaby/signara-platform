"""
Application layer: Use cases for PVT operations.

Contains business logic for processing PVT (Process-Voltage-Temperature) mode strings.
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class MergePVTMode:
    """
    Use case: Merge PVT mode strings by removing mode suffixes and deduplicating.
    
    Takes a list of PVT strings with mode suffixes (e.g., "_PreLoopBack", "_PostLoopBack")
    and returns the unique PVT values without modes, along with the count.
    """
    
    def execute(self, pvt_mode_list: list[str]) -> Tuple[list[str], int]:
        """
        Remove mode suffixes from PVT strings and return unique PVT values.
        
        Args:
            pvt_mode_list: List of PVT strings with mode suffixes
                          (e.g., ["ssg0p675v125c_PreLoopBack", "ssg0p675v125c_PostLoopBack"])
        
        Returns:
            Tuple containing:
                - List of unique PVT strings without mode suffixes (preserving order of first occurrence)
                - Count of unique PVT values
        
        Example:
            Input: ["ssg0p675v125c_PreLoopBack", "ssg0p675v125c_PostLoopBack", "tt0p75v25c_PreLoopBack"]
            Output: (["ssg0p675v125c", "tt0p75v25c"], 2)
        
        Raises:
            ValueError: If input list is None or contains invalid entries
        """
        if pvt_mode_list is None:
            logger.warning("None value provided for pvt_mode_list")
            raise ValueError("PVT mode list cannot be None")
        
        if not pvt_mode_list:
            logger.info("Empty PVT mode list provided, returning empty result")
            return ([], 0)
        
        logger.info(f"Processing {len(pvt_mode_list)} PVT mode entries")
        
        # Extract PVT by removing mode suffix (everything after last underscore)
        unique_pvts = []
        seen = set()
        
        for pvt_mode in pvt_mode_list:
            if not isinstance(pvt_mode, str):
                logger.error(f"Invalid entry in list: {pvt_mode} (type: {type(pvt_mode)})")
                raise ValueError(f"All entries must be strings, got: {type(pvt_mode)}")
            
            if not pvt_mode.strip():
                logger.warning("Empty or whitespace-only string found in list")
                continue
            
            # Split by underscore and take all parts except the last (mode)
            parts = pvt_mode.rsplit('_', 1)
            pvt = parts[0] if len(parts) > 1 else pvt_mode
            
            # Add only if not seen before (preserve order)
            if pvt not in seen:
                unique_pvts.append(pvt)
                seen.add(pvt)
        
        count = len(unique_pvts)
        logger.info(f"Extracted {count} unique PVT values from input")
        logger.debug(f"Unique PVTs: {unique_pvts}")
        
        return (unique_pvts, count)


__all__ = ['MergePVTMode']

