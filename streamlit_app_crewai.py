# -*- coding: utf-8 -*-
# Copyright 2024-2025 Streamlit Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Stock Peer Analysis Dashboard - CrewAI Enhanced Version

This version uses CrewAI agents to provide intelligent stock analysis with:
- Data Analyst Agent: Fetches and processes stock data
- Performance Analyst Agent: Analyzes stock performance metrics
- Insights Agent: Generates actionable insights and recommendations
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import altair as alt
from crewai import Agent, Task, Crew, Process
from crewai_tools import CSVSearchTool
from langchain_openai import ChatOpenAI
import os

st.set_page_config(
    page_title="Stock peer analysis dashboard (CrewAI)",
    page_icon=":chart_with_upwards_trend:",
    layout="wide",
)

"""
# :material/query_stats: Stock peer analysis (CrewAI Enhanced)

Easily compare stocks against others in their peer group with AI-powered insights.
"""

""  # Add some space.

# Check for OpenAI API key
if "OPENAI_API_KEY" not in os.environ:
    st.warning("Please set your OPENAI_API_KEY environment variable to use CrewAI features.")
    st.info("You can still use the basic dashboard features without the AI insights.")
    USE_CREWAI = False
else:
    USE_CREWAI = True

cols = st.columns([1, 3])

STOCKS = [
    "AAPL", "ABBV", "ACN", "ADBE", "ADP", "AMD", "AMGN", "AMT", "AMZN", "APD",
    "AVGO", "AXP", "BA", "BK", "BKNG", "BMY", "BRK.B", "BSX", "C", "CAT",
    "CI", "CL", "CMCSA", "COST", "CRM", "CSCO", "CVX", "DE", "DHR", "DIS",
    "DUK", "ELV", "EOG", "EQR", "FDX", "GD", "GE", "GILD", "GOOG", "GOOGL",
    "HD", "HON", "HUM", "IBM", "ICE", "INTC", "ISRG", "JNJ", "JPM", "KO",
    "LIN", "LLY", "LMT", "LOW", "MA", "MCD", "MDLZ", "META", "MMC", "MO",
    "MRK", "MSFT", "NEE", "NFLX", "NKE", "NOW", "NVDA", "ORCL", "PEP", "PFE",
    "PG", "PLD", "PM", "PSA", "REGN", "RTX", "SBUX", "SCHW", "SLB", "SO",
    "SPGI", "T", "TJX", "TMO", "TSLA", "TXN", "UNH", "UNP", "UPS", "V",
    "VZ", "WFC", "WM", "WMT", "XOM",
]

DEFAULT_STOCKS = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMZN", "TSLA", "META"]


def stocks_to_str(stocks):
    return ",".join(stocks)


if "tickers_input" not in st.session_state:
    st.session_state.tickers_input = st.query_params.get(
        "stocks", stocks_to_str(DEFAULT_STOCKS)
    ).split(",")


def update_query_param():
    if st.session_state.tickers_input:
        st.query_params["stocks"] = stocks_to_str(st.session_state.tickers_input)
    else:
        st.query_params.pop("stocks", None)


top_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with top_left_cell:
    tickers = st.multiselect(
        "Stock tickers",
        options=sorted(set(STOCKS) | set(st.session_state.tickers_input)),
        default=st.session_state.tickers_input,
        placeholder="Choose stocks to compare. Example: NVDA",
        accept_new_options=True,
    )

horizon_map = {
    "1 Months": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "5 Years": "5y",
    "10 Years": "10y",
    "20 Years": "20y",
}

with top_left_cell:
    horizon = st.pills(
        "Time horizon",
        options=list(horizon_map.keys()),
        default="6 Months",
    )

tickers = [t.upper() for t in tickers]

if tickers:
    st.query_params["stocks"] = stocks_to_str(tickers)
else:
    st.query_params.pop("stocks", None)

if not tickers:
    top_left_cell.info("Pick some stocks to compare", icon=":material/info:")
    st.stop()

right_cell = cols[1].container(
    border=True, height="stretch", vertical_alignment="center"
)


@st.cache_resource(show_spinner=False, ttl="6h")
def load_data(tickers, period):
    tickers_obj = yf.Tickers(tickers)
    data = tickers_obj.history(period=period)
    if data is None:
        raise RuntimeError("YFinance returned no data.")
    return data["Close"]


# Load the data
try:
    data = load_data(tickers, horizon_map[horizon])
except yf.exceptions.YFRateLimitError as e:
    st.warning("YFinance is rate-limiting us :(\nTry again later.")
    load_data.clear()
    st.stop()

empty_columns = data.columns[data.isna().all()].tolist()

if empty_columns:
    st.error(f"Error loading data for the tickers: {', '.join(empty_columns)}.")
    st.stop()

