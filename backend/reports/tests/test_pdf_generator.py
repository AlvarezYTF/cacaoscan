"""
Tests for PDF generator.
"""
import pytest
from io import BytesIO
from unittest.mock import patch, MagicMock
from reports.pdf_generator import CacaoReportPDFGenerator


@pytest.mark.django_db
class TestCacaoReportPDFGenerator:
    """Tests for CacaoReportPDFGenerator class."""
    
    @pytest.fixture
    def generator(self):
        """Create PDF generator instance."""
        return CacaoReportPDFGenerator()
    
    @pytest.fixture
    def mock_user(self, admin_user):
        """Create mock user."""
        return admin_user
    
    @pytest.fixture
    def mock_images_queryset(self):
        """Create mock images queryset."""
        mock_queryset = MagicMock()
        mock_queryset.count.return_value = 0
        mock_queryset.exists.return_value = False
        mock_queryset.filter.return_value = mock_queryset
        mock_queryset.select_related.return_value = mock_queryset
        mock_queryset.__iter__ = MagicMock(return_value=iter([]))
        return mock_queryset
    
    def test_initialization(self, generator):
        """Test generator initialization."""
        assert generator is not None
        assert hasattr(generator, 'styles')
        assert 'CustomTitle' in generator.styles.byName
    
    def test_setup_custom_styles(self, generator):
        """Test custom styles setup."""
        assert 'CustomTitle' in generator.styles.byName
        assert 'CustomHeading' in generator.styles.byName
        assert 'CustomNormal' in generator.styles.byName
    
    def test_generate_quality_report_empty_queryset(self, generator, mock_user, mock_images_queryset):
        """Test generating quality report with empty queryset."""
        buffer = generator.generate_quality_report(
            images_queryset=mock_images_queryset,
            user=mock_user,
            filters=None
        )
        
        assert isinstance(buffer, BytesIO)
        assert buffer.getvalue() is not None
    
    def test_generate_quality_report_with_filters(self, generator, mock_user, mock_images_queryset):
        """Test generating quality report with filters."""
        filters = {
            'date_from': '2024-01-01',
            'date_to': '2024-12-31'
        }
        
        buffer = generator.generate_quality_report(
            images_queryset=mock_images_queryset,
            user=mock_user,
            filters=filters
        )
        
        assert isinstance(buffer, BytesIO)

