# plot_functions.py

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd


def calculate_slot_metrics(df):
    ref_date = pd.to_datetime("2024-12-01")
    df["appointment_date"] = pd.to_datetime(df["appointment_date"], errors="coerce")
    before_ref = df[df["appointment_date"] < ref_date]
    total_slots_before_ref = len(before_ref)
    non_available_before_ref = len(before_ref[before_ref["is_available"] == False])
    fill_rate_before_ref = (non_available_before_ref / total_slots_before_ref) * 100 if total_slots_before_ref > 0 else 0
    total_operating_days = (df["appointment_date"].max() - df["appointment_date"].min()).days + 1
    total_working_days = df["appointment_date"].nunique()
    slots_per_day = df.groupby("appointment_date").size().mean()
    slots_per_week = slots_per_day * 7
    total_slots = len(df)
    return {
      "Total Operating Days": total_operating_days,
      "Total Working Days": total_working_days,
      "Slots Per Day": int(slots_per_day),
      "Slots Per Week": int(slots_per_week),
      "Total Slots": total_slots,
      "Fill Rate Before Reference Date": round(fill_rate_before_ref, 1)
    }


def plot_slots_availability(df):
    if not pd.api.types.is_datetime64_any_dtype(df['appointment_date']):
        df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    df["year"] = df["appointment_date"].dt.year
    grouped = df.groupby(["year", "is_available"]).size().unstack(fill_value=0)
    grouped.columns = grouped.columns.astype(bool)
    total_slots = grouped.sum(axis=1)
    non_available_percent = (grouped[False] / total_slots) * 100
    available_percent = (grouped[True] / total_slots) * 100
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor("#fafafa")
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (-0.04, 0.02), 1.06, 1.1,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor="#222",
        linewidth=0.25,
        clip_on=False,
        zorder=-3,
        linestyle="-",
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    years = grouped.index
    non_available = grouped[False]
    available = grouped[True]
    ax.bar(years, non_available, label="Non-Available Slots", color="#FF6F61", edgecolor="#fafafa", zorder=3, width=0.7)
    ax.bar(years, available, bottom=non_available, label="Available Slots", color="#43AD7E", edgecolor="#fafafa", zorder=3, width=0.7)
    fig.suptitle("Slot Availability Over the Years", fontsize=12, x=0.19, y=1, ha="center", fontweight='bold')
    ax.set_xlabel("Year", labelpad=10)
    ax.set_ylabel("Number of Slots")
    ax.legend(loc="upper right", bbox_to_anchor=(1.06, 1.2), frameon=False)
    ax.set_xticks(years)
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    ax.spines[["right", "top"]].set_visible(False)
    ax.yaxis.set_ticks_position("none")
    ax.xaxis.set_ticks_position("none")
    for i, year in enumerate(years):
        # Non-available percentage
        plt.text(
            year, non_available.iloc[i] / 2,
            f"{non_available_percent.iloc[i]:.0f}%",
            fontsize=9, ha="center", color="#ffffff",
            fontweight="bold"
        )
        # Available percentage
        plt.text(
            year, non_available.iloc[i] + available.iloc[i] / 2,
            f"{available_percent.iloc[i]:.0f}%",
            fontsize=9, ha="center", color="#ffffff",
            fontweight="bold"
        )
    plt.subplots_adjust(bottom=0.2)
    plt.show()



