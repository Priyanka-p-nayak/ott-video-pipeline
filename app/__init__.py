from flask import Flask
from app.routes.upload import upload_bp
from app.routes.status import status_bp
from app.config import MAX_CONTENT_LENGTH


def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH
    app.register_blueprint(upload_bp)
    app.register_blueprint(status_bp)

    @app.errorhandler(413)
    def file_too_large(e):
        from flask import jsonify
        return jsonify({'error': 'File too large. Maximum allowed size is 500MB'}), 413

    return app