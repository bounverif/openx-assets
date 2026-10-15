"""Print the README.adoc vehicle gallery as an HTML table for GitHub release notes.

Images and links point at the given commit of the GitHub repository, so the
release notes keep showing the thumbnails of the released assets.
"""

import argparse
import html
import pathlib
import re
import sys

IMAGE = re.compile(
    r'^\|\s*image:(?P<path>[^\[]+)\[alt="(?P<alt>[^"]*)".*?link="(?P<link>[^"]*)"'
)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "repository", help="GitHub repository, e.g. vevalabs/openx-assets"
    )
    parser.add_argument("commit", help="Commit SHA the images and links point at")
    parser.add_argument(
        "--readme", type=pathlib.Path, default=pathlib.Path("README.adoc")
    )
    parser.add_argument("--columns", type=int, default=4)
    args = parser.parse_args()

    base = f"https://github.com/{args.repository}"
    cells = []
    for line in args.readme.read_text(encoding="utf-8").splitlines():
        m = IMAGE.match(line)
        if m:
            alt = html.escape(m["alt"])
            cells.append(
                f'<td align="center"><a href="{base}/tree/{args.commit}/{m["link"]}">'
                f'<img src="{base}/raw/{args.commit}/{m["path"]}" alt="{alt}" width="200"></a>'
                f"<br>{alt}</td>"
            )
    if not cells:
        sys.exit(f"No gallery images found in {args.readme}")

    print("## Vehicle Gallery\n")
    print("<table>")
    for i in range(0, len(cells), args.columns):
        print("<tr>" + "".join(cells[i : i + args.columns]) + "</tr>")
    print("</table>")


if __name__ == "__main__":
    main()
