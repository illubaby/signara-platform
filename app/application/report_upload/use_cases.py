"""Use cases for uploading reports to Perforce."""
from dataclasses import dataclass
from app.infrastructure.p4.p4_path_repository import upload_file_to_p4
from app.infrastructure.logging.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class UploadReportInput:
    """Input for uploading a report file to P4."""
    local_path: str
    depot_path: str
    description: str | None = None


@dataclass
class UploadReportOutput:
    """Output of the upload operation."""
    success: bool
    message: str


class UploadReportToP4:
    """Use case for uploading a report file to Perforce depot."""
    
    def execute(self, input_data: UploadReportInput) -> UploadReportOutput:
        """
        Upload a local file to Perforce depot.
        
        Args:
            input_data: Upload parameters (local_path, depot_path, description)
            
        Returns:
            UploadReportOutput with success status and message
        """
        logger.info(f"[UploadReportToP4] Starting upload: {input_data.local_path} -> {input_data.depot_path}")
        
        try:
            success = upload_file_to_p4(
                local_path=input_data.local_path,
                depot_path=input_data.depot_path,
                description=input_data.description
            )
            
            if success:
                message = f"Successfully uploaded to {input_data.depot_path}"
                logger.info(f"[UploadReportToP4] {message}")
                return UploadReportOutput(success=True, message=message)
            else:
                message = "Upload failed."
                logger.error(f"[UploadReportToP4] {message}")
                return UploadReportOutput(success=False, message=message)
                
        except Exception as e:
            message = f"Upload error: {str(e)}"
            logger.error(f"[UploadReportToP4] {message}")
            return UploadReportOutput(success=False, message=message)
