from msd2.paths import static_paths


class ExamplePaths:
    msd_stats = static_paths.temp / "msd_stats"
    valid_ids_json = msd_stats / "valid_ids.json"
    valid_ids_csv = msd_stats / "valid_ids.csv"
    workflow = static_paths.temp / "workflow"
    temp = static_paths.temp / "temp"
