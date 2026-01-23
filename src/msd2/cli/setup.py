from cyclopts import App

from msd2.readin.scripts import find_and_write_valid_unit_ids, summarize_dataset

setup_app = App("setup")


@setup_app.command()
def show_summary():
    summarize_dataset()


@setup_app.command()
def write_valid_unit_ids():
    find_and_write_valid_unit_ids()
