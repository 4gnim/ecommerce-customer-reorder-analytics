from __future__ import annotations

from pathlib import Path
import time

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PRIOR_FILE = RAW_DIR / "order_products__prior.csv"
TRAIN_FILE = RAW_DIR / "order_products__train.csv"
ORDERS_FILE = RAW_DIR / "orders.csv"
PRODUCTS_FILE = RAW_DIR / "products.csv"
AISLES_FILE = RAW_DIR / "aisles.csv"
DEPARTMENTS_FILE = RAW_DIR / "departments.csv"

CHUNK_SIZE = 1_000_000
EXPECTED_PRODUCTS = 49_688
EXPECTED_TOTAL_ITEMS = 33_819_106
EXPECTED_REORDERED_ITEMS = 19_955_360


def require_files() -> None:
    files = [
        PRIOR_FILE,
        TRAIN_FILE,
        ORDERS_FILE,
        PRODUCTS_FILE,
        AISLES_FILE,
        DEPARTMENTS_FILE,
    ]
    missing = [str(p) for p in files if not p.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing required raw files:\n- " + "\n- ".join(missing)
        )


def load_product_dimension() -> pd.DataFrame:
    products = pd.read_csv(
        PRODUCTS_FILE,
        usecols=["product_id", "product_name", "aisle_id", "department_id"],
        dtype={
            "product_id": "int32",
            "product_name": "string",
            "aisle_id": "int16",
            "department_id": "int16",
        },
    )
    aisles = pd.read_csv(
        AISLES_FILE,
        dtype={"aisle_id": "int16", "aisle": "string"},
    )
    departments = pd.read_csv(
        DEPARTMENTS_FILE,
        dtype={"department_id": "int16", "department": "string"},
    )

    if len(products) != EXPECTED_PRODUCTS:
        raise ValueError(
            f"Expected {EXPECTED_PRODUCTS:,} products, got {len(products):,}."
        )

    result = products.merge(aisles, on="aisle_id", how="left", validate="many_to_one")
    result = result.merge(
        departments,
        on="department_id",
        how="left",
        validate="many_to_one",
    )

    if result[["aisle", "department"]].isna().any().any():
        raise ValueError("Product dimension contains unresolved aisle/department links.")

    return result


def load_order_number_map() -> tuple[np.ndarray, int]:
    """Load order_number into a compact NumPy array indexed by order_id."""
    orders = pd.read_csv(
        ORDERS_FILE,
        usecols=["order_id", "order_number"],
        dtype={"order_id": "int32", "order_number": "int16"},
    )

    if orders["order_id"].duplicated().any():
        raise ValueError("orders.csv contains duplicate order_id values.")

    max_order_id = int(orders["order_id"].max())
    order_number_by_id = np.zeros(max_order_id + 1, dtype=np.int16)
    order_number_by_id[orders["order_id"].to_numpy()] = orders["order_number"].to_numpy()

    return order_number_by_id, max_order_id


