# app/services/file_parser_service.py

from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from PyPDF2 import PdfReader
from docx import Document as DocxDocument


class FileParserService:
    SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}

    @staticmethod
    def _get_extension(filename: str | None) -> str:
        if not filename or "." not in filename:
            return ""
        return "." + filename.rsplit(".", 1)[-1].lower()

    @staticmethod
    def validate_file(file: UploadFile) -> None:
        """
        Validate uploaded file type using filename extension.
        """
        ext = FileParserService._get_extension(file.filename)

        if ext not in FileParserService.SUPPORTED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type. Allowed types: .txt, .pdf, .docx",
            )

    @staticmethod
    def parse_txt(file_bytes: bytes) -> str:
        try:
            return file_bytes.decode("utf-8").strip()
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not decode text file as UTF-8",
            )

    @staticmethod
    def parse_pdf(file_bytes: bytes) -> str:
        try:
            reader = PdfReader(BytesIO(file_bytes))
            pages_text = []

            for page in reader.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    pages_text.append(page_text.strip())

            return "\n".join(pages_text).strip()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse PDF file",
            )

    @staticmethod
    def parse_docx(file_bytes: bytes) -> str:
        try:
            doc = DocxDocument(BytesIO(file_bytes))
            paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs).strip()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to parse DOCX file",
            )

    @staticmethod
    async def parse_upload_file(file: UploadFile) -> dict:
        """
        Parse uploaded file and return extracted text + metadata.
        """
        FileParserService.validate_file(file)

        file_bytes = await file.read()
        ext = FileParserService._get_extension(file.filename)

        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty",
            )

        if ext == ".txt":
            raw_text = FileParserService.parse_txt(file_bytes)
            mime_type = "text/plain"

        elif ext == ".pdf":
            raw_text = FileParserService.parse_pdf(file_bytes)
            mime_type = "application/pdf"

        elif ext == ".docx":
            raw_text = FileParserService.parse_docx(file_bytes)
            mime_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type",
            )

        if not raw_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No readable text could be extracted from the uploaded file",
            )

        return {
            "file_name": file.filename,
            "mime_type": mime_type,
            "raw_text": raw_text,
        }