from app.fetch import load
import argparse


def non_negative_int(value: int) -> int:
    """Returns non negative value, if possible.

    Args:
        value: argument to check
    Returns:
        unchanged argument
    """
    value = int(value)
    if value < 0:
        raise argparse.ArgumentTypeError("Negative values are not allowed.")
    return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run the load function with a start value"
    )

    parser.add_argument(
        "-s",
        "--start",
        required=False,
        default=None,
        type=non_negative_int,
        help="Starting ID",
    )

    args = parser.parse_args()

    load.run(start=args.start)
