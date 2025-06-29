from crewai import Task
from agents import logistics_analyst, optimization_strategist

# Task 1: Comprehensive Logistics Analysis
logistics_analysis_task = Task(
    description=(
        "Conduct a comprehensive analysis of the current logistics operations for the provided locations. "
        "Your analysis should include:\n"
        "1. **24-Hour Traffic Pattern Analysis**: Use Google Maps tool to fetch travel time matrices for every hour of the day "
        "(00:00 to 23:00) to understand complete traffic patterns and identify optimal time windows\n"
        "2. **Peak and Off-Peak Hour Identification**: Analyze which hours have the highest and lowest traffic congestion\n"
        "3. **Route Efficiency Assessment**: Analyze the current state of route efficiency between all location pairs across different times\n"
        "4. **Operational Bottlenecks**: Identify potential bottlenecks and inefficiencies in the current routing approach\n"
        "5. **Time Window Optimization**: Determine optimal departure times for each location based on comprehensive traffic analysis\n"
        "6. **Traffic Pattern Insights**: Provide detailed insights about traffic patterns, including morning rush, midday, evening rush, and night periods\n"
        "7. **Congestion Analysis**: Calculate congestion ratios, travel time variations, and optimal time windows for different activities\n\n"
        "Input: List of locations (addresses)\n"
        "Output: Comprehensive 24-hour traffic analysis report including hourly matrices, efficiency metrics, and optimization recommendations"
    ),
    agent=logistics_analyst,
    expected_output=(
        "Detailed 24-hour logistics analysis report containing:\n"
        "- Complete hourly traffic time matrices (00:00-23:00)\n"
        "- Peak and off-peak hour identification\n"
        "- Traffic patterns by time period (morning rush, midday, evening rush, night)\n"
        "- Current route efficiency metrics across all hours\n"
        "- Identified bottlenecks and inefficiencies\n"
        "- Optimal departure time recommendations for each location\n"
        "- Comprehensive traffic pattern insights and congestion analysis\n"
        "- Best and worst time windows for travel"
    )
)

# Task 2: Strategic Route Optimization
route_optimization_task = Task(
    description=(
        "Based on the comprehensive 24-hour logistics analysis provided, create an optimal travel strategy that:\n"
        "1. **Solves the Traveling Salesman Problem (TSP)**: Find the most efficient route that visits each location exactly once and returns to the starting point\n"
        "2. **Incorporates 24-Hour Timing Optimization**: Use the complete hourly traffic analysis to determine the optimal departure time from each location\n"
        "3. **Leverages Peak/Off-Peak Insights**: Utilize the identified peak and off-peak hours to avoid congestion and optimize travel times\n"
        "4. **Considers Traffic Dynamics**: Use the detailed traffic pattern analysis to plan routes around morning rush, midday, evening rush, and night periods\n"
        "5. **Provides Detailed Travel Plan**: Create a step-by-step travel itinerary with precise timing recommendations based on hourly data\n"
        "6. **Calculates Performance Metrics**: Provide total travel time, efficiency improvements, and cost savings compared to non-optimized routes\n"
        "7. **Offers Multiple Optimization Strategies**: Consider different starting times and provide alternative optimal routes\n\n"
        "Use advanced optimization algorithms to solve the TSP while incorporating the comprehensive 24-hour traffic constraints. "
        "Consider multiple starting points and evaluate which provides the best overall solution based on the detailed hourly analysis.\n\n"
        "Input: Comprehensive 24-hour logistics analysis from the Logistics Analyst\n"
        "Output: Complete optimized travel plan with precise timing recommendations based on hourly traffic patterns"
    ),
    agent=optimization_strategist,
    expected_output=(
        "Complete optimized travel plan including:\n"
        "- Optimal route sequence (TSP solution) based on 24-hour traffic analysis\n"
        "- Precise departure time recommendations for each location using hourly data\n"
        "- Total estimated travel time with traffic considerations\n"
        "- Step-by-step itinerary with exact timing based on peak/off-peak analysis\n"
        "- Performance metrics and efficiency gains compared to non-optimized routes\n"
        "- Alternative route options with different timing strategies\n"
        "- Traffic avoidance recommendations for each leg of the journey"
    )
)