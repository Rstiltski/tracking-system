"""
Job Actuals Tools - Calculate and update actual costs for completed jobs.

These tools handle the calculation of actual hours, materials costs, and variance
analysis for jobs, providing visibility into profitability and performance.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_TOOLS_REFERENCE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any
from brain.core.tool import Tool, ToolInput
from brain.core.result import ToolOutput
import db

@dataclass
class CalculateJobActualsInput(ToolInput):
    """Input for calculating job actuals."""
    job_id: int

class CalculateJobActualsTool(Tool):
    """
    Calculate and update actual costs for a completed job.
    
    This tool:
    1. Calculates actual hours from time entries
    2. Calculates actual materials cost from job_materials
    3. Calculates actual travel time
    4. Performs variance analysis (actual vs estimate)
    5. Updates job record with calculated values
    6. Updates job type averages
    
    Risk Tier: LOW (read-heavy calculation, updates only financial tracking fields)
    """

    @property
    def input_schema(self):
        return CalculateJobActualsInput

    def execute(self, input_data: CalculateJobActualsInput) -> ToolOutput:
        """
        Execute job actuals calculation.
        
        Args:
            input_data: CalculateJobActualsInput with job_id
            
        Returns:
            ToolOutput with calculated actuals
        """
        try:
            job_id = input_data.job_id
            job = db.get_job(job_id, company_id=input_data.company_id)
            if not job:
                return ToolOutput(success=False, error_code='JOB_NOT_FOUND', error_message=f'Job {job_id} not found')
            with db.get_conn() as conn:
                time_result = conn.execute('\n                    SELECT SUM(hours_worked) as total_hours\n                    FROM time_entries\n                    WHERE job_id = ? AND clock_out IS NOT NULL\n                ', (job_id,)).fetchone()
                actual_hours = float(time_result.get('total_hours', 0) or 0) if time_result else 0.0
                materials_result = conn.execute('\n                    SELECT SUM(quantity * unit_cost) as total_cost\n                    FROM job_materials\n                    WHERE job_id = ?\n                ', (job_id,)).fetchone()
                actual_materials_cost = float(materials_result.get('total_cost', 0) or 0) if materials_result else 0.0
                travel_result = conn.execute("\n                    SELECT SUM(hours_worked) as travel_hours\n                    FROM time_entries\n                    WHERE job_id = ? AND time_type = 'travel' AND clock_out IS NOT NULL\n                ", (job_id,)).fetchone()
                actual_travel_time = float(travel_result.get('travel_hours', 0) or 0) if travel_result else 0.0
                estimated_hours = float(job.get('estimated_hours', 0) if job else 0)
                estimated_materials_cost = float(job.get('estimated_materials_cost', 0) if job else 0)
                estimated_total = estimated_hours + estimated_materials_cost
                actual_total = actual_hours + actual_materials_cost
                quoted_price = float(job.get('quoted_price', 0) if job else 0)
                variance_percent = 0.0
                estimated_profit = 0.0
                actual_profit = 0.0
                if quoted_price > 0:
                    estimated_profit = quoted_price - estimated_total
                    actual_profit = quoted_price - actual_total
                    if estimated_profit != 0:
                        variance_percent = (actual_profit - estimated_profit) / estimated_profit * 100
                conn.execute('\n                    UPDATE jobs\n                    SET actual_hours = ?,\n                        actual_materials_cost = ?,\n                        actual_travel_time = ?,\n                        variance_percent = ?,\n                        updated_at = CURRENT_TIMESTAMP\n                    WHERE id = ?\n                ', (actual_hours, actual_materials_cost, actual_travel_time, variance_percent, job_id))
            if job.get('job_type', '') if job else '':
                db.recalculate_job_type_averages(job.get('job_type', 0) if job else 0)
            return ToolOutput(success=True, data={'job_id': job_id, 'actual_hours': actual_hours, 'actual_materials_cost': actual_materials_cost, 'actual_travel_time': actual_travel_time, 'actual_total_cost': actual_total, 'estimated_hours': estimated_hours, 'estimated_materials_cost': estimated_materials_cost, 'estimated_total_cost': estimated_total, 'quoted_price': quoted_price, 'estimated_profit': estimated_profit, 'actual_profit': actual_profit, 'variance_percent': variance_percent})
        except Exception as e:
            return ToolOutput(success=False, error_code='CALCULATION_ERROR', error_message=f'Failed to calculate job actuals: {str(e)}')
