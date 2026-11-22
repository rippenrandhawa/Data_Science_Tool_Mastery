// ===========================================================================
// LAB 6 - POWER QUERY : M code for the Retail Analytics data model
// ===========================================================================
// How to use: Power BI Desktop > Get data > Blank query > Advanced editor,
//             paste this whole block, rename the query "Staging", click Done.
//             Then reference "Staging" for each table listed in the model below.
//
// Source file: ..\data\online_retail_sales_sample.csv
//              (a real extract of the UCI "Online Retail" dataset, DOI 10.24432/C5BW33)
// ===========================================================================


// ---------------------------------------------------------------------------
// 1. STAGING QUERY  - one row per transaction line
// ---------------------------------------------------------------------------
let
    Source = Csv.Document(
        File.Contents("C:\Path\To\Data_Science_Tool_Mastery\data\online_retail_sales_sample.csv"),
        [Delimiter = ",", Columns = 9, Encoding = 1252, QuoteStyle = QuoteStyle.None]
    ),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(
        Promoted,
        {
            {"InvoiceNo",   type text},
            {"StockCode",   type text},
            {"Description", type text},
            {"Quantity",    Int64.Type},
            {"InvoiceDate", type datetime},
            {"UnitPrice",   type number},
            {"CustomerID",  type number},
            {"Country",     type text},
            {"line_total",  type number}
        }
    ),
    Cleaned = Table.SelectRows(
        Typed,
        each [Quantity] > 0 and [UnitPrice] > 0 and [line_total] > 0
    ),
    Renamed = Table.RenameColumns(
        Cleaned,
        {
            {"InvoiceNo",   "invoice_no"},
            {"StockCode",   "stock_code"},
            {"Description", "description"},
            {"InvoiceDate", "invoice_date"},
            {"UnitPrice",   "unit_price"},
            {"CustomerID",  "customer_id"},
            {"Country",     "country"},
            {"Quantity",    "quantity"},
            {"line_total",  "line_total"}
        }
    ),
    AddedMonth = Table.AddColumn(
        Renamed,
        "year_month",
        each Date.ToText(DateTime.Date([invoice_date]), "yyyy-MM"),
        type text
    )
in
    AddedMonth


// ---------------------------------------------------------------------------
// 2. dim_date  - calendar table (also writable as DAX, see the build guide)
// ---------------------------------------------------------------------------
let
    StartDate = List.Min(Staging[invoice_date]),
    EndDate   = List.Max(Staging[invoice_date]),
    Days      = Duration.Days(EndDate - StartDate) + 1,
    Source    = List.Dates(StartDate, Days, #duration(1, 0, 0, 0)),
    Table     = Table.FromList(Source, Splitter.SplitByNothing()),
    Renamed   = Table.RenameColumns(Table, {"Column1": "date"}),
    Typed     = Table.TransformColumnTypes(Renamed, {"date", type date}),
    AddedYear = Table.AddColumn(Typed, "year", each Date.Year([date]), Int64.Type),
    AddedMonth = Table.AddColumn(AddedYear, "month", each Date.Month([date]), Int64.Type),
    AddedMonthName = Table.AddColumn(
        AddedMonth, "month_name", each Date.MonthName([date]), type text
    ),
    AddedQuarter = Table.AddColumn(
        AddedMonthName, "quarter", each "Q" & Text.From(Date.QuarterOfYear([date])), type text
    )
in
    AddedQuarter


// ---------------------------------------------------------------------------
// 3. dim_customer
// ---------------------------------------------------------------------------
let
    Source = Table.SelectColumns(Staging, {"customer_id", "country"}),
    Distinct = Table.Distinct(Source),
    Sorted = Table.Sort(Distinct, {"customer_id", Order.Ascending})
in
    Sorted


// ---------------------------------------------------------------------------
// 4. dim_product
// ---------------------------------------------------------------------------
let
    Source = Table.SelectColumns(Staging, {"stock_code", "description"}),
    Grouped = Table.Group(Source, {"stock_code"}, {{"description", each List.First(_[description]), type text}}),
    Sorted = Table.Sort(Grouped, {"stock_code", Order.Ascending})
in
    Sorted


// ---------------------------------------------------------------------------
// 5. fact_order_items
// ---------------------------------------------------------------------------
let
    Source = Table.SelectColumns(
        Staging,
        {"invoice_no", "stock_code", "quantity", "unit_price", "line_total"}
    )
in
    Source


// ---------------------------------------------------------------------------
// 6. fact_orders
// ---------------------------------------------------------------------------
let
    Source = Table.SelectColumns(
        Staging,
        {"invoice_no", "invoice_date", "customer_id", "country"}
    ),
    Distinct = Table.Distinct(Source)
in
    Distinct
