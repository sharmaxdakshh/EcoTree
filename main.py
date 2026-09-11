#!/usr/bin/env python3
"""
EcoTree CLI – Tree Inventory & Environmental Impact System
"""

import click
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.data_loader import generate_sample_data
from src.database import init_db
from src.analysis import (
    load_trees_df, get_summary_stats, zone_summary,
    species_summary, get_critical_trees
)
from src.visualization import (
    plot_species_distribution, plot_health_status,
    plot_carbon_by_zone, plot_age_vs_health, create_interactive_map
)
from src.report_generator import generate_pdf_report


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """🌳 EcoTree – Tree & Environment Management System"""
    pass


@cli.command()
@click.option("--count", default=800, show_default=True, help="Number of sample trees to generate")
def init(count):
    """Initialize database and generate realistic sample data"""
    click.echo("Initializing EcoTree database...")
    init_db()
    generate_sample_data(n_trees=count)
    click.secho("✅ Database ready with sample data.", fg="green")


@cli.command()
def summary():
    """Show high-level project statistics"""
    df = load_trees_df()
    stats = get_summary_stats(df)

    click.echo("\n" + "=" * 45)
    click.secho("  EcoTree – Project Summary", fg="green", bold=True)
    click.echo("=" * 45)
    for key, value in stats.items():
        label = key.replace("_", " ").title()
        click.echo(f"  {label:<32}: {value}")
    click.echo("=" * 45 + "\n")


@cli.command()
def zones():
    """Show zone-wise performance table"""
    df = load_trees_df()
    result = zone_summary(df)
    click.echo("\nZone-wise Summary:\n")
    click.echo(result.to_string())
    click.echo()


@cli.command()
def species():
    """Show species distribution and impact"""
    df = load_trees_df()
    result = species_summary(df)
    click.echo("\nSpecies Summary:\n")
    click.echo(result.to_string())
    click.echo()


@cli.command()
@click.option("--limit", default=15, help="Number of trees to show")
def critical(limit):
    """List trees that need immediate attention"""
    df = load_trees_df()
    result = get_critical_trees(df, limit=limit)
    click.echo(f"\nTop {limit} Critical / At-Risk Trees:\n")
    click.echo(result.to_string(index=False))
    click.echo()


@cli.command()
def plots():
    """Generate all static analysis plots"""
    click.echo("Generating plots...")
    df = load_trees_df()
    paths = [
        plot_species_distribution(df),
        plot_health_status(df),
        plot_carbon_by_zone(df),
        plot_age_vs_health(df)
    ]
    click.secho("✅ Plots saved:", fg="green")
    for p in paths:
        click.echo(f"   → {p}")


@cli.command(name="map")
def create_map():
    """Generate interactive Folium map"""
    click.echo("Building interactive map...")
    df = load_trees_df()
    path = create_interactive_map(df)
    click.secho(f"✅ Map saved → {path}", fg="green")
    click.echo("   Open the HTML file in any browser.")


@cli.command()
@click.option("--output", default="outputs/reports/ecotree_report.pdf",
              show_default=True, help="Output PDF path")
def report(output):
    """Generate comprehensive PDF report"""
    click.echo("Generating PDF report...")
    df = load_trees_df()
    path = generate_pdf_report(df, output_path=output)
    click.secho(f"✅ Report ready → {path}", fg="green")


@cli.command()
def all():
    """Run complete analysis pipeline (plots + map + report)"""
    click.echo("Running full EcoTree analysis pipeline...\n")
    df = load_trees_df()

    click.echo("1/4  Generating plots...")
    plot_species_distribution(df)
    plot_health_status(df)
    plot_carbon_by_zone(df)
    plot_age_vs_health(df)

    click.echo("2/4  Creating interactive map...")
    create_interactive_map(df)

    click.echo("3/4  Generating PDF report...")
    generate_pdf_report(df)

    click.echo("4/4  Computing summary...")
    stats = get_summary_stats(df)

    click.echo("\n" + "=" * 45)
    click.secho("  Pipeline Complete – Key Numbers", fg="green", bold=True)
    click.echo("=" * 45)
    click.echo(f"  Total Trees          : {stats['total_trees']:,}")
    click.echo(f"  Carbon (tonnes/yr)   : {stats['total_carbon_tonnes']}")
    click.echo(f"  Avg Health Score     : {stats['avg_health']}")
    click.echo(f"  Critical Trees       : {stats['critical_count']}")
    click.echo("=" * 45)
    click.secho("\n✅ All outputs are in the 'outputs/' folder.", fg="green")


if __name__ == "__main__":
    cli()
