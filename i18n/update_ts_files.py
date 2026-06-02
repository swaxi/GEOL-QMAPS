#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update es, pt, zh .ts files based on GEOL_QMAPS_fr_update_report.txt.

Changes applied to each language:
  - Remove 21 obsolete <message> blocks
  - Update 58 <source> strings (strip &lt;p&gt; wrappers, fix typos)
  - Fix 2 source strings with whitespace issues (no <p> wrappers)
  - Insert 6 new <message> blocks (unfinished translations)
"""

import re
import os

base_dir = os.path.dirname(os.path.abspath(__file__))
LANGUAGES = ['es', 'pt', 'zh']


# ---------------------------------------------------------------------------
# Obsolete source texts to remove entirely (exact strings as in the files,
# BEFORE the <p>-strip step so we match the current file content)
# ---------------------------------------------------------------------------
OBSOLETE_GEOL_QMAPS = [
    r"&lt;p&gt;Export compilation layers to common themes\.&lt;p&gt;",
    r"&lt;p&gt;Control fork of custom Stereonet plugin display\.&lt;p&gt;",
    r"&lt;p&gt;Select Checkbox to switch to Great Circle Display for Stereonet Plugin&lt;p&gt;",
    r"&lt;p&gt;Select Checkbox to add Contour Display for Stereonet Plugin&lt;p&gt;",
    r"&lt;p&gt;Select Checkbox to add kinematics for Lineation Display for Stereonet Plugin&lt;p&gt;",
    r"&lt;p&gt;Select Checkbox to add Associated Great Circles to Lineation Display for Stereonet Plugin&lt;p&gt;",
    r"&lt;p&gt;Select Checkbox to display rose diagram instead of stereoplot in Stereonet Plugin&lt;p&gt;",
    r"&lt;p&gt;Select Checkbox to control Display behaviour for Stereonet Plugin&lt;p&gt;",
    r"&lt;p&gt;Browse to the folder that contains field and sample photographs\.&lt;p&gt;",
]

# DockWidget obsolete sources (plain text, no <p> wrappers)
OBSOLETE_DOCK = [
    r"Choose your Main Project ",
    r"Stereographic Projection Settings",
    r"Select Features to Plot \(Lower Hemisphere, Equal-Area Stereonet Projection\):",
    r"Update Settings",
    r"Contours",
    r"Great Circles",
    r"Kinematics",
    r"Rose Diagram",
    r"Lineation-bearing Planes",
    r"Please visit the Help - Roadmap section of the User Guide:",
    r"This tool controls the display of the qgis-stereonet plugin, available here: ",
    r"QGIS-stereonet plugin ",
]


# ---------------------------------------------------------------------------
# New messages to INSERT (after a specific anchor source text).
# Keys are the *new* (post-strip) source text of the anchor message.
# Values are the XML block to insert after the anchor's </message> tag.
# ---------------------------------------------------------------------------
NEW_GEOL_QMAPS = [
    # anchor → new block
    (
        "Generate scratch layers containing standardised lithological and/or structural legacy datapoints. Do not forget to merge them to field data compilation layers (Step 4)!",
        """
    <message>
        <location filename="../GEOL_QMAPS.py"/>
        <source>Generate GEOL-QMAPS-compatible scratch layers</source>
        <translation type="unfinished"></translation>
    </message>"""
    ),
    (
        "Merge scratch layers containing standardised lithological and/or structural legacy datapoints to field data compilation layers.",
        """
    <message>
        <location filename="../GEOL_QMAPS.py"/>
        <source>Merge scratch layers into GEOL-QMAPS permanent compilation layers</source>
        <translation type="unfinished"></translation>
    </message>"""
    ),
    (
        "Enables to save a new .qlr QGIS layer definition file in a directory to be supplied. This file includes customised styles for empty field data layers and updated dictionaries. It guarantees to keep consistent mapping standards for different projects, which facilitates post-field data compilation and processing.",
        """
    <message>
        <location filename="../GEOL_QMAPS.py"/>
        <source>Path to the folder where to save the updated GEOL-QMAPS layer definition file.</source>
        <translation type="unfinished"></translation>
    </message>"""
    ),
    (
        "Allows a new directory to be defined for the storage of field and sampling pictures (to enable the display of Map Tips miniatures for field and sample photographs in QGIS), and retrieve EXIF metadata for image orientation if available.",
        """
    <message>
        <location filename="../GEOL_QMAPS.py"/>
        <source>Path to the folder that contains field and sample photographs.</source>
        <translation type="unfinished"></translation>
    </message>"""
    ),
]

NEW_DOCK = [
    (
        "Update Repository",
        """
    <message>
        <location filename="../GEOL_QMAPS_dockwidget.py"/>
        <source>Update photograph paths in the project repository.</source>
        <translation type="unfinished"></translation>
    </message>"""
    ),
    (
        "Roadmap for Future Development",
        """
    <message>
        <location filename="../GEOL_QMAPS_dockwidget.py"/>
        <source>Please visit the following page:</source>
        <translation type="unfinished"></translation>
    </message>"""
    ),
]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def remove_message(content, source_pattern):
    """Remove the <message>…</message> block whose <source> matches source_pattern."""
    pat = (
        r'\n[ \t]*<message>\n'
        r'[ \t]*<location[^\n]*/>\n'
        r'[ \t]*<source>' + source_pattern + r'</source>\n'
        r'[ \t]*<translation[^>]*>.*?</translation>\n'
        r'[ \t]*</message>'
    )
    new, n = re.subn(pat, '', content, flags=re.DOTALL)
    if n == 0:
        print(f"  WARNING: pattern not found for removal: {source_pattern[:60]!r}")
    else:
        print(f"  Removed {n} block(s) matching: {source_pattern[:60]!r}")
    return new


def strip_p_from_sources(content):
    """
    Replace <source>&lt;p&gt;TEXT&lt;p&gt;</source>  (and &lt;/p&gt; variant)
    with    <source>TEXT</source>.
    Also fixes the 'toogled' typo while we are in there.
    """
    def fix(m):
        text = m.group(1)
        text = re.sub(r'^&lt;p&gt;\s*', '', text)       # remove leading <p>
        text = re.sub(r'\s*&lt;/?p&gt;$', '', text)     # remove trailing <p> or </p>
        text = text.replace('toogled', 'toggled')        # fix typo
        return '<source>' + text + '</source>'

    new, n = re.subn(
        r'<source>(&lt;p&gt;.*?&lt;/?p&gt;)</source>',
        fix, content, flags=re.DOTALL
    )
    print(f"  Stripped <p> wrappers from {n} source string(s)")
    return new


def fix_plain_sources(content):
    """Fix source strings that don't have <p> wrappers but still need updating."""
    # "Old Project Folder ( version ..." → "(version ..." (remove extra space)
    old = '<source>Old Project Folder ( version must be &gt;v3.1.0):</source>'
    new = '<source>Old Project Folder (version must be &gt;v3.1.0):</source>'
    if old in content:
        content = content.replace(old, new)
        print(f"  Fixed: 'Old Project Folder' source")
    else:
        print(f"  WARNING: 'Old Project Folder' source not found")

    # "Minimal Neighbour Distance (m) :" → "(m):" (remove space before colon)
    old = '<source>Minimal Neighbour Distance (m) :</source>'
    new = '<source>Minimal Neighbour Distance (m):</source>'
    if old in content:
        content = content.replace(old, new)
        print(f"  Fixed: 'Minimal Neighbour Distance' source")
    else:
        print(f"  WARNING: 'Minimal Neighbour Distance' source not found")

    return content


