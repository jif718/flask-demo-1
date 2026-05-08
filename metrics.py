from prometheus_flask_exporter import PrometheusMetrics


def init_metrics(app):
    metrics = PrometheusMetrics(app)

    metrics.info(
        "flask_demo_info",
        "Flask demo application info",
        version="1.0.0",
        app="flask-demo-1"
    )

    return metrics