from crewai import Crew, Task
from agents import logistics_analyst, optimization_strategist
from tasks import logistics_analysis_task, route_optimization_task
from dotenv import load_dotenv
load_dotenv()

def create_optimization_crew(locations):
    """
    Create a logistics optimization crew for the given locations.
    
    Args:
        locations (list): List of location addresses to optimize routes for
    
    Returns:
        Crew: Configured crew for logistics optimization
    """
    locations_str = ', '.join(locations)
    analysis_task = Task(
        description=logistics_analysis_task.description + f"\n\nLocations: {locations_str}",
        agent=logistics_analyst,
        expected_output=logistics_analysis_task.expected_output
    )
    optimization_task = Task(
        description=route_optimization_task.description + f"\n\nLocations: {locations_str}",
        agent=optimization_strategist,
        expected_output=route_optimization_task.expected_output
    )
    crew = Crew(
        agents=[logistics_analyst, optimization_strategist],
        tasks=[analysis_task, optimization_task],
        verbose=True
    )
    return crew

def optimize_routes(locations):
    """
    Optimize routes for the given locations.
    
    Args:
        locations (list): List of location addresses
    
    Returns:
        dict: Optimization results
    """
    crew = create_optimization_crew(locations)
    result = crew.kickoff()
    return result

# Example usage
if __name__ == "__main__":
    # Example locations - replace with your actual locations
    sample_locations = [
        "MG Road, Bangalore, Karnataka",
        "Commercial Street, Bangalore, Karnataka",
        "Indiranagar, Bangalore, Karnataka",
        "Koramangala, Bangalore, Karnataka"
    ]
    
    print("Starting logistics optimization...")
    print(f"Optimizing routes for {len(sample_locations)} locations")
    
    result = optimize_routes(sample_locations)
    print("\nOptimization Complete!")
    print("Results:", result)