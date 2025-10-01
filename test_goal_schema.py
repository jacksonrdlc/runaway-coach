#!/usr/bin/env python3
"""
Test script to verify goal assessment schema matches iOS expectations
"""
import asyncio
import sys
sys.path.insert(0, '/Users/jack.rudelic/projects/labs/runaway/runaway-coach')

from core.agents.goal_strategy_agent import GoalStrategyAgent
from dataclasses import asdict
import json

async def test_goal_schema():
    """Test that goal assessment schema matches iOS expectations"""
    print("Testing goal assessment schema...")
    
    # Sample goal data
    goal_data = {
        "id": "test_goal_1",
        "type": "race_time",
        "target_value": "sub 20min 5K",
        "deadline": "2024-06-01"
    }
    
    # Sample activities data
    activities_data = [
        {
            "distance": 5000,  # 5km in meters
            "elapsed_time": 1200,  # 20 minutes in seconds
            "name": "Morning Run"
        },
        {
            "distance": 3000,  # 3km in meters
            "elapsed_time": 720,   # 12 minutes in seconds
            "name": "Easy Run"
        }
    ]
    
    # Test the agent
    agent = GoalStrategyAgent()
    
    try:
        assessments = await agent.assess_goals([goal_data], activities_data)
        
        if assessments:
            assessment = assessments[0]
            assessment_dict = asdict(assessment)
            
            print("✅ Goal assessment generated successfully")
            print(f"Assessment ID: {assessment.goal_id}")
            print(f"Progress: {assessment.progress_percentage}%")
            print(f"Status: {assessment.current_status}")
            
            # Check key_metrics schema
            key_metrics = assessment.key_metrics
            required_fields = ["current_pace", "target_pace", "weekly_mileage", "target_mileage"]
            
            print("\n🔍 Key Metrics Schema Check:")
            for field in required_fields:
                if field in key_metrics:
                    print(f"  ✅ {field}: {key_metrics[field]}")
                else:
                    print(f"  ❌ {field}: MISSING")
            
            print(f"\n📊 Full key_metrics: {json.dumps(key_metrics, indent=2)}")
            print(f"\n🎯 Sample recommendations: {assessment.recommendations[:2]}")
            
            # Test JSON serialization
            json_str = json.dumps(assessment_dict, indent=2)
            print(f"\n✅ JSON serialization successful (length: {len(json_str)} chars)")
            
        else:
            print("❌ No assessments generated")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_goal_schema())