def plot_population_pyramid(df):
    gender_counts = df.groupby(['age_group', 'sex'], observed=True).size().unstack(fill_value=0)
    males = -gender_counts['Male'].values
    females = gender_counts['Female'].values
    total_population = np.sum(gender_counts.values)
    shift = 0.006 * len(df)
    bar_color_male = '#4583b5'
    bar_color_female = '#ef7a84'
    background_color = '#fafafa'
    fontsize = 9
    label_offset = len(df) / 500
    fig, ax = plt.subplots(figsize=(9, 6))
    age_groups = gender_counts.index
    bars_male = ax.barh(age_groups, males, color=bar_color_male, align='center', height=0.7, left=-shift, label='Male', zorder=3)
    bars_female = ax.barh(age_groups, females, color=bar_color_female, align='center', height=0.7, left=shift, label='Female', zorder=3)
    border_radius = 0.015
    rect = patches.FancyBboxPatch((0.03, 0), 1, 1.1, transform=fig.transFigure, facecolor=background_color,
                                  edgecolor='black', linewidth=0.25, clip_on=False, zorder=-3,
                                  boxstyle=f"round,pad=0.03,rounding_size={border_radius}")
    fig.patches.extend([rect])
    ax.set_facecolor(background_color)
    ax.yaxis.set_ticks_position('none')
    max_population = max(abs(males).max(), females.max()) * 1.2
    ax.set_xlim(left=-max_population, right=max_population)
    fig.suptitle('Population distribution by age and sex', fontsize=12, x=0.065, y=1.03, ha="left", fontweight='bold')
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_position(('data', shift))
    for bars, color, ha in [(bars_male, bar_color_male, 'right'), (bars_female, bar_color_female, 'left')]:
        for bar in bars:
            width = bar.get_width()
            label_x_pos = bar.get_x() + (width - label_offset if ha == 'right' else width + label_offset)
            ax.text(label_x_pos, bar.get_y() + bar.get_height() / 2,
                    f'{abs(width) / total_population:.1%}', va='center', ha=ha, color=color, fontsize=fontsize, fontweight='bold')
    for label in age_groups:
        ax.text(0, label, f' {label} ', va='center', ha='center', color='black', backgroundcolor=background_color)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'{int(abs(x))}'))
    ax.set_xlabel('Population', labelpad=10)
    for text, x, color in [
        (f'Female: {np.sum(females)} ({np.sum(females) / total_population:.1%})', 1.1, bar_color_female),
        (f'Male: {np.sum(males) * -1} ({np.sum(males) * -1 / total_population:.1%})', (  0.14 + (0.00000035 * len(df)) ), bar_color_male)
    ]:
        ax.text(x, 1.05, text, transform=ax.transAxes, fontsize=10, ha='right', va='top', color="white",
                weight='bold', bbox=dict(facecolor=color, edgecolor='#eeeeee', boxstyle=f"round,pad=1.2,rounding_size={0.2}"))

    plt.show()


def plot_insurance_distribution(df):
    insurance_counts = df['insurance'].value_counts(normalize=True).sort_values() * 100
    insurances = insurance_counts.index
    percentage_probs = insurance_counts.values
    fig, ax = plt.subplots(figsize=(8, 6))
    border_radius = 0.015
    rect = patches.FancyBboxPatch((-0.12, 0.03), 1.13, 1.04, transform=fig.transFigure, facecolor="#fafafa",
                                  edgecolor='black', linewidth=0.25, clip_on=False, zorder=-3,
                                  boxstyle=f"round,pad=0.03,rounding_size={border_radius}")
    fig.patches.append(rect)
    ax.set_facecolor('#fafafa')
    fig.suptitle('Percentage of Patients by Insurance Type', fontsize=12, x=-0.08, y=1, ha="left", fontweight='bold')
    bars = ax.barh(insurances, percentage_probs, height=0.8, color='#67A7D4')
    ax.spines[['right', 'top', 'bottom']].set_visible(False)
    ax.xaxis.set_visible(False)
    ax.bar_label(bars, padding=5, color='#222', fontsize=10, label_type='edge', fmt='%.1f%%', fontweight='bold')
    plt.show()


def plot_patients_visits(df):
    visit_counts = df['patient_id'].value_counts()
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.set_facecolor('#fafafa')
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (-0.09, 0.06), 1.1, 1.1,
        transform=fig.transFigure, facecolor="#fafafa", edgecolor='#222',
        linewidth=0.25, clip_on=False, zorder=-3, linestyle='-', boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    bins = range(1, max(visit_counts) + 2)
    counts, edges = np.histogram(visit_counts, bins=bins)
    percentages = (counts / visit_counts.size) * 100
    
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    valid_x = [x for x, _, _ in valid_bins]
    valid_counts = [count for _, count, _ in valid_bins]
    valid_percentages = [percentage for _, _, percentage in valid_bins]
    
    fig.suptitle(
        'Patient Visit Distribution Over the Last 10 Years',
        fontsize=12, x=0.24, y=1.04, ha="center", fontweight='bold'
    )
    plt.bar(
        valid_x, valid_counts, width=0.9, align='center',
        edgecolor='#fafafa', color='#67A7D4'
    )
    ax.set_xticks(range(1, max(valid_x) + 1))
    ax.set_xticklabels([int(b) for b in range(1, max(valid_x) + 1)], ha="center", fontweight='bold')
    ax.set_ylabel('Number of Patients', labelpad=10)
    plt.xlabel('Number of Visits', labelpad=10)
    ax.spines[['right', 'top']].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    plt.subplots_adjust(left=0.08, bottom=0.25)
    
    for x, count, percentage in zip(valid_x, valid_counts, valid_percentages):
        plt.text(
            x, count + (max(valid_counts) * 0.02),
            f"{percentage:.1f}%", fontsize=8, fontweight='bold',
            color='#222', ha='center'
        )
    plt.show()


