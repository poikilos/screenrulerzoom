# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [git] - 2021-08-25
### Added
- Translate comments in `paintEvent`.
- Add more comments.
- Add variables to replace hard coded parts for clarity: `settingsToProperties`, `propertiesToSettings`

### Changed
- `cpt` to `count`
- `sXY` to `rulerSize` or `rulerSizeItem` for clarity (Item stands for Menu item).
- `cUM` to `unitIndex`
- `unitMeasure` to `unitDefs` or `unitDefsItem` for clarity.
- `colors` to `colorsItem` where ambiguous
- `zoom` to `zoomItem` where ambiguous
- `butttonClose` to `closeButton`
- `self.rulerSize` to `zoomNames` where ambiguous (It was just set to 0 after filled with a different kind of data then copied to `self.zooms` :( ).
