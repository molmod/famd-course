# How to contribute to this repository?

Contributions are always welcome!
:thumbsup: :tada: :heart_eyes: :100:
These can include small corrections, clarifications, improved instructions for some operating system, etc.

New contributions are only accepted in the form of a **pull request**.
The lecturers of the course will review the pull request and possibly ask for further changes.
If you feel something should be improved, but are not sure how, it may be more appropriate to open an **issue** instead.
After some discussion in the issue, things may become clearer and you can still open a pull request.

Formatting of most files can be automatically corrected with the [pre-commit](https://pre-commit.com) program.
To set up `pre-commit` (once), run the following:

```bash
# Tested on Linux with Conda or Mamba. One can also use: `pip install pre-commit`
conda install pre-commit
# The following must be executed in the directory of a git repository.
# It assumes that a file .pre-commit-config.yaml is present.
pre-commit install
```

Once `pre-commit` is installed, it will automatically correct formatting when you run `git commit ...`.
If corrections are made, the commit may be aborted, allowing you to check the result and commit again.
You can also correct files before committing with the command: `pre-commit run --all-files`

Not all formatting issues can be fixed automatically.
Try to take care of the following when editing.

- Many mistakes can be avoided with a live preview of your Markdown file while writing.
  - In Atom, the preview is activated with `ctrl-shift-m`.
  - In Jupyter Lab, click with the right-mouse button in the Markdown editor and select `Show Markdown Preview`.
  - In VSCode, the preview is activated with `ctrl-shift-v` or with `ctrl-k v`.
  - Also the online Markdown editor [StackEdit](https://stackedit.io/) has a live preview.
- Put every sentence on its own line.
  This facilitates reviewing.

Thanks!
