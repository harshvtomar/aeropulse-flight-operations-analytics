# Methodology and design decisions

## Population and lineage
Download the complete official reporting-carrier monthly archives, not marketing-carrier records. Each archive contains one flight CSV and a readme. Pandas loads source cells as strings so validation can distinguish missing values from parsing failures. A selected set of 28 official fields is retained (see dictionary); all original columns remain in the raw ZIP and its recorded schema. Origin/Destination airport IDs supplement codes to avoid relying on reused codes.

Each accepted fact corresponds to one CSV data row. Its technical ID is `source_sha256:source_row`, where the row is one-based excluding the header. This is auditable source identity, not a claim that a business-key tuple is universally unique. Duplicate candidates are retained and flagged using date + DOT carrier + flight number + origin/destination IDs + scheduled departure. This run found zero candidates.

## Validation policy
Hard failures (invalid dates, identifiers, flags, airport format, nonpositive distance, HHMM, parsing or calendar mismatches) quarantine records. Source rows always reconcile to accepted + quarantined. Airport format checks alone do not validate membership in a separate airport registry. Dimensions are source-derived and do not invent airline names, coordinates or metadata.

Operational anomalies remain in accepted data with warning counts: extreme signed delays outside [-120,2880], missing normal-flight delays/times, arrival-indicator disagreements, cancellation reasons, overlapping statuses, negative cause minutes and unexpected arrival values for cancellations/diversions. Extreme delays are reviewed, not truncated. Missing arrival times for cancellations are expected. No facts are deduplicated or winsorized.

## Incremental and failure behavior
One bundle per calendar month contains validated Parquet, quarantine Parquet, quality JSON and a manifest. A staging directory is atomically renamed only after successful validation and writes. Same-checksum reruns verify bundle checksums and do no duplicate ingestion. A different file for an existing month is rejected; compare source revisions before explicit replacement. Header drift is rejected, including otherwise harmless changes, to force review. Run one importer/warehouse writer at a time. Source file hashes identify the downloaded bytes; a repackaged CSV will have a different hash.

The warehouse is rebuilt into a temporary DuckDB file, checked, then replaced atomically. Readers should reconnect after rebuilds. Indexes enforce unique dimension identities and fact technical IDs; a source code-to-ID conflict fails construction rather than multiplying joins. This quarter has 14 carrier IDs, 333 airport IDs and 90 dates. Numeric source fields use float64 to preserve missing values; integer domain checks apply to identifiers/calendar fields. SQL dates are normalized in the date dimension.

## Analytical limits
January–March 2025 is not a full seasonal cycle. Network mix and month length affect comparisons. Route eligibility thresholds are 1,000 normal arrivals per quarter and 500 for airline-origin comparisons. These are transparent screening rules, not statistical significance tests. Results are descriptive; uncertainty intervals, mix adjustment and policy recommendations are future work.

Source availability/revisions may change. Reproduction against current downloads must compare hashes with committed manifests before claiming the identical snapshot. MacOS installation instructions are provided; execution was verified on Linux with Python 3.12, not on a physical Mac.

## Reconciliation
Pandas independently re-derives eligibility from raw status/delay columns in validated Parquet, without reusing SQL-derived flags. It compares global counts, rates and means; per-month, carrier, origin and destination counts/means; and five cause sums against DuckDB. This is computation independence, not a second independent government dataset. Raw-to-processed counts and file fingerprints supply the separate source audit.
