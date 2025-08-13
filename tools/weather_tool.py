from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class WeatherInput(BaseModel):
    location: str = Field(description="City or location to get weather for")

class WeatherTool(BaseTool):
    name: str = "Get Weather"
    description: str = "Get current weather information for a specific location"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, location: str) -> str:
        try:
            # Check if Serper API key is available
            api_key = os.getenv('SERPER_API_KEY')
            if not api_key:
                return f"Weather service not configured. Please set SERPER_API_KEY in .env file."
            
            # Use Serper API directly
            url = "https://google.serper.dev/search"
            headers = {
                'X-API-KEY': api_key,
                'Content-Type': 'application/json'
            }
            
            query = f"current weather in {location} temperature conditions forecast today"
            payload = {
                'q': query,
                'location': location,
                'num': 1
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract weather information from the response
                weather_info = []
                
                # Check for answer box (often contains weather info)
                if 'answerBox' in data:
                    answer = data['answerBox']
                    if 'answer' in answer:
                        weather_info.append(answer['answer'])
                    if 'snippet' in answer:
                        weather_info.append(answer['snippet'])
                
                # Check for knowledge graph (contains structured weather data)
                if 'knowledgeGraph' in data:
                    kg = data['knowledgeGraph']
                    if 'description' in kg:
                        weather_info.append(kg['description'])
                    if 'attributes' in kg:
                        for key, value in kg['attributes'].items():
                            weather_info.append(f"{key}: {value}")
                
                # Check organic results for weather info
                if 'organic' in data and data['organic']:
                    for result in data['organic'][:2]:
                        if 'snippet' in result:
                            weather_info.append(result['snippet'])
                
                if weather_info:
                    return f"Weather information for {location}:\n" + "\n".join(weather_info)
                else:
                    return f"Could not find specific weather information for {location}"
            else:
                return f"Error fetching weather data: HTTP {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return f"Network error getting weather: {str(e)}"
        except Exception as e:
            return f"Error getting weather: {str(e)}. Make sure SERPER_API_KEY is set in .env"