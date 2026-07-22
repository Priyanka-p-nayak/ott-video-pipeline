"""Route for serving the analytics dashboard HTML page."""

from flask import Blueprint, render_template  # type: ignore

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard', methods=['GET'])
def show_dashboard():
    """Render the dashboard page."""
    return render_template('dashboard.html')