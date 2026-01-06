"""
Tests for date parsing functionality in medline_parser.py
"""
import os
from lxml import etree
import pubmed_parser as pp
from pubmed_parser.medline_parser import parse_date_element


def test_parse_date_element_full_date():
    """Test parsing a complete date with Year, Month, and Day"""
    xml_str = """
    <DateCompleted>
        <Year>2002</Year>
        <Month>12</Month>
        <Day>30</Day>
    </DateCompleted>
    """
    element = etree.fromstring(xml_str)
    result = parse_date_element(element)
    assert result == "2002-12-30"


def test_parse_date_element_year_month_only():
    """Test parsing a date with only Year and Month"""
    xml_str = """
    <DateCompleted>
        <Year>2002</Year>
        <Month>12</Month>
    </DateCompleted>
    """
    element = etree.fromstring(xml_str)
    result = parse_date_element(element)
    assert result == "2002-12"


def test_parse_date_element_year_only():
    """Test parsing a date with only Year"""
    xml_str = """
    <DateCompleted>
        <Year>2002</Year>
    </DateCompleted>
    """
    element = etree.fromstring(xml_str)
    result = parse_date_element(element)
    assert result == "2002"


def test_parse_date_element_none():
    """Test parsing when element is None"""
    result = parse_date_element(None)
    assert result == ""


def test_parse_date_element_empty():
    """Test parsing when element is empty"""
    xml_str = "<DateCompleted></DateCompleted>"
    element = etree.fromstring(xml_str)
    result = parse_date_element(element)
    assert result == ""


def test_parse_date_element_month_abbreviation():
    """Test parsing a date with month abbreviation (like 'Jan')"""
    xml_str = """
    <DateCompleted>
        <Year>2002</Year>
        <Month>Jan</Month>
        <Day>15</Day>
    </DateCompleted>
    """
    element = etree.fromstring(xml_str)
    result = parse_date_element(element)
    assert result == "2002-01-15"


def test_parse_date_element_single_digit_month_day():
    """Test parsing a date with single digit month and day"""
    xml_str = """
    <DateCompleted>
        <Year>2002</Year>
        <Month>5</Month>
        <Day>7</Day>
    </DateCompleted>
    """
    element = etree.fromstring(xml_str)
    result = parse_date_element(element)
    assert result == "2002-05-07"


def test_medline_xml_integration():
    """Test that parse_medline_xml includes date_completed and date_revised"""
    parsed_medline = pp.parse_medline_xml('data/pubmed20n0014.xml.gz')
    articles = list(parsed_medline)
    
    # Check that we have articles
    assert len(articles) > 0
    
    # Check first article has the new fields
    first_article = articles[0]
    assert 'date_completed' in first_article
    assert 'date_revised' in first_article
    
    # Check the values are non-empty strings for first article
    assert isinstance(first_article['date_completed'], str)
    assert isinstance(first_article['date_revised'], str)
    assert len(first_article['date_completed']) > 0
    assert len(first_article['date_revised']) > 0


def test_medline_xml_date_format():
    """Test that dates in actual MEDLINE XML are formatted correctly"""
    parsed_medline = pp.parse_medline_xml('data/pubmed20n0014.xml.gz')
    articles = list(parsed_medline)
    
    # Test first article (PMID: 399296)
    # Based on inspection, this should have:
    # DateCompleted: 1980-11-20
    # DateRevised: 2003-11-14
    first_article = articles[0]
    assert first_article['pmid'] == '399296'
    assert first_article['date_completed'] == '1980-11-20'
    assert first_article['date_revised'] == '2003-11-14'


def test_medline_xml_multiple_articles():
    """Test date parsing for multiple articles"""
    parsed_medline = pp.parse_medline_xml('data/pubmed20n0014.xml.gz')
    articles = list(parsed_medline)
    
    # Test that all articles have the date fields
    for article in articles[:100]:  # Test first 100 articles
        assert 'date_completed' in article
        assert 'date_revised' in article
        # Date fields should be strings (even if empty)
        assert isinstance(article['date_completed'], str)
        assert isinstance(article['date_revised'], str)


def test_date_format_validation():
    """Test that parsed dates follow the expected format"""
    parsed_medline = pp.parse_medline_xml('data/pubmed20n0014.xml.gz')
    articles = list(parsed_medline)
    
    import re
    # Pattern for YYYY, YYYY-MM, or YYYY-MM-DD
    date_pattern = re.compile(r'^(\d{4}(-\d{2}(-\d{2})?)?)?$')
    
    for article in articles[:100]:  # Test first 100 articles
        date_completed = article['date_completed']
        date_revised = article['date_revised']
        
        # Both should match the pattern (including empty string)
        assert date_pattern.match(date_completed), \
            f"Invalid date_completed format: '{date_completed}' for PMID {article['pmid']}"
        assert date_pattern.match(date_revised), \
            f"Invalid date_revised format: '{date_revised}' for PMID {article['pmid']}"
