# defusedxml
#
# Copyright (c) 2013 by Christian Heimes <christian@python.org>
# Licensed to PSF under a Contributor Agreement.
# See https://www.python.org/psf/license for licensing details.
"""Defused xml.etree.cElementTree
"""
from __future__ import absolute_import

import warnings

from .common import _generate_etree_functions

# This module IS the safe replacement: it wraps these raw stdlib parsers
# with entity/DTD-forbidding handlers below, so importing them here is required.
from xml.etree.cElementTree import TreeBuilder as _TreeBuilder  # nosec
from xml.etree.cElementTree import parse as _parse  # nosec
from xml.etree.cElementTree import tostring  # nosec

# iterparse from ElementTree!
from xml.etree.ElementTree import iterparse as _iterparse  # nosec

# This module is an alias for ElementTree just like xml.etree.cElementTree
from .ElementTree import (
    XML,
    XMLParse,
    XMLParser,
    XMLTreeBuilder,
    fromstring,
    iterparse,
    parse,
    tostring,
    DefusedXMLParser,
    ParseError,
)

__origin__ = "xml.etree.cElementTree"


warnings.warn(
    "defusedxml.cElementTree is deprecated, import from defusedxml.ElementTree instead.",
    category=DeprecationWarning,
    stacklevel=2,
)

# XMLParse is a typo, keep it for backwards compatibility
XMLTreeBuilder = XMLParse = XMLParser = DefusedXMLParser

parse, iterparse, fromstring = _generate_etree_functions(
    DefusedXMLParser, _TreeBuilder, _parse, _iterparse
)
XML = fromstring

__all__ = [
    "ParseError",
    "XML",
    "XMLParse",
    "XMLParser",
    "XMLTreeBuilder",
    "fromstring",
    "iterparse",
    "parse",
    "tostring",
]
