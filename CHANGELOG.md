
# Changelog

## [Unreleased]

## [0.1.5]
### Added
- `MANIFEST.in` file added - thanks @mobiusklein

## [0.1.4]
### Added
- Support for PBS/TORQUE added [experimental]
### Changed
- Renamed `pyjob.platform.platform_factory()` to `pyjob.platform.Platform()`
- Renamed `TASK_ID` to `ARRAY_TASK_ID` in `pyjob.platform.platform.Platform() classes`
### Fixed
- `LocalJobServer` `Worker` instances are now terminated properly

## [0.1.3]
### Changed
- Critical bug fix in ``prep_array_script()`` for cluster job submission

## [0.1.2]
### Changed
- ``PyJobNotImplementedError`` replaced with ``NotImplementedError``
- Bug fix for script submission in ``Job.submit()``

## [0.1.1]
### Changed
- Fix for PyPi installation
- Added additional information to README file

## [0.1]
### Added
- Initial release
