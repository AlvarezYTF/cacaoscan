"""
Base Excel generator for CacaoScan.
Contains common functionality and styles for Excel report generation.
"""
import logging
import io
from datetime import datetime
from django.utils import timezone
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side

logger = logging.getLogger("cacaoscan.services.report.excel.base")


class ExcelBaseGenerator:
    """
    Base class for Excel report generation.
    Provides common functionality and styles.
    """
    
    def __init__(self):
        self.workbook = None
        self.ws = None
    
    def _create_workbook(self, sheet_title: str = "Reporte"):
        """Creates a new workbook and worksheet."""
        self.workbook = Workbook()
        self.ws = self.workbook.active
        self.ws.title = sheet_title
    
    def _create_header(self, title: str, user=None):
        """
        Creates report header.
        
        Args:
            title: Report title
            user: User who requested the report
        """
        # Main title
        self.ws['A1'] = title
        self.ws['A1'].font = Font(size=16, bold=True, color="2F4F4F")
        self.ws['A1'].alignment = Alignment(horizontal='center')
        self.ws.merge_cells('A1:F1')
        
        # Report information
        self.ws['A3'] = f"Generado el: {timezone.now().strftime('%d/%m/%Y %H:%M')}"
        self.ws['A3'].font = Font(size=10, italic=True)
        
        if user:
            self.ws['A4'] = f"Usuario: {user.get_full_name() or user.username}"
            self.ws['A4'].font = Font(size=10, italic=True)
        
        # Space
        self.ws['A6'] = ""
    
    def _apply_header_style(self, row_num: int, num_cols: int):
        """
        Applies header style to a row.
        
        Args:
            row_num: Row number
            num_cols: Number of columns
        """
        header_fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        header_alignment = Alignment(horizontal='center', vertical='center')
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        
        for col in range(1, num_cols + 1):
            cell = self.ws.cell(row=row_num, column=col)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = thin_border
    
    def _apply_cell_border(self, row_num: int, col_num: int):
        """
        Applies border to a cell.
        
        Args:
            row_num: Row number
            col_num: Column number
        """
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        cell = self.ws.cell(row=row_num, column=col_num)
        cell.border = thin_border
    
    def _adjust_column_widths(self, column_widths: dict):
        """
        Adjusts column widths.
        
        Args:
            column_widths: Dict with column letters as keys and widths as values
        """
        for col, width in column_widths.items():
            try:
                self.ws.column_dimensions[col].width = width
            except Exception as e:
                logger.warning(f"Error adjusting column width {col}: {e}")
    
    def _save_to_buffer(self) -> bytes:
        """
        Saves workbook to buffer and returns content.
        
        Returns:
            bytes: Excel file content
        """
        buffer = io.BytesIO()
        try:
            self.workbook.save(buffer)
        except Exception as save_error:
            logger.error(f"Error saving workbook: {save_error}", exc_info=True)
            raise
        
        buffer.seek(0)
        content = buffer.getvalue()
        
        # Validate content
        if not content:
            logger.error("Generated Excel file is empty")
            raise ValueError("Generated Excel file is empty")
        
        if len(content) < 50:
            logger.warning(f"Generated Excel file is very small: {len(content)} bytes")
        
        return content
    
    def _get_client_ip(self, request):
        """Gets client IP address."""
        if not request:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _create_section_title(self, cell_address: str, title: str):
        """
        Creates a section title.
        
        Args:
            cell_address: Cell address (e.g., 'A8')
            title: Section title text
        """
        self.ws[cell_address] = title
        self.ws[cell_address].font = Font(size=14, bold=True, color="2F4F4F")
    
    def _create_table_with_data(
        self,
        data: list[list],
        start_row: int,
        header_row: int,
        column_widths: dict = None,
        header_alignment: str = 'center',
        body_alignment: str = 'center'
    ):
        """
        Creates a table with headers and data rows.
        
        Args:
            data: List of rows, first row should be headers
            start_row: Starting row number
            header_row: Row number for headers (usually same as start_row)
            column_widths: Dict with column letters as keys and widths as values
            header_alignment: Alignment for header cells ('center', 'left', 'right')
            body_alignment: Alignment for body cells ('center', 'left', 'right')
        """
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        header_fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        alignment_map = {
            'center': Alignment(horizontal='center'),
            'left': Alignment(horizontal='left'),
            'right': Alignment(horizontal='right')
        }
        header_align = alignment_map.get(header_alignment, Alignment(horizontal='center'))
        body_align = alignment_map.get(body_alignment, Alignment(horizontal='center'))
        
        for row_num, row_data in enumerate(data, start_row):
            is_header = row_num == header_row
            for col_num, cell_value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=cell_value)
                
                if is_header:
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_align
                else:
                    cell.alignment = body_align
                
                cell.border = thin_border
        
        if column_widths:
            self._adjust_column_widths(column_widths)
    
    def _create_table_with_headers(
        self,
        headers: list,
        data_rows: list[list],
        start_row: int,
        column_widths: list = None,
        header_alignment: str = 'center',
        body_alignment: str = 'center'
    ):
        """
        Creates a table with separate headers and data rows.
        
        Args:
            headers: List of header strings
            data_rows: List of data rows
            start_row: Starting row number for headers
            column_widths: List of widths (will be mapped to column letters)
            header_alignment: Alignment for header cells
            body_alignment: Alignment for body cells
        """
        thin_border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
        header_fill = PatternFill(start_color="2F4F4F", end_color="2F4F4F", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        alignment_map = {
            'center': Alignment(horizontal='center'),
            'left': Alignment(horizontal='left'),
            'right': Alignment(horizontal='right')
        }
        header_align = alignment_map.get(header_alignment, Alignment(horizontal='center'))
        body_align = alignment_map.get(body_alignment, Alignment(horizontal='center'))
        
        # Create headers
        for col_num, header in enumerate(headers, 1):
            cell = self.ws.cell(row=start_row, column=col_num, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border
        
        # Create data rows
        for row_offset, row_data in enumerate(data_rows, 1):
            row_num = start_row + row_offset
            for col_num, value in enumerate(row_data, 1):
                cell = self.ws.cell(row=row_num, column=col_num, value=value)
                cell.alignment = body_align
                cell.border = thin_border
        
        # Adjust column widths
        if column_widths:
            width_dict = {}
            for i, width in enumerate(column_widths, 1):
                col_letter = chr(64 + i)
                width_dict[col_letter] = width
            self._adjust_column_widths(width_dict)

