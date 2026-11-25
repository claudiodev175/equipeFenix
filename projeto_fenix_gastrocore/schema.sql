-- ==============================================================================
-- GASTROCORE ERP • SCHEMA POSTGRESQL PARA SUPABASE (CÓPIA EDUCACIONAL APONTI)
-- Versão: 0.3.0 (Dual-Shell Backoffice + KDS, Kardex & Multi-Unidades)
-- Regras de Negócio: UAN, ANVISA RDC 216, Fator de Correção (FC), PVPS e Hot Box
-- Nota de Segurança: Seed sanitizado sem credenciais administrativas de SaaS.
-- ==============================================================================

-- 1. TABELA DE UNIDADES OPERACIONAIS (FILIAIS DA REDE)
CREATE TABLE IF NOT EXISTS kitchen_units (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  code TEXT NOT NULL,
  type TEXT NOT NULL CHECK (type IN ('industrial', 'hospitalar', 'escolar')),
  address TEXT NOT NULL,
  manager_name TEXT NOT NULL,
  contact_email TEXT NOT NULL,
  average_pax_per_day NUMERIC NOT NULL DEFAULT 0,
  contract_price_per_pax NUMERIC NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'ativa' CHECK (status IN ('ativa', 'manutencao', 'inativa')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. TABELA DE INSUMOS & ESTOQUE (ALMOXARIFADO CENTRAL E COZINHA)
CREATE TABLE IF NOT EXISTS ingredients (
  id TEXT PRIMARY KEY,
  unit_id TEXT REFERENCES kitchen_units(id) ON DELETE SET NULL,
  name TEXT NOT NULL,
  item_type TEXT DEFAULT 'alimento' CHECK (item_type IN ('alimento', 'descartavel', 'higiene', 'utensilio', 'equipamento')),
  category TEXT NOT NULL,
  unit TEXT NOT NULL CHECK (unit IN ('kg', 'g', 'l', 'L', 'ml', 'un', 'cx', 'pct', 'rolo')),
  current_stock NUMERIC NOT NULL DEFAULT 0,
  min_stock NUMERIC NOT NULL DEFAULT 0,
  unit_cost NUMERIC NOT NULL DEFAULT 0,
  supplier TEXT NOT NULL,
  brand TEXT,
  barcode TEXT,
  lot_number TEXT,
  expiration_date TEXT,
  status TEXT DEFAULT 'normal' CHECK (status IN ('normal', 'baixo', 'vencendo', 'vencido')),
  allergens TEXT[] DEFAULT '{}',
  location TEXT,
  batches JSONB DEFAULT '[]',
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Migração idempotente caso tabela `ingredients` já exista com constraint antiga sem 'L' / 'rolo'
ALTER TABLE ingredients DROP CONSTRAINT IF EXISTS ingredients_unit_check;
ALTER TABLE ingredients ADD CONSTRAINT ingredients_unit_check
  CHECK (unit IN ('kg', 'g', 'l', 'L', 'ml', 'un', 'cx', 'pct', 'rolo'));

-- 3. TABELA DE FICHAS TÉCNICAS (RECEITUÁRIO PADRONIZADO E POP)
CREATE TABLE IF NOT EXISTS technical_sheets (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('principal', 'guarnicao', 'salada', 'sobremesa', 'bebida', 'molho', 'lanche')),
  target_audience TEXT[] DEFAULT '{}',
  dietary_tags TEXT[] DEFAULT '{}',
  yield_portions NUMERIC NOT NULL DEFAULT 1,
  portion_size_grams NUMERIC NOT NULL DEFAULT 100,
  preparation_time_min INTEGER NOT NULL DEFAULT 30,
  preparation_method TEXT,
  cooking_factor NUMERIC NOT NULL DEFAULT 1.0,
  ingredients JSONB NOT NULL DEFAULT '[]',
  total_cost NUMERIC NOT NULL DEFAULT 0,
  cost_per_portion NUMERIC NOT NULL DEFAULT 0,
  suggested_selling_price NUMERIC NOT NULL DEFAULT 0,
  margin_percent NUMERIC NOT NULL DEFAULT 40,
  allergens_summary TEXT[] DEFAULT '{}',
  allergens TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. TABELA DE PLANEJAMENTO DE CARDÁPIO (GRADE SEMANAL)
CREATE TABLE IF NOT EXISTS daily_menu_plans (
  id TEXT PRIMARY KEY,
  unit_id TEXT REFERENCES kitchen_units(id) ON DELETE SET NULL,
  date_str TEXT NOT NULL,
  day_of_week TEXT NOT NULL,
  shift TEXT NOT NULL DEFAULT 'Almoço',
  planned_pax NUMERIC NOT NULL DEFAULT 100,
  price_per_pax_contracted NUMERIC NOT NULL DEFAULT 0,
  principais_ids TEXT[] DEFAULT '{}',
  guarnicoes_ids TEXT[] DEFAULT '{}',
  bases_ids TEXT[] DEFAULT '{}',
  saladas_ids TEXT[] DEFAULT '{}',
  molhos_ids TEXT[] DEFAULT '{}',
  sobremesas_ids TEXT[] DEFAULT '{}',
  bebidas_ids TEXT[] DEFAULT '{}',
  dietas_ids TEXT[] DEFAULT '{}',
  notes TEXT,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. TABELA DE BALANÇA DE SOBRAS & DESPERDÍCIO (ANVISA RDC 216)
CREATE TABLE IF NOT EXISTS waste_records (
  id TEXT PRIMARY KEY,
  unit_id TEXT NOT NULL,
  timestamp TEXT NOT NULL,
  period TEXT NOT NULL,
  operation_type TEXT NOT NULL,
  unit_name TEXT NOT NULL,
  category TEXT NOT NULL CHECK (category IN ('pre_preparo', 'sobra_limpa', 'resto_ingesto')),
  item_or_recipe_name TEXT NOT NULL,
  weight_kg NUMERIC NOT NULL,
  estimated_cost_per_kg NUMERIC NOT NULL,
  total_loss_brl NUMERIC NOT NULL,
  reason TEXT NOT NULL,
  reported_by TEXT NOT NULL,
  action_taken TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. TABELA DE EXPEDIÇÃO TÉRMICA HOT BOX (>60°C)
CREATE TABLE IF NOT EXISTS hot_box_deliveries (
  id TEXT PRIMARY KEY,
  unit_id TEXT REFERENCES kitchen_units(id) ON DELETE SET NULL,
  client_name TEXT NOT NULL,
  vehicle_plate TEXT NOT NULL,
  driver_name TEXT NOT NULL,
  departure_time TEXT NOT NULL,
  arrival_time_estimated TEXT NOT NULL,
  dispatch_temp_celsius NUMERIC NOT NULL,
  arrival_temp_celsius NUMERIC,
  status TEXT NOT NULL DEFAULT 'em_preparo' CHECK (status IN ('em_preparo', 'em_transito', 'entregue', 'nao_conforme')),
  boxes_count NUMERIC NOT NULL DEFAULT 1,
  seal_number TEXT NOT NULL,
  pax_count NUMERIC NOT NULL DEFAULT 1,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. TABELA DE ORÇAMENTOS E EVENTOS / COFFEE BREAKS
CREATE TABLE IF NOT EXISTS proposal_quotes (
  id TEXT PRIMARY KEY,
  unit_id TEXT REFERENCES kitchen_units(id) ON DELETE SET NULL,
  client_name TEXT NOT NULL,
  event_type TEXT NOT NULL CHECK (event_type IN ('coffee_break', 'almoco_corporativo', 'coquetel', 'contrato_mensal')),
  event_date TEXT NOT NULL,
  pax NUMERIC NOT NULL DEFAULT 50,
  raw_food_cost NUMERIC NOT NULL DEFAULT 0,
  disposables_cost NUMERIC NOT NULL DEFAULT 0,
  staff_cost NUMERIC NOT NULL DEFAULT 0,
  logistics_cost NUMERIC NOT NULL DEFAULT 0,
  target_margin_percent NUMERIC NOT NULL DEFAULT 40,
  final_price_per_pax NUMERIC NOT NULL DEFAULT 0,
  total_proposal_value NUMERIC NOT NULL DEFAULT 0,
  status TEXT NOT NULL DEFAULT 'rascunho' CHECK (status IN ('rascunho', 'enviada', 'aprovada', 'recusada')),
  items_included TEXT[] DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. TABELA DE CONFIGURAÇÃO DE TENANT (WHITE-LABEL)
CREATE TABLE IF NOT EXISTS tenant_configs (
  id TEXT PRIMARY KEY DEFAULT 'default_tenant',
  company_name TEXT NOT NULL,
  trading_name TEXT NOT NULL,
  cnpj TEXT NOT NULL,
  primary_color TEXT NOT NULL DEFAULT '#059669',
  active_plan TEXT NOT NULL DEFAULT 'pro',
  enabled_modules JSONB,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. TABELA DE USUÁRIOS, PINS OPERACIONAIS E PERFIS DE ACESSO (RBAC)
CREATE TABLE IF NOT EXISTS app_users (
  id TEXT PRIMARY KEY,
  email TEXT NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin', 'gerente', 'nutricionista', 'cozinheiro', 'estoquista', 'financeiro', 'atendente')),
  unit_id TEXT REFERENCES kitchen_units(id) ON DELETE SET NULL,
  pin TEXT,
  password_hash TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE app_users ADD COLUMN IF NOT EXISTS pin TEXT;

-- 10. TABELA DE AUDITORIA TÉRMICA & TERMOMETRIA (ANVISA RDC 216 - CHÃO DE FÁBRICA)
CREATE TABLE IF NOT EXISTS temperature_logs (
  id TEXT PRIMARY KEY,
  unit_id TEXT REFERENCES kitchen_units(id) ON DELETE SET NULL,
  equipment TEXT NOT NULL,
  equipment_type TEXT DEFAULT 'quente' CHECK (equipment_type IN ('quente', 'frio')),
  temperature NUMERIC NOT NULL,
  is_compliant BOOLEAN NOT NULL,
  time_str TEXT NOT NULL,
  shift TEXT NOT NULL,
  recorded_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE temperature_logs ADD COLUMN IF NOT EXISTS equipment_type TEXT DEFAULT 'quente';

-- 11. TABELA DE KARDEX & MOVIMENTAÇÕES DE ESTOQUE (RASTREABILIDADE PVPS)
CREATE TABLE IF NOT EXISTS stock_movements (
  id TEXT PRIMARY KEY,
  ingredient_id TEXT NOT NULL,
  ingredient_name TEXT NOT NULL,
  batch_id TEXT,
  lot_number TEXT,
  brand TEXT,
  type TEXT NOT NULL CHECK (type IN ('entrada', 'saida', 'perda', 'ajuste')),
  quantity NUMERIC NOT NULL,
  unit TEXT NOT NULL,
  unit_cost NUMERIC,
  total_cost NUMERIC,
  previous_stock NUMERIC NOT NULL,
  new_stock NUMERIC NOT NULL,
  reason TEXT NOT NULL,
  document_number TEXT,
  timestamp TEXT NOT NULL,
  user_name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. TABELA DE STATUS DE FILA KDS (SINCRONIZAÇÃO DE PRODUÇÃO NA COZINHA)
CREATE TABLE IF NOT EXISTS kds_dish_status (
  id TEXT PRIMARY KEY,
  unit_id TEXT REFERENCES kitchen_units(id) ON DELETE CASCADE,
  date_str TEXT NOT NULL,
  shift TEXT NOT NULL,
  recipe_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'a_iniciar' CHECK (status IN ('a_iniciar', 'preparando', 'pronto')),
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. TABELA DE KEEP-ALIVE / HEARTBEAT (ANTI-SLEEP NO SUPABASE FREE TIER)
CREATE TABLE IF NOT EXISTS system_heartbeat (
  id TEXT PRIMARY KEY,
  environment TEXT NOT NULL,
  last_ping_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  source TEXT NOT NULL DEFAULT 'github-actions'
);

-- ==============================================================================
-- SEGURANÇA E POLÍTICAS RLS (MODO PILOTO / DEMONSTRAÇÃO)
-- ==============================================================================

ALTER TABLE kitchen_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE technical_sheets ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_menu_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE waste_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE hot_box_deliveries ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposal_quotes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE app_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE temperature_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE stock_movements ENABLE ROW LEVEL SECURITY;
ALTER TABLE kds_dish_status ENABLE ROW LEVEL SECURITY;
ALTER TABLE system_heartbeat ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read/write kitchen_units" ON kitchen_units;
CREATE POLICY "Allow public read/write kitchen_units" ON kitchen_units FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write ingredients" ON ingredients;
CREATE POLICY "Allow public read/write ingredients" ON ingredients FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write technical_sheets" ON technical_sheets;
CREATE POLICY "Allow public read/write technical_sheets" ON technical_sheets FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write daily_menu_plans" ON daily_menu_plans;
CREATE POLICY "Allow public read/write daily_menu_plans" ON daily_menu_plans FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write waste_records" ON waste_records;
CREATE POLICY "Allow public read/write waste_records" ON waste_records FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write hot_box_deliveries" ON hot_box_deliveries;
CREATE POLICY "Allow public read/write hot_box_deliveries" ON hot_box_deliveries FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write proposal_quotes" ON proposal_quotes;
CREATE POLICY "Allow public read/write proposal_quotes" ON proposal_quotes FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write tenant_configs" ON tenant_configs;
CREATE POLICY "Allow public read/write tenant_configs" ON tenant_configs FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write app_users" ON app_users;
CREATE POLICY "Allow public read/write app_users" ON app_users FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write temperature_logs" ON temperature_logs;
CREATE POLICY "Allow public read/write temperature_logs" ON temperature_logs FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write stock_movements" ON stock_movements;
CREATE POLICY "Allow public read/write stock_movements" ON stock_movements FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write kds_dish_status" ON kds_dish_status;
CREATE POLICY "Allow public read/write kds_dish_status" ON kds_dish_status FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

DROP POLICY IF EXISTS "Allow public read/write system_heartbeat" ON system_heartbeat;
CREATE POLICY "Allow public read/write system_heartbeat" ON system_heartbeat FOR ALL TO anon, authenticated USING (true) WITH CHECK (true);

-- ==============================================================================
-- CARGA INICIAL DE DEMONSTRAÇÃO (SEED IDEMPOTENTE BONDEGUSTO)
-- ==============================================================================

INSERT INTO kitchen_units (id, name, code, type, address, manager_name, contact_email, average_pax_per_day, contract_price_per_pax, status)
VALUES
  ('unit-industrial', 'Unidade Industrial Metalmecânica (Fábrica Alpha)', 'IND-01', 'industrial', 'Av. das Indústrias, 4500 - Distrito Industrial', 'Carlos Mendonça', 'gerente.alpha@gastrocore.com.br', 550, 14.50, 'ativa'),
  ('unit-hospitalar', 'Unidade Hospitalar São Lucas (Clínica & Leitos)', 'HOSP-02', 'hospitalar', 'Rua das Palmeiras Médicas, 120 - Centro de Saúde', 'Dra. Vanessa Rios (RT)', 'rt.nutri@saolucas.com.br', 320, 18.90, 'ativa'),
  ('unit-escolar', 'Unidade Colégio Monteiro Lobato (Ensino Integral / PNAE)', 'ESC-03', 'escolar', 'Alameda dos Ipês, 880 - Bairro Jardins', 'Juliana Paiva', 'nutricao@monteiro.edu.br', 420, 12.80, 'ativa')
ON CONFLICT (id) DO NOTHING;

INSERT INTO tenant_configs (id, company_name, trading_name, cnpj, primary_color, active_plan, enabled_modules)
VALUES (
  'default_tenant',
  'Bondegusto Alimentação & Serviços Ltda',
  'Bondegusto Refeições Coletivas',
  '24.680.135/0001-88',
  '#059669',
  'pro',
  '{"fichasTecnicas": true, "cardapiosDietas": true, "estoqueLotes": true, "desperdicioRealtime": true, "logisticaHotbox": true, "orcamentosEventos": true, "relatoriosCustos": true, "auditoriaRDC216": true}'::jsonb
)
ON CONFLICT (id) DO NOTHING;

INSERT INTO app_users (id, email, full_name, role, unit_id, pin, password_hash)
VALUES
  ('user-admin', 'admin@gastrolab.com.br', 'Helena Tavares (Diretora Geral Lab)', 'admin', NULL, '7100', 'LabAdmin#2026'),
  ('user-gerente', 'gerente@gastrolab.com.br', 'Carlos Henrique (Gerente Operacional)', 'gerente', 'unit-industrial', '7200', 'LabGerente#2026'),
  ('user-nutri', 'nutri@gastrolab.com.br', 'Dra. Beatriz Moura (Nutricionista RT)', 'nutricionista', 'unit-hospitalar', '7300', 'LabNutri#2026'),
  ('user-chef', 'chef@gastrolab.com.br', 'Chef Antônio Silva (Chefe de Produção)', 'cozinheiro', 'unit-industrial', '8100', 'LabChef#2026'),
  ('user-estoque', 'estoque@gastrolab.com.br', 'Rafael Costa (Almoxarife)', 'estoquista', 'unit-industrial', '7400', 'LabEstoque#2026'),
  ('user-financeiro', 'financeiro@gastrolab.com.br', 'Juliana Prado (Controladoria & CMV)', 'financeiro', NULL, '7500', 'LabFin#2026'),
  ('user-atendente', 'atendente@gastrolab.com.br', 'Larissa Gomes (Atendente de Salão)', 'atendente', 'unit-escolar', '8200', 'LabAtend#2026')
ON CONFLICT (id) DO NOTHING;
