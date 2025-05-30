import streamlit as st
import random
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_excel("Demo-Hygine Data V6.xlsx")
df = df[(df['Date'] != '2025-02-06') & (df['Date'] != '2025-02-07') & (df['Date'] != '2025-02-11')]
df.reset_index(drop = True)
# df_sales = pd.read_excel("sales.xlsx")

df_oshea_sales_amz = pd.read_excel("Origami_sales_amz.xlsx")
# df_oshea_sales_fk = pd.read_excel("Origami_sales_fk.xlsx")
# df_oshea_summary_fk = pd.read_excel('Origami Daily Sales Report - Flipkart Summary (27th Jan).xlsx',sheet_name='Flipkart Original')
# df_oshea_growth_fk = pd.read_excel('Origami Daily Sales Report - Flipkart Summary (27th Jan).xlsx',sheet_name='Flipkart Summary - Growing Categories')
# df_oshea_degrowth_fk = pd.read_excel('Origami Daily Sales Report - Flipkart Summary (27th Jan).xlsx',sheet_name='Flipkart Summary - De-Growing Categories')
df_oshea_summary_amz = pd.read_excel('Origami Daily Sales Report - Amazon Summary.xlsx',sheet_name='Amazon Original')
df_oshea_growth_amz = pd.read_excel('Origami Daily Sales Report - Amazon Summary.xlsx',sheet_name='Amazon Summary - Growing Categories')
df_oshea_degrowth_amz = pd.read_excel('Origami Daily Sales Report - Amazon Summary.xlsx',sheet_name='Amazon Summary - De-Growing Categories')

sales = {"Oshea":[df_oshea_sales_amz[:0],df_oshea_summary_amz[:0],df_oshea_growth_amz[:0],df_oshea_degrowth_amz[:0],df_oshea_summary_amz[:0],df_oshea_growth_amz[:0],df_oshea_degrowth_amz[:0],df_oshea_sales_amz[:0]],
"Origami":[df_oshea_sales_amz,df_oshea_summary_amz,df_oshea_growth_amz,df_oshea_degrowth_amz,df_oshea_summary_amz,df_oshea_growth_amz,df_oshea_degrowth_amz,df_oshea_sales_amz], 
"Harissons":[df_oshea_sales_amz[:0],df_oshea_summary_amz[:0],df_oshea_growth_amz[:0],df_oshea_degrowth_amz[:0],df_oshea_summary_amz[:0],df_oshea_growth_amz[:0],df_oshea_degrowth_amz[:0],df_oshea_sales_amz[:0]]}



# Hide menu & footer
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

def force_rerun():
    # Change the URL query parameters to force a rerun
    st.query_params = {"rerun": str(random.random())}

def show_login():
    st.title("Login Page")
    valid_users = {"alice":"password123", "bob":"qwerty"}

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in valid_users and valid_users[username] == password:
            st.session_state["logged_in"] = True
            st.session_state["page"] = "brand"
            #force_rerun()
        else:
            st.error("Invalid username or password.")

def show_brand():
    if not st.session_state.get("logged_in"):
        st.warning("Please login first.")
        st.session_state["page"] = "login"
        #force_rerun()
        return

    st.title("Choose Brand")
    brands = ["Oshea", "Origami", "Harissons"]
    choice = st.selectbox("Select brand:", brands)

    if st.button("Next"):
        st.session_state["selected_brand"] = choice
        st.session_state["page"] = "analytics"
        force_rerun()

def show_analytics():
    # Guard checks
    if not st.session_state.get("logged_in"):
        st.warning("Please log in first.")
        st.session_state["page"] = "login"
        force_rerun()
        return
    if "selected_brand" not in st.session_state:
        st.warning("Please select a brand first.")
        st.session_state["page"] = "brand_selection"
        force_rerun()
        return


    # Show the sidebar only on this page
    st.sidebar.header("Analytics Sections")
    mode = st.sidebar.radio("View mode:", ["Summary", "Drill Down", "Sales vs Target Trend","Sales Report"])

    st.title(f"Analytics for {st.session_state['selected_brand']}")

    df_selection = df[df['Brand'] == st.session_state['selected_brand']]

    sales_selection  = sales[st.session_state['selected_brand']]

    if mode == "Summary":
        show_summary_tab(df_selection)
    elif mode == "Sales vs Target Trend":
        show_sales_vs_target_tab(sales_selection)
    elif mode == "Sales Report":
        show_sales_report(sales_selection)
    else:
        show_drilldown_tab(df_selection)

