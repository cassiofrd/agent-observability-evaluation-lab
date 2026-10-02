from observability.metrics import calculate_metrics, load_traces


def main():
    traces = load_traces()
    metrics = calculate_metrics(traces)

    print("\n--- METRICS ---")

    for key, value in metrics.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()