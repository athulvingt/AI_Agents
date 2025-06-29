# Logistics Route Optimization Agent with CrewAI

A comprehensive logistics optimization system that analyzes current operations and creates optimal travel plans with precise timing recommendations. The system uses two specialized AI agents working together to solve complex routing problems while considering real-time traffic conditions across all 24 hours of the day.

> **Note:**
> - **Google Maps API only provides traffic data for future and current times, not past times.**
> - The system automatically generates and uses only future time slots for traffic analysis. Any past time slots are skipped with a warning.
> - The tool can accept time slots as either Python `datetime` objects or as dictionaries (e.g., `{"hour": 5, "minute": 0}`), which are automatically converted to valid future datetimes.

## 🎯 System Overview

This system consists of two specialized agents:

1. **Senior Logistics Operations Analyst**: Conducts comprehensive 24-hour analysis of current logistics operations, traffic patterns, and route efficiency
2. **Strategic Route Optimization Specialist**: Creates optimal travel strategies using advanced algorithms to solve the Traveling Salesman Problem (TSP) with precise timing

## 🚀 Features

- **24-Hour Traffic Analysis**: Analyzes traffic patterns for every hour of the day (00:00-23:00)
- **Peak/Off-Peak Identification**: Automatically identifies peak and off-peak hours for optimal timing
- **Real-time Traffic Integration**: Uses Google Maps API for current traffic conditions
- **TSP Optimization**: Solves the Traveling Salesman Problem for optimal route sequencing
- **Precise Timing Optimization**: Recommends optimal departure times based on comprehensive hourly data
- **Traffic Pattern Classification**: Categorizes traffic into morning rush, midday, evening rush, and night periods
- **Comprehensive Reporting**: Provides detailed analysis and optimization results
- **Efficiency Metrics**: Calculates performance improvements and cost savings
- **Multiple Optimization Strategies**: Offers alternative routes with different timing approaches
- **Future-Only Traffic Analysis**: Ensures all traffic queries are for future or current times (never past)

## 📋 Requirements

- Python 3.8+
- Google Maps API key
- Required packages (see installation section)

## 🔧 Installation

1. Clone the repository:
```bash
git clone https://github.com/athulvingt/AI_Agents
cd 8.1-Route_optimization_agent_crewAI
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your Google Maps API key:
```bash
export GOOGLE_MAPS_API_KEY="your_api_key_here"
```

Or create a `.env` file:
```
GOOGLE_MAPS_API_KEY=your_api_key_here
```

## 🎯 Usage

### Basic Usage

```python
from crew import optimize_routes

# Define your locations
locations = [
    "123 Main St, New York, NY",
    "456 Broadway, New York, NY", 
    "789 5th Ave, New York, NY",
    "321 Park Ave, New York, NY"
]

# Run optimization with 24-hour analysis (uses only future time slots)
result = optimize_routes(locations)
print(result)
```

### Advanced Usage

```python
from crew import create_optimization_crew

# Create a custom crew
crew = create_optimization_crew(locations)