def show_summary_tab(df):
    st.subheader("Summary View")

    # Let the user pick a sub‐category
    categories = df["Sub-category"].dropna().unique()
    selected_cat = st.selectbox("Select a category:",["All"]+list(categories))

    # Filter to just that sub‐category
    if selected_cat != "All":
        filtered = df[df["Sub-category"] == selected_cat].copy()
    else:
        filtered = df.copy()

    # Sort the unique dates
    unique_dates = sorted(filtered["Date"].unique())
    if len(unique_dates) == 0:
        st.write("No data available for this category.")
        return

    # Always take the latest date
    latest_date = unique_dates[-1]

    # Take the second-latest date if it exists, otherwise None
    if len(unique_dates) >= 2:
        prev_date = unique_dates[-2]
    else:
        prev_date = None

    # List of hygiene metrics
    metrics = [
        "Activation_Hygiene", "Price_Hygiene", "EDD_Hygiene", "Buy Box_Hygiene",
        "Catalog_Hygiene", "Rating_Hygiene", "Availability_Hygiene",
        "Deal_Hygiene", "Overall_Brand_Score"
    ]

    # Average for the latest date
    latest_means = filtered[filtered["Date"] == latest_date][metrics].mean()

    # Average for the previous date (if present)
    prev_means = (filtered[filtered["Date"] == prev_date][metrics].mean()
                  if prev_date else None)

    # Helper: display a single metric in percentage form
    def display_metric(col, label, current_val, prev_val):
        # If current is NaN, treat it as 0 for display
        if pd.isna(current_val):
            current_val = 0

        # If there's no previous date or it's NaN, we show no delta
        if (prev_val is None) or pd.isna(prev_val):
            delta_str = ""
        else:
            diff = current_val - prev_val
            delta_str = f"{diff:.1f}%"

        col.metric(
            label,
            f"{current_val:.1f}%",
            delta_str
        )

    # Layout columns (8 metrics -> 2 rows of 4)
    col1, col2, col3, col4 = st.columns(4)
    display_metric(col1, "Activation",   latest_means["Activation_Hygiene"],  
                   None if prev_means is None else prev_means["Activation_Hygiene"])
    display_metric(col2, "Price",        latest_means["Price_Hygiene"],       
                   None if prev_means is None else prev_means["Price_Hygiene"])
    display_metric(col3, "EDD",          latest_means["EDD_Hygiene"],         
                   None if prev_means is None else prev_means["EDD_Hygiene"])
    display_metric(col4, "Catalog",      latest_means["Catalog_Hygiene"],     
                   None if prev_means is None else prev_means["Catalog_Hygiene"])

    col5, col6, col7, col8 = st.columns(4)
    display_metric(col5, "Rating",       latest_means["Rating_Hygiene"],      
                   None if prev_means is None else prev_means["Rating_Hygiene"])
    display_metric(col6, "Availability", latest_means["Availability_Hygiene"],
                   None if prev_means is None else prev_means["Availability_Hygiene"])
    display_metric(col7, "Deal",         latest_means["Deal_Hygiene"],        
                   None if prev_means is None else prev_means["Deal_Hygiene"])
    display_metric(col8, "Overall Score",latest_means["Overall_Brand_Score"], 
                   None if prev_means is None else prev_means["Overall_Brand_Score"])

    # Finally, plot a trend line of Overall_Brand_Score vs. Date
    st.markdown("### Overall Brand Score Trend")
    trend_df = (
        filtered.groupby("Date", as_index=False)["Overall_Brand_Score"]
                .mean()
    )
    trend_df.set_index("Date", inplace=True)
    st.line_chart(trend_df["Overall_Brand_Score"])

import streamlit as st
import pandas as pd
import numpy as np

