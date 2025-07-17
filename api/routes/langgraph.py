from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging

from ..main import get_current_user

router = APIRouter(prefix="/langgraph", tags=["langgraph"])
logger = logging.getLogger(__name__)

# Lazy initialization of workflow to improve startup time
_workflow: Optional[object] = None

def get_workflow():
    """Lazy initialization of RunnerAnalysisWorkflow"""
    global _workflow
    if _workflow is None:
        try:
            from ...core.workflows.runner_analysis_workflow import RunnerAnalysisWorkflow
            _workflow = RunnerAnalysisWorkflow()
            logger.info("LangGraph workflow initialized")
        except Exception as e:
            logger.error(f"Failed to initialize LangGraph workflow: {e}")
            raise HTTPException(status_code=500, detail="LangGraph workflow initialization failed")
    return _workflow

@router.get("/graph")
async def get_workflow_graph(current_user: dict = Depends(get_current_user)):
    """
    Get the LangGraph workflow visualization as a Mermaid diagram
    
    This endpoint returns the workflow graph that shows how the AI agents
    are connected and the flow of data between them.
    """
    try:
        workflow = get_workflow()
        mermaid_graph = workflow.get_workflow_graph()
        
        return {
            "success": True,
            "graph": {
                "format": "mermaid",
                "diagram": mermaid_graph,
                "description": "Runner analysis workflow showing agent connections and data flow"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow graph: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate graph: {str(e)}")

@router.get("/graph/html")
async def get_workflow_graph_html(current_user: dict = Depends(get_current_user)):
    """
    Get the LangGraph workflow as an HTML page with Mermaid rendering
    
    Returns an HTML page that renders the workflow graph using Mermaid.js
    """
    try:
        workflow = get_workflow()
        mermaid_graph = workflow.get_workflow_graph()
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Runaway Coach - LangGraph Workflow</title>
            <script src="https://unpkg.com/mermaid@10/dist/mermaid.min.js"></script>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .description {{
                    background-color: #e3f2fd;
                    padding: 15px;
                    border-radius: 5px;
                    margin-bottom: 20px;
                    border-left: 4px solid #2196f3;
                }}
                .graph-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .node-info {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🏃‍♂️ Runaway Coach - LangGraph Workflow</h1>
                
                <div class="description">
                    <h3>AI Agent Workflow</h3>
                    <p>This diagram shows how the AI agents work together to analyze your running data:</p>
                    <ul>
                        <li><strong>Performance Analysis</strong>: Analyzes your running metrics and trends</li>
                        <li><strong>Goal Assessment</strong>: Evaluates your goals and progress</li>
                        <li><strong>Pace Optimization</strong>: Recommends optimal paces for different training zones</li>
                        <li><strong>Workout Planning</strong>: Creates personalized workout recommendations</li>
                        <li><strong>Final Synthesis</strong>: Combines all analyses into comprehensive insights</li>
                    </ul>
                </div>
                
                <div class="graph-container">
                    <div class="mermaid">
                        {mermaid_graph}
                    </div>
                </div>
                
                <div class="node-info">
                    <h3>🔍 How to Use This Visualization</h3>
                    <p>Each node represents an AI agent that processes your running data. The arrows show the flow of information from one agent to the next. This helps you understand how your analysis is built step by step.</p>
                    
                    <h4>🔗 API Integration</h4>
                    <p>Use <code>POST /analysis/runner</code> to trigger this workflow and get comprehensive running analysis.</p>
                </div>
            </div>
            
            <script>
                mermaid.initialize({{ 
                    startOnLoad: true,
                    theme: 'default',
                    flowchart: {{
                        useMaxWidth: true,
                        htmlLabels: true
                    }}
                }});
            </script>
        </body>
        </html>
        """
        
        from fastapi.responses import HTMLResponse
        return HTMLResponse(content=html_content)
        
    except Exception as e:
        logger.error(f"Failed to generate HTML graph: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate HTML graph: {str(e)}")

@router.get("/schema")
async def get_workflow_schema(current_user: dict = Depends(get_current_user)):
    """
    Get the LangGraph workflow state schema
    
    Returns the structure of data that flows through the workflow nodes.
    """
    try:
        workflow = get_workflow()
        schema = workflow.get_workflow_state_schema()
        
        return {
            "success": True,
            "schema": schema,
            "description": "Data structure that flows through the LangGraph workflow nodes"
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow schema: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")

@router.get("/info")
async def get_workflow_info(current_user: dict = Depends(get_current_user)):
    """
    Get information about the LangGraph workflow
    
    Returns metadata about the workflow including nodes, edges, and capabilities.
    """
    try:
        return {
            "success": True,
            "workflow_info": {
                "name": "Runner Analysis Workflow",
                "version": "1.0",
                "description": "AI-powered workflow for comprehensive running analysis",
                "nodes": [
                    {
                        "name": "performance_analysis",
                        "description": "Analyzes running performance metrics and trends",
                        "agent": "PerformanceAnalysisAgent"
                    },
                    {
                        "name": "goal_assessment", 
                        "description": "Evaluates goal feasibility and progress",
                        "agent": "GoalStrategyAgent"
                    },
                    {
                        "name": "pace_optimization",
                        "description": "Optimizes paces for different training zones", 
                        "agent": "PaceOptimizationAgent"
                    },
                    {
                        "name": "workout_planning",
                        "description": "Creates personalized workout recommendations",
                        "agent": "WorkoutPlanningAgent"
                    },
                    {
                        "name": "final_synthesis",
                        "description": "Combines all analyses into final insights",
                        "agent": "WorkflowSynthesis"
                    }
                ],
                "flow": "performance_analysis → goal_assessment → pace_optimization → workout_planning → final_synthesis",
                "features": [
                    "Visual workflow debugging",
                    "State management between agents",
                    "Parallel processing capabilities",
                    "Error handling and recovery",
                    "Processing time tracking"
                ]
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get workflow info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get workflow info: {str(e)}")