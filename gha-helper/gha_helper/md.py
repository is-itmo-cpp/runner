from contextlib import contextmanager

from tabulate import tabulate


_summary_md = open("SUMMARY.md", "w")


def raw(text=""):
    _summary_md.write(text)
    _summary_md.write("\n")


@contextmanager
def spoiler(summary):
    raw(f"<details>\n<summary>{summary}</summary>\n")
    yield
    raw("</details>\n")


def code(text):
    backticks = "`" * 80
    raw(f"{backticks}\n{text}\n{backticks}")


def table(rows):
  raw(tabulate(rows, tablefmt="pipe", headers="firstrow", stralign="center"))
  raw()