def plot_appointments_by_status(df):
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    ref_date = pd.to_datetime("2024-12-01")
    filtered_df = df[(df["appointment_date"] <= ref_date)]
    grouped = filtered_df["status"].value_counts(normalize=True).sort_values(ascending=False) * 100
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_facecolor("#fafafa")
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (-0.08, -0.05), 1.15, 1.25,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor="#222",
        linewidth=0.25,
        clip_on=False,
        zorder=-3,
        linestyle="-",
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    color_map = {
      "attended": "#B69DE1",
      "cancelled": "#B3C1F2",
      "did not attend": "#BDE3F0",
      "unknown": "#E5E5E5"
    }
    statuses = grouped.index
    percentages = grouped.values
    colors = [color_map.get(status, "#4583b5") for status in statuses]
    bars = ax.bar(statuses, percentages, color=colors, edgecolor="#fafafa", width=0.5, zorder=3)
    fig.suptitle("Appointments by Status (Last Month)", fontsize=12, x=0.4, y=1.05, ha="center", fontweight='bold')
    ax.set_xlabel("Status", labelpad=10)
    ax.spines[["right", "top"]].set_visible(False)
    ax.yaxis.set_ticks_position("none")
    ax.xaxis.set_ticks_position("none")
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    for bar, percent in zip(bars, percentages):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f"{percent:.1f}%", ha="center", fontsize=9, color="#222", fontweight="bold")
    plt.subplots_adjust(bottom=0.2)
    plt.show()


def plot_appointments_by_status_future(df):
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    ref_date = pd.to_datetime("2024-12-01")
    filtered_df = df[(df["appointment_date"] > ref_date)]
    grouped = filtered_df["status"].value_counts(normalize=True).sort_values(ascending=False) * 100
    color_map = {
        "scheduled": "#CD77B6",
        "cancelled": "#B3C1F2"
    }
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_facecolor("#fafafa")
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (-0.08, -0.05), 1.15, 1.25,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor="#222",
        linewidth=0.25,
        clip_on=False,
        zorder=-3,
        linestyle="-",
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    statuses = grouped.index
    percentages = grouped.values
    colors = [color_map.get(status, "#4583b5") for status in statuses]
    bars = ax.bar(statuses, percentages, color=colors, edgecolor="#fafafa", width=0.17, zorder=3)
    fig.suptitle("Upcoming Appointments by Status", fontsize=12, x=0.075, y=1.05, ha="left", fontweight='bold')
    ax.set_xlabel("Status", labelpad=10)
    ax.spines[["right", "top"]].set_visible(False)
    ax.yaxis.set_ticks_position("none")
    ax.xaxis.set_ticks_position("none")
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    for bar, percent in zip(bars, percentages):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
                f"{percent:.1f}%", ha="center", fontsize=9, color="#222", fontweight="bold")
    plt.subplots_adjust(bottom=0.2)
    plt.show()