def insert_after_anchor(content, anchor_source, new_block):
    """Insert new_block immediately after the </message> that contains anchor_source."""
    escaped = re.escape(anchor_source)
    pat = r'(<source>' + escaped + r'</source>.*?</message>)'
    new, n = re.subn(pat, r'\1' + new_block, content, count=1, flags=re.DOTALL)
    if n == 0:
        print(f"  WARNING: anchor not found for insertion: {anchor_source[:60]!r}")
    else:
        print(f"  Inserted new message after: {anchor_source[:60]!r}")
    return new


# ---------------------------------------------------------------------------
# Main processing
# ---------------------------------------------------------------------------

def process_language(lang):
    path = os.path.join(base_dir, f'GEOL_QMAPS_{lang}.ts')
    print(f"\n{'='*60}")
    print(f"Processing: {path}")
    print('='*60)

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Step 1: Remove obsolete messages (use old &lt;p&gt; format before stripping)
    print("\n-- Removing obsolete GEOL_QMAPS messages --")
    for pat in OBSOLETE_GEOL_QMAPS:
        content = remove_message(content, pat)

    print("\n-- Removing obsolete DockWidget messages --")
    for pat in OBSOLETE_DOCK:
        content = remove_message(content, pat)

    # Step 2: Strip <p> wrappers and fix typo in source strings
    print("\n-- Updating source strings --")
    content = strip_p_from_sources(content)
    content = fix_plain_sources(content)

    # Step 3: Insert new messages (anchors are now the clean/updated source text)
    print("\n-- Inserting new GEOL_QMAPS messages --")
    for anchor, block in NEW_GEOL_QMAPS:
        content = insert_after_anchor(content, anchor, block)

    print("\n-- Inserting new DockWidget messages --")
    for anchor, block in NEW_DOCK:
        content = insert_after_anchor(content, anchor, block)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"\n  Written: {path}")


if __name__ == '__main__':
    for lang in LANGUAGES:
        process_language(lang)
    print("\n\nAll languages updated successfully.")
