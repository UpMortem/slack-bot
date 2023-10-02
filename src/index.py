import click
from flask import Flask
from flask.cli import with_appcontext

flask_app = Flask("Haly")

@click.command(name='test')
@with_appcontext
def test_command():
    """Run the tests."""
    import pytest
    pytest.main(["tests"])

flask_app.cli.add_command(test_command)

if __name__ == "__main__":
    flask_app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
