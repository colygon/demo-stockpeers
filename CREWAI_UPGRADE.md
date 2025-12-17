# CrewAI Upgrade Documentation

## Overview

This document describes the CrewAI integration for the Stock Peer Analysis Dashboard. The upgrade adds AI-powered stock analysis capabilities while maintaining full compatibility with the original dashboard.

## What's New

### Version 0.3.0 - CrewAI Integration

The Stock Peer Analysis Dashboard has been enhanced with CrewAI to provide intelligent, AI-powered stock analysis alongside the traditional visualization features.

## Architecture

### Two Versions Available

1. **Original Version** (`streamlit_app.py`)
   - Classic stock peer analysis dashboard
   - No AI features
   - No external API dependencies
   - Lightweight and fast

2. **CrewAI Enhanced Version** (`streamlit_app_crewai.py`)
   - All features from the original version
   - AI-powered analysis using three specialized agents
   - Requires OpenAI API key
   - Provides actionable investment insights

### CrewAI Agents

The CrewAI version implements three specialized agents working in sequential process:

#### 1. Stock Data Analyst
- **Role**: Stock Data Analyst
- **Goal**: Analyze stock price data and calculate key performance metrics
- **Capabilities**:
  - Processes historical price data
  - Calculates returns and volatility metrics
  - Provides quantitative summaries

#### 2. Performance Analyst
- **Role**: Performance Analyst
- **Goal**: Evaluate stock performance relative to peers and identify trends
- **Capabilities**:
  - Compares stocks against peer group
  - Identifies outperformers and underperformers
  - Spots trends and patterns in the data
  - Analyzes competitive dynamics

#### 3. Investment Insights Specialist
- **Role**: Investment Insights Specialist
- **Goal**: Generate actionable insights and investment recommendations
- **Capabilities**:
  - Synthesizes analysis from other agents
  - Generates 3-5 actionable recommendations
  - Provides practical investment guidance
  - Delivers clear, investor-focused insights

## Installation

### Prerequisites

- Python >= 3.10
- OpenAI API key (for CrewAI version only)
- uv package manager (recommended)

### Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone https://github.com/colygon/demo-stockpeers.git
   cd demo-stockpeers
   ```

2. **Create virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   uv sync
   ```

4. **Set up OpenAI API key** (for CrewAI version):
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Running the Original Version

```bash
streamlit run streamlit_app.py
```

### Running the CrewAI Enhanced Version

```bash
streamlit run streamlit_app_crewai.py
```

**Note**: The CrewAI version will show a warning if no OpenAI API key is set, but will still function as a basic dashboard without AI features.

## Features

### Original Features (Both Versions)

- Interactive stock ticker selection
- Multiple time horizon options (1 month to 20 years)
- Normalized price comparison charts
- Best/worst performer metrics
- Individual stock vs peer average comparison
- Delta analysis charts
- Raw data display

### New AI Features (CrewAI Version Only)

- **Data Analysis**: Comprehensive metrics summary with returns and volatility
- **Performance Analysis**: Comparative analysis identifying trends and patterns
- **Investment Insights**: 3-5 actionable recommendations based on data
- Expandable sections for easy navigation
- Real-time AI analysis with loading indicators

## Dependencies

### Core Dependencies

```toml
altair>=5.5.0
pandas>=2.2.3
streamlit>=1.44.2
yfinance>=0.2.55
```

### New CrewAI Dependencies

```toml
crewai>=0.86.0
langchain-openai>=0.3.0
```

## Technical Details

### Sequential Processing

The CrewAI agents use **sequential processing** (Process.sequential), meaning:
- Agents execute tasks in order
- Each agent completes its task before the next begins
- Results flow from one agent to the next
- Ensures logical progression: Data → Analysis → Insights

### Compatibility

- ✅ Fully backward compatible
- ✅ Original version unchanged and still available
- ✅ No breaking changes to existing functionality
- ✅ Graceful degradation when API key is missing
- ✅ Same UI/UX as original version

### Performance Considerations

- AI analysis adds ~10-30 seconds depending on:
  - Number of stocks selected
  - OpenAI API response time
  - Complexity of analysis required
- Results are not cached (real-time analysis)
- Stock data is still cached (6-hour TTL)

## Configuration

### LLM Settings

The default configuration uses:
- Model: `gpt-4o-mini`
- Temperature: `0.7`

To modify, edit in `streamlit_app_crewai.py`:
```python
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
```

### Agent Verbosity

Agents are set to `verbose=False` for cleaner UI. To enable detailed logging:
```python
agent = Agent(
    ...
    verbose=True,  # Change to True
)
```

## Troubleshooting

### Common Issues

1. **"Please set your OPENAI_API_KEY environment variable"**
   - Solution: Set the OpenAI API key as described in Setup Instructions
   - The app will still work without AI features

2. **"YFinance is rate-limiting us"**
   - Solution: Wait a few minutes and try again
   - This is a YFinance API limitation, not related to CrewAI

3. **"Error running AI analysis"**
   - Check your OpenAI API key is valid
   - Ensure you have sufficient API credits
   - Check internet connectivity
   - The app will continue with standard analysis

### Debug Mode

To enable verbose logging for troubleshooting:
```python
crew = Crew(
    agents=[data_analyst, performance_analyst, insights_agent],
    tasks=[task1, task2, task3],
    process=Process.sequential,
    verbose=True,  # Enable detailed logging
)
```

## Examples

### Example Analysis Output

When you select stocks like AAPL, MSFT, GOOGL, NVDA over 6 months, the AI agents will provide:

**Data Analysis**:
- Total returns for each stock
- Volatility metrics
- Statistical summary

**Performance Analysis**:
- Relative performance rankings
- Trend identification (e.g., "NVDA showing strong momentum")
- Peer comparison insights

**Investment Insights**:
- "Consider NVDA for growth potential based on 45% outperformance"
- "MSFT shows lower volatility, suitable for risk-averse portfolios"
- "Watch for mean reversion in underperforming stocks"

## Future Enhancements

Potential improvements for future versions:

- [ ] Add more specialized agents (e.g., Risk Analyst, Sector Analyst)
- [ ] Integrate real-time news sentiment analysis
- [ ] Add fundamental analysis capabilities
- [ ] Support for custom agent configurations
- [ ] Historical AI analysis caching
- [ ] Export analysis reports to PDF/markdown
- [ ] Multi-language support for insights
- [ ] Integration with additional LLM providers

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Maintain backward compatibility
2. Add tests for new features
3. Update documentation
4. Follow existing code style
5. Submit pull requests to the `crewai-upgrade` branch

## License

This project maintains the original Apache License 2.0. See LICENSE file for details.

## Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## Version History

### 0.3.0 (Current)
- Added CrewAI integration
- Three specialized AI agents
- Sequential processing workflow
- Comprehensive documentation

### 0.2.0 (Original)
- Base stock peer analysis dashboard
- Interactive visualizations
- Multi-ticker comparison

## Acknowledgments

- Original app by Streamlit team
- CrewAI integration by Agent 12
- Built with CrewAI framework
- Powered by OpenAI GPT-4

---

**Note**: This is an enhanced version of the original Streamlit demo. The original functionality remains unchanged and is available in `streamlit_app.py`.