# Normalize prices (start at 1)
normalized = data.div(data.iloc[0])

latest_norm_values = {normalized[ticker].iat[-1]: ticker for ticker in tickers}
max_norm_value = max(latest_norm_values.items())
min_norm_value = min(latest_norm_values.items())

# Export stock data to CSV for CSVSearchTool
csv_file_path = "/tmp/stock_analysis_data.csv"
# Create a comprehensive CSV with stock metrics
stock_metrics_data = []
for ticker in tickers:
    pct_change = normalized[ticker].pct_change().dropna()
    total_return = (normalized[ticker].iat[-1] - 1) * 100
    volatility = pct_change.std() * 100
    start_price = data[ticker].iloc[0]
    end_price = data[ticker].iloc[-1]

    stock_metrics_data.append({
        'Ticker': ticker,
        'Start_Price': f"{start_price:.2f}",
        'End_Price': f"{end_price:.2f}",
        'Total_Return_Percent': f"{total_return:.2f}",
        'Volatility_Percent': f"{volatility:.2f}",
        'Performance_Category': 'Outperformer' if total_return > 0 else 'Underperformer',
        'Time_Period': horizon
    })

stock_metrics_df = pd.DataFrame(stock_metrics_data)
stock_metrics_df.to_csv(csv_file_path, index=False)

bottom_left_cell = cols[0].container(
    border=True, height="stretch", vertical_alignment="center"
)

with bottom_left_cell:
    cols = st.columns(2)
    cols[0].metric(
        "Best stock",
        max_norm_value[1],
        delta=f"{round(max_norm_value[0] * 100)}%",
        width="content",
    )
    cols[1].metric(
        "Worst stock",
        min_norm_value[1],
        delta=f"{round(min_norm_value[0] * 100)}%",
        width="content",
    )

# Plot normalized prices
with right_cell:
    st.altair_chart(
        alt.Chart(
            normalized.reset_index().melt(
                id_vars=["Date"], var_name="Stock", value_name="Normalized price"
            )
        )
        .mark_line()
        .encode(
            alt.X("Date:T"),
            alt.Y("Normalized price:Q").scale(zero=False),
            alt.Color("Stock:N"),
        )
        .properties(height=400)
    )

""
""

# ============================================================================
# CrewAI Integration: AI-Powered Stock Analysis
# ============================================================================

