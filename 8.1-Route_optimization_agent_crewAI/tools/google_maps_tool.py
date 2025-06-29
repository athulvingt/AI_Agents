import googlemaps
from datetime import datetime, timedelta
from crewai.tools import BaseTool
import time
from typing import Optional, List, Dict, Any
from pydantic import Field

class GoogleMapsTimeMatrixTool(BaseTool):
    name: str = "Google Maps Distance Matrix Tool"
    description: str = "Fetches comprehensive travel time matrices using Google Maps Distance Matrix API for future time slots to analyze detailed traffic patterns. Note: Google Maps only provides traffic data for future and current times, not past times."
    client: Optional[googlemaps.Client] = Field(default=None, exclude=True)

    def __init__(self, api_key: str):
        super().__init__()
        self.client = googlemaps.Client(key=api_key)

    def _run(self, locations: List[str], time_slots: Optional[List[Any]] = None, hourly_analysis: bool = True) -> Dict[str, Any]:
        """
        Fetch travel time matrices for comprehensive time analysis.
        
        Args:
            locations: list of addresses
            time_slots: list of specific time slots to analyze (optional) - can be datetime objects or dicts with hour/minute
            hourly_analysis: if True, analyze every hour of the day (default: True)
        
        Returns:
            dict: Comprehensive traffic analysis with matrices for each time slot
        """
        current_time = datetime.now()
        
        # Convert time_slots to proper datetime objects if they're passed as dicts
        if time_slots is not None:
            converted_time_slots = []
            for slot in time_slots:
                if isinstance(slot, dict) and 'hour' in slot:
                    # Convert dict format to datetime
                    hour = slot.get('hour', 0)
                    minute = slot.get('minute', 0)
                    # Use tomorrow as base date to ensure future times
                    tomorrow = current_time + timedelta(days=1)
                    converted_slot = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    converted_time_slots.append(converted_slot)
                elif isinstance(slot, datetime):
                    converted_time_slots.append(slot)
                else:
                    print(f"Warning: Skipping invalid time slot format: {slot}")
            time_slots = converted_time_slots
        
        if time_slots is None and hourly_analysis:
            # Generate hourly time slots for the next 24 hours starting from current time
            time_slots = []
            
            # Start from the next hour to ensure all times are in the future
            start_hour = current_time.hour + 1
            if start_hour >= 24:
                start_hour = 0
                # Move to next day
                tomorrow = current_time + timedelta(days=1)
                base_date = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                base_date = current_time.replace(hour=start_hour, minute=0, second=0, microsecond=0)
            
            # Create time slots for the next 24 hours
            for i in range(24):
                time_slot = base_date + timedelta(hours=i)
                time_slots.append(time_slot)
            
            print(f"Analyzing traffic patterns for the next 24 hours starting from {base_date.strftime('%I:%M %p')}...")
        elif time_slots is None:
            # Default time slots: next 3 key times (morning, afternoon, evening)
            tomorrow = current_time + timedelta(days=1)
            time_slots = [
                tomorrow.replace(hour=8, minute=0, second=0, microsecond=0),   # 8 AM tomorrow
                tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),  # 12 PM tomorrow
                tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)   # 5 PM tomorrow
            ]
            print(f"Analyzing traffic patterns for 3 key time slots tomorrow...")
        else:
            # Filter out past time slots and warn user
            future_time_slots = []
            for time_slot in time_slots:
                if time_slot > current_time:
                    future_time_slots.append(time_slot)
                else:
                    print(f"Warning: Skipping past time slot {time_slot.strftime('%I:%M %p')} - Google Maps only provides future traffic data")
            
            if not future_time_slots:
                print("No future time slots provided. Generating default future time slots...")
                tomorrow = current_time + timedelta(days=1)
                time_slots = [
                    tomorrow.replace(hour=8, minute=0, second=0, microsecond=0),
                    tomorrow.replace(hour=12, minute=0, second=0, microsecond=0),
                    tomorrow.replace(hour=17, minute=0, second=0, microsecond=0)
                ]
            else:
                time_slots = future_time_slots
        
        analysis_results = {}
        
        for i, time_slot in enumerate(time_slots):
            time_key = time_slot.strftime("%I:%M %p, %b %d")
            unix_timestamp = int(time_slot.timestamp())
            
            print(f"Fetching traffic data for {time_key} ({i+1}/{len(time_slots)})...")
            
            matrix = self._get_time_matrix(locations, unix_timestamp)
            analysis_results[time_key] = {
                'matrix': matrix,
                'timestamp': unix_timestamp,
                'datetime': time_slot.isoformat(),
                'hour': time_slot.hour,
                'is_future': time_slot > current_time
            }
            
            # Rate limiting to avoid API quota issues
            time.sleep(1)
        
        # Calculate comprehensive efficiency metrics
        efficiency_metrics = self._calculate_comprehensive_efficiency_metrics(analysis_results, locations)
        analysis_results['efficiency_metrics'] = efficiency_metrics
        
        return analysis_results
    
    def _get_time_matrix(self, locations: List[str], departure_time: int) -> List[List[Dict[str, Any]]]:
        """Get travel time matrix for a specific departure time."""
        matrix = []
        current_timestamp = int(datetime.now().timestamp())
        
        # Check if departure time is in the past
        if departure_time < current_timestamp:
            print(f"Warning: Departure time {datetime.fromtimestamp(departure_time).strftime('%I:%M %p, %b %d')} is in the past. Skipping this time slot.")
            # Return empty matrix for past times
            return [[{'error': 'Past time - no traffic data available', 'duration_seconds': 0, 'duration_minutes': 0, 'distance_meters': 0, 'distance_km': 0} for _ in locations] for _ in locations]
        
        for origin in locations:
            try:
                result = self.client.distance_matrix(
                    origins=[origin],
                    destinations=locations,
                    departure_time=departure_time,
                    traffic_model='best_guess',
                    mode='driving'
                )
                
                row = []
                for element in result['rows'][0]['elements']:
                    if element['status'] == 'OK':
                        # Get duration in traffic (seconds)
                        duration = element.get('duration_in_traffic', {}).get('value', 0)
                        # Get distance (meters)
                        distance = element.get('distance', {}).get('value', 0)
                        row.append({
                            'duration_seconds': duration,
                            'duration_minutes': round(duration / 60, 1),
                            'distance_meters': distance,
                            'distance_km': round(distance / 1000, 2)
                        })
                    else:
                        row.append({
                            'duration_seconds': 0,
                            'duration_minutes': 0,
                            'distance_meters': 0,
                            'distance_km': 0,
                            'status': element['status']
                        })
                matrix.append(row)
                
            except Exception as e:
                error_msg = str(e)
                if "departure_time is in the past" in error_msg:
                    print(f"Error: {error_msg}")
                    # Return empty matrix for past times
                    error_row = [{'error': 'Past time - no traffic data available', 'duration_seconds': 0, 'duration_minutes': 0, 'distance_meters': 0, 'distance_km': 0} for _ in locations]
                else:
                    print(f"Error fetching data for origin {origin}: {error_msg}")
                    error_row = [{'error': error_msg, 'duration_seconds': 0, 'duration_minutes': 0, 'distance_meters': 0, 'distance_km': 0} for _ in locations]
                matrix.append(error_row)
        
        return matrix
    
    def _calculate_comprehensive_efficiency_metrics(self, analysis_results: Dict[str, Any], locations: List[str]) -> Dict[str, Any]:
        """Calculate comprehensive efficiency metrics across all time slots."""
        metrics = {
            'total_locations': len(locations),
            'time_slots_analyzed': len([k for k in analysis_results.keys() if k != 'efficiency_metrics']),
            'hourly_travel_times': {},
            'peak_hours': {},
            'off_peak_hours': {},
            'traffic_patterns': {},
            'optimal_time_windows': {},
            'congestion_analysis': {}
        }
        
        # Calculate average travel times for each hour
        hourly_data = {}
        for time_slot, data in analysis_results.items():
            if time_slot == 'efficiency_metrics':
                continue
                
            hour = data['hour']
            matrix = data['matrix']
            total_time = 0
            valid_entries = 0
            
            for row in matrix:
                for cell in row:
                    if isinstance(cell, dict) and 'duration_seconds' in cell:
                        total_time += cell['duration_seconds']
                        valid_entries += 1
            
            if valid_entries > 0:
                avg_time = total_time / valid_entries
                hourly_data[hour] = {
                    'avg_seconds': round(avg_time, 0),
                    'avg_minutes': round(avg_time / 60, 1),
                    'time_slot': time_slot
                }
        
        metrics['hourly_travel_times'] = hourly_data
        
        # Identify peak and off-peak hours
        if hourly_data:
            # Sort by average travel time
            sorted_hours = sorted(hourly_data.items(), key=lambda x: x[1]['avg_seconds'])
            
            # Peak hours (top 25% most congested)
            peak_count = max(1, len(sorted_hours) // 4)
            metrics['peak_hours'] = {
                'hours': [item[0] for item in sorted_hours[-peak_count:]],
                'avg_travel_time_minutes': round(sum(item[1]['avg_seconds'] for item in sorted_hours[-peak_count:]) / (peak_count * 60), 1)
            }
            
            # Off-peak hours (bottom 25% least congested)
            metrics['off_peak_hours'] = {
                'hours': [item[0] for item in sorted_hours[:peak_count]],
                'avg_travel_time_minutes': round(sum(item[1]['avg_seconds'] for item in sorted_hours[:peak_count]) / (peak_count * 60), 1)
            }
            
            # Traffic patterns by time of day
            morning_rush = [h for h in range(7, 10)]  # 7-9 AM
            evening_rush = [h for h in range(17, 20)]  # 5-7 PM
            midday = [h for h in range(10, 17)]  # 10 AM - 4 PM
            night = [h for h in range(20, 24)] + [h for h in range(0, 7)]  # 8 PM - 6 AM
            
            metrics['traffic_patterns'] = {
                'morning_rush': {
                    'hours': morning_rush,
                    'avg_travel_time_minutes': self._calculate_period_avg(hourly_data, morning_rush)
                },
                'midday': {
                    'hours': midday,
                    'avg_travel_time_minutes': self._calculate_period_avg(hourly_data, midday)
                },
                'evening_rush': {
                    'hours': evening_rush,
                    'avg_travel_time_minutes': self._calculate_period_avg(hourly_data, evening_rush)
                },
                'night': {
                    'hours': night,
                    'avg_travel_time_minutes': self._calculate_period_avg(hourly_data, night)
                }
            }
            
            # Optimal time windows for different activities
            metrics['optimal_time_windows'] = {
                'best_start_time': sorted_hours[0][1]['time_slot'],
                'worst_start_time': sorted_hours[-1][1]['time_slot'],
                'best_hours': [item[0] for item in sorted_hours[:3]],  # Top 3 best hours
                'worst_hours': [item[0] for item in sorted_hours[-3:]]  # Top 3 worst hours
            }
            
            # Congestion analysis
            all_times = [item[1]['avg_seconds'] for item in sorted_hours]
            metrics['congestion_analysis'] = {
                'min_travel_time_minutes': round(min(all_times) / 60, 1),
                'max_travel_time_minutes': round(max(all_times) / 60, 1),
                'avg_travel_time_minutes': round(sum(all_times) / len(all_times) / 60, 1),
                'congestion_variation_minutes': round((max(all_times) - min(all_times)) / 60, 1),
                'congestion_ratio': round(max(all_times) / min(all_times), 2) if min(all_times) > 0 else 0
            }
        
        return metrics
    
    def _calculate_period_avg(self, hourly_data: Dict[int, Dict[str, Any]], hours: List[int]) -> float:
        """Calculate average travel time for a specific period."""
        period_times = []
        for hour in hours:
            if hour in hourly_data:
                period_times.append(hourly_data[hour]['avg_seconds'])
        
        if period_times:
            return round(sum(period_times) / len(period_times) / 60, 1)
        return 0