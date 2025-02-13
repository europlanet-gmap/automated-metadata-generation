# Changelog

All changes that impact users of this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

<!---
This document is intended for users of the applications and API. Changes to things
like tests should not be noted in this document.

When updating this file for a PR, add an entry for your change under Unreleased
and one of the following headings:
 - Added - for new features.
 - Changed - for changes in existing functionality.
 - Deprecated - for soon-to-be removed features.
 - Removed - for now removed features.
 - Fixed - for any bug fixes.
 - Security - in case of vulnerabilities.

If the heading does not yet exist under Unreleased, then add it as a 3rd heading,
with three #.


When preparing for a public release candidate add a new 2nd heading, with two #, under
Unreleased with the version number and the release date, in year-month-day
format. Then, add a link for the new version at the bottom of this document and
update the Unreleased link so that it compares against the latest release tag.


When preparing for a bug fix release create a new 2nd heading above the Fixed
heading to indicate that only the bug fixes and security fixes are in the bug fix
release.
-->

## Unreleased

### Added
  - Support for parsing bands from ISIS cube labels and ability to populate stac EO extension using said metadata.

### Fixed
  - STAC key stop_datetime is updated to be end_datetime in order to be specification compliant
  - Unified metadata object fixed to gracefully call hasattr. hasattr executes the calling block and if the called block raises, the process exits. This changes makes it so that hasattr can still be used (instead of vars()) and a metadata object can fail. Users are still alterted on failure because the attribute is inaccessible (a warning is raised).

## [1.0.0 2021-12-04]

### Added
  - Added support for transverse mercator projection in FGDC driver
  - Added start_date, stop_date to CamInfo driver
  - Added JSONEncoder class to support encoding numpy arrays and datetime objects
  - Conda recipe for dev builds 
  - GitHub Actions for automated dev deploy on anaconda channel
  
### Fixed
  - Sun elevation is using local time or local solar time and not local
    incidence angle
  - Fixed a bug where STAC observation date was not written when start/stop time were parsed
  - Dependencies are all now coming from conda-forge (removal of all pip dependencies)
  - Warning in pytest due to use of distutils copy_tree. Replaced with shutil.copytree

## [0.3.0 2021-11-05]

### Added
- Added driver for ISIS caminfo PVL output

### Fixed
- Removed deprecated `getchildren` call in XML parsing in the fgdcmetadata object
- Added CI for py3.9
- Added support for view geometry STAC extension
- Updates API to pystac 1.0.0 with proper extension support

