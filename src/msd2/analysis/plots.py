from pathlib import Path
import polars as pl
import altair as alt

from msd2.analysis.data import QOI, QOIRegistry


def make_corr_plot(qoi_csv: Path, metrics_csv: Path):
    qoi_df = pl.read_csv(qoi_csv)
    metrics_df = pl.read_csv(metrics_csv)

    df = qoi_df.join(metrics_df, on="case")  # .filter(pl.col("case") != 5542)
    metrics = [
        "num_zones",
        "num_zones_afn",
        "area",
        "area_afn",
        "ratio_area_afn",
        "num_afn_surfaces",
        "bounding_aspect_raio",
    ]
    x_labels = [
        "Number of Zones",
        "Number of Zones in AFN",
        "Total Area [m2]",
        "Area of Zones in AFN [m2]",
        "Area Ratio (AFN Area / Total)",
        "Number of Surfaces in AFN",
        "Aspect Ratio (of Rectangular Bounding Box - X/Y)",
    ]

    def make_chart(qoi: QOI):
        charts = []
        for var, label in zip(metrics, x_labels):
            panel = (
                alt.Chart(df)
                .mark_point()
                .encode(
                    # Set the custom label as the axis title here
                    x=alt.X(f"{var}:Q", title=label).scale(zero=False),
                    y=alt.Y(f"{qoi.nickname}:Q").title(qoi.label).scale(zero=False),
                )
                .properties(width=150, height=150)
            )
            charts.append(panel)

        final_chart = (
            alt.hconcat(*charts).resolve_axis(y="shared").resolve_scale(y="shared")
        )
        return final_chart

    return [make_chart(qoi) for qoi in [QOIRegistry.net_flow, QOIRegistry.temp]]
