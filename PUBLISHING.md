# Publishing **fastmvc-db-models** to PyPI

## Prerequisites

- PyPI account and [API token](https://pypi.org/manage/account/token/)
- `pip install build twine`

## Version and changelog

1. Bump `version` in `pyproject.toml`.
2. Update `CHANGELOG.md` under `## [Unreleased]` and add a dated section when you tag a release.

## Monorepo releases

If you use the **FastMVC** monorepo scripts, see [../RELEASE.md](../RELEASE.md) and `scripts/release_all.sh` at the repository root.

## Package-specific upload

1. Run tests: `make test` or `pytest`.
2. Build: `make build` or `python -m build`.
3. Upload:

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=<pypi-token>
twine upload dist/*
```

- **PyPI project name:** `fastmvc-db-models`
- **Typical import:** `fastmvc_db_models`
- **Repository / homepage:** https://github.com/shregar1/fastmvc-db-models