if USE_CREWAI and len(tickers) > 1:
    st.markdown("---")
    """
    ## AI-Powered Stock Analysis

    Our AI agents analyze the stock data to provide insights and recommendations.
    """

    # Display the CSV data being analyzed
    with st.expander("View Stock Metrics CSV Data", expanded=False):
        st.info("This CSV data is searchable by the AI agents using CSVSearchTool for semantic queries.")
        st.dataframe(stock_metrics_df, use_container_width=True)

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    # Initialize CSVSearchTool for semantic search of stock data
    csv_search_tool = CSVSearchTool(csv=csv_file_path)

    # Create specialized agents
    data_analyst = Agent(
        role="Stock Data Analyst",
        goal="Analyze stock price data and calculate key performance metrics",
        backstory=(
            "You are an experienced quantitative analyst specializing in stock market data analysis. "
            "You excel at processing historical price data and calculating relevant metrics like returns, "
            "volatility, and relative performance. You have access to a CSV search tool that allows you "
            "to perform semantic searches on stock metrics data."
        ),
        tools=[csv_search_tool],
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    performance_analyst = Agent(
        role="Performance Analyst",
        goal="Evaluate stock performance relative to peers and identify trends",
        backstory=(
            "You are a senior equity analyst with deep expertise in comparative stock analysis. "
            "You can identify outperformers and underperformers, spot trends, and understand "
            "the competitive dynamics within peer groups."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    insights_agent = Agent(
        role="Investment Insights Specialist",
        goal="Generate actionable insights and investment recommendations",
        backstory=(
            "You are a portfolio manager with 20 years of experience. You synthesize complex "
            "financial data into clear, actionable recommendations for investors. You focus on "
            "practical insights that help investors make informed decisions."
        ),
        llm=llm,
        verbose=False,
        allow_delegation=False,
    )

    # Prepare data summary for analysis
    returns = {}
    volatility = {}
    for ticker in tickers:
        pct_change = normalized[ticker].pct_change().dropna()
        returns[ticker] = (normalized[ticker].iat[-1] - 1) * 100  # Total return %
        volatility[ticker] = pct_change.std() * 100  # Volatility as %

    data_summary = f"""
    Time Period: {horizon}
    Stocks Analyzed: {', '.join(tickers)}

    Performance Summary:
    """

    for ticker in tickers:
        data_summary += f"\n- {ticker}: Return: {returns[ticker]:.2f}%, Volatility: {volatility[ticker]:.2f}%"

    data_summary += f"\n\nBest Performer: {max_norm_value[1]} (+{round(max_norm_value[0] * 100)}%)"
    data_summary += f"\nWorst Performer: {min_norm_value[1]} (+{round(min_norm_value[0] * 100)}%)"

    # Create tasks for the crew
    task1 = Task(
        description=(
            f"Using the CSV search tool, analyze the stock performance data for the following stocks: {', '.join(tickers)}.\n\n"
            f"The data covers the time period: {horizon}\n\n"
            "Use the CSV search tool to find:\n"
            "1. Which stocks are categorized as 'Outperformer' vs 'Underperformer'\n"
            "2. The total return percentage for each stock\n"
            "3. The volatility metrics for comparison\n\n"
            "Then calculate and summarize key metrics including total returns and volatility for each stock. "
            "Highlight any notable patterns in the data discovered through the CSV search."
        ),
        expected_output="A concise summary of the key performance metrics for all stocks analyzed, including insights from CSV search queries.",
        agent=data_analyst,
    )

    task2 = Task(
        description=(
            f"Based on the performance data:\n\n{data_summary}\n\n"
            "Identify which stocks are outperforming or underperforming relative to the peer group. "
            "Highlight any notable trends or patterns in the data."
        ),
        expected_output="An analysis of relative performance highlighting outperformers, underperformers, and key trends.",
        agent=performance_analyst,
    )

    task3 = Task(
        description=(
            "Based on the data analysis and performance evaluation, provide 3-5 actionable insights "
            "or recommendations for investors. Focus on practical takeaways about the comparative "
            "performance of these stocks."
        ),
        expected_output="A list of 3-5 clear, actionable insights and recommendations for investors.",
        agent=insights_agent,
    )

    # Create and run the crew
    crew = Crew(
        agents=[data_analyst, performance_analyst, insights_agent],
        tasks=[task1, task2, task3],
        process=Process.sequential,
        verbose=False,
    )

    with st.spinner("AI agents are analyzing your stocks..."):
        try:
            result = crew.kickoff()

            st.success("Analysis complete!")

            # Display results in expandable sections
            with st.expander("Data Analysis", expanded=True):
                st.markdown(result.tasks_output[0].raw)

            with st.expander("Performance Analysis", expanded=True):
                st.markdown(result.tasks_output[1].raw)

            with st.expander("Investment Insights", expanded=True):
                st.markdown(result.tasks_output[2].raw)

        except Exception as e:
            st.error(f"Error running AI analysis: {str(e)}")
            st.info("Continuing with standard analysis...")

# ============================================================================
# Original Dashboard Features
# ============================================================================

"""
## Individual stocks vs peer average

For the analysis below, the "peer average" when analyzing stock X always
excludes X itself.
"""

if len(tickers) <= 1:
    st.warning("Pick 2 or more tickers to compare them")
    st.stop()

NUM_COLS = 4
cols = st.columns(NUM_COLS)

for i, ticker in enumerate(tickers):
    # Calculate peer average (excluding current stock)
    peers = normalized.drop(columns=[ticker])
    peer_avg = peers.mean(axis=1)

    # Create DataFrame with peer average.
    plot_data = pd.DataFrame(
        {
            "Date": normalized.index,
            ticker: normalized[ticker],
            "Peer average": peer_avg,
        }
    ).melt(id_vars=["Date"], var_name="Series", value_name="Price")

    chart = (
        alt.Chart(plot_data)
        .mark_line()
        .encode(
            alt.X("Date:T"),
            alt.Y("Price:Q").scale(zero=False),
            alt.Color(
                "Series:N",
                scale=alt.Scale(domain=[ticker, "Peer average"], range=["red", "gray"]),
                legend=alt.Legend(orient="bottom"),
            ),
            alt.Tooltip(["Date", "Series", "Price"]),
        )
        .properties(title=f"{ticker} vs peer average", height=300)
    )

    cell = cols[(i * 2) % NUM_COLS].container(border=True)
    cell.write("")
    cell.altair_chart(chart, use_container_width=True)

    # Create Delta chart
    plot_data = pd.DataFrame(
        {
            "Date": normalized.index,
            "Delta": normalized[ticker] - peer_avg,
        }
    )

    chart = (
        alt.Chart(plot_data)
        .mark_area()
        .encode(
            alt.X("Date:T"),
            alt.Y("Delta:Q").scale(zero=False),
        )
        .properties(title=f"{ticker} minus peer average", height=300)
    )

    cell = cols[(i * 2 + 1) % NUM_COLS].container(border=True)
    cell.write("")
    cell.altair_chart(chart, use_container_width=True)

""
""

"""
## Raw data
"""

data
