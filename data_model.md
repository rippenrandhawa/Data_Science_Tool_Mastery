# Power BI data model — star schema

Built from the same real extract used by every other lab
(`data/online_retail_sales_sample.csv`, derived from the UCI *Online Retail* dataset,
DOI `10.24432/C5BW33`).

```
                          dim_date
                              │
                              │ 1
                              │
                       ┌──────┴───────┐
                       │  fact_orders  │
                       │──────────────│
                       │ invoice_no  PK│
                       │ invoice_date  │
                       │ customer_id FK│
                       │ country       │
                       └──────┬───────┘
                              │ 1
                              │
                              │ *
   dim_customer        ┌──────┴──────────┐          dim_product
   ─────────────       │ fact_order_items │          ────────────
   customer_id  PK ────│─────────────────│──── stock_code PK
   country             │ invoice_no   FK │          description
                       │ stock_code   FK │
                       │ customer_id  FK │
                       │ quantity        │
                       │ unit_price      │
                       │ line_total      │
                       └─────────────────┘
```

## Tables

| Table | Type | Rows | Grain | Key |
|---|---|---:|---|---|
| `fact_order_items` | Fact (transaction line) | 9,479 | one row per invoice line | `invoice_no` + `stock_code` |
| `fact_orders` | Fact (order header) | 468 | one row per invoice | `invoice_no` |
| `dim_customer` | Dimension | 394 | one row per registered customer | `customer_id` |
| `dim_product` | Dimension | 2,187 | one row per stock code | `stock_code` |
| `dim_date` | Dimension | 373 | one row per calendar day | `date` |

> Row counts are for the relational subset that covers registered customers.
> The flat sample also holds 2,698 guest lines, which are analysed in Python
> (`guest` behaviour) but are outside the star schema because they have no
> `customer_id`.

## Relationships

| Child (many) | Parent (one) | Column |
|---|---|---|
| `fact_order_items` | `fact_orders` | `invoice_no` |
| `fact_order_items` | `dim_product` | `stock_code` |
| `fact_order_items` | `dim_customer` | `customer_id` |
| `fact_orders` | `dim_customer` | `customer_id` |
| `fact_orders` | `dim_date` | `invoice_date` → `date` |

All relationships are **many-to-one, single cross-filter direction**, which is the
simplest model that answers every business question in the dashboard without
ambiguous filter paths.

## Why a star schema

* **Query speed** — aggregations hit narrow fact tables instead of one wide table.
* **Reusable measures** — `Total Revenue` is defined once and responds to any
  combination of customer, product and date filters.
* **Clean DAX** — time intelligence needs a proper `dim_date`, which is why the
  calendar table exists even though the source CSV has no separate date table.
* **Extensibility** — adding a `dim_store` or `dim_promotion` later means one new
  relationship, not a rebuild.
