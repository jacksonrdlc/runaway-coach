"""
Simple test for database connection
"""
import os
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("🔍 Testing Supabase connection...\n")

try:
    # Get credentials
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_KEY")

    if not url or not key:
        print("❌ Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env file")
        exit(1)

    print(f"📍 Connecting to: {url[:30]}...")

    # Create client
    client = create_client(url, key)

    # Test 1: Athletes
    print("\n1️⃣ Testing athletes table...")
    result = client.table("athletes").select("id, first_name, last_name").limit(1).execute()
    if result.data:
        athlete = result.data[0]
        print(f"   ✅ Found athlete: {athlete.get('first_name')} {athlete.get('last_name')} (ID: {athlete.get('id')})")
    else:
        print("   ⚠️  No athletes found")

    # Test 2: Athlete Stats
    print("\n2️⃣ Testing athlete_stats table...")
    stats_result = client.table("athlete_stats").select("athlete_id, count, distance").limit(1).execute()
    if stats_result.data:
        stats = stats_result.data[0]
        distance_km = float(stats.get('distance', 0)) / 1000
        print(f"   ✅ Stats found for athlete {stats.get('athlete_id')}: {stats.get('count')} activities, {distance_km:.1f}km")
    else:
        print("   ⚠️  No stats found")

    # Test 3: Activities with enhanced columns
    print("\n3️⃣ Testing activities table...")
    activities = client.table("activities").select(
        "id, distance, average_heart_rate, average_cadence, weather_condition, elevation_gain"
    ).limit(1).execute()
    if activities.data:
        activity = activities.data[0]
        print(f"   ✅ Activity found (ID: {activity.get('id')}):")
        print(f"      - Distance: {float(activity.get('distance', 0))/1000:.2f}km")
        print(f"      - Avg HR: {activity.get('average_heart_rate') or 'N/A'}")
        print(f"      - Avg Cadence: {activity.get('average_cadence') or 'N/A'}")
        print(f"      - Weather: {activity.get('weather_condition') or 'N/A'}")
        print(f"      - Elevation: {activity.get('elevation_gain') or 'N/A'}m")
    else:
        print("   ⚠️  No activities found")

    # Test 4: Running Goals
    print("\n4️⃣ Testing running_goals table...")
    goals = client.table("running_goals").select("id, title, goal_type, is_active").limit(1).execute()
    if goals.data:
        goal = goals.data[0]
        print(f"   ✅ Goal found: '{goal.get('title')}' ({goal.get('goal_type')})")
    else:
        print("   ℹ️  No running goals yet (can be created via API)")

    # Test 5: Gear
    print("\n5️⃣ Testing gear table...")
    gear = client.table("gear").select("id, name, gear_type, total_distance").limit(1).execute()
    if gear.data:
        gear_item = gear.data[0]
        miles = (float(gear_item.get('total_distance', 0)) / 1000) * 0.621371
        print(f"   ✅ Gear found: {gear_item.get('name')} ({gear_item.get('gear_type')}) - {miles:.0f} miles")
    else:
        print("   ℹ️  No gear found yet")

    print("\n" + "="*60)
    print("✅ CONNECTION TEST SUCCESSFUL!")
    print("="*60)
    print("\n📊 Database is ready for enhanced features:")
    print("   ✅ All tables exist")
    print("   ✅ Enhanced columns available")
    print("   ✅ Connection working")
    print("\n✨ Next step: Start the local server")

except Exception as e:
    print("\n" + "="*60)
    print("❌ CONNECTION TEST FAILED")
    print("="*60)
    print(f"\n🔴 Error: {e}")
    print("\n🔧 Troubleshooting:")
    print("  1. Check .env file exists in project root")
    print("  2. Verify SUPABASE_URL is correct")
    print("  3. Verify SUPABASE_SERVICE_KEY is correct")
    print("  4. Ensure Supabase project is active")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()