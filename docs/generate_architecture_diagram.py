"""
Generate Architecture Diagram for Autonomous Pricing Engine
Run this script to create a PNG diagram for PPT submission.

Requirements:
    pip install diagrams

Usage:
    python generate_architecture_diagram.py
"""

import os

# Ensure Graphviz bin is on PATH (Windows install location)
_graphviz_bin = r"C:\Program Files\Graphviz\bin"
if _graphviz_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = _graphviz_bin + os.pathsep + os.environ.get("PATH", "")

from diagrams import Diagram, Cluster, Edge
from diagrams.aws.compute import Lambda
from diagrams.aws.database import Dynamodb
from diagrams.aws.integration import Eventbridge, SQS
from diagrams.aws.ml import Bedrock
from diagrams.aws.network import APIGateway
from diagrams.aws.storage import S3
from diagrams.aws.management import Cloudwatch
from diagrams.onprem.client import Client
from diagrams.generic.blank import Blank

# Graph attributes for clean output
graph_attr = {
    "fontsize": "20",
    "bgcolor": "white",
    "pad": "0.5",
    "splines": "ortho",
    "nodesep": "0.8",
    "ranksep": "1.5",
}

node_attr = {
    "fontsize": "14",
    "fontname": "Arial",
    "style": "filled",
    "fillcolor": "#E8F4F8",
}

edge_attr = {
    "color": "#2D3748",
    "fontname": "Arial",
    "fontsize": "12",
}

with Diagram(
    "Autonomous Pricing Engine - AWS Architecture",
    show=False,
    direction="TB",
    graph_attr=graph_attr,
    node_attr=node_attr,
    edge_attr=edge_attr,
    filename="architecture_diagram",
    outformat="png",
):

    # External sources
    with Cluster("External Data Sources", graph_attr={"bgcolor": "#FFF5F5"}):
        competitor = Blank("Competitor\nPrices")
        demand = Blank("Demand\nSignals")
        market = Blank("Market\nTrends")

    # Ingestion Layer
    with Cluster("Ingestion Layer (AWS)", graph_attr={"bgcolor": "#F0FFF4"}):
        sqs = SQS("Market Data\nQueue")
        eventbridge = Eventbridge("Event Bus")

    # Decision Engine
    with Cluster("Pricing Decision Engine (Lambda)", graph_attr={"bgcolor": "#EBF8FF"}):
        market_processor = Lambda("Market\nProcessor")
        pricing_engine = Lambda("Pricing\nEngine")
        guardrail = Lambda("Guardrail\nExecutor")

    # AI Layer
    with Cluster("AI Layer (Bedrock)", graph_attr={"bgcolor": "#FAF5FF"}):
        correction_agent = Lambda("Correction\nAgent")
        ai_interface = Lambda("AI\nInterface")
        bedrock = Bedrock("Claude Haiku\n4.5")

    # Monitoring
    with Cluster("Monitoring", graph_attr={"bgcolor": "#FFFAF0"}):
        monitoring = Lambda("Monitoring\nAgent")

    # Data Layer
    with Cluster("Data Layer (DynamoDB)", graph_attr={"bgcolor": "#F5F5F5"}):
        products_table = Dynamodb("Products")
        decisions_table = Dynamodb("Decisions")
        corrections_table = Dynamodb("Corrections")

    # API Layer
    with Cluster("API Layer", graph_attr={"bgcolor": "#E6FFFA"}):
        api_gateway = APIGateway("API\nGateway")

    # Frontend
    with Cluster("Frontend (Streamlit)", graph_attr={"bgcolor": "#FFF5F5"}):
        dashboard = Client("Seller\nDashboard")

    # Flow connections
    # External to Ingestion
    competitor >> Edge(label="price updates") >> sqs
    demand >> Edge(label="signals") >> sqs
    market >> Edge(label="trends") >> sqs

    # Ingestion to Event
    sqs >> Edge(label="events") >> eventbridge

    # Event to processors
    eventbridge >> Edge(label="trigger") >> market_processor
    market_processor >> Edge(label="processed") >> pricing_engine
    pricing_engine >> Edge(label="recommend") >> guardrail

    # Guardrail to decisions
    guardrail >> Edge(label="validated") >> decisions_table
    products_table >> Edge(label="product data") >> pricing_engine

    # Monitoring flow
    decisions_table >> Edge(label="track") >> monitoring
    monitoring >> Edge(label="deviation") >> correction_agent

    # AI Correction flow
    correction_agent >> Edge(label="analyze") >> bedrock
    bedrock >> Edge(label="reasoning") >> correction_agent
    correction_agent >> Edge(label="correction") >> corrections_table
    correction_agent >> Edge(label="update") >> decisions_table

    # AI Interface flow
    api_gateway >> Edge(label="query") >> ai_interface
    ai_interface >> Edge(label="process") >> bedrock
    ai_interface >> Edge(label="response") >> products_table
    ai_interface >> Edge(label="history") >> decisions_table
    ai_interface >> Edge(label="corrections") >> corrections_table

    # Frontend connection
    dashboard >> Edge(label="REST API") >> api_gateway

    # CloudWatch (monitoring all)
    cloudwatch = Cloudwatch("CloudWatch\nLogs")
    market_processor >> Edge(style="dashed", color="gray") >> cloudwatch
    pricing_engine >> Edge(style="dashed", color="gray") >> cloudwatch
    correction_agent >> Edge(style="dashed", color="gray") >> cloudwatch