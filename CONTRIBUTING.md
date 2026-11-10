# Contributing to Repo Ready

Thank you for helping maintain an open-source tool. Useful, tested contributions of any size are welcome.

## How to start

1. Read the README and look through the roadmap for a small improvement.
2. Open an issue describing a reproducible bug or proposal before undertaking a large change.
3. Fork the repository, create a descriptive branch, and add a test for changed detection behavior.
4. Run `python -m unittest discover -s tests -v` and `python -m repo_ready . --strict`.
5. Open a pull request that explains the problem, change, and verification steps.

## Project principles

- No runtime third-party dependencies unless strongly justified.
- Never read or print secrets; the scanner inspects names and structure only.
- Keep detection cross-platform and independent of internet access.
- Be accurate about limitations and false positives.
- Follow the community expectations in CODE_OF_CONDUCT.md.

## Good first contributions

- Add support for test naming conventions from another language.
- Improve how false positives are explained in the README.
- Add tests covering package manifests used in additional ecosystems.
- Improve Windows examples or accessibility of terminal output.

All contributors retain credit for their work under the MIT license.
