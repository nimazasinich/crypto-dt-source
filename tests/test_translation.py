"""
Test suite for Persian to English translation
Tests verify that the index.html file has been properly translated
"""

import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup


# Load the HTML file once for all tests
@pytest.fixture(scope="module")
def html_content():
    """Load and parse the index.html file"""
    html_path = Path("index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    return content


@pytest.fixture(scope="module")
def soup(html_content):
    """Parse HTML content with BeautifulSoup"""
    return BeautifulSoup(html_content, "html.parser")


class TestHTMLAttributes:
    """
    Unit tests for HTML attributes
    Feature: persian-to-english-translation, Property 2: HTML language attributes are English
    Validates: Requirements 2.1, 2.2
    """

    def test_html_lang_attribute_is_english(self, soup):
        """Test that the HTML lang attribute is set to 'en'"""
        html_tag = soup.find("html")
        assert html_tag is not None, "HTML tag not found"
        assert (
            html_tag.get("lang") == "en"
        ), f"Expected lang='en', got lang='{html_tag.get('lang')}'"

    def test_html_dir_attribute_is_ltr(self, soup):
        """Test that the HTML dir attribute is set to 'ltr'"""
        html_tag = soup.find("html")
        assert html_tag is not None, "HTML tag not found"
        assert html_tag.get("dir") == "ltr", f"Expected dir='ltr', got dir='{html_tag.get('dir')}'"


class TestSpecificElements:
    """
    Unit tests for specific HTML elements
    """

    def test_page_title_is_english(self, soup):
        """
        Feature: persian-to-english-translation, Property 4: Page title is in English
        Validates: Requirements 2.3
        """
        title_tag = soup.find("title")
        assert title_tag is not None, "Title tag not found"
        title_text = title_tag.get_text()

        # Check that title doesn't contain Persian characters
        persian_pattern = re.compile(r"[\u0600-\u06FF]")
        assert not persian_pattern.search(
            title_text
        ), f"Title contains Persian characters: {title_text}"

        # Check that title contains expected English text
        assert (
            "Crypto Intelligence Hub" in title_text
        ), f"Expected 'Crypto Intelligence Hub' in title, got: {title_text}"

    def test_navigation_tabs_are_english(self, soup):
        """
        Feature: persian-to-english-translation, Property 3: Navigation tabs are in English
        Validates: Requirements 1.1
        """
        expected_tabs = [
            "Dashboard",
            "Market",
            "AI Models",
            "Sentiment",
            "News",
            "Providers",
            "Diagnostics",
            "API",
        ]

        nav = soup.find("nav", class_="tabs-nav")
        assert nav is not None, "Navigation tabs not found"

        tab_buttons = nav.find_all("button", class_="tab-btn")
        assert len(tab_buttons) >= len(
            expected_tabs
        ), f"Expected at least {len(expected_tabs)} tabs, found {len(tab_buttons)}"

        # Extract text from tabs (removing emojis)
        tab_texts = []
        for button in tab_buttons:
            text = button.get_text().strip()
            # Remove emoji characters
            text = re.sub(r"[\U0001F300-\U0001F9FF]", "", text).strip()
            tab_texts.append(text)

        # Check that all expected tabs are present
        for expected_tab in expected_tabs:
            assert (
                expected_tab in tab_texts
            ), f"Expected tab '{expected_tab}' not found in {tab_texts}"

        # Check no Persian characters in any tab
        persian_pattern = re.compile(r"[\u0600-\u06FF]")
        for tab_text in tab_texts:
            assert not persian_pattern.search(
                tab_text
            ), f"Tab contains Persian characters: {tab_text}"

    def test_status_messages_are_english(self, soup):
        """
        Feature: persian-to-english-translation, Property 5: Status messages are in English
        Validates: Requirements 1.3
        """
        status_badge = soup.find("div", class_="status-badge")
        assert status_badge is not None, "Status badge not found"

        status_text = status_badge.get_text()

        # Check that status doesn't contain Persian characters
        persian_pattern = re.compile(r"[\u0600-\u06FF]")
        assert not persian_pattern.search(
            status_text
        ), f"Status badge contains Persian characters: {status_text}"

        # Check that status contains expected English text
        assert (
            "Checking" in status_text or "Connected" in status_text or "Online" in status_text
        ), f"Expected English status message, got: {status_text}"


from hypothesis import given, settings
from hypothesis import strategies as st


class TestPersianCharacterDetection:
    """
    Property-based tests for Persian character detection
    Feature: persian-to-english-translation, Property 1: No Persian text in user interface
    Validates: Requirements 1.2, 1.4, 3.1, 3.2, 3.3, 3.4, 5.1, 5.2, 5.3, 5.4, 5.5
    """

    def test_no_persian_characters_in_visible_text(self, soup):
        """Test that no visible text elements contain Persian characters"""
        persian_pattern = re.compile(r"[\u0600-\u06FF]")

        # Get all text-containing elements
        text_elements = soup.find_all(text=True)

        # Filter out script and style tags
        visible_texts = []
        for element in text_elements:
            parent = element.parent
            if parent.name not in ["script", "style", "head"]:
                text = element.strip()
                if text:
                    visible_texts.append(text)

        # Check each visible text for Persian characters
        persian_found = []
        for text in visible_texts:
            if persian_pattern.search(text):
                persian_found.append(text)

        assert (
            len(persian_found) == 0
        ), f"Found {len(persian_found)} text elements with Persian characters: {persian_found[:5]}"

    def test_no_persian_in_button_labels(self, soup):
        """Test that all button labels are in English"""
        persian_pattern = re.compile(r"[\u0600-\u06FF]")

        buttons = soup.find_all("button")
        for button in buttons:
            button_text = button.get_text().strip()
            assert not persian_pattern.search(
                button_text
            ), f"Button contains Persian characters: {button_text}"

    def test_no_persian_in_form_labels(self, soup):
        """Test that all form labels are in English"""
        persian_pattern = re.compile(r"[\u0600-\u06FF]")

        labels = soup.find_all("label")
        for label in labels:
            label_text = label.get_text().strip()
            assert not persian_pattern.search(
                label_text
            ), f"Label contains Persian characters: {label_text}"

    def test_no_persian_in_placeholders(self, soup):
        """Test that all placeholder attributes are in English"""
        persian_pattern = re.compile(r"[\u0600-\u06FF]")

        # Find all elements with placeholder attribute
        elements_with_placeholder = soup.find_all(attrs={"placeholder": True})
        for element in elements_with_placeholder:
            placeholder = element.get("placeholder", "")
            assert not persian_pattern.search(
                placeholder
            ), f"Placeholder contains Persian characters: {placeholder}"

    def test_no_persian_in_headings(self, soup):
        """Test that all headings (h1-h6) are in English"""
        persian_pattern = re.compile(r"[\u0600-\u06FF]")

        for heading_level in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            headings = soup.find_all(heading_level)
            for heading in headings:
                heading_text = heading.get_text().strip()
                assert not persian_pattern.search(
                    heading_text
                ), f"{heading_level.upper()} contains Persian characters: {heading_text}"

    @settings(max_examples=100)
    @given(st.text(alphabet=st.characters(min_codepoint=0x0600, max_codepoint=0x06FF), min_size=1))
    def test_persian_character_detection_works(self, persian_text):
        """
        Property-based test to verify our Persian character detection works correctly
        This test generates random Persian text and verifies our regex can detect it
        """
        persian_pattern = re.compile(r"[\u0600-\u06FF]")
        assert persian_pattern.search(
            persian_text
        ), f"Persian pattern should detect Persian text: {persian_text}"

    def test_consistent_terminology(self, soup):
        """Test that consistent English terminology is used throughout"""
        # Check that "Refresh" is used consistently for refresh buttons
        refresh_buttons = soup.find_all("button", class_="btn-refresh")
        for button in refresh_buttons:
            button_text = button.get_text().strip()
            # Remove emoji
            button_text = re.sub(r"[\U0001F300-\U0001F9FF]", "", button_text).strip()
            assert "Refresh" in button_text, f"Expected 'Refresh' in button, got: {button_text}"

        # Check that "Analyze" is used consistently for analysis buttons
        analyze_buttons = soup.find_all("button", string=re.compile(r"Analyze", re.IGNORECASE))
        assert len(analyze_buttons) > 0, "Expected to find 'Analyze' buttons"

        for button in analyze_buttons:
            button_text = button.get_text().strip()
            # Remove emoji
            button_text = re.sub(r"[\U0001F300-\U0001F9FF]", "", button_text).strip()
            assert (
                "Analyze" in button_text or "Analysis" in button_text
            ), f"Expected 'Analyze' or 'Analysis' in button, got: {button_text}"
