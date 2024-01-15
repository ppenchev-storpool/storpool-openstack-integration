<!--
SPDX-FileCopyrightText: 2022 - 2024  StorPool <support@storpool.com>
SPDX-License-Identifier: Apache-2.0
-->

# sp-openstack: detect, install, and configure the StorPool fixes

## Synopsis

``` sh
sp-openstack [-Nv] detect component...
sp-openstack [-Nv] -a detect

sp-openstack [-Nv] check component...
sp-openstack [-Nv] -a check

sp-openstack [-DNv] install component...
sp-openstack [-DNv] -a install

sp-openstack [-DNv] uninstall component...
sp-openstack [-DNv] -a uninstall

sp-openstack [-Nv] groups component...
sp-openstack [-Nv] -a groups

sp-openstack [-Nv] validate
```

## Description

The `sp-openstack` tool examines an OpenStack installation, determines which
versions of which OpenStack components (`cinder`, `glance`, `nova`, `os_brick`) are
currently installed, and, if necessary, installs updated versions containing
StorPool fixes.

The `sp-openstack` tool accepts the following command-line options:

- `-a`, `--all` - process all known OpenStack components
- `-D`, `--no-divert` - do not use `dpkg-divert` even on Debian/Ubuntu systems
- `-N`, `--noop` - no-operation mode; display what would be done
- `-v`, `--verbose` - verbose operation; display diagnostic output

The `sp-openstack` tool must be invoked with one of the following subcommands.

### sp-openstack check

In check mode, the `sp-openstack` tool performs the following actions:

- load the component definitions file
- look through the Python module search path (either the distribution default, or
  more directories added via the `PYTHONPATH` environment variable) for the files
  listed in the definitions of the specified components (or all if the `-a`
  option is specified)
- calculate the files' checksums and match them against the component definitions
- if any OpenStack components are outdated
  (see the [Matching versions](#matching-versions) section below), list them on
  the standard error output stream and exit with a non-zero code
- if all of the OpenStack components are at non-outdated versions, display
  an informational message on the standard output stream and exit with
  code 0

### sp-openstack detect

In detect mode, the `sp-openstack` tool performs the following actions:

- load the component definitions file
- look through the Python module search path (either the distribution default, or
  more directories added via the `PYTHONPATH` environment variable) for the files
  listed in the definitions of the specified components (or all if the `-a`
  option is specified)
- calculate the files' checksums and match them against the component definitions
- list the OpenStack components and their detected versions and outdated status on
  the standard output stream

### sp-openstack install

In install mode, the `sp-openstack` tool performs the following actions:

- load the component definitions file
- look through the Python module search path (either the distribution default, or
  more directories added via the `PYTHONPATH` environment variable) for the files
  listed in the definitions of the specified components (or all if the `-a`
  option is specified)
- calculate the files' checksums and match them against the component definitions
- if any OpenStack components are outdated
  (see the [Matching versions](#matching-versions) section below), replace
  the currently installed files with the StorPool fixed versions for
  the corresponding component and OpenStack version
- on Debian/Ubuntu systems, if the `--no-divert` command-line option is not
  specified, `sp-openstack` will attempt to use the `dpkg-divert` tool to
  create a local diversion of the original file before replacing it, so that
  a future update of the upstream OpenStack package (obtained from the Debian
  package archive, or from the Ubuntu Cloud archive, etc.) will not overwrite
  the updated StorPool one.
  The diverted file will be in the same directory, with a `.sp-ospkg`
  extension appended.
- if the `--no-divert` command-line option is specified or on non-Debian/Ubuntu
  systems, `sp-openstack` will copy the original file to a file in
  the same directory with a `.sp-ospkg` extension appended

<!--
Note that the "replace the upstream files" step will probably change if
we decide to switch to applying patches instead of replacing files.
-->

### sp-openstack uninstall

In install mode, the `sp-openstack` tool performs the following actions:

- load the component definitions file
- look through the Python module search path (either the distribution default, or
  more directories added via the `PYTHONPATH` environment variable) for the files
  listed in the definitions of the specified components (or all if the `-a`
  option is specified)
- calculate the files' checksums and match them against the component definitions
- if any of the component files have been updated by an earlier invocation of
  `sp-openstack install`, restore them (move the original file, the one saved with
  the `.sp-ospkg` extension, to its original name) and, if `dpkg-divert` was
  used, also remove the local diversion

### sp-openstack validate

In validate mode, the `sp-openstack` tool performs the following actions:

- load the component definitions file
- for non-outdated records, make sure that the files in the StorPool OpenStack
  integration repository that are supposed to be StorPool replacements for
  the upstream files indeed have the same checksums as the recorded ones
- for outdated records, make sure that there is at least one file in
  the StorPool OpenStack integration repository that has a different checksum
  than the one in the record
- for outdated records, make sure that the component definition lists exactly
  one non-outdated version with the same checksums for the detect-only files

## The component definitions file

FIXME: write me up:

- describe the three types of files that we list checksums for:
    - files that we carry along (updated, non-outdated versions)
    - upstream files that we want to replace (outdated versions)
    - upstream files that we only use for detection, to differentiate between
      different OpenStack releases for the same component
- OpenStack components
    - OpenStack releases for each component
        - non-outdated records for files we carry along and detection-only files
        - outdated records for upstream versions that we want to replace
        - non-outdated records for components where we do not carry any changes

<!--
When writing this up, note that the record format will probably change if
we decide to switch to applying patches instead of replacing files.
-->

### Matching versions

For each OpenStack component, the component definitions file should have at
least the following records:

- if there are no StorPool changes for the component files, one or more
  records (with different file checksums) marked as non-outdated, so that
  `sp-openstack` knows that there is nothing to install
- if there are any StorPool changes for the component files:
    - one or more records containing the checksums of the original upstream files
      (both files that StorPool has fixes for and ones used only for detection
      purposes) marked as outdated, so that `sp-openstack` knows that some of
      them need to be replaced
    - one or more records containing the checksums of the files as they should be in
      the updated version: the checksums of the files `sp-openstack` carries along, and
      the original checksums for the files used only for detection purposes

## Examples

FIXME: write me up

## More

FIXME: write a couple of other sections up