def show_sales_vs_target_tab(sales):
    st.subheader("Sales vs Targeted GMV Trend")

    # Dropdown to select category
    platforms = ['Amazon'] #,'Flipkart'
    selected_plaform = st.selectbox("Select Platform", platforms)

    # Filter data for the selected category
    if selected_plaform == "Amazon":
        df = sales[0]
        st.markdown("### Amazon")
    else:
        df = sales[-1]
        st.markdown("### Flipkart")





    # Dropdown to select category
    categories = df['Category'].dropna().unique()
    selected_category = st.selectbox("Select Category", categories)

    # Filter data for the selected category
    filtered_df = df[df['Category'] == selected_category].copy()

    # Ensure the Date column is in datetime format
    filtered_df['Date'] = pd.to_datetime(filtered_df['Date'])

    # Prepare data for the trend line
    trend_data = filtered_df[['Date', 'Cumulative_GMV', 'Targeted_GMV']].set_index('Date')

    # Plot using Streamlit's line_chart
    st.line_chart(trend_data)

def highlight_diff(val):
    """Color negative values red, positive values green, else white."""
    if val > 0:
        color = 'green'
    elif val < 0:
        color = 'red'
    else:
        color = 'white'
    return f'background-color: {color}'

def highlight_forecast(val):
    """Color negative values red, positive values green, else white."""
    if val > 100:
        color = 'green'
    elif val < 100:
        color = 'red'
    else:
        color = 'white'
    return f'background-color: {color}'

def format_inr(x):
    if pd.isna(x):
        return ""
    try:
        return format_decimal(x, locale="en_IN")  # e.g. 123456 => "1,23,456"
    except:
        # Fallback for non-numeric values
        return str(x)

def show_sales_report(sales):
    st.subheader("Daily Sales Report")

    # Dropdown to select category
    platforms = ['Amazon'] #,'Flipkart'
    selected_plaform = st.selectbox("Select Platform", platforms)

    # Filter data for the selected category
    if selected_plaform == "Amazon":
        df_summary = sales[4]
        df_growth = sales[5]
        df_degrowth = sales[6]
        st.markdown("### Amazon")
    else:
        df_summary = sales[1]
        df_growth = sales[2]
        df_degrowth = sales[3]
        st.markdown("### Flipkart")

    # df_summary["Attainment%_Forecast"] = df_summary["Attainment%_Forecast"]/100
    df_summary["Attainment%_Forecast"] = pd.to_numeric(df_summary["Attainment%_Forecast"], errors="coerce")
    df_summary["Comparative difference"] = pd.to_numeric(df_summary["Comparative difference"], errors="coerce")
    df_summary = df_summary.replace([np.inf, -np.inf], np.nan)
    df_summary = df_summary.fillna(0)

    cols_to_inr = [col for col in df_summary.columns if "GMV" in col]

    styled_summary = (
        df_summary.style
            .format(format_inr, subset=cols_to_inr)
            .background_gradient(cmap='RdYlGn', subset=['Comparative difference'])
    )
    # Ensure the Date column is in datetime format
    st.dataframe(styled_summary, hide_index=True,
        column_config={
            "Category" : {"pinned": True},
            # Show Attainment%_Forecast as a progress bar from 0% to 150%
            "Attainment%_Forecast": st.column_config.ProgressColumn(
                label="Attainment Forecast (%)",
                help="Shows the forecast progress (0% to 100%)",
                format="%.0f%%",
                min_value=0,
                max_value=100,
                pinned=True
            ),
            "Attainment%_MTD": st.column_config.NumberColumn(
            format="%.0f%%",  # or "{:.0f}%"
            pinned=True
        ),
            "Comparative difference": st.column_config.NumberColumn(
            format="%.0f%%",  # or "{:.0f}%"

        )})

    # styled_growth = (
    #     df_growth.style
    #         .background_gradient(cmap='RdYlGn', subset=['Growth %'])
    # )

    # Prepare data for the trend line
    st.dataframe(df_growth, hide_index=True, column_config={
            "Growth %": st.column_config.NumberColumn(
            format="%.0f%%",  # or "{:.0f}%"
        )})

    # Plot using Streamlit's line_chart
    st.dataframe(df_degrowth, hide_index=True, column_config={
            "De-Growth %": st.column_config.NumberColumn(
            format="%.0f%%",  # or "{:.0f}%"
        )})

