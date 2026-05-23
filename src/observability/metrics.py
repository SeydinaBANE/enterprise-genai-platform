from prometheus_client import Counter, Histogram

llm_calls_total = Counter(
    "llm_calls_total",
    "Total LLM API calls",
    ["model", "status"],
)

llm_latency_seconds = Histogram(
    "llm_latency_seconds",
    "LLM call latency in seconds",
    ["model"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

token_usage_total = Counter(
    "token_usage_total",
    "Total tokens consumed",
    ["model", "type"],
)

retrieval_latency_seconds = Histogram(
    "retrieval_latency_seconds",
    "Vector retrieval latency in seconds",
    ["store"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0],
)

retrieval_results_count = Histogram(
    "retrieval_results_count",
    "Number of results returned by retrieval",
    ["store"],
    buckets=[1, 2, 3, 5, 10, 20],
)
