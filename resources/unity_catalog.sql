-- Reproducible Unity Catalog setup for the Paperlane POC.
-- This file was not executed. The Unity Catalog service was not contacted.
-- The local enforcer in lakehouse_poc.catalog mirrors these grants.

CREATE CATALOG IF NOT EXISTS paperlane;
CREATE SCHEMA IF NOT EXISTS paperlane.governance;
CREATE SCHEMA IF NOT EXISTS paperlane.bronze;
CREATE SCHEMA IF NOT EXISTS paperlane.silver;
CREATE SCHEMA IF NOT EXISTS paperlane.gold;

CREATE TABLE IF NOT EXISTS paperlane.governance.principal_tenant (
  principal STRING,
  tenant_id STRING
);

CREATE OR REPLACE FUNCTION paperlane.governance.tenant_match(row_tenant STRING)
RETURNS BOOLEAN
RETURN row_tenant = (
  SELECT tenant_id
  FROM paperlane.governance.principal_tenant
  WHERE principal = current_user()
);

ALTER TABLE paperlane.gold.daily_category_revenue
SET ROW FILTER paperlane.governance.tenant_match ON (tenant_id);

GRANT USE CATALOG ON CATALOG paperlane TO `analyst`;
GRANT USE SCHEMA ON SCHEMA paperlane.gold TO `analyst`;
GRANT SELECT ON TABLE paperlane.gold.daily_category_revenue TO `analyst`;
GRANT SELECT ON TABLE paperlane.gold.order_features TO `analyst`;

GRANT USE CATALOG ON CATALOG paperlane TO `engineer`;
GRANT USE SCHEMA ON SCHEMA paperlane.bronze TO `engineer`;
GRANT USE SCHEMA ON SCHEMA paperlane.silver TO `engineer`;
GRANT USE SCHEMA ON SCHEMA paperlane.gold TO `engineer`;
GRANT SELECT ON TABLE paperlane.bronze.orders TO `engineer`;
GRANT SELECT ON TABLE paperlane.bronze.events TO `engineer`;
GRANT SELECT ON TABLE paperlane.silver.orders TO `engineer`;
GRANT SELECT ON TABLE paperlane.silver.events TO `engineer`;
GRANT SELECT ON TABLE paperlane.gold.daily_category_revenue TO `engineer`;
GRANT SELECT ON TABLE paperlane.gold.order_features TO `engineer`;
GRANT MODIFY ON SCHEMA paperlane.gold TO `engineer`;

CREATE OR REPLACE VIEW paperlane.governance.lineage AS
SELECT 'silver_orders' AS child_name, 'bronze_orders' AS parent_name
UNION ALL SELECT 'silver_events', 'bronze_events'
UNION ALL SELECT 'gold_daily_category_revenue', 'silver_orders'
UNION ALL SELECT 'gold_order_features', 'silver_orders'
UNION ALL SELECT 'gold_order_features', 'silver_events';
