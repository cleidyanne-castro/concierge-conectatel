"""Ponto de entrada local do Concierge."""
from .config import Settings
from .handler import handle
import argparse
def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument('--question',required=True); args=parser.parse_args()
    print(handle(args.question, Settings()))

if __name__ == "__main__":
    main()