def plot_status_distribution_last_30_days(df):
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    ref_date = pd.to_datetime("2024-12-01")
    filtered_df = df[(df["appointment_date"] < ref_date) & (df["appointment_date"] >= ref_date - pd.Timedelta(days=30))]
    grouped = filtered_df.groupby(["appointment_date", "status"]).size().unstack(fill_value=0)
    color_map = {
        "attended": "#B69DE1",
        "cancelled": "#B3C1F2",
        "did not attend": "#BDE3F0",
        "unknown": "#E5E5E5"
    }
    dates = grouped.index
    statuses = grouped.columns
    colors = [color_map.get(status, "#4583b5") for status in statuses]
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.set_facecolor("#fafafa")
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (0.05, 0), 0.9, 1.2,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor="#222",
        linewidth=0.5,
        clip_on=False,
        zorder=-3,
        linestyle="-",
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    bottom_values = [0] * len(dates)
    for status, color in zip(statuses, colors):
        values = grouped[status]
        ax.bar(dates, values, bottom=bottom_values, label=status.capitalize(), color=color, edgecolor="#fafafa", zorder=3)
        bottom_values = [i + j for i, j in zip(bottom_values, values)]
    
    total_per_date = grouped.sum(axis=1)
    for i, (date, total) in enumerate(zip(dates, total_per_date)):
        ax.text(date, total + 0.6, f"{total}", ha="center", va="bottom", fontsize=10, color="#222", fontweight="bold")

    fig.suptitle("Appointments Status Distribution (Last 30 Days)", fontsize=12, x=0.24, y=1.07, ha="center", fontweight='bold')
    ax.set_xlabel("Date", labelpad=10)
    ax.set_ylabel("Number of Appointments")
    ax.legend(loc="upper right", bbox_to_anchor=(1.01, 1.35), frameon=False) 
    ax.set_xticks(dates)
    ax.set_xticklabels(dates.strftime("%Y-%m-%d"), rotation=45, ha="right")
    ax.spines[["right", "top"]].set_visible(False)
    ax.yaxis.set_ticks_position("none")
    ax.xaxis.set_ticks_position("none")
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    plt.subplots_adjust(bottom=0.3)
    plt.show()



def plot_status_distribution_next_30_days(df):
    df["appointment_date"] = pd.to_datetime(df["appointment_date"])
    ref_date = pd.to_datetime("2024-12-01")
    filtered_df = df[(df["appointment_date"] >= ref_date) & (df["appointment_date"] < ref_date + pd.Timedelta(days=30))]
    grouped = filtered_df.groupby(["appointment_date", "status"]).size().unstack(fill_value=0)
    column_order = ["scheduled", "cancelled"]
    grouped = grouped.reindex(columns=column_order, fill_value=0)
    color_map = {
        "scheduled": "#CD77B6",
        "cancelled": "#B3C1F2"
    }
    dates = grouped.index
    statuses = grouped.columns
    colors = [color_map.get(status, "#4583b5") for status in statuses]
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.set_facecolor("#fafafa")
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (0.03, 0), 0.94, 1.2,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor="#222",
        linewidth=0.5,
        clip_on=False,
        zorder=-3,
        linestyle="-",
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    bottom_values = [0] * len(dates)
    for status, color in zip(statuses, colors):
        values = grouped[status]
        ax.bar(dates, values, bottom=bottom_values, label=status.capitalize(), color=color, edgecolor="#fafafa", zorder=3)
        bottom_values = [i + j for i, j in zip(bottom_values, values)]

    total_per_date = grouped.sum(axis=1)
    for i, (date, total) in enumerate(zip(dates, total_per_date)):
        ax.text(date, total + 0.4, f"{total}", ha="center", va="bottom", fontsize=10, color="#222", fontweight="bold")

    fig.suptitle("Appointments Status Distribution (Next 30 Days)", fontsize=12, x=0.25, y=1.07, ha="center", fontweight='bold')
    ax.set_xlabel("Date", labelpad=10)
    ax.set_ylabel("Number of Appointments")
    ax.legend(loc="upper right", bbox_to_anchor=(1.01, 1.35), frameon=False) 
    ax.set_xticks(dates)
    ax.set_xticklabels(dates.strftime("%Y-%m-%d"), rotation=45, ha="right")
    ax.spines[["right", "top"]].set_visible(False)
    ax.yaxis.set_ticks_position("none")
    ax.xaxis.set_ticks_position("none")
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    plt.subplots_adjust(bottom=0.3)
    plt.show()