# (Context is now handled via task descriptions and tool input)
result = crew.kickoff()
```

## 🔍 How It Works

### Phase 1: 24-Hour Logistics Analysis
The **Senior Logistics Operations Analyst** performs:

1. **24-Hour Traffic Pattern Analysis**: Fetches travel time matrices for every hour (00:00-23:00)
2. **Peak and Off-Peak Hour Identification**: Analyzes which hours have highest/lowest traffic congestion
3. **Route Efficiency Assessment**: Analyzes current route efficiency across all time periods
4. **Operational Bottlenecks**: Identifies inefficiencies in current routing
5. **Time Window Optimization**: Determines optimal departure times based on comprehensive analysis
6. **Traffic Pattern Classification**: Categorizes traffic into morning rush, midday, evening rush, and night
7. **Congestion Analysis**: Calculates congestion ratios and travel time variations

### Phase 2: Strategic Route Optimization
The **Strategic Route Optimization Specialist** creates:

1. **TSP Solution**: Finds the most efficient route visiting each location once
2. **24-Hour Timing Optimization**: Uses complete hourly data for precise timing
3. **Peak/Off-Peak Leverage**: Utilizes identified optimal time windows
4. **Traffic Pattern Avoidance**: Plans routes around congestion periods
5. **Detailed Itinerary**: Creates step-by-step travel plan with exact timing
6. **Performance Metrics**: Calculates efficiency improvements and savings
7. **Alternative Strategies**: Offers multiple optimization approaches

## 🕒 Time Slot Handling & Limitations

- **Google Maps API Limitation:** Only future and current times are supported for traffic data. Past times are not allowed and will be skipped.
- **Automatic Future Slot Generation:**
  - By default, the tool generates 24 hourly time slots starting from the next hour (all in the future).
  - If you provide custom time slots, any in the past are skipped with a warning.
- **Flexible Input:**
  - You can provide time slots as Python `datetime` objects or as dicts like `{"hour": 8, "minute": 0}`. Dicts are automatically converted to valid future datetimes (using tomorrow as the base date).

### Example: Custom Time Slots

```python
from datetime import datetime
from tools.google_maps_tool import GoogleMapsTimeMatrixTool

# Custom time slots as dicts (will be converted to tomorrow's times)
custom_times = [
    {"hour": 7, "minute": 0},   # 7 AM tomorrow
    {"hour": 10, "minute": 0},  # 10 AM tomorrow
    {"hour": 15, "minute": 0},  # 3 PM tomorrow
    {"hour": 19, "minute": 0}   # 7 PM tomorrow
]

# Use with tool (hourly_analysis=False for custom times)
tool = GoogleMapsTimeMatrixTool(api_key="your_key")
results = tool._run(locations, time_slots=custom_times, hourly_analysis=False)
```

### Example: 24-Hour Future Analysis (Default)

```python
from tools.google_maps_tool import GoogleMapsTimeMatrixTool

tool = GoogleMapsTimeMatrixTool(api_key="your_key")
results = tool._run(locations)  # hourly_analysis=True by default, uses only future slots
```

## 🔧 Configuration

### Environment Variables

- `GOOGLE_MAPS_API_KEY`: Your Google Maps API key (required)
- `CREWAI_VERBOSE`: Set to "true" for detailed logging

### API Limits & Traffic Data Availability

- **Google Maps API only provides traffic data for future and current times.**
- Any request for a past time will be skipped and a warning will be printed.
- The tool automatically ensures all time slots are valid for the API.

## 📈 Performance Considerations

- **API Usage**: Each optimization uses 24 API calls (one per hour) × N locations
- **Processing Time**: Analysis time scales with number of locations
- **Rate Limiting**: Built-in delays prevent API quota exhaustion
- **Error Handling**: Robust error handling for network issues
- **Comprehensive Data**: 24-hour analysis provides much more accurate optimization

## 🎯 Key Benefits of 24-Hour Analysis

1. **Precise Timing**: Identifies exact optimal departure times for each location
2. **Peak Avoidance**: Automatically avoids peak congestion hours
3. **Off-Peak Utilization**: Leverages off-peak hours for faster travel
4. **Pattern Recognition**: Identifies traffic patterns across different time periods
5. **Multiple Strategies**: Offers alternative routes with different timing approaches
6. **Comprehensive Optimization**: Considers all possible timing scenarios

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## 🔮 Future Enhancements

- [ ] Multi-vehicle routing support
- [ ] Real-time traffic updates
- [ ] Integration with delivery management systems
- [ ] Machine learning-based traffic prediction
- [ ] Mobile app integration
- [ ] Weather condition consideration
- [ ] Fuel efficiency optimization
- [ ] Historical traffic pattern analysis
- [ ] Weekend vs weekday traffic differentiation 