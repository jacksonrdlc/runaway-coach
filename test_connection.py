"""
Test database connection and verify enhanced data model
"""
import asyncio
from integrations.supabase_client import SupabaseClient
from integrations.supabase_queries import SupabaseQueries

async def test_connection():
    print("🔍 Testing Supabase connection...\n")

    try:
        # Initialize client
        client = SupabaseClient()
        queries = client.queries

        # Test 1: Basic connection
        print("1️⃣ Testing basic connection...")
        result = client.client.table("athletes").select("id, first_name, last_name").limit(1).execute()
        if result.data:
            print(f"   ✅ Connected! Found athlete: {result.data[0].get('first_name')} {result.data[0].get('last_name')}")
        else:
            print("   ⚠️  No athletes found in database")

        # Test 2: Check athlete_stats
        print("\n2️⃣ Testing athlete_stats table...")
        stats_result = client.client.table("athlete_stats").select("athlete_id, count, distance").limit(1).execute()
        if stats_result.data:
            stats = stats_result.data[0]
            print(f"   ✅ Stats found: {stats.get('count')} activities, {float(stats.get('distance', 0))/1000:.1f}km")
        else:
            print("   ⚠️  No athlete stats found")

        # Test 3: Check activities with enhanced columns
        print("\n3️⃣ Testing activities with enhanced columns...")
        activities_result = client.client.table("activities").select(
            "id, distance, average_heart_rate, average_cadence, weather_condition"
        ).limit(1).execute()
        if activities_result.data:
            activity = activities_result.data[0]
            print(f"   ✅ Activity found:")
            print(f"      - Distance: {float(activity.get('distance', 0))/1000:.1f}km")
            print(f"      - HR: {activity.get('average_heart_rate', 'N/A')}")
            print(f"      - Cadence: {activity.get('average_cadence', 'N/A')}")
            print(f"      - Weather: {activity.get('weather_condition', 'N/A')}")
        else:
            print("   ⚠️  No activities found")

        # Test 4: Check running_goals
        print("\n4️⃣ Testing running_goals table...")
        goals_result = client.client.table("running_goals").select("id, title, goal_type, is_active").limit(1).execute()
        if goals_result.data:
            goal = goals_result.data[0]
            print(f"   ✅ Goal found: {goal.get('title')} ({goal.get('goal_type')})")
        else:
            print("   ℹ️  No running goals found (this is OK - goals can be created later)")

        # Test 5: Check gear
        print("\n5️⃣ Testing gear table...")
        gear_result = client.client.table("gear").select("id, name, gear_type, total_distance").limit(1).execute()
        if gear_result.data:
            gear = gear_result.data[0]
            miles = (float(gear.get('total_distance', 0)) / 1000) * 0.621371
            print(f"   ✅ Gear found: {gear.get('name')} ({gear.get('gear_type')}) - {miles:.0f} miles")
        else:
            print("   ℹ️  No gear found (this is OK - gear can be added later)")

        print("\n" + "="*60)
        print("✅ CONNECTION TEST SUCCESSFUL!")
        print("="*60)
        print("\n📊 Summary:")
        print(f"   - Database connection: ✅")
        print(f"   - Athletes table: ✅")
        print(f"   - Enhanced columns: ✅")
        print(f"   - All required tables: ✅")
        print("\n✨ You're ready to start the local server!")

    except Exception as e:
        print("\n" + "="*60)
        print("❌ CONNECTION TEST FAILED")
        print("="*60)
        print(f"\nError: {e}")
        print("\nPlease check:")
        print("  1. SUPABASE_URL is correct in .env")
        print("  2. SUPABASE_SERVICE_KEY is correct in .env")
        print("  3. Supabase project is running")
        print("  4. Network connection is available")

if __name__ == "__main__":
    asyncio.run(test_connection())