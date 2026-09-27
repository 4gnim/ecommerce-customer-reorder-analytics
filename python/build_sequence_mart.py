from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

ORDERS_FILE = RAW_DIR / "orders.csv"
PRIOR_FILE = RAW_DIR / "order_products__prior.csv"
TRAIN_FILE = RAW_DIR / "order_products__train.csv"

CHUNK_SIZE = 1_000_000
EXPECTED_ORDERS = 3_346_083
EXPECTED_TOTAL_ITEMS = 33_819_106
EXPECTED_REORDERED_ITEMS = 19_955_360


def load_order_number_map() -> np.ndarray:
    orders = pd.read_csv(
        ORDERS_FILE,
        usecols=["order_id", "order_number", "eval_set"],
        dtype={
            "order_id": "int32",
            "order_number": "int16",
            "eval_set": "string",
        },
    )

    analyzed = orders[orders["eval_set"].isin(["prior", "train"])].copy()

    if len(analyzed) != EXPECTED_ORDERS:
        raise ValueError(
            f"Expected {EXPECTED_ORDERS:,} analyzed orders, got {len(analyzed):,}."
        )

    max_order_id = int(orders["order_id"].max())
    order_number_by_id = np.zeros(max_order_id + 1, dtype=np.int16)
    order_number_by_id[
        analyzed["order_id"].to_numpy()
    ] = analyzed["order_number"].to_numpy()

    return order_number_by_id


def aggregate_order_items(path: Path, max_order_id: int):
    order_items = np.zeros(max_order_id + 1, dtype=np.int64)
    order_reordered = np.zeros(max_order_id + 1, dtype=np.int64)

    processed = 0

    for chunk_no, chunk in enumerate(
        pd.read_csv(
            path,
            usecols=["order_id", "reordered"],
            dtype={"order_id": "int32", "reordered": "int8"},
            chunksize=CHUNK_SIZE,
        ),
        start=1,
    ):
        order_ids = chunk["order_id"].to_numpy()
        reordered = chunk["reordered"].to_numpy(dtype=np.int64)

        order_items += np.bincount(
            order_ids, minlength=max_order_id + 1
        )
        order_reordered += np.bincount(
            order_ids,
            weights=reordered,
            minlength=max_order_id + 1,
        ).astype(np.int64)

        processed += len(chunk)
        print(
            f"  {path.name}: chunk {chunk_no:>2} | "
            f"{processed:,} rows processed",
            flush=True,
        )

    return order_items, order_reordered


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Project 3 - Build Order Sequence Mart")
    print("=" * 72)

    order_number_by_id = load_order_number_map()
    max_order_id = len(order_number_by_id) - 1

    print("\n[1/3] Streaming prior order-product data...")
    prior_items, prior_reordered = aggregate_order_items(
        PRIOR_FILE, max_order_id
    )

    print("\n[2/3] Streaming train order-product data...")
    train_items, train_reordered = aggregate_order_items(
        TRAIN_FILE, max_order_id
    )

    order_items = prior_items + train_items
    order_reordered = prior_reordered + train_reordered

    analyzed_order_ids = np.flatnonzero(order_items)
    order_numbers = order_number_by_id[analyzed_order_ids]

    if len(analyzed_order_ids) != EXPECTED_ORDERS:
        raise ValueError(
            f"Expected {EXPECTED_ORDERS:,} analyzed orders with items, "
            f"got {len(analyzed_order_ids):,}."
        )

    if (order_numbers < 1).any():
        raise ValueError(
            "Found analyzed order items without a valid order_number."
        )

    print("\n[3/3] Building sequence mart...")

    # All three arrays are explicitly sliced [1:] so they all represent
    # order_number 1..100 and therefore have the same length.
    total_orders = np.bincount(
        order_numbers, minlength=101
    )[1:]
    total_items = np.bincount(
        order_numbers,
        weights=order_items[analyzed_order_ids],
        minlength=101,
    )[1:]
    reordered_items = np.bincount(
        order_numbers,
        weights=order_reordered[analyzed_order_ids],
        minlength=101,
    )[1:]

    sequence = pd.DataFrame(
        {
            "order_number": np.arange(1, 101, dtype=np.int16),
            "total_orders": total_orders.astype(np.int64),
            "total_items": total_items.astype(np.int64),
            "reordered_items": reordered_items.astype(np.int64),
        }
    )

    sequence["item_reorder_rate_pct"] = np.where(
        sequence["total_items"] > 0,
        100.0 * sequence["reordered_items"] / sequence["total_items"],
        0.0,
    ).round(2)

    sequence = sequence[sequence["total_orders"] > 0].copy()

    # Reconciliation.
    if int(sequence["total_orders"].sum()) != EXPECTED_ORDERS:
        raise ValueError("Sequence order count reconciliation failed.")
    if int(sequence["total_items"].sum()) != EXPECTED_TOTAL_ITEMS:
        raise ValueError("Sequence total item reconciliation failed.")
    if int(sequence["reordered_items"].sum()) != EXPECTED_REORDERED_ITEMS:
        raise ValueError("Sequence reordered item reconciliation failed.")

    output = PROCESSED_DIR / "order_sequence_performance.csv"
    sequence.to_csv(output, index=False)

    total_items_sum = int(sequence["total_items"].sum())
    reordered_items_sum = int(sequence["reordered_items"].sum())

    print("\nSequence mart written:")
    print(f"  {output.name}: {len(sequence):,} rows")
    print(f"  Total analyzed orders: {sequence['total_orders'].sum():,}")
    print(f"  Total items: {total_items_sum:,}")
    print(f"  Reordered items: {reordered_items_sum:,}")
    print(
        "  Overall item reorder rate: "
        f"{100.0 * reordered_items_sum / total_items_sum:.2f}%"
    )
    print("=" * 72)


if __name__ == "__main__":
    main()
