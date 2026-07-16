try:
    import importlib
    flask = importlib.import_module('flask')
    Flask = flask.Flask
    jsonify = flask.jsonify
except ImportError as e:
    raise ImportError("Flask is not installed. Install it with 'pip install flask'.") from e

from app.routes.upload import upload_bp
from app.routes.status import status_bp
from app.routes.analytics import analytics_bp
from app.routes.stats import stats_bp
from app.routes.dashboard import dashboard_bp
from app.routes.videos import videos_bp  # 👈 NEW IMPORT
from app.config import MAX_CONTENT_LENGTH


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    
    app.register_blueprint(upload_bp)
    app.register_blueprint(status_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(stats_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(videos_bp)  # 👈 NEW REGISTRATION

    @app.errorhandler(413)
    def file_too_large(e):
        return jsonify({'error': 'File too large. Maximum allowed size is 500MB'}), 413

    return app