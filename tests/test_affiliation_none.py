"""Test for handling None values in affiliation text."""
from lxml import etree
from pubmed_parser.medline_parser import parse_author_affiliation


def test_affiliation_with_none_text():
    """Test that parse_author_affiliation handles None values in affiliation text."""
    # Create a test XML structure with an affiliation element that has None text
    xml_string = """
    <MedlineCitation>
        <Article>
            <AuthorList>
                <Author>
                    <LastName>Doe</LastName>
                    <ForeName>John</ForeName>
                    <Initials>J</Initials>
                    <AffiliationInfo>
                        <Affiliation>Department of Medicine, University Hospital</Affiliation>
                    </AffiliationInfo>
                    <AffiliationInfo>
                        <Affiliation></Affiliation>
                    </AffiliationInfo>
                    <AffiliationInfo>
                        <Affiliation>Research Center</Affiliation>
                    </AffiliationInfo>
                </Author>
            </AuthorList>
        </Article>
    </MedlineCitation>
    """
    
    medline = etree.fromstring(xml_string.encode('utf-8'))
    
    # This should not raise an AttributeError
    authors = parse_author_affiliation(medline)
    
    # Verify the result
    assert len(authors) == 1
    assert authors[0]['lastname'] == 'Doe'
    assert authors[0]['forename'] == 'John'
    assert authors[0]['initials'] == 'J'
    # The empty affiliation should be filtered out
    assert authors[0]['affiliation'] == 'Department of Medicine, University Hospital|Research Center'


def test_affiliation_with_all_none():
    """Test that parse_author_affiliation handles all None values in affiliation text."""
    xml_string = """
    <MedlineCitation>
        <Article>
            <AuthorList>
                <Author>
                    <LastName>Smith</LastName>
                    <ForeName>Jane</ForeName>
                    <Initials>J</Initials>
                    <AffiliationInfo>
                        <Affiliation></Affiliation>
                    </AffiliationInfo>
                </Author>
            </AuthorList>
        </Article>
    </MedlineCitation>
    """
    
    medline = etree.fromstring(xml_string.encode('utf-8'))
    
    # This should not raise an AttributeError
    authors = parse_author_affiliation(medline)
    
    # Verify the result
    assert len(authors) == 1
    assert authors[0]['lastname'] == 'Smith'
    assert authors[0]['forename'] == 'Jane'
    assert authors[0]['initials'] == 'J'
    # All empty affiliations should result in empty string
    assert authors[0]['affiliation'] == ''


def test_affiliation_with_special_text():
    """Test that the special affiliation text is properly replaced."""
    xml_string = """
    <MedlineCitation>
        <Article>
            <AuthorList>
                <Author>
                    <LastName>Brown</LastName>
                    <ForeName>Bob</ForeName>
                    <Initials>B</Initials>
                    <AffiliationInfo>
                        <Affiliation>For a full list of the authors' affiliations please see the Acknowledgements section.</Affiliation>
                    </AffiliationInfo>
                    <AffiliationInfo>
                        <Affiliation>Valid Affiliation</Affiliation>
                    </AffiliationInfo>
                </Author>
            </AuthorList>
        </Article>
    </MedlineCitation>
    """
    
    medline = etree.fromstring(xml_string.encode('utf-8'))
    
    # This should not raise an AttributeError
    authors = parse_author_affiliation(medline)
    
    # Verify the result
    assert len(authors) == 1
    assert authors[0]['lastname'] == 'Brown'
    # The special text should be replaced with empty string, leaving only the valid affiliation
    # Note: empty string after replace will be filtered out by the join
    assert authors[0]['affiliation'] == '|Valid Affiliation'