def process_order_products(
    path: Path,
    n_products: int,
    max_order_id: int,
    order_number_by_id: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Stream one order-product CSV and return four compact aggregate arrays:
      product item count, product reordered count,
      order item count, order reordered count.
    """
    product_items = np.zeros(n_products + 1, dtype=np.int64)
    product_reordered = np.zeros(n_products + 1, dtype=np.int64)
    order_items = np.zeros(max_order_id + 1, dtype=np.int64)
    order_reordered = np.zeros(max_order_id + 1, dtype=np.int64)

    processed = 0
    start = time.time()

    for chunk_no, chunk in enumerate(
        pd.read_csv(
            path,
            usecols=["order_id", "product_id", "reordered"],
            dtype={
                "order_id": "int32",
                "product_id": "int32",
                "reordered": "int8",
            },
            chunksize=CHUNK_SIZE,
        ),
        start=1,
    ):
        order_ids = chunk["order_id"].to_numpy()
        product_ids = chunk["product_id"].to_numpy()
        reordered = chunk["reordered"].to_numpy(dtype=np.int64)

        if product_ids.min(initial=1) < 1 or product_ids.max(initial=0) > n_products:
            raise ValueError(f"{path.name}: product_id outside expected range.")
        if order_ids.min(initial=1) < 1 or order_ids.max(initial=0) > max_order_id:
            raise ValueError(f"{path.name}: order_id outside expected range.")
        if not np.isin(reordered, [0, 1]).all():
            raise ValueError(f"{path.name}: reordered contains values other than 0/1.")

        # Product-level metrics.
        product_items += np.bincount(product_ids, minlength=n_products + 1)
        product_reordered += np.bincount(
            product_ids, weights=reordered, minlength=n_products + 1
        ).astype(np.int64)

        # Order-level metrics; used later for order-sequence analysis.
        order_items += np.bincount(order_ids, minlength=max_order_id + 1)
        order_reordered += np.bincount(
            order_ids, weights=reordered, minlength=max_order_id + 1
        ).astype(np.int64)

        processed += len(chunk)
        print(
            f"  {path.name}: chunk {chunk_no:>2} | "
            f"{processed:,} rows processed",
            flush=True,
        )

    elapsed = time.time() - start
    print(f"  Finished {path.name} in {elapsed / 60:.1f} minutes.\n", flush=True)
    return product_items, product_reordered, order_items, order_reordered


def build_product_marts(product_items: np.ndarray, product_reordered: np.ndarray, products: pd.DataFrame) -> None:
    metrics = pd.DataFrame(
        {
            "product_id": np.arange(1, len(product_items), dtype=np.int32),
            "total_items": product_items[1:],
            "reordered_items": product_reordered[1:],
        }
    )
    metrics["item_reorder_rate_pct"] = np.where(
        metrics["total_items"] > 0,
        100.0 * metrics["reordered_items"] / metrics["total_items"],
        0.0,
    )

    product_mart = products.merge(
        metrics,
        on="product_id",
        how="left",
        validate="one_to_one",
    )
    for col in ["total_items", "reordered_items"]:
        product_mart[col] = product_mart[col].fillna(0).astype("int64")
    product_mart["item_reorder_rate_pct"] = product_mart[
        "item_reorder_rate_pct"
    ].fillna(0).round(2)

    output = PROCESSED_DIR / "product_performance.csv"
    product_mart.to_csv(output, index=False)

    department = (
        product_mart.groupby(["department_id", "department"], as_index=False)
        .agg(
            total_items=("total_items", "sum"),
            reordered_items=("reordered_items", "sum"),
        )
    )
    department["item_reorder_rate_pct"] = (
        100.0 * department["reordered_items"] / department["total_items"]
    ).round(2)
    department.to_csv(PROCESSED_DIR / "department_performance.csv", index=False)

    aisle = (
        product_mart.groupby(["aisle_id", "aisle"], as_index=False)
        .agg(
            total_items=("total_items", "sum"),
            reordered_items=("reordered_items", "sum"),
        )
    )
    aisle["item_reorder_rate_pct"] = (
        100.0 * aisle["reordered_items"] / aisle["total_items"]
    ).round(2)
    aisle.to_csv(PROCESSED_DIR / "aisle_performance.csv", index=False)

    # Reconciliation against the independently validated source totals.
    total_items = int(product_mart["total_items"].sum())
    reordered_items = int(product_mart["reordered_items"].sum())
    if total_items != EXPECTED_TOTAL_ITEMS:
        raise ValueError(
            f"Product total_items reconciliation failed: {total_items:,} "
            f"!= {EXPECTED_TOTAL_ITEMS:,}."
        )
    if reordered_items != EXPECTED_REORDERED_ITEMS:
        raise ValueError(
            f"Product reordered_items reconciliation failed: {reordered_items:,} "
            f"!= {EXPECTED_REORDERED_ITEMS:,}."
        )

    print("Product marts written:")
    print(f"  {output.name}: {len(product_mart):,} rows")
    print(f"  department_performance.csv: {len(department):,} rows")
    print(f"  aisle_performance.csv: {len(aisle):,} rows")
    print(f"  Total items: {total_items:,}")
    print(f"  Reordered items: {reordered_items:,}")
    print(
        f"  Overall item reorder rate: "
        f"{100.0 * reordered_items / total_items:.2f}%\n"
    )


def build_sequence_mart(order_items: np.ndarray, order_reordered: np.ndarray, order_number_by_id: np.ndarray) -> None:
    # Test orders have no product-level items, so order_items > 0 identifies
    # the analyzed prior/train population without needing another join.
    order_ids = np.nonzero(order_items > 0)[0]
    order_numbers = order_number_by_id[order_ids]

    if (order_numbers < 1).any():
        raise ValueError("Found analyzed order items without a valid order_number.")

    total_orders = np.bincount(order_numbers, minlength=101)[1:]
    total_items = np.bincount(
        order_numbers,
        weights=order_items[order_ids],
        minlength=101,
    )
    reordered_items = np.bincount(
        order_numbers,
        weights=order_reordered[order_ids],
        minlength=101,
    )

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

    # Keep order numbers that actually occur in the analyzed item population.
    sequence = sequence[sequence["total_orders"] > 0].copy()
    output = PROCESSED_DIR / "order_sequence_performance.csv"
    sequence.to_csv(output, index=False)

    print(f"Sequence mart written: {output.name}: {len(sequence):,} rows")


def main() -> None:
    require_files()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 72)
    print("Project 3 - Large-Scale Python Mart Builder")
    print("=" * 72)
    print(f"Chunk size: {CHUNK_SIZE:,}\n")

    print("[1/5] Loading product dimension...")
    products = load_product_dimension()
    print(f"  Products loaded: {len(products):,}\n")

    print("[2/5] Loading compact order-number lookup...")
    order_number_by_id, max_order_id = load_order_number_map()
    print(f"  Max order_id: {max_order_id:,}\n")

    print("[3/5] Streaming prior order-product data...")
    prior = process_order_products(
        PRIOR_FILE,
        EXPECTED_PRODUCTS,
        max_order_id,
        order_number_by_id,
    )

    print("[4/5] Streaming train order-product data...")
    train = process_order_products(
        TRAIN_FILE,
        EXPECTED_PRODUCTS,
        max_order_id,
        order_number_by_id,
    )

    product_items = prior[0] + train[0]
    product_reordered = prior[1] + train[1]
    order_items = prior[2] + train[2]
    order_reordered = prior[3] + train[3]

    print("[5/5] Writing analytical marts...\n")
    build_product_marts(product_items, product_reordered, products)
    build_sequence_mart(order_items, order_reordered, order_number_by_id)

    print("=" * 72)
    print("DONE")
    print("=" * 72)
    print(f"Processed output directory: {PROCESSED_DIR}")


if __name__ == "__main__":
    main()