def show_drilldown_tab(df):
    st.subheader("Drill Down View")

    # 8 possible indicators
    indicator_list = [
        "Activation_Hygiene",
        "Price_Hygiene",
        "Buy Box_Hygiene",
        "EDD_Hygiene",
        "Catalog_Hygiene",
        "Rating_Hygiene",
        "Availability_Hygiene",
        "Deal_Hygiene",
        "Overall_Brand_Score"
    ]
    
    # For each indicator, specify which "extra" columns to display
    indicator_columns = {
        "Activation_Hygiene": ['SNS Rule', 'Live SNS',
       'SNS Validation', 'BXGY Rule', 'Live BXGY', 'BXGY Validation'],
        "Price_Hygiene": ['Price Rule','Live Price_400013', 'Live Price_600005', 'Live Price_122102',
                        'Live Price_700016', 'Live Price_560068'],
        "EDD_Hygiene":       [ 'EDD_400013', 'EDD_600005', 'EDD_122102',
       'EDD_700016', 'EDD_560068'],
        "Buy Box_Hygiene": ['Sold By_400013', 'Sold By_600005', 'Sold By_122102',
                        'Sold By_700016', 'Sold By_560068'],
        "Catalog_Hygiene":    ['Ratings', 'Title Length','Bullet Point Count','Images Count', 'A+'],
        "Rating_Hygiene":     ['3 Star Ratings', '2 Star Ratings',
       '1 Star Ratings', 'Total Ratings', 'Ratings'],
        "Availability_Hygiene": ['Availability'],
        "Deal_Hygiene":       ['Coupon Rule',
       'Live Coupon', 'Coupon Validation'],
        "Overall_Brand_Score": ['Activation_Hygiene', 'Price_Hygiene', 'EDD_Hygiene','Buy Box_Hygiene', 'Catalog_Hygiene',
       'Rating_Hygiene', 'Availability_Hygiene', 'Deal_Hygiene']
    }

    # Category selection
    categories = df["Sub-category"].dropna().unique()
    cat_filter = st.selectbox("Category Filter", ["All"] + list(categories))

    # Indicator selection
    chosen_indicator = st.selectbox("Indicator", ["All"] + indicator_list)

    # Date selection (with “All” option)
    all_dates = sorted(df["Date"].dropna().unique())
    date_choice = st.selectbox("Select a Date", ["All"] + list(all_dates))

    # Range slider for the chosen indicator
    if chosen_indicator != 'All':
        valid_vals = df[chosen_indicator].dropna()
        if valid_vals.empty:
            low, high = 0, 100
        else:
            low, high = float(valid_vals.min()), float(valid_vals.max())

        if high == 0:
            high = 0.01
        threshold_range = st.slider("Threshold Range", low, high, (low, high))
    else:
        low, high = 0.0, 100.0
        threshold_range = st.slider("Threshold Range", low, high, (low, high))

    # --- Filtering ---
    filtered_df = df.copy()

    if cat_filter != "All":
        filtered_df = filtered_df[filtered_df["Sub-category"] == cat_filter]
    if date_choice != "All":
        filtered_df = filtered_df[filtered_df["Date"] == date_choice]

    # Keep rows whose chosen_indicator is within the threshold range
    #mask = filtered_df[chosen_indicator].between(*threshold_range, inclusive="both")
    if chosen_indicator == "All":
        mask = filtered_df[indicator_list].apply(lambda row: row.between(*threshold_range).any(), axis=1)
    else:
        mask = filtered_df[chosen_indicator].between(*threshold_range, inclusive="both")
    filtered_df = filtered_df[mask]

    st.markdown("### Filtered Results")


    # Base columns you always want to see:
    #base_cols = ["ASIN", "Generic Title", chosen_indicator]
    # Add in the extra columns for the chosen indicator
    #extra_cols = indicator_columns.get(chosen_indicator, [])
    base_cols = ["ASIN", "Generic Title", chosen_indicator] if chosen_indicator != "All" else ["ASIN", "Generic Title"]+indicator_list
    extra_cols = indicator_columns.get(chosen_indicator, []) if chosen_indicator != "All" else []

    # Combine & only keep columns that actually exist in df
    columns_to_show = base_cols + extra_cols
    final_cols = [c for c in columns_to_show if c in filtered_df.columns]

    st.dataframe(filtered_df[final_cols])

print(st.session_state)


# -----------------------
# Main Router
# -----------------------
if "page" not in st.session_state:
    st.session_state["page"] = "login"

page = st.session_state["page"]
if page == "login":
    show_login()
elif page == "brand":
    show_brand()
elif page == "analytics":
    show_analytics()