def plot_scheduling_interval_distribution(df):
    fig, ax = plt.subplots(figsize=(16, 6))
    ax.set_facecolor('#fafafa')
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (0.03, 0.05), 0.92, 1.1,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor='#222',
        linewidth=0.25,
        clip_on=False,
        zorder=-3,
        linestyle='-',
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    
    scheduling_intervals = df['scheduling_interval']
    bins = range(scheduling_intervals.min(), scheduling_intervals.max() +1 )
    counts, edges = np.histogram(scheduling_intervals, bins=bins)
    percentages = (counts / scheduling_intervals.size) * 100
    
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    valid_x = [x for x, _, _ in valid_bins]
    valid_counts = [count for _, count, _ in valid_bins]
    valid_percentages = [percentage for _, _, percentage in valid_bins]
    
    fig.suptitle(
        'How Far in Advance Do Patients Schedule?',
        fontsize=12, x=0.2, y=1.04, ha="center", fontweight='bold'
    )
    
    plt.bar(
        valid_x, valid_counts, width=1, align='center',
        edgecolor='#fafafa', color='#67A7D4'
    )
    
    ax.set_xticks(bins[:-1])
    ax.set_xticklabels([int(b) for b in bins[:-1]], ha="center")
    ax.set_ylabel('Number of Appointments', labelpad=10)
    plt.xlabel('Scheduling Interval (Days)', labelpad=10)
    ax.spines[['right', 'top']].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    plt.subplots_adjust(bottom=0.25)
    for x, count, percentage in zip(valid_x, valid_counts, valid_percentages):
        plt.text(
            x, count + (max(valid_counts) * 0.02),
            f"{percentage:.1f}%", fontsize=8, fontweight='bold',
            color='#222', ha='center'
        )
    
    plt.show()


def plot_appointment_duration_distribution(df):
    durations = df['appointment_duration'].dropna()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_facecolor('#fafafa')
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (-0.13, 0.05), 1.2, 1.1,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor='#222',
        linewidth=0.25,
        clip_on=False,
        zorder=-3,
        linestyle='-',
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    fig.suptitle('How Long Are Appointments? A Duration Breakdown', fontsize=12, x=0.4, y=1.03, ha="center", fontweight='bold')
    
    initial_bins = np.arange(0, durations.max() + 5, 5)
    counts, edges = np.histogram(durations, bins=initial_bins)
    percentages = (counts / durations.size) * 100
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    
    if valid_bins:
        max_bin = valid_bins[-1][0] + 5
    else:
        max_bin = 5

    bins = np.arange(0, max_bin, 5)
    counts, edges = np.histogram(durations, bins=bins)
    percentages = (counts / durations.size) * 100
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    
    valid_x = [x for x, _, _ in valid_bins]
    valid_counts = [count for _, count, _ in valid_bins]
    valid_percentages = [percentage for _, _, percentage in valid_bins]
    
    plt.bar(
        valid_x, valid_counts, width=np.diff(edges)[:len(valid_x)], align='edge',
        edgecolor='#fafafa', color='#67A7D4'
    )
    
    ax.set_xticks(bins)
    ax.set_xticklabels([int(b) for b in bins], ha="left")
    ax.set_ylabel('Number of Appointments', labelpad=10)
    plt.xlabel('Appointment Duration (Minutes)', labelpad=10)
    ax.spines[['right', 'top']].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    plt.subplots_adjust(bottom=0.25)
    
    for x, count, percentage in zip(valid_x, valid_counts, valid_percentages):
        plt.text(
            x + 2.8, count + (max(valid_counts) * 0.02),
            f"{percentage:.1f}%", fontsize=8, fontweight='bold',
            color='#222', ha='center'
        )
    
    plt.show()

def plot_waiting_time_distribution(df):
    durations = df['waiting_time'].dropna()
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.set_facecolor('#fafafa')
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (0.005, 0.05), 0.96, 1.1,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor='#222',
        linewidth=0.25,
        clip_on=False,
        zorder=-3,
        linestyle='-',
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    fig.suptitle('How Much Time Do Patients Spend Waiting?', fontsize=12, x=0.215, y=1.04, ha="center", fontweight='bold')
    
    initial_bins = np.arange(0, durations.max() + 10, 10)
    counts, edges = np.histogram(durations, bins=initial_bins)
    percentages = (counts / durations.size) * 100
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    
    if valid_bins:
        max_bin = valid_bins[-1][0] + 10
    else:
        max_bin = 10  # Por defecto al menos un bin

    bins = np.arange(0, max_bin, 10)
    counts, edges = np.histogram(durations, bins=bins)
    percentages = (counts / durations.size) * 100
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    
    valid_x = [x for x, _, _ in valid_bins]
    valid_counts = [count for _, count, _ in valid_bins]
    valid_percentages = [percentage for _, _, percentage in valid_bins]
    
    plt.bar(
        valid_x, valid_counts, width=np.diff(edges)[:len(valid_x)], align='edge',
        edgecolor='#fafafa', color='#67A7D4'
    )
    
    ax.set_xticks(bins)
    ax.set_xticklabels([int(b) for b in bins], ha="center")
    ax.set_ylabel('Number of Appointments', labelpad=10)
    plt.xlabel('Waiting Time (Minutes)', labelpad=10)
    ax.spines[['right', 'top']].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    plt.subplots_adjust(bottom=0.25)
    
    for x, count, percentage in zip(valid_x, valid_counts, valid_percentages):
        plt.text(
            x + 5, count + (max(valid_counts) * 0.02),
            f"{percentage:.1f}%", fontsize=8, fontweight='bold',
            color='#222', ha='center'
        )
    
    plt.show()


