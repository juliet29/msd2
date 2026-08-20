from cyclopts import App
from utils4plans.logs import logset

from msd2.cli.studies.fullrun import fullrun

studies_app = App()
# studies_app.command(runstress)
# studies_app.command(windows)
# studies_app.command(ag)
studies_app.command(fullrun)


def main():
    logset()
    studies_app()


if __name__ == "__main__":
    main()
