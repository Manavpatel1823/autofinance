import sys

from auto_finance.actions import analyze_stock
from auto_finance.base import handler


def main(raw_args):
    actions = [analyze_stock]

    handler.handle(
        prog="python3 -m auto_finance.cli",
        description="The stock market portfolio management with genai.",
        actions=actions,
        raw_args=raw_args,
    )

 
if __name__ == "__main__":
    main(sys.argv[1:])
