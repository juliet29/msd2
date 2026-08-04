from cyclopts import App
from utils4plans.logs import logset

from msd2.cli.studies.run_stress import runstress
from msd2.cli.studies.windows import windows

studies_app = App()
studies_app.command(runstress)
studies_app.command(windows)


def main():
    logset()
    studies_app()


if __name__ == "__main__":
    main()
