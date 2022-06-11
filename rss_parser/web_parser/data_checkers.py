"""This module provides checkers to check tags from html page."""

import re
from abc import ABC, abstractmethod


class TagChecker(ABC):
    """Abstract class for checkers.

    Inherited classes must redefine the "check" method.
    """

    @abstractmethod
    def check(self, tag, instance_flag):
        """Provide the "check" method as a required interface.

        Args:
            tag: html tag
            instance_flag: the flag that shows to which instance the tag belongs
        """


class CaptionHrefChecker(TagChecker):
    """Inherited class of "TagChecker".

    If image caption is not empty, look for "href" in it. Return True if image caption contains "href".
    """

    def check(self, tag, _instance_flag):
        """Look for "href" symbols in image caption. Return True if image caption contains "href".

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        caption = tag.get("alt")
        if caption:
            return "href" in caption
        return False


class Icons(TagChecker):
    """Inherited class of "TagChecker".

    Look for the icons pattern in the image url.
    """

    def check(self, tag, _instance_flag):
        """Look for the icons pattern in the image url.

        Example icons pattern: 200x200, 670x50

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        icons_pattern = r"\d0{1,2}(:|x)\d{1,2}0"
        image = tag.get("src")
        if re.search(icons_pattern, image):
            return True
        return False


class StatsResearchLinks(TagChecker):
    """Inherited class of "TagChecker".

    Look for links in "img" tag that provides by statistics collection sites.
    """

    def check(self, tag, _instance_flag):
        """Look for the names of statistics collection sites in image links. Return True if the names are found.

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        statistics_collection_sites = [
            "stats",
            "scorecardresearch",
            "noscript",
            "top-fwz1",
            "mc.yandex.ru",
        ]
        image = tag.get("src")
        for site in statistics_collection_sites:
            if site in image:
                return True
        return False


class ImageBBCComNotSrc(TagChecker):
    """Inherited class of "TagChecker".

    Special checker for "bbc.com" rss-news.
    All images in the articles on this site should contain the "srcset" tag.
    """

    def check(self, tag, _instance_flag):
        """Check "bbc.com" images.

        Look for "bbc" symbols in image links. If there are symbols,
        look for "srcset" in the "img" tag. Return True if the "srcset" tag is empty.

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        image = tag.get("src")
        if "bbc" in image:
            image_src_set = tag.get("srcset")
            if image_src_set is None:
                return True
            if "line" in image:
                return True
        return False


class ImageDoubleColon(TagChecker):
    """Inherited class of "TagChecker".

    Look for "::" symbols in image links. Links with these symbols doesn't work as expected.
    """

    def check(self, tag, _instance_flag):
        """Look for "::" symbols in image links. Return True if the symbols are found.

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        image = tag.get("src")
        return "::" in image


class ImageDuplicateChecker(TagChecker):
    """Inherited class of "TagChecker".

    Look for repetitive image links.
    """

    instance = None
    duplicates = set()

    def check(self, tag, instance_flag):
        """Look for repetitive image links. Return True if repetition are found.

        "instance_flag" is used to check, if there are the same images in different news.

        Args:
            tag: "img" tag
            instance_flag: the flag that shows to which instance the tag belongs, uses to reset duplicates for new news

        Returns:
            bool
        """
        image = tag.get("src")
        if ImageDuplicateChecker.instance is None or ImageDuplicateChecker.instance != instance_flag:
            ImageDuplicateChecker.instance = instance_flag
            ImageDuplicateChecker.duplicates = set()

        if image in ImageDuplicateChecker.duplicates:
            return True
        ImageDuplicateChecker.duplicates.add(image)
        return False


class NewsPageLogoChecker(TagChecker):
    """Inherited class of "TagChecker".

    Look for "a" in the parent tag of the "img" tag.
    """

    def check(self, tag, _instance_flag):
        """Look for "a" in the parent tag of the "img" tag. Return True if "a" is found in the parent tag.

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        img_parent = tag.findParent()
        return img_parent.name == "a"


class ImageExtensionChecker(TagChecker):
    """Inherited class of "TagChecker".

    Look for prohibited extensions in image links.
    """

    def __init__(self):
        """Define tuple of prohibited extensions."""
        self.prohibited_extensions = ("gif", "svg")

    def check(self, tag, _instance_flag):
        """Look for prohibited extensions in image links. Return True if prohibited extensions are found.

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        image = tag.get("src")
        return image.endswith(self.prohibited_extensions)


class NoImageExistenceChecker(TagChecker):
    """Inherited class of "TagChecker".

    Look for image link existence.
    """

    def check(self, tag, _instance_flag):
        """Look for image link existence. Return True if link doesn't exist.

        Args:
            tag: "img" tag
            _instance_flag: the flag that shows to which instance the tag belongs

        Returns:
            bool
        """
        image = tag.get("src")
        return not bool(image)


def html_image_checker(tag, instance_flag):
    """Provide checking system of image source of "img" tag.

    If any of the checks is passed (return True), then the check will be considered failed and return False.
    If all of the checks are passed, the tag is accepted and True returns.

    Args:
        tag: "img" tag
        instance_flag: the flag that shows to which instance the tag belongs

    Returns:
        bool
    """
    classes_to_check = [
        NoImageExistenceChecker,
        ImageExtensionChecker,
        NewsPageLogoChecker,
        ImageDuplicateChecker,
        ImageDoubleColon,
        ImageBBCComNotSrc,
        StatsResearchLinks,
        Icons,
    ]
    for class_name in classes_to_check:
        if class_name().check(tag, instance_flag):
            return False
    return True


def html_caption_checker(tag, instance_flag):
    """Provide checking system of caption of "img" tag.

    If any of the checks is passed (return True), then the check will be considered failed and return False.
    If all of the checks are passed, the tag is accepted and True returns.

    Args:
        tag: "img" tag
        instance_flag: the flag that shows to which instance the tag belongs

    Returns:
        bool
    """
    classes_to_check = [
        CaptionHrefChecker,
    ]
    for class_name in classes_to_check:
        if class_name().check(tag, instance_flag):
            return False
    return True


def html_data_checker(tag, instance_flag):
    """Provide checking system of "img" tag.

    If any of the checks is passed (return True), then the check will be considered failed and return False.
    If all of the checks are passed, the tag is accepted and True returns.

    Args:
        tag: "img" tag
        instance_flag: the flag that shows to which instance the tag belongs

    Returns:
        bool
    """
    check_functions = [
        html_image_checker,
        html_caption_checker,
    ]
    for func in check_functions:
        if not func(tag, instance_flag):
            return False
    return True