def plot_arrival_time_distribution(df):
    attended_appointments = df[(df['status'] == 'attended') & df['check_in_time'].notna()].copy()
    attended_appointments['arrival_time_diff'] = round(
        (pd.to_datetime(attended_appointments['check_in_time'], format='%H:%M:%S', errors='coerce') -
         pd.to_datetime(attended_appointments['appointment_time'], format='%H:%M:%S', errors='coerce')).dt.total_seconds() / 60.0, 0
    )
    arrival_time_diff = attended_appointments['arrival_time_diff'].dropna()
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.set_facecolor('#fafafa')
    border_radius = 0.02
    rect = patches.FancyBboxPatch(
        (-0.14, 0.05), 1.17, 1.1,
        transform=fig.transFigure,
        facecolor="#fafafa",
        edgecolor='#222',
        linewidth=0.25,
        clip_on=False,
        zorder=-3,
        linestyle='-',
        boxstyle=f"round,pad=0,rounding_size={border_radius}"
    )
    fig.patches.extend([rect])
    fig.suptitle('How Early or Late Do Patients Arrive?', fontsize=12, x=0.2, y=1.04, ha="center", fontweight='bold')
    initial_bins = range(int(np.floor(arrival_time_diff.min() / 5.0) * 5), int(np.ceil(arrival_time_diff.max() / 5.0) * 5) + 5, 5)
    counts, edges = np.histogram(arrival_time_diff, bins=initial_bins)
    percentages = (counts / arrival_time_diff.size) * 100
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    if valid_bins:
        min_valid_bin = valid_bins[0][0]
        max_valid_bin = valid_bins[-1][0] + 5
    else:
        min_valid_bin = 0
        max_valid_bin = 0 
    bins = range(min_valid_bin, max_valid_bin, 5)
    counts, edges = np.histogram(arrival_time_diff, bins=bins)
    percentages = (counts / arrival_time_diff.size) * 100
    valid_bins = [(x, count, percentage) for x, count, percentage in zip(edges[:-1], counts, percentages) if percentage >= 0.1]
    valid_x = [x for x, _, _ in valid_bins]
    valid_counts = [count for _, count, _ in valid_bins]
    valid_percentages = [percentage for _, _, percentage in valid_bins]
    bar_colors = ['#67A7D4' if x < 0 else '#f9a369' for x in valid_x]
    plt.bar(
        valid_x, valid_counts, width=np.diff(edges)[:len(valid_x)], align='edge',
        edgecolor='#fafafa', color=bar_colors
    )
    ax.axvline(0, color='#222', linestyle='--', linewidth=1.5, zorder=3)
    ax.set_xticks(bins)
    ax.set_xticklabels([int(b) for b in bins], ha="center")
    ax.set_ylabel('Number of Patients', labelpad=10)
    plt.xlabel('Arrival Time Difference (Minutes)', labelpad=10)
    ax.spines[['right', 'top']].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.7, zorder=-1)
    plt.subplots_adjust(left=0.08, bottom=0.25)
    legend_handles = [
        patches.Patch(color='#67A7D4', label='Early Arrival'),
        patches.Patch(color='#f9a369', label='Late Arrival')
    ]
    ax.legend(
        handles=legend_handles, loc='upper right', frameon=False, fontsize=10,
        bbox_to_anchor=(1.02, 1.25), title=None, handlelength=1.5, handleheight=1.5,
        labelspacing=1.0, alignment='left'
    )
    for x, count, percentage in zip(valid_x, valid_counts, valid_percentages):
        plt.text(
            x + 2.5, count + (max(valid_counts) * 0.02),
            f"{percentage:.1f}%", fontsize=8, fontweight='bold',
            color='#222', ha='center'
        )
    plt.show()
