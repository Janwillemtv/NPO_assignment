"""Main faust App and configuration"""
import faust

app = faust.App(
    'faust_api',
    broker='kafka://localhost',
    version=1,
    autodiscover=True,
    origin='faust_api'
)


def main() -> None:
    """Run app"""
    app.main()
