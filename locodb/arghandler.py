import argparse


class ArgHandler(argparse.ArgumentParser):
    def __init__(self):
        super().__init__()
        self.add_argument(
            "-m",
            "--local-mongo-dir",
            type=str,
            help="The path to the local mongo database directory",
            default="amd-db",
            required=False,
        )
        self.add_argument(
            "-g",
            "--google-sheet",
            default=None,
            type=str,
            help="Google Sheet ID to import/export to.",
            required=False,
        )
        self.add_argument(
            "-c",
            "--google-credentials",
            default="credentials.json",
            type=str,
            help="Google OAuth credentials.",
            required=False,
        )

    def parse_args(self):
        self.args = super().parse_args()
