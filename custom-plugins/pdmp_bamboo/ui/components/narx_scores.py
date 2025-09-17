"""
NarxCare Scores Component

Displays NarxCare risk scores from PDMP responses.
"""

from typing import Dict, Any, List, Optional
from logger import log


class NarxScoresComponent:
    """Component for displaying NarxCare scores."""
    
    def create_component(self, parsed_data: Dict[str, Any]) -> Optional[str]:
        """
        Create NarxCare scores component.
        
        Args:
            parsed_data: Parsed PDMP response data
            
        Returns:
            HTML string for scores display, or None if no scores
        """
        if not parsed_data.get("parsed") or not parsed_data.get("narx_scores"):
            return None
        
        scores = parsed_data["narx_scores"]
        log.info(f"NarxScoresComponent: Creating scores component with {len(scores)} scores")
        
        return self._build_scores_html(scores)
    
    def _build_scores_html(self, scores: List[Dict[str, Any]]) -> str:
        """Build HTML for displaying NarxCare scores."""
        scores_html = ""
        for score in scores:
            scores_html += self._build_score_item(score)
        
        return f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 4px; margin: 15px 0; border: 1px solid #dee2e6;">
            <h4 style="margin-top: 0; color: #495057;">📊 NarxCare Risk Scores</h4>
            {scores_html}
        </div>
        """
    
    def _build_score_item(self, score: Dict[str, Any]) -> str:
        """Build HTML for a single score item."""
        return f"""
        <div style="background-color: #f8f9fa; border-left: 4px solid {score.get('risk_color', '#666')}; padding: 10px; margin: 5px 0; border-radius: 4px;">
            <strong>{score.get('type', 'Unknown')} Score:</strong> 
            <span style="color: {score.get('risk_color', '#666')}; font-weight: bold;">{score.get('value', 'N/A')}</span>
            <span style="color: #666; font-size: 0.9em;">({score.get('risk_level', 'Unknown Risk')})</span>
        </div>
        """
