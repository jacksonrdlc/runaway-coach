#!/usr/bin/env python3
"""
Visualize LangGraph workflow as Mermaid diagram

This script generates a Mermaid diagram showing the flow of agents
in the Runaway Coach analysis workflow.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.workflows.runner_analysis_workflow import RunnerAnalysisWorkflow
from core.workflows.enhanced_runner_analysis_workflow import EnhancedRunnerAnalysisWorkflow


def generate_manual_diagram():
    """Generate manual Mermaid diagram for the workflow"""
    return """graph TD
    START([Start]) --> PERF[Performance Analysis]

    PERF --> WEATHER[Weather Context]
    PERF --> VO2MAX[VO2 Max Estimation]
    PERF --> LOAD[Training Load]
    PERF --> GOAL[Goal Assessment]

    WEATHER --> PACE[Pace Optimization]
    VO2MAX --> PACE
    LOAD --> PACE
    GOAL --> PACE

    PACE --> WORKOUT[Workout Planning]
    WORKOUT --> SYNTH[Final Synthesis]
    SYNTH --> END([End])

    style PERF fill:#3B82F6,color:#fff
    style WEATHER fill:#F59E0B,color:#fff
    style VO2MAX fill:#8B5CF6,color:#fff
    style LOAD fill:#EF4444,color:#fff
    style GOAL fill:#10B981,color:#fff
    style PACE fill:#EC4899,color:#fff
    style WORKOUT fill:#6366F1,color:#fff
    style SYNTH fill:#14B8A6,color:#fff
"""


def save_mermaid_diagram(mermaid_code: str, filename: str):
    """Save Mermaid diagram to file"""
    output_path = Path(__file__).parent.parent / filename

    with open(output_path, 'w') as f:
        f.write("# Workflow Diagram\n\n")
        f.write("```mermaid\n")
        f.write(mermaid_code)
        f.write("\n```\n")

    print(f"✅ Diagram saved to: {output_path}")
    return output_path


def visualize_runner_workflow():
    """Generate diagram for main runner analysis workflow"""
    print("🔍 Generating Runner Analysis Workflow diagram...")

    workflow = RunnerAnalysisWorkflow()

    # Get the compiled app and generate Mermaid diagram
    try:
        mermaid_code = workflow.app.get_graph().draw_mermaid()
    except Exception as e:
        print(f"⚠️  Warning: {e}")
        print("Generating manual diagram instead...")
        mermaid_code = generate_manual_diagram()

    output_path = save_mermaid_diagram(mermaid_code, "WORKFLOW_DIAGRAM.md")

    print("\n📊 Workflow Steps:")
    print("1. Performance Analysis")
    print("2. Goal Assessment")
    print("3. Pace Optimization")
    print("4. Workout Planning")
    print("5. Weather Context")
    print("6. VO2 Max Estimation")
    print("7. Training Load Analysis")
    print("8. Final Synthesis")

    return output_path


def visualize_enhanced_workflow():
    """Generate diagram for enhanced workflow"""
    print("\n🔍 Generating Enhanced Workflow diagram...")

    # Import here to avoid circular imports
    from integrations.supabase_client import SupabaseClient

    supabase_client = SupabaseClient()
    workflow = EnhancedRunnerAnalysisWorkflow(supabase_queries=supabase_client.queries)

    # Enhanced workflow uses get_graph() directly
    try:
        mermaid_code = workflow.workflow.get_graph().draw_mermaid()
        output_path = save_mermaid_diagram(mermaid_code, "ENHANCED_WORKFLOW_DIAGRAM.md")

        print("\n📊 Enhanced Workflow Features:")
        print("✅ Full Strava data integration")
        print("✅ Goal auto-progress tracking")
        print("✅ Gear rotation recommendations")
        print("✅ Segment suggestions")

        return output_path
    except Exception as e:
        print(f"❌ Error generating enhanced workflow diagram: {e}")
        return None


def main():
    """Main entry point"""
    print("=" * 60)
    print("🏃 Runaway Coach - Workflow Visualization")
    print("=" * 60)
    print()

    # Generate main workflow diagram
    workflow_path = visualize_runner_workflow()

    # Generate enhanced workflow diagram
    enhanced_path = visualize_enhanced_workflow()

    print("\n" + "=" * 60)
    print("✅ Visualization Complete!")
    print("=" * 60)
    print("\nGenerated files:")
    print(f"  1. {workflow_path.name}")
    if enhanced_path:
        print(f"  2. {enhanced_path.name}")

    print("\n📝 To view diagrams:")
    print("  • Open in VS Code with Mermaid extension")
    print("  • Paste into https://mermaid.live")
    print("  • View on GitHub (renders Mermaid automatically)")
    print()


if __name__ == "__main__":
    main()
