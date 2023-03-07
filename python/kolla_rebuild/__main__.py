# SPDX-FileCopyrightText: 2023  StorPool <support@storpool.com>
# SPDX-License-Identifier: Apache-2.0
"""Update Kolla containers as needed to support the StorPool backend."""

from __future__ import annotations

import shlex
import subprocess
import sys
import tempfile

from typing import TYPE_CHECKING

import click

from kolla_rebuild import defs
from kolla_rebuild import find
from kolla_rebuild import prepare


if TYPE_CHECKING:
    import pathlib

    from typing import Final


ALL_COMPONENTS: Final = ("cinder-volume", "nova-compute")
"""The known containers that we want to rebuild."""

DEFAULT_RELEASE: Final = "master"
"""The default OpenStack release (or "master") to rebuild the containers for."""

DEFAULT_COMPONENTS: Final = list(ALL_COMPONENTS)
"""The components to build containers for by default."""


def build_config(*, quiet: bool, release: str, sp_osi: str | None) -> defs.Config:
    """Prepare the runtime configuration object."""
    sp_osi_version: Final = sp_osi if sp_osi is not None else find.find_sp_osi_version()
    return defs.Config(
        topdir=find.find_topdir(), release=release, sp_osi_version=sp_osi_version, verbose=not quiet
    )


@click.command(
    name="kolla-rebuild", help="rebuild Kolla containers for the StorPool Cinder backend"
)
@click.option(
    "-c",
    "--component",
    type=str,
    multiple=True,
    default=DEFAULT_COMPONENTS,
    help="the OpenStack component containers to rebuild",
)
@click.option("--pull", is_flag=True, help="update the upstream container image before rebuilding")
@click.option("-q", "--quiet", is_flag=True, help="quiet operation; no diagnostic output")
@click.option(
    "-r",
    "--release",
    type=str,
    default=DEFAULT_RELEASE,
    help="the OpenStack release to rebuild the containers for",
)
@click.option(
    "-s",
    "--sp-osi",
    type=str,
    help="the storpool-openstack-integration version to use instead of the last released one",
)
def main(
    *, component: list[str], pull: bool, quiet: bool, release: str, sp_osi: str | None
) -> None:
    """Parse command-line options, gather files, invoke docker-build."""

    def build_component(component: str) -> None:
        """Rebuild the container for a single component."""
        parts: Final = component.split("-", maxsplit=1)
        if len(parts) != 2:  # noqa: PLR2004  # this will go away with match/case
            sys.exit(f"Internal error: build_component() invoked with {component=!r}")
        kolla_component, kolla_service = parts
        build: Final = prepare.build_dockerfile(cfg, files, kolla_component, kolla_service)

        with tempfile.NamedTemporaryFile(
            mode="wt", encoding="UTF-8", prefix="Dockerfile."
        ) as dockerfile:
            dockerfile.write(build.dockerfile)
            dockerfile.flush()
            subprocess.check_call(["ls", "-l", "--", dockerfile.name])
            subprocess.check_call(["cat", "--", dockerfile.name])

            cmd: Final[list[str | pathlib.Path]] = [
                "docker",
                "build",
                "-t",
                f"storpool/{build.container_name}",
                "--rm",
                *(["--pull"] if pull else []),
                "-f",
                dockerfile.name,
                "--",
                datadir,
            ]
            cmd_str: Final = shlex.join(str(word) for word in cmd)
            cfg.diag(lambda: f"Running `{cmd_str}`")
            try:
                subprocess.run(cmd, check=True)
            except (OSError, subprocess.CalledProcessError) as err:
                sys.exit(f"Could not run `{cmd_str}`: {err}")

    if release not in prepare.ALL_RELEASES:
        sys.exit(
            f"Unsupported release {release!r}, must be one of {' '.join(prepare.ALL_RELEASES)}"
        )
    if any(comp for comp in component if comp not in ALL_COMPONENTS):
        sys.exit(f"Unrecognized components, must be one or more of {' '.join(ALL_COMPONENTS)}")
    cfg: Final = build_config(quiet=quiet, release=release, sp_osi=sp_osi)

    datadir: Final = cfg.topdir / defs.DATA_DIR
    files: Final = prepare.prepare_data_files(cfg, datadir)

    for comp in component:
        build_component(comp)


if __name__ == "__main__":
    main()  # pylint: disable=missing-kwoa
